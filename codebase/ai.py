"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.
    Thông báo lỗi ở đây đã được che key (xem _redact) vì nó đi vào trace và cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Model thật: MODEL_PROVIDER = deepseek | openai (cả hai dùng API kiểu OpenAI "chat completions").
    .env: MODEL_PROVIDER, MODEL_NAME, API_KEY (bắt buộc) · MODEL_BASE_URL, MODEL_MAX_TOKENS (tuỳ chọn, mặc định 700).
    Hướng dẫn nhóm: docs/model-setup-nhom.md. Không dán API key vào file này. Chỉ dùng thư viện chuẩn (urllib).
"""
import contextlib
import json
import os
import re
import time
import urllib.error
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()

TIMEOUT_S = 30          # mỗi lần gọi
RETRY_WAIT_S = 2        # chờ trước lần thử lại (tối đa 1 lần thử lại)
DEFAULT_MAX_TOKENS = 700

# Cả hai nhà cung cấp dùng POST <base_url>/chat/completions, header "Authorization: Bearer <key>".
# Nguồn (đọc 27/11/2026):
#   DeepSeek: api-docs.deepseek.com — base_url https://api.deepseek.com, "POST /chat/completions", tham số max_tokens.
#             deepseek-flash MẶC ĐỊNH BẬT chế độ suy nghĩ; tắt bằng {"thinking": {"type": "disabled"}} (đưa thẳng vào body).
#   OpenAI:   developers.openai.com/api/reference/resources/chat — "POST /chat/completions" ở https://api.openai.com/v1;
#             max_tokens đã "deprecated in favor of max_completion_tokens".
PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com", "max_key": "max_tokens",
                 "extra": {"thinking": {"type": "disabled"}}},
    "openai": {"base_url": "https://api.openai.com/v1", "max_key": "max_completion_tokens", "extra": {}},
}


class MissingConfigError(NotImplementedError):
    """Thiếu API_KEY / MODEL_NAME hoặc provider lạ. Là NotImplementedError để khung (run.py eval, simulate, app.py)
    báo "chưa nối model" và DỪNG, không ghi file lượt nào — tránh sinh lượt chấm hỏng khi quên điền key."""


def _redact(text) -> str:
    """Che key khỏi mọi thông báo lỗi (lỗi đi vào trace, cột error và màn hình). Phản hồi 401 của OpenAI còn in một phần key."""
    t = str(text)
    if API_KEY:
        t = t.replace(API_KEY, "***")
    t = re.sub(r"(?i)bearer\s+[\w\-\.\*]+", "Bearer ***", t)
    t = re.sub(r"\bsk-[\w\-\*\.]{4,}", "sk-***", t)
    return t


_min_max_tokens = [0]   # sàn tạm thời do max_tokens_at_least() đặt (0 = không có)


@contextlib.contextmanager
def max_tokens_at_least(n: int):
    """Trong khối `with`, mỗi lần gọi model được phép ra ÍT NHẤT n token (lấy số lớn hơn giữa n và
    MODEL_MAX_TOKENS / mặc định). Dùng cho bước cần JSON dài hơn mà KHÔNG đổi chữ ký call_model(system, user)."""
    old = _min_max_tokens[0]
    _min_max_tokens[0] = max(old, int(n))
    try:
        yield
    finally:
        _min_max_tokens[0] = old


def _max_tokens() -> int:
    raw = (os.environ.get("MODEL_MAX_TOKENS") or "").strip()
    if not raw:
        return max(DEFAULT_MAX_TOKENS, _min_max_tokens[0])
    try:
        n = int(raw)
        if n < 1:
            raise ValueError
    except ValueError:
        raise MissingConfigError("MODEL_MAX_TOKENS trong .env phải là số nguyên ≥1 (đang là %r). Để trống = %d."
                                 % (raw, DEFAULT_MAX_TOKENS))
    return max(n, _min_max_tokens[0])


def _url(spec) -> str:
    base = (os.environ.get("MODEL_BASE_URL") or "").strip() or spec["base_url"]
    base = base.rstrip("/")
    return base if base.endswith("/chat/completions") else base + "/chat/completions"


def _wants_json(system: str) -> bool:
    """Prompt hệ thống của agent đòi JSON (chứa chữ "JSON") → bật chế độ ép JSON của API.
    Cả hai API đều đòi prompt nhắc tới JSON thì mới cho bật. Chữ ký call_model không đổi."""
    return "json" in (system or "").lower()


def build_body(system: str, user: str, spec: dict) -> dict:
    messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
    body = {"model": MODEL_NAME, "messages": messages, spec["max_key"]: _max_tokens()}
    body.update(spec["extra"])
    if _wants_json(system):
        body["response_format"] = {"type": "json_object"}
    return body


def _retryable(code: int, body_text: str) -> bool:
    """429 và 5xx thì thử lại. 429 do hết hạn mức / số dư (billing) thì KHÔNG: thử lại cũng không khỏi."""
    if code == 429:
        low = body_text.lower()
        return not any(w in low for w in ("quota", "credit", "balance", "spend", "billing"))
    return 500 <= code <= 599


def _http_message(code: int, body_text: str) -> str:
    if code in (401, 403):   # không in phản hồi: có thể chứa một phần key
        return "HTTP %d: key bị từ chối (sai, hết hạn hoặc không đủ quyền). Kiểm API_KEY trong .env." % code
    hint = " (hết số dư hoặc hạn mức tài khoản)" if code == 402 or "quota" in body_text.lower() else ""
    return "HTTP %d%s: %s" % (code, hint, _redact(body_text)[:300])


def _post(url: str, headers: dict, body: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers=dict({"Content-Type": "application/json"}, **headers))
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        return json.loads(r.read().decode("utf-8"))


def request_json(url: str, headers: dict, body: dict) -> dict:
    """POST, thử lại TỐI ĐA 1 lần (chờ RETRY_WAIT_S) khi lỗi mạng / HTTP 429 / 5xx. Lỗi khác bay ra ngay.
    Mọi exception ném ra đã che key và không chứa header Authorization."""
    for attempt in (1, 2):
        try:
            return _post(url, headers, body)
        except urllib.error.HTTPError as e:
            try:
                text = e.read().decode("utf-8", "replace")
            except Exception:
                text = ""
            if attempt == 1 and _retryable(e.code, text):
                pass
            else:
                raise RuntimeError(_http_message(e.code, text)) from None
        except ValueError:  # JSON hỏng (json.JSONDecodeError là ValueError)
            raise RuntimeError("Phản hồi API không phải JSON hợp lệ.") from None
        except OSError as e:  # URLError, hết giờ (TimeoutError), mất mạng
            if attempt == 2:
                raise RuntimeError("Lỗi mạng khi gọi model (%s): %s" % (type(e).__name__, _redact(e))) from None
        time.sleep(RETRY_WAIT_S)


def _tokens_out(usage: dict) -> int:
    """Token ra = completion_tokens. Token suy luận (completion_tokens_details.reasoning_tokens) được API tính vào
    completion_tokens (OpenAI: "Reported output token usage includes all tokens generated", chỉ là một phần
    BÓC TÁCH — không cộng hai lần). Riêng DeepSeek tài liệu không nói rõ; deepseek-flash đã tắt suy nghĩ
    nên reasoning_tokens = 0. Phòng khi một API nào đó tính riêng: chỉ cộng thêm reasoning_tokens khi
    total_tokens của CHÍNH phản hồi đó khớp prompt + completion + reasoning (tức nó chưa nằm trong completion)."""
    comp = usage["completion_tokens"]
    details = usage.get("completion_tokens_details")
    reasoning = details.get("reasoning_tokens") if isinstance(details, dict) else 0
    total = usage.get("total_tokens")
    if (isinstance(reasoning, int) and not isinstance(reasoning, bool) and reasoning > 0
            and isinstance(total, int) and total >= usage["prompt_tokens"] + comp + reasoning):
        return comp + reasoning
    return comp


def parse_response(data: dict) -> dict:
    """Phản hồi chat completions → 4 khoá của hợp đồng. Thiếu usage thì báo lỗi, không đoán token."""
    try:
        text = data["choices"][0]["message"].get("content") or ""
    except (KeyError, IndexError, TypeError, AttributeError):
        raise RuntimeError("Phản hồi API thiếu choices[0].message.content.") from None
    usage = data.get("usage")
    ok = (isinstance(usage, dict)
          and all(isinstance(usage.get(k), int) and not isinstance(usage.get(k), bool)
                  for k in ("prompt_tokens", "completion_tokens")))
    if not ok:
        raise RuntimeError("Phản hồi API thiếu usage.prompt_tokens / usage.completion_tokens — không ước lượng token.")
    served = str(data.get("model") or "").strip()
    # Trả tên đã yêu cầu khi API chỉ trả bản chốt của nó (vd gpt-4o-mini → gpt-4o-mini-2024-07-18), để simulate
    # tra đúng giá theo tên trong cost/personas.yaml. API trả model KHÁC hẳn thì giữ tên đó.
    name = MODEL_NAME if (not served or served.lower().startswith(MODEL_NAME.lower())) else served
    return {"text": text, "model": name, "tokens_in": usage["prompt_tokens"], "tokens_out": _tokens_out(usage)}


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER in ("", "fake"):
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    spec = PROVIDERS.get(MODEL_PROVIDER)
    if spec is None:
        raise MissingConfigError(
            "MODEL_PROVIDER=%s chưa được hỗ trợ trong codebase/ai.py (đang có: %s, fake). Nhà cung cấp có API kiểu OpenAI: "
            "thêm một mục vào PROVIDERS (base_url, max_key, extra) hoặc dùng MODEL_PROVIDER=openai kèm MODEL_BASE_URL. "
            "Kiểu API khác: xem docs/connect-model.md mục 2.4." % (MODEL_PROVIDER, ", ".join(sorted(PROVIDERS))))
    if not API_KEY:
        raise MissingConfigError("Thiếu API_KEY trong .env — chép .env.example thành .env rồi điền key (xem docs/model-setup-nhom.md).")
    if not MODEL_NAME:
        raise MissingConfigError("Thiếu MODEL_NAME trong .env (mã model, xem docs/model-setup-nhom.md).")

    data = request_json(_url(spec), {"Authorization": "Bearer " + API_KEY}, build_body(system, user, spec))
    return parse_response(data)
