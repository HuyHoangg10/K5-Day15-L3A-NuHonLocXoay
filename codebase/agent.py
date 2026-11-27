"""Luồng chính — agent xem tình trạng có CĂN CỨ XIN TẠM HOÃN gọi nhập ngũ hay không. NHÓM VIẾT.

`python run.py`, `python run.py eval`, `python run.py simulate` đều gọi answer(text).

Hợp đồng khung: answer(text: str) -> {"output": str}. Mỗi câu thử là MỘT chuỗi, MỘT lượt: "hỏi lại" là một kết quả (can_hoi_them).

Hình dạng: workflow cố định, 9 bước (sơ đồ ở spec.md §4):
  1 tiền xử lý (code) · 2 chặn đầu vào (code) · 3 trích dữ kiện (model→JSON) · 4 thiếu dữ kiện? (code)
  5 tra căn cứ (công cụ tra_dieu_luat) · 6 quyết định (model→JSON) · 7 kiểm đầu ra (code)
  8 định dạng (code) · 9 lỗi model / quá thời gian → thông báo lỗi lịch sự (code)

Tập nhãn: co_can_cu_xem_xet · khong_thuoc_dien_nay · can_hoi_them · tu_choi · ngoai_pham_vi
Sức khỏe KHÔNG phải quyết định riêng của agent: chỉ nói "kết luận do Hội đồng khám sức khỏe đưa ra".
Nội dung luật chỉ đến từ kho data/kb/dieu41.json (hiện là kho GIẢ, xem data/kb/README.md).
note() chỉ ghi LÝ DO, không bao giờ ghi nội dung người dùng gõ (trace không được chứa dữ liệu cá nhân).
"""
import json
import re
import time
import unicodedata

import prompts as P
from ai import call_model
from tools import all_codes, load_kb, tra_dieu_luat
from tracing import note

LABELS = P.LABELS
DEADLINE_S = 90          # tổng thời gian cho cả hai lần gọi model; quá thì báo lỗi lịch sự (bước 9)

# [CHỜ người A xác nhận theo văn bản gốc] Dữ kiện bắt buộc cho từng chủ đề (bước 4).
# Thiếu dữ kiện nào thì agent hỏi lại (can_hoi_them) thay vì kết luận.
REQUIRED_FACTS = {
    "hoc_tap": ["dang_hoc", "trinh_do", "he_chinh_quy"],
    "suc_khoe": ["co_giay_kham"],
}

BOOL_FACTS = ("dang_hoc", "he_chinh_quy", "qua_han", "bao_luu", "co_giay_kham")
Y_DO = ("hop_phap", "lach_luat", "ngoai_pham_vi")

# Cụm tuyệt đối: model viết ra là bị chặn ở bước 7 (không tự hứa kết quả)
ABSOLUTE_PHRASES = ["chắc chắn được", "chắc chắn sẽ được", "chắc chắn hợp lệ", "100%",
                    "giấy hợp lệ", "đảm bảo", "bảo đảm"]


# ================================================================ bước 1: tiền xử lý

_RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_RE_PHONE = re.compile(r"(?<!\w)(?:\+?84|0)(?:[\s.\-]?\d){9}(?!\d)")
_RE_CCCD = re.compile(r"(?<!\d)\d{12}(?!\d)")
_RE_CMND = re.compile(r"(?<!\d)\d{9}(?!\d)")


def preprocess(text: str):
    """NFKC, gộp khoảng trắng, che email / SĐT VN / CCCD (12 số) / CMND (9 số). → (văn bản đã che, danh sách loại đã che)."""
    t = unicodedata.normalize("NFKC", text or "")
    t = re.sub(r"\s+", " ", t).strip()
    kinds = []
    for kind, rx, token in (("email", _RE_EMAIL, "[EMAIL]"), ("sdt", _RE_PHONE, "[SĐT]"),
                            ("cccd", _RE_CCCD, "[CCCD]"), ("cmnd", _RE_CMND, "[CCCD]")):
        t, n = rx.subn(token, t)
        if n:
            kinds.append(kind)
    return t, kinds


# ================================================================ bước 2: chặn đầu vào

