"""B2 (nhánh thử exp/post-cp4-prompt): đường một lượt có khối quy tắc riêng "không hỏi lại dữ kiện đã có trong 'Dữ
kiện đã trích'". Quy tắc 6, 12, 16, 17 giữ nguyên chữ. Model giả, không gọi mạng. CHƯA kiểm bằng model thật."""
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import prompts as P  # noqa: E402
from test_guards import STUDENT_FACTS, decision_json, facts_json, scripted  # noqa: E402


class RuleDuKienTests(unittest.TestCase):
    def test_block_in_single_turn_prompt(self):
        self.assertIn(P.RULES_DU_KIEN, P.SYSTEM_QUYET_DINH)
        self.assertIn('KHÔNG hỏi lại dữ kiện đã có trong "Dữ kiện đã trích"', P.RULES_DU_KIEN)
        self.assertTrue(P.SYSTEM_QUYET_DINH.rstrip().endswith("Viết tiếng Việt."))
        self.assertTrue(P.SYSTEM_QUYET_DINH_PHIEN.startswith(P.SYSTEM_QUYET_DINH))   # đường có phiên cũng có

    def test_other_rules_unchanged(self):
        self.assertIn("12. can_hoi_them: chỉ khi need_more_information; 1–2 câu hỏi cụ thể nhất, là dữ kiện quyết định "
                      "kết quả.", P.SYSTEM_QUYET_DINH)
        self.assertIn("16. Đủ dữ kiện thì kết luận, không hỏi lại.", P.RULES_PHIEN)
        self.assertIn("17. can_hoi_them chỉ hỏi dữ kiện còn thiếu", P.RULES_PHIEN)
        self.assertNotIn("15b.", P.RULES_PHIEN)

    def test_single_turn_sends_block_and_facts_line(self):
        fn = scripted(facts_json(**STUDENT_FACTS), decision_json())
        with mock.patch.object(agent, "call_model", fn):
            out = agent.answer("Em đang học đại học chính quy năm 2, có được tạm hoãn không?")["output"]
        self.assertTrue(out.startswith("NHAN: eligible_for_review"))
        system, user = fn.calls[-1]
        self.assertEqual(system, P.SYSTEM_QUYET_DINH)
        self.assertIn("15b.", system)
        self.assertIn("Dữ kiện đã trích: ", user)
        self.assertIn("trinh_do=đại học", user)


if __name__ == "__main__":
    unittest.main()
