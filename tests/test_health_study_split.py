"""A2: câu lẫn sức khỏe + học tập trong bản demo có phiên (model kịch bản, không gọi mạng): hiển thị hai phần — sức khỏe
ngoài phạm vi kèm chỗ hỏi đúng; mời hỏi riêng phần học tập bằng câu gợi ý ghép từ dữ kiện đã trích. Không gọi thêm model,
nhãn / bản gốc / đường eval không đổi."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import demo_ui  # noqa: E402
import prompts as P  # noqa: E402
import session as S  # noqa: E402
from test_chat_session import Model, nhan, turn  # noqa: E402
from test_guards import facts_json  # noqa: E402

TEXT = "Em cận 4 độ, đang học đại học chính quy năm 1, em được hoãn vì cận hay vì đi học?"
HEALTH_STUDY = facts_json(chu_de="suc_khoe", dang_hoc=True, trinh_do="đại học", he_chinh_quy=True, nam_thu=1)


class HealthStudySplitTests(unittest.TestCase):
    def test_two_parts_with_study_hint(self):
        s, m = S.ChatSession(), Model()
        out, _ = turn(s, m, TEXT, HEALTH_STUDY)
        self.assertEqual(nhan(out), "out_of_scope")                       # nhãn không đổi
        self.assertEqual(len(m.calls), 1)                                 # không gọi thêm model
        nice = demo_ui.pretty(out, user_text=TEXT, facts=s.facts)
        self.assertIn("Câu của bạn có hai phần", nice)
        self.assertIn(P.REDIRECT_HEALTH, nice)
        self.assertIn('"Em đang học đại học hệ chính quy năm 1, [đã / chưa từng được tạm hoãn]', nice)
        self.assertNotIn("Việc bạn nên làm", nice)
        self.assertTrue(nice.startswith(demo_ui.LABEL_TEXT["out_of_scope"]))

    def test_hint_placeholders_and_values(self):
        self.assertIn("[trình độ", demo_ui.study_question_hint({}))
        h = demo_ui.study_question_hint({"trinh_do": "cao đẳng", "he_chinh_quy": False, "da_tam_hoan_truoc": False})
        self.assertEqual(h, "Em đang học cao đẳng hệ không chính quy, chưa từng được tạm hoãn — có được tạm hoãn vì học tập không?")

    def test_pure_health_or_no_session_unchanged(self):
        s, m = S.ChatSession(), Model()
        out, _ = turn(s, m, "Em bị hen suyễn có được miễn không?", facts_json(chu_de="suc_khoe"))
        for kw in ({"user_text": "Em bị hen suyễn có được miễn không?", "facts": s.facts},   # không nhắc việc học
                   {"user_text": TEXT}):                                                     # không phiên (facts=None)
            nice = demo_ui.pretty(out, **kw)
            self.assertNotIn("hai phần", nice)
            self.assertIn(P.REDIRECT_HEALTH, nice)


if __name__ == "__main__":
    unittest.main()
