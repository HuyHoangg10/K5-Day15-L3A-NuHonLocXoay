"""Bước trích dữ kiện trả JSON hợp lệ nhưng chu_de / y_do = null: hỏi lại chủ đề thay vì safe_fallback."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
from test_guards import facts_json, first_line, scripted  # noqa: E402


class NullExtractTests(unittest.TestCase):
    def _answer(self, extract):
        model = scripted(extract)
        with mock.patch.object(agent, "call_model", model):
            out = agent.answer("Em có phải đi không?")
        return out, model.calls

    def test_all_null_asks_topic_without_decision_call(self):
        out, calls = self._answer(facts_json(chu_de=None, y_do=None, hoi_quy_dinh_chung=None))
        self.assertEqual(first_line(out), "NHAN: need_more_information")
        self.assertEqual(len(calls), 1)

    def test_null_topic_out_of_scope_intent(self):
        out, calls = self._answer(facts_json(chu_de=None, y_do="ngoai_pham_vi"))
        self.assertEqual(first_line(out), "NHAN: out_of_scope")
        self.assertEqual(len(calls), 1)

    def test_null_topic_evasion_intent_still_refuses(self):
        out, _ = self._answer(facts_json(chu_de=None, y_do="lach_luat"))
        self.assertEqual(first_line(out), "NHAN: refuse")

    def test_null_intent_with_real_topic_stays_safe(self):
        # chủ đề rõ mà không biết ý định → không đoán là hợp pháp
        out, calls = self._answer(facts_json(chu_de="hoc_tap", y_do=None))
        self.assertEqual(first_line(out), "NHAN: safe_fallback")
        self.assertEqual(len(calls), 1)

    def test_invalid_values_still_safe(self):
        out, _ = self._answer(facts_json(chu_de="thoi_tiet", y_do="hop_phap"))
        self.assertEqual(first_line(out), "NHAN: safe_fallback")


if __name__ == "__main__":
    unittest.main()
