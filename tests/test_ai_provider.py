"""Kiểm nhánh model thật của codebase/ai.py mà KHÔNG tốn tiền và KHÔNG cần key thật:
urllib.request.urlopen được giả lập (mock), key là chuỗi giả. Chạy: python -m unittest discover tests
"""
import io
import json
import os
import sys
import unittest
import urllib.error
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import ai  # noqa: E402
import tracing  # noqa: E402

FAKE_KEY = "sk-TESTKEY-0123456789abcdef"


class FakeResp:
    def __init__(self, data):
        self._b = json.dumps(data).encode("utf-8")

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def reply(text="ok", prompt=10, completion=5, total=None, reasoning=None, model="deepseek-flash"):
    usage = {"prompt_tokens": prompt, "completion_tokens": completion,
             "total_tokens": prompt + completion if total is None else total}
    if reasoning is not None:
        usage["completion_tokens_details"] = {"reasoning_tokens": reasoning}
    return {"model": model, "choices": [{"message": {"role": "assistant", "content": text}}], "usage": usage}


def http_error(code, body="{}"):
    return urllib.error.HTTPError("https://x/chat/completions", code, "err", {}, io.BytesIO(body.encode("utf-8")))


class ProviderTestCase(unittest.TestCase):
    provider = "deepseek"
    model = "deepseek-flash"

    def setUp(self):
        for p in (mock.patch.multiple(ai, MODEL_PROVIDER=self.provider, MODEL_NAME=self.model, API_KEY=FAKE_KEY),
                  mock.patch.dict(os.environ, {"MODEL_BASE_URL": "", "MODEL_MAX_TOKENS": ""}),
                  mock.patch.object(ai.time, "sleep")):
            p.start()
            self.addCleanup(p.stop)
        self.sleep = ai.time.sleep

    def urlopen(self, *responses):
        """Giả lập urlopen: mỗi lần gọi trả / ném phần tử kế tiếp. Ghi lại (request, timeout)."""
        calls = []
        queue = list(responses)

        def fn(req, timeout=None):
            calls.append((req, timeout))
            item = queue.pop(0)
            if isinstance(item, BaseException):
                raise item
            return FakeResp(item)
        p = mock.patch.object(ai.urllib.request, "urlopen", side_effect=fn)
        p.start()
        self.addCleanup(p.stop)
        return calls


