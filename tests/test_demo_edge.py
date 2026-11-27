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


class OnTopicShortInputTests(unittest.TestCase):
    """Câu ngắn có từ khóa chủ đề mà bước trích gắn ngoai_pham_vi: bản demo hỏi lại, không trả out_of_scope."""

    def test_short_topic_word_asks_instead_of_out_of_scope(self):
        for text in ("hoãn?", "em là sinh viên", "nghia vu quan su", "Em là SV"):
            with self.subTest(text=text):
                out, notes = turn(S.ChatSession(), Model(), text, OFFTOPIC_FACTS)
                self.assertEqual(nhan(out), "need_more_information")
                self.assertTrue(any(n.startswith("W_ONTOPIC") for n in notes))

    def test_student_fact_goes_to_study_questions(self):
        out, _ = turn(S.ChatSession(), Model(), "em là sinh viên",
                      facts_json(chu_de="hoc_tap", y_do="ngoai_pham_vi", dang_hoc=True))
        self.assertEqual(nhan(out), "need_more_information")
        self.assertIn(P.STUDY_QUESTIONS[0], out)

    def test_real_off_topic_stays_out_of_scope(self):
        for text in ("Cho mình công thức nấu phở bò", "Giá vàng hôm nay bao nhiêu?", "Thủ tục xin visa du học Úc?",
                     "Hoàn thành bài tập Python giúp mình"):
            with self.subTest(text=text):
                out, notes = turn(S.ChatSession(), Model(), text, OFFTOPIC_FACTS)
                self.assertEqual(nhan(out), "out_of_scope")
                self.assertFalse(any(n.startswith("W_ONTOPIC") for n in notes))

    def test_single_turn_path_unchanged(self):
        m = Model()
        m.push(OFFTOPIC_FACTS)
        with mock.patch.object(agent, "call_model", m):
            out = agent.answer("hoãn?")["output"]
        self.assertEqual(nhan(out), "out_of_scope")

    def test_attack_still_refused_first(self):
        out, _ = turn(S.ChatSession(), Model(), "sinh viên muốn mua giấy hoãn ở đâu")
        self.assertEqual(nhan(out), "refuse")


class OffTopicDisplayTests(unittest.TestCase):
    """Hiển thị: câu ngoài chủ đề hẳn không kèm bước "hỏi Ban Chỉ huy quân sự" và lưu ý về Hội đồng NVQS."""

    def _offtopic_output(self):
        m = Model()
        m.push(OFFTOPIC_FACTS)
        with mock.patch.object(agent, "call_model", m):
            return agent.answer("Cho mình công thức nấu phở bò")["output"]

    def test_offtopic_pretty_has_no_military_redirect(self):
        raw = self._offtopic_output()
        self.assertIn(P.REDIRECT_OTHER, raw)               # bản gốc (/goc, eval) giữ nguyên
        nice = demo_ui.pretty(raw)
        self.assertNotIn("Ban Chỉ huy", nice)
        self.assertNotIn("Lưu ý", nice)
        self.assertIn(demo_ui.OFFTOPIC_HINT, nice)
        self.assertTrue(nice.startswith(demo_ui.LABEL_TEXT["out_of_scope"]))

    def test_health_out_of_scope_keeps_redirect(self):
        raw = agent.render("out_of_scope", P.OUT_OF_SCOPE, P.REDIRECT_HEALTH)["output"]
        nice = demo_ui.pretty(raw)
        self.assertIn("Hội đồng khám sức khỏe", nice)
        self.assertNotIn(demo_ui.OFFTOPIC_HINT, nice)

    def test_model_out_of_scope_with_steps_keeps_them(self):
        raw = agent.render("out_of_scope", "Câu này về xử phạt, ngoài phạm vi.",
                           ["Đọc Điều 10.", P.REDIRECT_OTHER])["output"]
        self.assertIn("Ban Chỉ huy", demo_ui.pretty(raw))


if __name__ == "__main__":
    unittest.main()