def _fold(s: str) -> str:
    """Bỏ dấu tiếng Việt, hạ chữ thường — để bắt cả câu gõ không dấu."""
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# Mẫu viết CÓ dấu, chữ thường. Cố ý hẹp: "giả sử", "đóng vai trò", "mua sách" không được dính.
_EVASION = [
    r"giả\s*(?:mạo\s*)?(?:giấy|hồ\s*sơ|bệnh\s*án|giấy\s*tờ|con\s*dấu|xác\s*nhận)",
    r"làm\s+giả",
    r"(?:giấy|hồ\s*sơ|bệnh\s*án)\s+(?:giả|khống)",
    r"\b(?:chạy|chạy\s+chọt)\s+(?:giấy|hoãn|miễn|khám|kết\s+luận|sức\s+khỏe|loại|trượt)",
    r"\bmua\s+(?:giấy|hồ\s*sơ|bệnh\s*án)?\s*(?:hoãn|miễn|tạm\s+hoãn|khám|sức\s+khỏe|kết\s+luận|xác\s+nhận|bệnh)",
    r"gian\s+lận\s+(?:khám|sức\s+khỏe|hồ\s*sơ|giấy|để)",
    r"khai\s+(?:man|gian|dối|khống)",
    r"(?:khám|đi\s+khám)\s+(?:thay|hộ|giùm|dùm)",
    r"(?:nhờ|thuê)\s+(?:người|ai)\s+(?:khác\s+)?(?:đi\s+)?khám",
    r"hối\s+lộ|đút\s+lót|lót\s+tay",
    r"lách\s+luật",
    r"(?:cách|làm\s+sao\s+để|làm\s+thế\s+nào\s+để|muốn)\s+(?:trốn|né|tránh)\s+(?:nghĩa\s+vụ|lính|quân\s+sự|nhập\s+ngũ|đi\s+bộ\s+đội|khám)",
    r"cố\s+ý\s+(?:gây|làm)\s+(?:thương\s+tích|hỏng|bệnh)",
]
_INJECTION = [
    r"bỏ\s+qua\s+(?:mọi\s+|tất\s+cả\s+|các\s+|những\s+)?(?:hướng\s+dẫn|chỉ\s+dẫn|lệnh|quy\s+tắc|luật\s+lệ|prompt)",
    r"(?:quên|phớt\s+lờ)\s+(?:mọi\s+|tất\s+cả\s+|các\s+|những\s+)?(?:hướng\s+dẫn|chỉ\s+dẫn|quy\s+tắc)",
    r"ignore\s+(?:all\s+|any\s+|the\s+|your\s+)?(?:previous|prior|above|earlier|instructions)",
    r"disregard\s+(?:all\s+|the\s+|your\s+)?(?:previous|prior|above|instructions)",
    r"(?:system|developer)\s+prompt|prompt\s+hệ\s+thống",
    r"tiết\s+lộ\s+(?:prompt|hướng\s+dẫn|cấu\s+hình)",
    r"giả\s+làm\s+\w+",
    r"đóng\s+vai\s+(?!trò)",
    r"bây\s+giờ\s+(?:bạn|mày|em)\s+là",
    r"you\s+are\s+now|pretend\s+(?:to|you)|jailbreak|developer\s+mode",
    r"chế\s+độ\s+(?:nhà\s+phát\s+triển|không\s+giới\s+hạn)",
]
_RX = {
    "lach_luat": ([re.compile(p) for p in _EVASION], [re.compile(_fold(p)) for p in _EVASION]),
    "chen_lenh": ([re.compile(p) for p in _INJECTION], [re.compile(_fold(p)) for p in _INJECTION]),
}


def screen_input(text: str):
    """Trả None nếu qua, hoặc "lach_luat" / "chen_lenh". Câu hỏi về hoãn HỢP PHÁP không được chặn.
    Câu có dấu: so mẫu có dấu (tránh "giá giấy" khớp nhầm "giả giấy"). Câu gõ KHÔNG dấu: so mẫu đã bỏ dấu."""
    low = text.lower()
    unaccented = _fold(text) == low
    for kind, (accented, folded) in _RX.items():
        patterns = folded if unaccented else accented
        if any(rx.search(low) for rx in patterns):
            return kind
    return None


# ================================================================ tiện ích JSON / định dạng

