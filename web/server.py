"""Web demo Trợ lý NVQS — máy chủ nhỏ, chỉ dùng thư viện chuẩn.

Chạy:  python web/server.py            (mở http://127.0.0.1:8765)
Nối vào agent có sẵn: codebase/agent.py → answer(text) → {"output": str}. Không sửa agent/tracing.
Không ghi log nội dung câu hỏi; không trả traceback ra trình duyệt.
"""
import csv
import json
import os
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import tracing  # noqa: E402
import kb  # noqa: E402
import agent  # noqa: E402
import ai  # noqa: E402  (nạp .env)

STATIC = os.path.join(HERE, "static")
SOURCES_CSV = os.path.join(ROOT, "kb-nvqs", "SOURCES.csv")
MAX_BODY = 32 * 1024
BUSY_WAIT_S = 3          # chờ tối đa bấy nhiêu giây để vào hàng; quá thì báo bận
ANSWER_FN = None         # test thay bằng stub (đánh dấu rõ); None = agent.answer thật
_lock = threading.Lock()  # tracing dùng trạng thái toàn cục → mỗi lúc chỉ một yêu cầu qua agent

MIME = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8"}


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


def run_agent(message):
    """Gọi agent trong khoá. Trả (http_status, dict)."""
    if not _lock.acquire(timeout=BUSY_WAIT_S):
        return 503, {"error": "Máy chủ đang xử lý câu hỏi khác. Hãy thử lại sau ít giây."}
    try:
        fn = ANSWER_FN or agent.answer
        tracing.begin("web")
        try:
            res = fn(message)
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
        return 200, {"output": out, "nhan": nhan, "citations": cites}
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
        if host not in ("localhost", "127.0.0.1", "::1"):
            return False
        origin = self.headers.get("Origin")
        if not origin or re.match(r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$", origin):
            return True
        # tunnel tạm (vd trycloudflare.com): chỉ khi người chạy bật WEB_ALLOW_ORIGIN_SUFFIX
        suf = (os.environ.get("WEB_ALLOW_ORIGIN_SUFFIX") or "").strip().lower()
        return bool(suf) and re.match(r"^https://[a-z0-9-]+(\.[a-z0-9-]+)*$", origin) is not None and origin.endswith(suf)

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
            return self._send(200, {"mode": mode(), "max_chars": agent.MAX_INPUT_CHARS, "wait_s": agent.DEADLINE_S})
        name = "index.html" if path == "/" else path.lstrip("/")
        if name in ("index.html", "app.css", "app.js"):
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
            msg = json.loads(self.rfile.read(n).decode("utf-8")).get("message")
        except Exception:
            return self._send(400, {"error": "Dữ liệu gửi không phải JSON hợp lệ."})
        if not isinstance(msg, str) or not msg.strip():
            return self._send(400, {"error": "Hãy nhập câu hỏi trước khi gửi."})
        if len(msg) > agent.MAX_INPUT_CHARS:
            return self._send(400, {"error": "Câu hỏi quá dài (tối đa %d ký tự)." % agent.MAX_INPUT_CHARS})
        code, body = run_agent(msg)
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
