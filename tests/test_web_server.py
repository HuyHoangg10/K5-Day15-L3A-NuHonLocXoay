"""Kiểm thử web demo (web/server.py). Agent bị THAY BẰNG STUB (đánh dấu STUB) — không gọi model thật."""
import http.client
import json
import os
import sys
import threading
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "web"))
import server  # noqa: E402


def stub_answer(text):  # STUB: không phải agent thật
    if "boom" in text:
        raise RuntimeError("secret-traceback-xyz")
    if "slow" in text:
        time.sleep(0.4)
    if "refuse" in text:
        return {"output": "NHAN: refuse\nCAN_CU: vbhn133-d10\n\nGiải thích: không hỗ trợ."}
    if "html" in text:
        return {"output": "NHAN: need_more_information\nCAN_CU: \n\nGiải thích: <script>alert(1)</script>"}
    return {"output": "NHAN: eligible_for_review\nCAN_CU: vbhn133-d41-k1-g,qa-q01\n\nGiải thích: echo " + text}


class WebTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = server.ANSWER_FN
        server.ANSWER_FN = stub_answer
        cls.srv = server.make_server("127.0.0.1", 0)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        server.ANSWER_FN = cls.old

    def req(self, method, path, body=None, headers=None, raw=None):
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        c.request(method, path, data, headers or {"Content-Type": "application/json"})
        r = c.getresponse()
        txt = r.read().decode("utf-8")
        c.close()
        try:
            return r.status, json.loads(txt)
        except ValueError:
            return r.status, txt

    def test_normal_and_citations(self):
        st, j = self.req("POST", "/api/chat", {"message": "hello"})
        self.assertEqual(st, 200)
        self.assertEqual(j["nhan"], "eligible_for_review")
        self.assertIn("Giải thích: echo hello", j["output"])
        ids = [c["id"] for c in j["citations"]]
        self.assertEqual(ids, ["vbhn133-d41-k1-g", "qa-q01"])
        self.assertTrue(j["citations"][0]["ten"].startswith("Điều 41 khoản 1 điểm g"))
        self.assertTrue(j["citations"][0]["url"].startswith("https://"))
        self.assertEqual(j["refs"], {})  # stub không có dòng "- id — ..."

    def test_refs_names_from_kb(self):
        out = ("NHAN: x\nCAN_CU: \n\nNguồn:\n- vbhn133-d41-k1-g — 133/2026/VBHN-LQ-VPQH; u; kiểm tra ngày 27/11/2026\n"
               "- qa-q01 — t; u")
        refs = server.ref_names(out)
        self.assertTrue(refs["vbhn133-d41-k1-g"]["ten"].startswith("Điều 41 khoản 1 điểm g"))
        self.assertIn("qa-q01", refs)

    def test_refuse_is_http_200(self):
        st, j = self.req("POST", "/api/chat", {"message": "refuse"})
        self.assertEqual((st, j["nhan"]), (200, "refuse"))

    def test_html_returned_verbatim(self):
        st, j = self.req("POST", "/api/chat", {"message": "html"})
        self.assertIn("<script>alert(1)</script>", j["output"])  # FE dùng textContent nên không chạy

    def test_agent_error_no_traceback(self):
        st, j = self.req("POST", "/api/chat", {"message": "boom"})
        self.assertEqual(st, 500)
        self.assertNotIn("secret-traceback-xyz", json.dumps(j))

    def test_bad_requests(self):
        self.assertEqual(self.req("POST", "/api/chat", raw=b"not json")[0], 400)
        self.assertEqual(self.req("POST", "/api/chat", {"message": "   "})[0], 400)
        self.assertEqual(self.req("POST", "/api/chat", {"message": 5})[0], 400)
        self.assertEqual(self.req("POST", "/api/chat", {"message": "a" * 5000})[0], 400)

    def test_host_header_rejected(self):
        st, _ = self.req("GET", "/api/sources", headers={"Host": "evil.example"})
        self.assertEqual(st, 403)

    def test_sources_match_csv(self):
        st, j = self.req("GET", "/api/sources")
        self.assertEqual(st, 200)
        self.assertGreater(len(j["sources"]), 3)
        self.assertTrue(all(s["url"] == "" or s["url"].startswith("http") for s in j["sources"]))

    def test_static_files(self):
        for p in ("/", "/legacy", "/app.css", "/legacy.css", "/app.js"):
            st, _ = self.req("GET", p)
            self.assertEqual(st, 200)
        self.assertEqual(self.req("GET", "/../server.py")[0], 404)

    def test_concurrent_no_mixup_and_serialized_tracing(self):
        active, peak, out = [0], [0], {}
        orig = server.tracing.begin

        def counting_begin(cid):
            active[0] += 1
            peak[0] = max(peak[0], active[0])
            orig(cid)
        end_orig = server.tracing.end

        def counting_end():
            active[0] -= 1
            return end_orig()
        server.tracing.begin, server.tracing.end = counting_begin, counting_end
        try:
            def go(k):
                out[k] = self.req("POST", "/api/chat", {"message": "slow %d" % k})
            ts = [threading.Thread(target=go, args=(k,)) for k in range(3)]
            [t.start() for t in ts]
            [t.join() for t in ts]
        finally:
            server.tracing.begin, server.tracing.end = orig, end_orig
        self.assertEqual(peak[0], 1)
        for k in range(3):
            self.assertEqual(out[k][0], 200)
            self.assertIn("echo slow %d" % k, out[k][1]["output"])

    def test_busy_message(self):
        old = server.BUSY_WAIT_S
        server.BUSY_WAIT_S = 0.05
        try:
            res = {}
            t = threading.Thread(target=lambda: res.setdefault("a", self.req("POST", "/api/chat", {"message": "slow a"})))
            t.start()
            time.sleep(0.1)
            st, j = self.req("POST", "/api/chat", {"message": "b"})
            t.join()
            self.assertEqual(st, 503)
            self.assertIn("thử lại", j["error"])
        finally:
            server.BUSY_WAIT_S = old


if __name__ == "__main__":
    unittest.main()
