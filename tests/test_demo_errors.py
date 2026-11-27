"""Demo: lỗi model được báo thân thiện theo loại, không lộ stack trace / key; thử lại tối đa 1 lần; móc tiến độ.
Mô phỏng lỗi bằng stub ở ai._post (không gọi mạng). Key dưới đây là chuỗi giả cho test."""
import builtins
import io
import json
import os
import sys
import unittest
import urllib.error
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import ai  # noqa: E402
import app  # noqa: E402
import demo_ui  # noqa: E402
import tracing  # noqa: E402
from test_guards import STUDENT_FACTS, decision_json, facts_json  # noqa: E402

FAKE_KEY = "sk-test-KHONGPHAIKEYTHAT123456"


def http_error(code, body):
    return urllib.error.HTTPError("https://x/chat/completions", code, "err", {}, io.BytesIO(body.encode("utf-8")))


def ok(text):
    return {"choices": [{"message": {"content": text}}], "usage": {"prompt_tokens": 1, "completion_tokens": 1},
            "model": "m"}


class RealPathStub:
    """Chạy agent qua ĐÚNG đường ai.call_model thật (nhà cung cấp openai) nhưng ai._post là stub."""

    def __init__(self, effects):
        self.effects, self.n = list(effects), 0

    def __call__(self, url, headers, body):
        self.n += 1
        e = self.effects.pop(0)
        if isinstance(e, BaseException):
            raise e
        return e

    def run(self, text="Em học đại học chính quy năm 2"):
        with mock.patch.multiple(ai, MODEL_PROVIDER="openai", API_KEY=FAKE_KEY, MODEL_NAME="m"), \
                mock.patch.object(ai, "_post", self), mock.patch.object(ai.time, "sleep", lambda s: None):
            tracing.begin("err")
            out = agent.answer(text)["output"]
            _, ev = tracing.end()
        return out, ev


class FriendlyErrorTests(unittest.TestCase):
    def check(self, effects, kind, retried=None):
        stub = RealPathStub(effects)
        out, ev = stub.run()
        self.assertTrue(out.startswith("LOI:"), out[:80])
        msg = demo_ui.friendly_error(out, ev)
        self.assertEqual(msg, demo_ui.FRIENDLY[kind])
        for s in (out, msg):
            self.assertNotIn(FAKE_KEY, s)
            self.assertNotIn("Traceback", s)
        self.assertNotIn(FAKE_KEY, json.dumps(ev, ensure_ascii=False))
        if retried is not None:
            self.assertEqual(stub.n, retried)
        return stub

    def test_quota_not_retried(self):
        self.check([http_error(429, '{"error": "insufficient_quota"}')], "quota", retried=1)

    def test_key_rejected_and_key_never_shown(self):
        self.check([http_error(401, '{"error": "bad key %s"}' % FAKE_KEY)], "key", retried=1)

    def test_timeout_retried_once(self):
        self.check([TimeoutError("timed out"), TimeoutError("timed out")], "timeout", retried=2)

    def test_network_error(self):
        self.check([urllib.error.URLError("getaddrinfo failed"), urllib.error.URLError("getaddrinfo failed")],
                   "network", retried=2)

    def test_bad_json_response(self):
        self.check([ValueError("Expecting value")], "bad_response", retried=1)

    def test_server_error_retried_then_ok(self):
        stub = RealPathStub([http_error(503, "busy"), ok(facts_json(**STUDENT_FACTS)), ok(decision_json())])
        out, ev = stub.run()
        self.assertTrue(out.startswith("NHAN: eligible_for_review"))
        self.assertEqual(stub.n, 3)                     # 1 lần lỗi + 1 lần thử lại + bước quyết định
        self.assertIsNone(demo_ui.friendly_error(out, ev))

    def test_empty_or_broken_model_text_is_safe_fallback_not_error(self):
        for text in ("", "không phải json"):
            with self.subTest(text=text):
                out, ev = RealPathStub([ok(text)]).run()
                self.assertTrue(out.startswith("NHAN: safe_fallback"))
                self.assertIsNone(demo_ui.friendly_error(out, ev))

    def test_classify_unknown_is_generic(self):
        self.assertEqual(demo_ui.friendly_error("LOI: x", []), demo_ui.FRIENDLY["other"])
        self.assertIsNone(demo_ui.friendly_error("NHAN: refuse", []))


class AppLoopTests(unittest.TestCase):
    def run_app(self, lines, answer):
        it = iter(lines)

        def fake_input(prompt=""):
            try:
                return next(it)
            except StopIteration:
                raise EOFError
        buf = io.StringIO()
        with mock.patch.object(builtins, "input", fake_input), mock.patch.object(agent, "answer", answer), \
                redirect_stdout(buf):
            code = app.main()
        agent.on_step = None
        return code, buf.getvalue()

    def test_unexpected_exception_is_friendly(self):
        def boom(text, session=None):
            raise RuntimeError("HTTP 401: key bị từ chối %s\nTraceback (most recent call last)" % FAKE_KEY)
        code, out = self.run_app(["Em học đại học"], boom)
        self.assertEqual(code, 0)
        self.assertIn(demo_ui.FRIENDLY["key"], out)
        self.assertNotIn(FAKE_KEY, out)
        self.assertNotIn("Traceback", out)
        self.assertNotIn("RuntimeError", out)

    def test_reset_command_and_status(self):
        def ans(text, session=None):
            agent._step("tra_cuu")
            return {"output": "NHAN: need_more_information\nCAN_CU: \n\nGiải thích: x"}
        code, out = self.run_app(["Em học đại học", "/moi"], ans)
        self.assertIn(demo_ui.STEP_TEXT["tra_cuu"], out)
        self.assertIn("Đã xóa cuộc trò chuyện", out)
        self.assertIn("tra cứu", out)


class ProgressHookTests(unittest.TestCase):
    def test_steps_in_order_and_hook_errors_ignored(self):
        seen = []
        model = lambda s, u: {"text": facts_json(**STUDENT_FACTS) if "trích dữ kiện" in s else decision_json(),  # noqa: E731
                              "model": "t", "tokens_in": 0, "tokens_out": 0}
        with mock.patch.object(agent, "call_model", model), mock.patch.object(agent, "on_step", seen.append):
            out = agent.answer("Em học đại học chính quy năm 2")["output"]
        self.assertEqual(seen, ["trich", "tra_cuu", "quyet_dinh"])

        def bad(name):
            raise ValueError("giao diện hỏng")
        with mock.patch.object(agent, "call_model", model), mock.patch.object(agent, "on_step", bad):
            self.assertEqual(agent.answer("Em học đại học chính quy năm 2")["output"], out)

    def test_step_timings(self):
        ev = [{"kind": "model", "latency_s": 2.0}, {"kind": "tool", "latency_s": 0.01}, {"kind": "model", "latency_s": 6.5}]
        self.assertEqual(demo_ui.step_timings(ev, 8.6), {"trich": 2.0, "tra_cuu": 0.01, "quyet_dinh": 6.5, "tong": 8.6})


if __name__ == "__main__":
    unittest.main()