def parse_json(raw: str):
    """Lấy một đối tượng JSON từ chữ model trả về (chịu được khung ```json). Không được → None."""
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    for candidate in (s, s[s.find("{"): s.rfind("}") + 1] if "{" in s and "}" in s else ""):
        try:
            data = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def clean_facts(d: dict):
    """Chuẩn hóa dữ kiện model trích; kiểu sai → None (không biết). y_do sai / thiếu → trả None (coi là hỏng)."""
    if d.get("y_do") not in Y_DO:
        return None
    f = {k: (d.get(k) if isinstance(d.get(k), bool) else None) for k in BOOL_FACTS}
    tr = d.get("trinh_do")
    f["trinh_do"] = tr.strip() if isinstance(tr, str) and tr.strip() else None
    n = d.get("nam_thu")
    f["nam_thu"] = n if isinstance(n, int) and not isinstance(n, bool) and 0 < n <= 10 else None
    f["y_do"] = d["y_do"]
    return f


def render(nhan: str, giai_thich: str, viec: str = "", passages=None, kb_fake: bool = False) -> dict:
    """Bước 8. Dòng đầu LUÔN là `NHAN: <nhan>` để chấm bằng code."""
    lines = ["NHAN: " + nhan, "", "Giải thích: " + giai_thich]
    if viec:
        lines.append("Việc cần làm: " + viec)
    if passages:
        lines.append("Nguồn:")
        for p in passages:
            lines.append("- %s — %s; hiệu lực: %s; tải ngày %s; %s"
                         % (p["code"], p["van_ban"], p["hieu_luc"], p["ngay_tai"], p["url"]))
    else:
        lines.append("Nguồn: không dùng đoạn căn cứ nào.")
    if kb_fake and passages:
        lines.append(P.KB_FAKE_WARNING)
    lines.append("Lưu ý: " + P.DISCLAIMER)
    return {"output": "\n".join(lines)}


def safe_answer(reason: str) -> dict:
    """CÂU AN TOÀN cố định khi kiểm đầu ra hỏng (bước 7). Ghi lý do vào trace."""
    note("câu an toàn: " + reason)
    return render("can_hoi_them", P.SAFE_SENTENCE)


def error_answer(reason: str) -> dict:
    """Bước 9: lỗi model / quá thời gian. Không bịa, không có dòng NHAN."""
    note("lỗi: " + reason)
    return {"output": "LOI: " + P.ERROR_MESSAGE}


# ================================================================ bước 4: dữ kiện / chủ đề

def detect_topics(f: dict) -> list:
    topics = []
    if f["dang_hoc"] is not None or any(f[k] is not None for k in ("trinh_do", "he_chinh_quy", "nam_thu", "qua_han", "bao_luu")):
        topics.append("hoc_tap")
    if f["co_giay_kham"] is not None:
        topics.append("suc_khoe")
    return topics


def missing_facts(f: dict, topics: list) -> list:
    need = []
    for t in topics:
        req = REQUIRED_FACTS[t]
        if t == "hoc_tap" and f["dang_hoc"] is False:   # không đi học: chỉ cần biết điều đó
            req = ["dang_hoc"]
        for k in req:
            if f[k] is None and k not in need:
                need.append(k)
    return need


# ================================================================ bước 7: kiểm đầu ra

def validate_decision(raw: str):
    """→ (quyết định đã chuẩn hóa, None) nếu đạt; (None, lý do) nếu hỏng."""
    d = parse_json(raw)
    if d is None:
        return None, "JSON không hợp lệ"
    nhan = d.get("nhan")
    if nhan not in LABELS:
        return None, "nhãn ngoài tập nhãn"
    codes = d.get("ma_dieu_khoan", [])
    if codes is None:
        codes = []
    if not isinstance(codes, list) or not all(isinstance(c, str) for c in codes):
        return None, "ma_dieu_khoan không phải danh sách chuỗi"
    codes = list(dict.fromkeys(c.strip() for c in codes))
    known = all_codes()
    bad = [c for c in codes if c not in known]
    if bad:
        return None, "mã điều khoản không có trong kho"
    if nhan == "co_can_cu_xem_xet" and not codes:
        return None, "co_can_cu_xem_xet nhưng không có mã nào"
    ly_do = d.get("ly_do")
    if not isinstance(ly_do, str) or not ly_do.strip():
        return None, "thiếu ly_do"
    viec = d.get("can_lam_gi", "")
    if isinstance(viec, list):
        viec = "; ".join(str(x) for x in viec)
    if not isinstance(viec, str):
        return None, "can_lam_gi sai kiểu"
    low = unicodedata.normalize("NFKC", ly_do + " " + viec).lower()
    if any(p in low for p in ABSOLUTE_PHRASES):
        return None, "chứa cụm tuyệt đối"
    return {"nhan": nhan, "ma_dieu_khoan": codes, "ly_do": ly_do.strip(), "can_lam_gi": viec.strip()}, None


