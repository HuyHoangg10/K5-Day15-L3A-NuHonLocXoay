"""Web demo Trợ lý NVQS — máy chủ nhỏ, chỉ dùng thư viện chuẩn.

Chạy:  python web/server.py            (mở http://127.0.0.1:8765)
Nối vào agent có sẵn: codebase/agent.py → answer(text) → {"output": str}. Không sửa agent/tracing.
Không ghi log nội dung câu hỏi; không trả traceback ra trình duyệt.
"""
import collections
import csv
import inspect
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import tracing  # noqa: E402
import kb  # noqa: E402
import agent  # noqa: E402
try:  # bộ nhớ hội thoại (nhánh feat/chat-memory): chưa merge thì không có, web chạy một lượt như cũ
    import session as chat_session  # noqa: E402
except Exception:  # pragma: no cover
    chat_session = None
import ai  # noqa: E402  (nạp .env)

STATIC = os.path.join(HERE, "static")
SOURCES_CSV = os.path.join(ROOT, "kb-nvqs", "SOURCES.csv")
MAX_BODY = 32 * 1024
BUSY_WAIT_S = 3          # chờ tối đa bấy nhiêu giây để vào hàng; quá thì báo bận
ANSWER_FN = None         # test thay bằng stub (đánh dấu rõ); None = agent.answer thật
_lock = threading.Lock()  # tracing dùng trạng thái toàn cục → mỗi lúc chỉ một yêu cầu qua agent

MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8"}

SHEET_ENTRIES = {
    "session_id": "entry.1442197971",
    "question_masked": "entry.193704735",
    "nhan": "entry.1264836539",
    "can_cu": "entry.1621608250",
    "model": "entry.792190072",
    "latency_s": "entry.1665943169",
}


def _sheet_log_url():
    u = (os.environ.get("SHEET_LOG_URL") or "").strip()
    return u if u.startswith("https://docs.google.com/forms/") else ""


def _build_sheet_payload(message, nhan, cites, latency_s, session_id="web"):
    """Chuẩn bị payload đã che PII/key để gửi Google Form (không lưu raw input)."""
    clean_q = ai._redact(agent.preprocess(message)[0])[:500]
    can_cu = ", ".join(c["id"] for c in (cites or []) if isinstance(c, dict) and c.get("id"))
    model_name = ai.MODEL_NAME or mode()
    return {
        SHEET_ENTRIES["session_id"]: str(session_id or "web")[:64],
        SHEET_ENTRIES["question_masked"]: clean_q,
        SHEET_ENTRIES["nhan"]: str(nhan or ""),
        SHEET_ENTRIES["can_cu"]: can_cu,
        SHEET_ENTRIES["model"]: str(model_name),
        SHEET_ENTRIES["latency_s"]: str(round(float(latency_s), 2)),
    }


def _log_to_sheet_async(message, nhan, cites, latency_s, session_id="web"):
    """Gửi log ngầm (daemon thread) khi .env đặt SHEET_LOG_URL. Lỗi mạng bỏ qua, không chặn chat."""
    url = _sheet_log_url()
    if not url:
        return
    data = urllib.parse.urlencode(_build_sheet_payload(message, nhan, cites, latency_s, session_id)).encode("utf-8")

    def _send():
        try:
            req = urllib.request.Request(url, data=data, method="POST",
                                         headers={"Content-Type": "application/x-www-form-urlencoded"})
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            pass

    threading.Thread(target=_send, daemon=True).start()


def _safe_url(u):
    u = (u or "").strip()
    return u if re.match(r"^https?://[^\s]+$", u) else ""


