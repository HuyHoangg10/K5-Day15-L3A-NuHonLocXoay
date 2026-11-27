"""A5: mục "Sau khi PR #24 merge vào main" trong docs/demo-guide.md còn khớp mã: có đủ lệnh (merge không rebase, sinh
lại bản chụp bằng model giả, test, check, lùi lại), đoạn quy tắc 16 cần thay còn đúng trong prompts.py, và thay theo
hướng dẫn thì giữ quy tắc 17, không đụng đường eval một lượt. Không gọi mạng."""
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"

import prompts as P  # noqa: E402

GUIDE = open(os.path.join(ROOT, "docs", "demo-guide.md"), encoding="utf-8").read()
SECTION = GUIDE[GUIDE.index("## 6. Sau khi PR #24 merge vào main"):]
NEW16 = ("16. (Cuộc trò chuyện) Khi áp dụng phần eligible_for_review của 6a: 'không nhắc tới' gồm cả tốt nghiệp trình "
         "độ khác, liên thông, văn bằng hai, thôi học, chuyển trường, bảo lưu, nợ môn, quá hạn, du học; không hỏi về học "
         "gián đoạn; nêu điều kiện một khóa học trong ly_do.")


def apply_short16(rules):
    """Làm đúng như mục 6.4: thay quy tắc 16 (từ '16. Đủ dữ kiện…' tới '…đã từng được tạm hoãn chưa.') bằng NEW16."""
    return re.sub(r"16\. Đủ dữ kiện thì kết luận.*?đã từng được tạm hoãn chưa\.", lambda m: NEW16, rules, count=1,
                  flags=re.S)


class DemoGuidePr24Tests(unittest.TestCase):
    def test_commands_present(self):
        for cmd in ("git merge --no-ff origin/main", '$env:MODEL_PROVIDER="fake"; python tests/make_single_turn_golden.py',
                    '$env:MODEL_PROVIDER="fake"; python -m unittest discover -s tests',
                    '$env:MODEL_PROVIDER="fake"; python run.py check', "git merge --abort", "git revert -m 1",
                    "git diff --exit-code tests/fixtures/single_turn_golden.json"):
            self.assertIn(cmd, SECTION, cmd)
        self.assertNotIn("rebase ", SECTION.replace("Không rebase", "").replace("không rebase", ""))
        self.assertNotIn("--force", SECTION)

    def test_rule16_text_verbatim(self):
        self.assertIn(NEW16, SECTION)

    def test_replacement_still_applies(self):
        short = apply_short16(P.RULES_PHIEN)
        self.assertNotEqual(short, P.RULES_PHIEN)                    # đoạn cần thay vẫn còn trong prompts.py
        self.assertIn(NEW16, short)
        self.assertNotIn("Đủ dữ kiện thì kết luận", short)
        self.assertIn("17. can_hoi_them chỉ hỏi dữ kiện còn thiếu", short)
        self.assertNotIn("16.", P.SYSTEM_QUYET_DINH)                 # đường eval một lượt không chứa quy tắc 16


if __name__ == "__main__":
    unittest.main()