# ================================================================ answer

def answer(text: str) -> dict:
    t0 = time.monotonic()

    # 1. Tiền xử lý
    clean, masked = preprocess(text if isinstance(text, str) else "")
    if masked:
        note("tiền xử lý: đã che " + ", ".join(masked))
    if not clean:
        note("đầu vào rỗng")
        return render("can_hoi_them", "Mình chưa nhận được nội dung nào.",
                      "Hãy mô tả tình trạng của bạn: " + P.TOPIC_QUESTION + ".")

    # 2. Chặn đầu vào (không gọi model)
    hit = screen_input(clean)
    if hit:
        note("chặn đầu vào: " + hit + " — không gọi model")
        return render("tu_choi", P.REFUSE_EVASION if hit == "lach_luat" else P.REFUSE_INJECTION)

    # 3. Trích dữ kiện (model → JSON)
    try:
        res = call_model(P.SYSTEM_TRICH, P.user_trich(clean))
    except NotImplementedError:
        raise                     # khung báo "chưa nối model"
    except Exception as e:        # hết lượt, mất mạng, quá thời gian…: lỗi đã được @model_call ghi vào trace
        return error_answer("trích dữ kiện — " + type(e).__name__)
    parsed = parse_json(res.get("text"))
    facts = clean_facts(parsed) if parsed is not None else None
    if facts is None:
        return safe_answer("trích dữ kiện: JSON hỏng hoặc y_do không hợp lệ")
    if facts["y_do"] == "lach_luat":
        note("model đánh dấu y_do=lach_luat — không tra căn cứ")
        return render("tu_choi", P.REFUSE_EVASION)
    if facts["y_do"] == "ngoai_pham_vi":
        note("model đánh dấu y_do=ngoai_pham_vi — không tra căn cứ")
        return render("ngoai_pham_vi", P.OUT_OF_SCOPE)

    # 4. Thiếu dữ kiện bắt buộc → can_hoi_them (code)
    topics = detect_topics(facts)
    if not topics:
        note("thiếu dữ kiện: chưa rõ chủ đề")
        return render("can_hoi_them", "Mình chưa biết bạn đang muốn xét căn cứ nào.",
                      "Cho mình biết: " + P.TOPIC_QUESTION + ".")
    need = missing_facts(facts, topics)
    if need:
        note("thiếu dữ kiện: " + ", ".join(need))
        return render("can_hoi_them", "Chưa đủ dữ kiện để nhận định.",
                      "Cho mình biết thêm: " + "; ".join(P.FACT_QUESTIONS[k] for k in need) + ".")

    # 5. Tra căn cứ (công cụ)
    try:
        passages = []
        for chu_de in topics:
            for p in tra_dieu_luat(chu_de):
                if p["code"] not in {q["code"] for q in passages}:
                    passages.append(p)
        kb_fake = load_kb()["la_kho_gia"]
    except Exception as e:        # thiếu / hỏng kho
        return error_answer("tra căn cứ — " + type(e).__name__)
    note("tra căn cứ: %d đoạn, chủ đề %s" % (len(passages), "+".join(topics)))

    # 6. Quyết định (model → JSON)
    if time.monotonic() - t0 > DEADLINE_S:
        return error_answer("quá thời gian trước bước quyết định")
    try:
        res = call_model(P.SYSTEM_QUYET_DINH, P.user_quyet_dinh(clean, facts, passages))
    except NotImplementedError:
        raise
    except Exception as e:
        return error_answer("quyết định — " + type(e).__name__)

    # 7. Kiểm đầu ra (code)
    try:
        decision, why = validate_decision(res.get("text"))
    except Exception as e:        # không đọc được kho để kiểm mã → không dám tin đầu ra
        return error_answer("kiểm đầu ra — " + type(e).__name__)
    if decision is None:
        return safe_answer(why)

    # 8. Định dạng đầu ra
    by_code = {p["code"]: p for p in passages}
    cited = [by_code[c] if c in by_code else next(q for q in load_kb()["doan"] if q["code"] == c)
             for c in decision["ma_dieu_khoan"]]
    note("quyết định: " + decision["nhan"])
    return render(decision["nhan"], decision["ly_do"], decision["can_lam_gi"], cited, kb_fake)
