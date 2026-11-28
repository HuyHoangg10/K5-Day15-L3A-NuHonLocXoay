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

    def test_exact_tunnel_origin_and_host(self):
        old = os.environ.get("WEB_ALLOW_ORIGIN")
        os.environ["WEB_ALLOW_ORIGIN"] = "https://demo-nvqs.trycloudflare.com"
        try:
            st_ok, _ = self.req("GET", "/api/sources", headers={
                "Host": "demo-nvqs.trycloudflare.com",
                "Origin": "https://demo-nvqs.trycloudflare.com",
            })
            self.assertEqual(st_ok, 200)
            st_bad_origin, _ = self.req("GET", "/api/sources", headers={
                "Host": "demo-nvqs.trycloudflare.com",
                "Origin": "https://other.trycloudflare.com",
            })
            self.assertEqual(st_bad_origin, 403)
            st_bad_host, _ = self.req("GET", "/api/sources", headers={
                "Host": "other.trycloudflare.com",
                "Origin": "https://demo-nvqs.trycloudflare.com",
            })
            self.assertEqual(st_bad_host, 403)
        finally:
            if old is None:
                os.environ.pop("WEB_ALLOW_ORIGIN", None)
            else:
                os.environ["WEB_ALLOW_ORIGIN"] = old

    def test_sheet_log_masks_pii_and_skips_when_unset(self):
        payload = server._build_sheet_payload(
            "CCCD 001202012345 SDT 0912345678 email a@b.com key sk-proj-SecretTest12345",
            "eligible_for_review",
            [{"id": "vbhn133-d41-k1-g"}],
            1.234,
        )
        q = payload[server.SHEET_ENTRIES["question_masked"]]
        self.assertNotIn("001202012345", q)
        self.assertNotIn("0912345678", q)
        self.assertNotIn("a@b.com", q)
        self.assertNotIn("SecretTest12345", q)
        self.assertEqual(payload[server.SHEET_ENTRIES["can_cu"]], "vbhn133-d41-k1-g")
        self.assertEqual(payload[server.SHEET_ENTRIES["latency_s"]], "1.23")


class MemoryTest(unittest.TestCase):
    """Đường có bộ nhớ: dùng ChatSession GIẢ và agent STUB có tham số session (đánh dấu rõ, không gọi model)."""

    class FakeSession:
        def __init__(self, sid=None):
            self.sid, self.seen = sid, []

    class FakeModule:
        pass

    def setUp(self):
        self.old = (server.ANSWER_FN, server.chat_session)
        fake = self.FakeModule()
        fake.ChatSession = self.FakeSession
        server.chat_session = fake
        server._sessions.clear()

        def stub(text, session=None):  # STUB
            session.seen.append(text)
            return {"output": "NHAN: need_more_information\nCAN_CU: \n\nGiải thích: đã thấy %d lượt" % len(session.seen)}
        server.ANSWER_FN = stub

    def tearDown(self):
        server.ANSWER_FN, server.chat_session = self.old
        server._sessions.clear()

    def test_same_id_remembers_other_id_isolated(self):
        sid_a, sid_b = "aaaaaaaa-1111", "bbbbbbbb-2222"
        self.assertIn("1 lượt", server.run_agent("x", sid_a)[1]["output"])
        self.assertIn("2 lượt", server.run_agent("y", sid_a)[1]["output"])
        self.assertIn("1 lượt", server.run_agent("z", sid_b)[1]["output"])

    def test_bad_id_runs_single_turn_without_crash(self):
        server.ANSWER_FN = lambda text: {"output": "NHAN: refuse\nCAN_CU: \n\nGiải thích: ok"}  # STUB một lượt
        st, j = server.run_agent("x", "!!")
        self.assertEqual((st, j["nhan"]), (200, "refuse"))

    def test_session_cap(self):
        old = server.MAX_SESSIONS
        server.MAX_SESSIONS = 3
        try:
            for i in range(6):
                server.run_agent("x", "sess-%04d-abcd" % i)
            self.assertEqual(len(server._sessions), 3)
        finally:
            server.MAX_SESSIONS = old

    def test_no_memory_when_agent_has_no_session_param(self):
        self.assertFalse(server.uses_memory(lambda text: {"output": ""}))


if __name__ == "__main__":
    unittest.main()