def load_sources():
    """Danh mục nguồn chung từ kb-nvqs/SOURCES.csv: chỉ tên, số hiệu, ghi chú hiệu lực của nhóm và URL http(s)."""
    out = []
    try:
        with open(SOURCES_CSV, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                out.append({"so_hieu": r.get("so_hieu", ""), "ten": r.get("ten", ""),
                            "hieu_luc": r.get("hieu_luc", ""), "url": _safe_url(r.get("url"))})
    except OSError:
        pass
    return out


def split_output(output):
    """Tách dòng NHAN:/CAN_CU: (nếu có đúng định dạng) và ánh xạ id qua kb.get_chunk. Không đoán gì thêm."""
    lines = output.split("\n")
    nhan, ids = "", []
    if len(lines) >= 2 and lines[0].startswith("NHAN:") and lines[1].startswith("CAN_CU:"):
        nhan = lines[0][5:].strip()
        ids = [i.strip() for i in lines[1][7:].split(",") if i.strip()]
    cites = []
    for cid in ids:
        c = kb.get_chunk(cid)
        if not c:
            cites.append({"id": cid, "ten": cid, "url": "", "known": False})
            continue
        if kb.is_qa_id(cid):
            cites.append({"id": cid, "ten": c.get("title", cid), "url": _safe_url(c.get("url")), "known": True})
        else:
            label = "Điều %s" % c.get("dieu") + (" khoản %s" % c["khoan"] if c.get("khoan") else "") \
                + (" điểm %s" % c["diem"] if c.get("diem") else "")
            cites.append({"id": cid, "ten": "%s · %s" % (label, c.get("so_hieu", "")),
                          "url": _safe_url(c.get("nguon")), "known": True})
    return nhan, cites


def ref_names(output):
    """Id trong các dòng '- <id> — ...' (Nguồn / Tham khảo) → tên đọc được + URL, lấy từ kho; id lạ thì bỏ qua."""
    refs = {}
    for m in re.finditer(r"^- ([\w.-]+) — ", output, re.M):
        cid = m.group(1)
        c = kb.get_chunk(cid)
        if not c:
            continue
        if kb.is_qa_id(cid):
            refs[cid] = {"ten": c.get("title", cid), "url": _safe_url(c.get("url"))}
        else:
            label = "Điều %s" % c.get("dieu") + (" khoản %s" % c["khoan"] if c.get("khoan") else "")                 + (" điểm %s" % c["diem"] if c.get("diem") else "")
            refs[cid] = {"ten": "%s · %s" % (label, c.get("so_hieu", "")), "url": _safe_url(c.get("nguon"))}
    return refs


MAX_SESSIONS = 300
_sessions = collections.OrderedDict()   # id -> ChatSession; quá MAX_SESSIONS thì bỏ phiên lâu nhất


def uses_memory(fn=None):
    """True khi agent nhận tham số session và codebase/session.py có mặt."""
    fn = fn or ANSWER_FN or agent.answer
    try:
        return chat_session is not None and "session" in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def _get_session(sid):
    if not re.fullmatch(r"[\w-]{8,64}", sid or ""):
        return None
    s = _sessions.pop(sid, None) or chat_session.ChatSession(sid)
    _sessions[sid] = s
    while len(_sessions) > MAX_SESSIONS:
        _sessions.popitem(last=False)
    return s


def run_agent(message, session_id="web"):
    """Gọi agent trong khoá. Trả (http_status, dict)."""
    if not _lock.acquire(timeout=BUSY_WAIT_S):
        return 503, {"error": "Máy chủ đang xử lý câu hỏi khác. Hãy thử lại sau ít giây."}
    try:
        fn = ANSWER_FN or agent.answer
        t0 = time.perf_counter()
        tracing.begin("web")
        try:
            sess = _get_session(session_id) if uses_memory(fn) else None
            res = fn(message, session=sess) if sess is not None else fn(message)
            out = res.get("output") if isinstance(res, dict) else None
        except Exception:
            return 500, {"error": "Agent gặp lỗi khi xử lý. Hãy thử lại."}
        finally:
            try:
                tracing.end()
            except Exception:
                pass
        if not isinstance(out, str) or not out.strip():
            return 500, {"error": "Agent không trả nội dung. Hãy thử lại."}
        nhan, cites = split_output(out)
        if ANSWER_FN is None:
            _log_to_sheet_async(message, nhan, cites, time.perf_counter() - t0, session_id=session_id)
        return 200, {"output": out, "nhan": nhan, "citations": cites, "refs": ref_names(out)}
    finally:
        _lock.release()


def mode():
    return "fake" if ai.MODEL_PROVIDER == "fake" else "real"


class Handler(BaseHTTPRequestHandler):
    server_version = "NVQSDemo"
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # không ghi log truy cập (tránh lộ nội dung)
        pass

    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0].strip("[]").lower()
        origin = (self.headers.get("Origin") or "").strip().lower()
        allow_origin = (os.environ.get("WEB_ALLOW_ORIGIN") or "").strip().rstrip("/").lower()
        allow_host = ""
        if allow_origin and re.match(r"^https://[a-z0-9-]+(\.[a-z0-9-]+)*$", allow_origin):
            allow_host = allow_origin.split("://", 1)[1]
        if host not in ("localhost", "127.0.0.1", "::1") and not (allow_host and host == allow_host):
            return False
        if not origin or re.match(r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$", origin):
            return True
        if allow_origin and origin == allow_origin:
            return True
        return False

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {"error": "Chỉ truy cập qua localhost."})
        path = self.path.split("?")[0]
        if path == "/api/sources":
            return self._send(200, {"sources": load_sources()})
        if path == "/api/info":
            return self._send(200, {"memory": uses_memory(), "mode": mode(), "max_chars": agent.MAX_INPUT_CHARS, "wait_s": agent.DEADLINE_S})
        name = {"/": "index.html", "/legacy": "legacy.html", "/legacy/": "legacy.html"}.get(path, path.lstrip("/"))
        if name in ("index.html", "legacy.html", "app.css", "legacy.css", "app.js"):
            with open(os.path.join(STATIC, name), "rb") as f:
                return self._send(200, f.read(), MIME[os.path.splitext(name)[1]])
        self._send(404, {"error": "Không tìm thấy."})

    def do_POST(self):
        if not self._host_ok():
            return self._send(403, {"error": "Chỉ truy cập qua localhost."})
        if self.path.split("?")[0] != "/api/chat":
            return self._send(404, {"error": "Không tìm thấy."})
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = -1
        if n <= 0 or n > MAX_BODY:
            return self._send(400, {"error": "Nội dung gửi không hợp lệ hoặc quá lớn."})
        try:
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
            msg = payload.get("message")
            sid = payload.get("session_id")
        except Exception:
            return self._send(400, {"error": "Dữ liệu gửi không phải JSON hợp lệ."})
        if not isinstance(msg, str) or not msg.strip():
            return self._send(400, {"error": "Hãy nhập câu hỏi trước khi gửi."})
        if len(msg) > agent.MAX_INPUT_CHARS:
            return self._send(400, {"error": "Câu hỏi quá dài (tối đa %d ký tự)." % agent.MAX_INPUT_CHARS})
        code, body = run_agent(msg, sid if isinstance(sid, str) else "web")
        self._send(code, body)


def make_server(host="127.0.0.1", port=8765):
    return ThreadingHTTPServer((host, port), Handler)


def main():
    port = int(os.environ.get("WEB_PORT") or 8765)
    srv = make_server("127.0.0.1", port)
    print("Trợ lý NVQS (demo) chạy tại http://127.0.0.1:%d — dừng bằng Ctrl+C" % port)
    print("Chế độ model:", "THẬT" if mode() == "real" else "GIẢ (fake) — kết quả chưa phải model thật")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")


if __name__ == "__main__":
    main()
