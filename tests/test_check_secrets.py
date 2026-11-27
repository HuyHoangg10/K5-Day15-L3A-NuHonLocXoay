"""scripts/check_secrets.py (offline, không gọi mạng). Chuỗi giống key THẬT được sinh ngẫu nhiên lúc chạy test — không ghi
nguyên văn vào file — để chính bộ quét không bắt file này."""
import contextlib
import io
import os
import secrets
import string
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import check_secrets as C  # noqa: E402


def rand(n, alphabet=string.ascii_letters + string.digits):
    while True:
        s = "".join(secrets.choice(alphabet) for _ in range(n))
        if not any(m in s.lower() for m in C.FAKE_MARKERS):
            return s


def levels(path, text):
    return [(lv, kind) for lv, kind, _, _ in C.scan_text(path, text)]


class CheckSecretsTests(unittest.TestCase):
    def test_blocks_real_looking_keys(self):
        cases = {"sk-key": "sk-" + rand(40), "sk-key ": "sk-ant-api03-" + rand(40), "bearer": "Bearer " + rand(32),
                 "github": "ghp_" + rand(36), "assigned-secret": "API_KEY = '%s'" % rand(32)}
        for kind, line in cases.items():
            with self.subTest(kind=kind):
                for path in ("codebase/x.py", "tests/test_x.py"):
                    self.assertIn(("CHẶN", kind.strip()), levels(path, "x = 1\n" + line + "\n"))

    def test_never_prints_full_value(self):
        key = "sk-" + rand(40)
        for _, _, _, shown in C.scan_text("a.py", key):
            self.assertNotIn(key, shown)
            self.assertLess(len(shown.split("…")[0]), 8)

    def test_fake_keys_in_tests_allowed_but_not_elsewhere(self):
        fake = "FAKE_KEY = 'sk-TESTKEY-0123456789abcdef'"
        self.assertEqual(levels("tests/test_ai.py", fake), [])
        self.assertIn(("CHẶN", "sk-key"), levels("codebase/ai.py", fake))

    def test_low_entropy_assignment_not_blocked(self):
        for line in ("API_KEY = (os.environ.get('API_KEY') or '').strip()", "TOKEN_LIMIT = 'aaaaaaaaaaaaaaaaaaaaaaaa'",
                     "secret_name = 'tenbienrattdai_khongphaikey'"):
            with self.subTest(line=line):
                self.assertNotIn("CHẶN", [lv for lv, _ in levels("codebase/x.py", line)])

    def test_pii_warns(self):
        got = levels("evidence/x.md", "liên hệ nguyen.van.a@gmail.com, 0912 345 678, CCCD 001203004567")
        self.assertEqual(sorted(k for _, k in got), ["cccd", "email", "sdt"])
        self.assertTrue(all(lv == "CẢNH BÁO" for lv, _ in got))
        self.assertEqual(levels("a.md", "mail noreply@example.com"), [])

    def test_pragma_allows_line(self):
        line = "sk-" + rand(40) + "  # " + C.PRAGMA
        self.assertEqual(levels("docs/a.md", line), [])

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            bad, good, env = os.path.join(d, "bad.py"), os.path.join(d, "good.py"), os.path.join(d, ".env")
            open(bad, "w", encoding="utf-8").write("k = 'sk-%s'\n" % rand(40))
            open(good, "w", encoding="utf-8").write("print('xin chào')\n")
            open(env, "w", encoding="utf-8").write("MODEL_NAME=x\n")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(C.main([good]), 0)
                self.assertEqual(C.main([bad]), 1)
                self.assertEqual(C.main([env]), 1)
                self.assertEqual(C.main(["--strict", good]), 0)

    def test_repository_has_no_blocking_findings(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = C.main([])
        self.assertEqual(code, 0, buf.getvalue()[-2000:])


if __name__ == "__main__":
    unittest.main()
