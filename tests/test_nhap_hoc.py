"""B3 (nhánh thử exp/post-cp4-prompt): dữ kiện "đã nhập học / mới trúng tuyển, chưa nhập học" (da_nhap_hoc) ở bước
trích + quy tắc quyết định riêng (15c): tạm hoãn vì học tập tính từ khi đã làm xong thủ tục nhập học và đang học.
Model giả, không gọi mạng. CHƯA kiểm bằng model thật."""
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
import session as S  # noqa: E402
from test_chat_session import Model, decision_prompts, turn  # noqa: E402
from test_guards import decision_json, facts_json, scripted  # noqa: E402

NEED = decision_json(nhan="need_more_information", can_cu=["vbhn133-d41-k1-g"],
                     ly_do="Tạm hoãn vì học tập chỉ tính từ khi bạn đã làm xong thủ tục nhập học và đang học.",
                     can_lam_gi=[], can_hoi_them=["Bạn đã làm xong thủ tục nhập học chưa?"])


class NhapHocTests(unittest.TestCase):
    def test_extract_prompt_and_fact_lists(self):
        self.assertIn('"da_nhap_hoc": true/false/null', P.SYSTEM_TRICH)
        for tup in (agent.BOOL_FACTS, agent.STUDY_DETAIL_FACTS, S.MEMORY_FACTS):
            self.assertIn("da_nhap_hoc", tup)
        self.assertIs(agent.clean_facts({"chu_de": "hoc_tap", "y_do": "hop_phap", "da_nhap_hoc": False})["da_nhap_hoc"],
                      False)
        self.assertIsNone(agent.clean_facts({"chu_de": "hoc_tap", "y_do": "hop_phap", "da_nhap_hoc": "chưa"})["da_nhap_hoc"])

    def test_rule_block_separate(self):
        self.assertIn(P.RULES_NHAP_HOC, P.SYSTEM_QUYET_DINH)
        self.assertIn("đã làm xong thủ tục nhập học", P.RULES_NHAP_HOC)
        self.assertNotIn("15c.", P.DOMAIN_RULES + P.STYLE_RULES + P.RULES_PHIEN)

    def test_not_enrolled_reaches_decision_with_fact(self):
        # chỉ biết "chưa nhập học" (không trình độ / hệ…): trước B3 bị G_ASK_STUDY hỏi chung chung; nay đi tới bước
        # quyết định, prompt có da_nhap_hoc=False để model áp quy tắc 15c
        fn = scripted(facts_json(da_nhap_hoc=False), NEED)
        with mock.patch.object(agent, "call_model", fn):
            out = agent.answer("Em vừa trúng tuyển, chưa làm thủ tục nhập học, có được tạm hoãn không?")["output"]
        self.assertTrue(out.startswith("NHAN: need_more_information"))
        self.assertIn("thủ tục nhập học", out)
        system, user = fn.calls[-1]
        self.assertEqual(system, P.SYSTEM_QUYET_DINH)
        self.assertIn("da_nhap_hoc=False", user)

    def test_session_remembers_enrolment(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em đã nhập học đại học", facts_json(dang_hoc=True, da_nhap_hoc=True, trinh_do="đại học"), NEED)
        turn(s, m, "hệ chính quy", facts_json(chu_de="khac", he_chinh_quy=True), decision_json())
        self.assertIs(s.facts.get("da_nhap_hoc"), True)
        self.assertIn("da_nhap_hoc=True", decision_prompts(m)[-1])


if __name__ == "__main__":
    unittest.main()