class RequestAndUsageTests(ProviderTestCase):
    def test_request_shape_deepseek(self):
        calls = self.urlopen(reply("xin chào", prompt=120, completion=45))
        out = ai.call_model("Bạn là trợ lý.", "Chào")
        req, timeout = calls[0]
        body = json.loads(req.data)
        self.assertEqual(req.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(req.get_header("Authorization"), "Bearer " + FAKE_KEY)
        self.assertEqual(timeout, 30)
        self.assertEqual(body["model"], "deepseek-flash")
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(body["max_tokens"], 700)
        self.assertEqual(body["thinking"], {"type": "disabled"})
        self.assertNotIn("response_format", body)
        self.assertEqual(body["messages"][0], {"role": "system", "content": "Bạn là trợ lý."})
        self.assertEqual(out, {"text": "xin chào", "model": "deepseek-flash", "tokens_in": 120, "tokens_out": 45})

    def test_json_mode_when_prompt_asks_for_json(self):
        calls = self.urlopen(reply("{}"))
        ai.call_model("Chỉ trả về MỘT đối tượng JSON.", "x")
        self.assertEqual(json.loads(calls[0][0].data)["response_format"], {"type": "json_object"})

    def test_overrides_from_env(self):
        calls = self.urlopen(reply())
        with mock.patch.dict(os.environ, {"MODEL_BASE_URL": "https://proxy.example/v9/", "MODEL_MAX_TOKENS": "321"}):
            ai.call_model("s", "u")
        req = calls[0][0]
        self.assertEqual(req.full_url, "https://proxy.example/v9/chat/completions")
        self.assertEqual(json.loads(req.data)["max_tokens"], 321)

    def test_bad_max_tokens_is_clear_error(self):
        self.urlopen()
        with mock.patch.dict(os.environ, {"MODEL_MAX_TOKENS": "nhieu"}):
            with self.assertRaises(NotImplementedError) as cm:
                ai.call_model("s", "u")
        self.assertIn("MODEL_MAX_TOKENS", str(cm.exception))

    def test_missing_usage_is_error_not_a_guess(self):
        data = reply()
        del data["usage"]
        self.urlopen(data)
        with self.assertRaises(RuntimeError) as cm:
            ai.call_model("s", "u")
        self.assertIn("usage", str(cm.exception))

    def test_model_name_keeps_requested_alias_for_price_lookup(self):
        for served, want in (("deepseek-flash", "deepseek-flash"), ("DeepSeek-Flash-1017", "deepseek-flash"),
                             ("", "deepseek-flash"), ("another-model", "another-model")):
            with self.subTest(served=served):
                self.urlopen(reply(model=served))
                self.assertEqual(ai.call_model("s", "u")["model"], want)


class ReasoningTokensTests(ProviderTestCase):
    def out(self, **kw):
        self.urlopen(reply(**kw))
        return ai.call_model("s", "u")["tokens_out"]

    def test_reasoning_already_inside_completion_is_not_added_twice(self):
        # completion 300 đã gồm 200 suy luận; tổng = vào + completion
        self.assertEqual(self.out(prompt=100, completion=300, reasoning=200, total=400), 300)

    def test_reasoning_reported_separately_is_added(self):
        # tổng = vào + completion + suy luận → suy luận nằm NGOÀI completion
        self.assertEqual(self.out(prompt=100, completion=100, reasoning=200, total=400), 300)

    def test_no_reasoning_details(self):
        self.assertEqual(self.out(prompt=100, completion=77), 77)

    def test_reasoning_zero(self):
        self.assertEqual(self.out(prompt=100, completion=77, reasoning=0), 77)


class OpenAITests(ProviderTestCase):
    provider = "openai"
    model = "gpt-4o-mini"

    def test_request_shape_openai(self):
        calls = self.urlopen(reply("hi", model="gpt-4o-mini-2024-07-18"))
        out = ai.call_model("s", "u")
        body = json.loads(calls[0][0].data)
        self.assertEqual(calls[0][0].full_url, "https://api.openai.com/v1/chat/completions")
        self.assertEqual(body["max_completion_tokens"], 700)
        self.assertNotIn("max_tokens", body)
        self.assertNotIn("thinking", body)
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(out["model"], "gpt-4o-mini")   # bản chốt 2024-07-18 → giữ tên để tra giá


class RetryTests(ProviderTestCase):
    def test_retries_once_on_429_then_succeeds(self):
        calls = self.urlopen(http_error(429, '{"error":{"code":"rate_limit_exceeded"}}'), reply("ok"))
        self.assertEqual(ai.call_model("s", "u")["text"], "ok")
        self.assertEqual(len(calls), 2)
        self.sleep.assert_called_once_with(2)

    def test_gives_up_after_one_retry(self):
        calls = self.urlopen(http_error(503), http_error(503), reply("không bao giờ tới"))
        with self.assertRaises(RuntimeError) as cm:
            ai.call_model("s", "u")
        self.assertEqual(len(calls), 2)
        self.assertIn("HTTP 503", str(cm.exception))

    def test_retries_on_network_error(self):
        calls = self.urlopen(urllib.error.URLError("mất mạng"), reply("ok"))
        self.assertEqual(ai.call_model("s", "u")["text"], "ok")
        self.assertEqual(len(calls), 2)

    def test_network_error_twice_raises(self):
        calls = self.urlopen(TimeoutError("hết giờ"), TimeoutError("hết giờ"))
        with self.assertRaises(RuntimeError) as cm:
            ai.call_model("s", "u")
        self.assertEqual(len(calls), 2)
        self.assertIn("Lỗi mạng", str(cm.exception))

    def test_no_retry_for_quota_or_client_errors(self):
        for err in (http_error(429, '{"error":{"code":"insufficient_quota"}}'), http_error(402, "{}"),
                    http_error(400, "{}"), http_error(401, "{}")):
            with self.subTest(code=err.code):
                calls = self.urlopen(err, reply("không được gọi"))
                with self.assertRaises(RuntimeError):
                    ai.call_model("s", "u")
                self.assertEqual(len(calls), 1)


class ConfigErrorTests(ProviderTestCase):
    def test_missing_key_is_vietnamese_error_and_no_request(self):
        calls = self.urlopen()
        with mock.patch.object(ai, "API_KEY", ""):
            with self.assertRaises(NotImplementedError) as cm:
                ai.call_model("s", "u")
        self.assertIn("Thiếu API_KEY trong .env", str(cm.exception))
        self.assertEqual(calls, [])

    def test_missing_model_name(self):
        self.urlopen()
        with mock.patch.object(ai, "MODEL_NAME", ""):
            with self.assertRaises(NotImplementedError) as cm:
                ai.call_model("s", "u")
        self.assertIn("MODEL_NAME", str(cm.exception))

    def test_unknown_provider_explains_how_to_add(self):
        calls = self.urlopen()
        with mock.patch.object(ai, "MODEL_PROVIDER", "nhacungcapla"):
            with self.assertRaises(NotImplementedError) as cm:
                ai.call_model("s", "u")
        self.assertIn("PROVIDERS", str(cm.exception))
        self.assertEqual(calls, [])


class NoKeyLeakTests(ProviderTestCase):
    def assert_clean(self, text):
        self.assertNotIn(FAKE_KEY, text)
        self.assertNotIn("TESTKEY", text)
        self.assertNotIn("Authorization", text)
        self.assertNotIn("Bearer " + FAKE_KEY, text)

    def test_http_errors_do_not_leak_key(self):
        echo = '{"error":{"message":"Incorrect API key provided: %s. Also sk-TESTKEY-0123****cdef"}}' % FAKE_KEY
        for code in (400, 401, 403, 404, 500):
            with self.subTest(code=code):
                self.urlopen(http_error(code, echo), http_error(code, echo))
                with self.assertRaises(RuntimeError) as cm:
                    ai.call_model("s", "u")
                self.assert_clean(str(cm.exception))

    def test_network_error_does_not_leak_key(self):
        self.urlopen(urllib.error.URLError("lỗi với " + FAKE_KEY), urllib.error.URLError("lỗi với " + FAKE_KEY))
        with self.assertRaises(RuntimeError) as cm:
            ai.call_model("s", "u")
        self.assert_clean(str(cm.exception))

    def test_trace_does_not_contain_key(self):
        self.urlopen(http_error(401, "key " + FAKE_KEY))
        tracing.begin("t")
        with self.assertRaises(RuntimeError):
            ai.call_model("s", "u")
        _, events = tracing.end()
        self.assert_clean(json.dumps(events, ensure_ascii=False))


class FakeProviderTests(unittest.TestCase):
    def test_fake_still_works_without_network_or_key(self):
        with mock.patch.multiple(ai, MODEL_PROVIDER="fake", MODEL_NAME="", API_KEY=""), \
                mock.patch.object(ai.urllib.request, "urlopen") as urlopen:
            out = ai.call_model("sys", "dòng 1\nem cận 5 độ")
        urlopen.assert_not_called()
        self.assertEqual(out["model"], "fake")
        self.assertEqual((out["tokens_in"], out["tokens_out"]), (0, 0))
        self.assertTrue(out["text"].startswith("[câu trả lời giả — chưa nối model] em cận 5 độ"))


if __name__ == "__main__":
    unittest.main()
