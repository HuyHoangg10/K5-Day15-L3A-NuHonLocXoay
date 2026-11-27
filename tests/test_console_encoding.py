"""Console Windows / mã hóa (model giả, không gọi mạng): app không ném UnicodeEncodeError khi luồng ra là cp1252 / cp437
không reconfigure được, chạy được khi chuyển hướng ra ống / file, và gộp đoạn dán nhiều dòng thành một câu hỏi."""
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


class StrictLegacyStream(io.TextIOWrapper):
    """Giống console cũ: mã hóa cp1252 / cp437 kiểu strict, KHÔNG cho reconfigure."""

    def reconfigure(self, *a, **k):
        raise io.UnsupportedOperation("không đổi được mã hóa")


def run_with_stdout(stream, inputs, more=None):
    old = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = stream
    try:
        with mock.patch("builtins.input", side_effect=inputs), \
                mock.patch.object(app, "_more_waiting", more or (lambda: False)):
            return app.main()
    finally:
        sys.stdout, sys.stderr = old


class LegacyConsoleTests(unittest.TestCase):
    def test_cp1252_and_cp437_no_unicode_error(self):
        for enc in ("cp1252", "cp437"):
            with self.subTest(enc=enc):
                raw = io.BytesIO()
                stream = StrictLegacyStream(raw, encoding=enc, errors="strict", write_through=True)
                with self.assertRaises(UnicodeEncodeError):        # chứng minh luồng này thật sự "khó tính"
                    stream.write("ữ")
                code = run_with_stdout(stream, ["Em học ĐH chính quy 🎓 ↪ ✓", "/help", "/goc", "/thoat"])
                self.assertEqual(code, 0)
                text = raw.getvalue().decode(enc)
                self.assertIn("/thoat", text)
                self.assertIn("?", text)                              # ký tự không mã hóa được thành '?'

    def test_utf8_pipe_keeps_vietnamese(self):
        raw = io.BytesIO()
        stream = io.TextIOWrapper(raw, encoding="utf-8", write_through=True)
        code = run_with_stdout(stream, ["/help", "/thoat"])
        self.assertEqual(code, 0)
        self.assertIn("bắt đầu cuộc trò chuyện mới", raw.getvalue().decode("utf-8"))

    def test_replace_writer_delegates(self):
        raw = io.BytesIO()
        w = app._ReplaceWriter(io.TextIOWrapper(raw, encoding="cp1252", write_through=True))
        w.write("Việt Nam 🎓")
        w.flush()
        self.assertEqual(raw.getvalue().decode("cp1252"), "Vi?t Nam ?")


class PasteTests(unittest.TestCase):
    def test_multiline_paste_becomes_one_message(self):
        flags = iter([True, True, False])
        with mock.patch("builtins.input", side_effect=["Em học đại học", "hệ chính quy", "năm 2, có được hoãn không?"]):
            msg = app.read_message("> ", more=lambda: next(flags))
        self.assertEqual(msg, "Em học đại học hệ chính quy năm 2, có được hoãn không?")

    def test_paste_capped_and_eof_safe(self):
        with mock.patch("builtins.input", side_effect=["dòng"] * (app.PASTE_MAX_LINES + 10)):
            msg = app.read_message("> ", more=lambda: True)
        self.assertEqual(len(msg.split()), app.PASTE_MAX_LINES)
        with mock.patch("builtins.input", side_effect=["a", EOFError()]):
            self.assertEqual(app.read_message("> ", more=lambda: True), "a")

    def test_pipe_input_is_one_line_per_turn(self):
        fake_stdin = io.StringIO("a\nb\n")
        with mock.patch.object(sys, "stdin", fake_stdin):
            self.assertFalse(app._more_waiting())

    def test_app_sends_pasted_block_as_one_turn(self):
        flags = iter([True, False, False, False])
        with mock.patch.object(agent, "answer", wraps=agent.answer) as ans:
            run_with_stdout(io.TextIOWrapper(io.BytesIO(), encoding="utf-8"), ["Em học", "đại học", "/thoat"],
                            more=lambda: next(flags))
        self.assertEqual(ans.call_count, 1)
        self.assertEqual(ans.call_args[0][0], "Em học đại học")


if __name__ == "__main__":
    unittest.main()
