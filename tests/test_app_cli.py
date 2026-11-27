"""Giao diện dòng lệnh (codebase/app.py) với model giả, không gọi mạng: /help, /thoat, lệnh lạ, Ctrl+C / EOF,
lỗi bất ngờ không lộ traceback, ngắt dòng theo độ rộng."""
import contextlib
import io
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import app  # noqa: E402
import demo_ui  # noqa: E402


def run_app(inputs):
    buf = io.StringIO()
    with mock.patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(buf):
        code = app.main()
    return code, buf.getvalue()


class AppCliTests(unittest.TestCase):
    def test_help_lists_commands(self):
        code, out = run_app(["/help", "/thoat"])
        self.assertEqual(code, 0)
        for c in ("/moi", "/goc", "/help", "/thoat"):
            self.assertIn(c, out)
        self.assertIn(demo_ui.BYE, out)

    def test_exit_variants(self):
        for seq in (["/exit"], ["/quit"], ["", ""], ["/thoát"]):
            with self.subTest(seq=seq):
                code, out = run_app(seq)
                self.assertEqual(code, 0)
                self.assertIn(demo_ui.BYE, out)

    def test_ctrl_c_and_eof_exit_cleanly(self):
        for exc in (KeyboardInterrupt, EOFError):
            with self.subTest(exc=exc.__name__):
                code, out = run_app([exc()])
                self.assertEqual(code, 0)
                self.assertIn(demo_ui.BYE, out)
                self.assertNotIn("Traceback", out)

    def test_unknown_command_not_sent_to_agent(self):
        with mock.patch.object(agent, "answer") as ans:
            code, out = run_app(["/mooi", "/thoat"])
        ans.assert_not_called()
        self.assertIn("/help", out.split("/mooi", 1)[1])

    def test_question_then_raw_then_reset(self):
        code, out = run_app(["hoãn?", "/goc", "/moi", "/thoat"])
        self.assertEqual(code, 0)
        self.assertIn("NHAN:", out)                  # /goc in bản gốc
        self.assertIn("Đã xóa cuộc trò chuyện", out)

    def test_unexpected_error_is_friendly(self):
        with mock.patch.object(agent, "answer", side_effect=ValueError("bí mật nội bộ /path/x.py line 3")):
            code, out = run_app(["em học đại học", "/thoat"])
        self.assertEqual(code, 0)
        self.assertNotIn("bí mật nội bộ", out)
        self.assertNotIn("Traceback", out)
        self.assertIn(demo_ui.FOOTER, out)


class WrapTests(unittest.TestCase):
    def test_wrap_respects_width_and_bullets(self):
        text = "Giải thích: " + "chữ " * 60 + "\n  • " + "bước " * 40 + "\n  1. " + "việc " * 40
        out = demo_ui.wrap(text, 50)
        self.assertTrue(all(len(line) <= 50 for line in out.splitlines()))
        lines = out.splitlines()
        bullet = [i for i, line in enumerate(lines) if line.startswith("  • ")][0]
        self.assertTrue(lines[bullet + 1].startswith("    "))       # dòng tiếp thụt thẳng hàng chữ
        self.assertEqual(demo_ui.wrap("ngắn", 50), "ngắn")

    def test_term_width_bounds(self):
        self.assertTrue(40 <= demo_ui.term_width() <= 100)


if __name__ == "__main__":
    unittest.main()
