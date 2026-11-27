"""Sửa edge case cho bản demo nhiều lượt (answer có session). Model giả, không gọi mạng.
Đường đo một lượt (không session) phải giữ nguyên: bản chụp ở tests/test_single_turn_invariance.py."""
import csv
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import demo_ui  # noqa: E402
import guards  # noqa: E402
import kb  # noqa: E402
import prompts as P  # noqa: E402
import session as S  # noqa: E402
from test_chat_session import Model, nhan, turn  # noqa: E402
from test_guards import decision_json, facts_json  # noqa: E402

OFFTOPIC_FACTS = facts_json(chu_de="khac", y_do="ngoai_pham_vi")


class DemoRuleBlockTests(unittest.TestCase):
    """Quy tắc 16–17: khối riêng, chỉ ghép khi có phiên; không chứa câu benchmark, không chứa cụm tuyệt đối."""

    def test_block_is_separate_and_eval_prompt_unchanged(self):
        self.assertTrue(P.SYSTEM_QUYET_DINH_PHIEN.startswith(P.SYSTEM_QUYET_DINH))
        self.assertNotIn("Quy tắc thêm cho cuộc trò chuyện", P.SYSTEM_QUYET_DINH)
        self.assertIn("16.", P.RULES_PHIEN)
        self.assertNotIn("\n6.", P.RULES_PHIEN)        # không sửa / lặp quy tắc 6

    def test_no_benchmark_input_in_block(self):
        rows = list(csv.DictReader(open(os.path.join(ROOT, "eval", "benchmark.csv"), encoding="utf-8")))
        block = kb.fold(P.RULES_PHIEN)
        for r in rows:
            words = kb.fold(r["input"]).split()
            for i in range(max(1, len(words) - 5)):
                chunk = " ".join(words[i:i + 6])
                if len(words) >= 6:
                    self.assertNotIn(chunk, block, r["id"])

    def test_no_absolute_phrase_in_block(self):
        self.assertFalse(guards.has_absolute(P.RULES_PHIEN))

    def test_session_uses_block_single_turn_does_not(self):
        for sess, want in ((None, P.SYSTEM_QUYET_DINH), (S.ChatSession(), P.SYSTEM_QUYET_DINH_PHIEN)):
            m = Model()
            m.push(facts_json(dang_hoc=True, trinh_do="cao đẳng", he_chinh_quy=True, nam_thu=1), decision_json())
            with mock.patch.object(agent, "call_model", m):
                agent.answer("Em học cao đẳng chính quy năm nhất", session=sess)
            self.assertEqual(m.calls[1][0], want)


if __name__ == "__main__":
    unittest.main()
