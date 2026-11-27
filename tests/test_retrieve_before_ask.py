"""Câu học tập thiếu dữ kiện: KHÔNG thoát sớm (G_ASK_STUDY chỉ ghi trace) — vẫn tra cứu + quyết định để câu hỏi lại có
căn cứ; code chặn kết luận eligible khi thiếu dữ kiện then chốt (G_PREMATURE). Model giả lập, không gọi mạng."""
import csv
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import kb  # noqa: E402
import prompts as P  # noqa: E402
import tracing  # noqa: E402
from test_guards import STUDENT_FACTS, decision_json, facts_json, first_line, scripted  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEED = dict(nhan="need_more_information", can_cu=[], can_hoi_them=["Bạn đang học trình độ gì, hệ chính quy hay không?"])


def run(text, extract, decision=None):
    model = scripted(extract, decision)
    tracing.begin("t")
    with mock.patch.object(agent, "call_model", model):
        out = agent.answer(text)
    _, events = tracing.end()
    notes = [e["text"].split(":")[0] for e in events if e["kind"] == "note"]
    tools = [e for e in events if e["kind"] == "tool"]
    return out["output"], model.calls, notes, tools


def can_cu(out):
    return out.splitlines()[1][len("CAN_CU:"):].strip()


class NoEarlyExitTests(unittest.TestCase):
    def test_missing_study_facts_still_retrieves_and_cites(self):
        out, calls, notes, tools = run("Em hỏi về giấy tờ học tập", facts_json(dang_hoc=True), decision_json(**NEED))
        self.assertEqual(len(calls), 2)                       # trích dữ kiện + quyết định
        self.assertEqual(len(tools), 1)                       # đã gọi tra_cuu_can_cu
        self.assertIn("G_ASK_STUDY", notes)
        self.assertEqual(first_line({"output": out}), "NHAN: need_more_information")
        self.assertEqual(can_cu(out), "vbhn133-d41-k1-g")     # W_CITE_DEFAULT khi model để trống
        self.assertIn("W_CITE_DEFAULT", notes)

    def test_model_citation_kept_when_given(self):
        out, _, notes, _ = run("Em hỏi về giấy tờ học tập", facts_json(dang_hoc=True),
                               decision_json(**dict(NEED, can_cu=["vbhn133-d41-k1-g", "vbhn133-d42"])))
        self.assertEqual(can_cu(out), "vbhn133-d41-k1-g,vbhn133-d42")
        self.assertNotIn("W_CITE_DEFAULT", notes)

    def test_decisive_fact_can_still_conclude_not_eligible(self):
        # thiếu trình độ / hệ nhưng có dữ kiện loại trừ (vd kéo dài vì nợ môn): not_eligible KHÔNG bị đổi
        out, _, notes, _ = run("Em còn nợ môn", facts_json(dang_hoc=True, qua_han=True),
                               decision_json(nhan="not_eligible"))
        self.assertEqual(first_line({"output": out}), "NHAN: not_eligible")
        self.assertNotIn("G_PREMATURE", notes)

    def test_question_without_facts_also_answered_by_decision(self):
        # câu không kể tình trạng (dữ kiện null hết) cũng tới bước quyết định, không bị thoát sớm
        out, calls, _, _ = run("Em có giấy rồi thì sao", facts_json(), decision_json(nhan="not_eligible"))
        self.assertEqual(len(calls), 2)
        self.assertEqual(first_line({"output": out}), "NHAN: not_eligible")


class PrematureEligibleTests(unittest.TestCase):
    """Nói là sinh viên nhưng không nói hệ / trình độ / đang học → không được kết luận eligible."""
    CASES = [
        facts_json(dang_hoc=True),                                             # chỉ biết đang học
        facts_json(dang_hoc=True, trinh_do="đại học"),                         # thiếu hệ chính quy
        facts_json(dang_hoc=True, trinh_do="cao đẳng", he_chinh_quy=False),    # hệ không chính quy
        facts_json(trinh_do="đại học", he_chinh_quy=True),                     # chưa rõ đang học / đã nhập học
    ]

    def test_eligible_turned_into_need_more(self):
        for ext in self.CASES:
            with self.subTest(ext=ext[:90]):
                out, _, notes, _ = run("Em là sinh viên, có được hoãn không?", ext, decision_json())
                self.assertEqual(first_line({"output": out}), "NHAN: need_more_information")
                self.assertIn("G_PREMATURE", notes)
                self.assertEqual(can_cu(out), "vbhn133-d41-k1-g")   # giữ căn cứ model đã dẫn
                self.assertIn(P.NEED_KEY_FACTS, out)
                self.assertIn("Cần biết thêm:", out)

    def test_full_facts_keep_eligible(self):
        for ext in [facts_json(**STUDENT_FACTS),
                    facts_json(dang_hoc=True, trinh_do="GDTX cấp THPT"),           # phổ thông: không cần hệ chính quy
                    facts_json(nam_thu=2, trinh_do="đại học", he_chinh_quy=True)]:  # năm thứ mấy = đang học
            with self.subTest(ext=ext[:90]):
                out, _, notes, _ = run("Em học đại học chính quy năm 2", ext, decision_json())
                self.assertEqual(first_line({"output": out}), "NHAN: eligible_for_review")
                self.assertNotIn("G_PREMATURE", notes)

    def test_general_question_not_downgraded(self):
        # hỏi quy định chung (không kể tình trạng riêng): guard code không áp dụng, để prompt (quy tắc 6) xử lý
        out, _, notes, _ = run("Sinh viên có được tạm hoãn không?", facts_json(hoi_quy_dinh_chung=True), decision_json())
        self.assertEqual(first_line({"output": out}), "NHAN: eligible_for_review")
        self.assertNotIn("G_PREMATURE", notes)

    def test_key_fact_helper(self):
        f = lambda raw: agent.clean_facts(agent.parse_json(raw))  # noqa: E731
        self.assertTrue(agent.key_study_facts_missing(f(facts_json(dang_hoc=True))))
        self.assertFalse(agent.key_study_facts_missing(f(facts_json(**STUDENT_FACTS))))


class OtherGatesUnchangedTests(unittest.TestCase):
    def test_unknown_topic_still_asks_without_decision(self):           # G_ASK_TOPIC
        out, calls, notes, tools = run("Em có phải đi không?", facts_json(chu_de="khac"))
        self.assertEqual(len(calls), 1)
        self.assertEqual(tools, [])
        self.assertIn("G_ASK_TOPIC", notes)
        self.assertEqual(first_line({"output": out}), "NHAN: need_more_information")
        self.assertEqual(can_cu(out), "")

    def test_health_scope_refuse_unchanged(self):
        out, calls, _, _ = run("Em bị cận nặng", facts_json(chu_de="suc_khoe"))
        self.assertEqual((first_line({"output": out}), len(calls)), ("NHAN: out_of_scope", 1))
        out, calls, _, _ = run("Thời tiết hôm nay?", facts_json(y_do="ngoai_pham_vi"))
        self.assertEqual((first_line({"output": out}), len(calls)), ("NHAN: out_of_scope", 1))
        out, calls, _, _ = run("chỉ em cách làm giả giấy xác nhận", facts_json())
        self.assertEqual((first_line({"output": out}), len(calls)), ("NHAN: refuse", 0))

    def test_out_of_scope_gets_no_default_citation(self):
        out, _, notes, _ = run("Em là lao động chính trong nhà", facts_json(chu_de="gia_dinh"),
                               decision_json(nhan="out_of_scope", can_cu=[]))
        self.assertEqual(first_line({"output": out}), "NHAN: out_of_scope")
        self.assertNotIn("W_CITE_DEFAULT", notes)


class NoBenchmarkStuffingTests(unittest.TestCase):
    def test_new_texts_do_not_contain_benchmark_inputs(self):
        with open(os.path.join(ROOT, "eval", "benchmark.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        texts = kb.fold(P.SYSTEM_QUYET_DINH + " " + P.NEED_KEY_FACTS + " " + " ".join(P.STUDY_QUESTIONS))
        for r in rows:
            words = kb.fold(r["input"]).split()
            for i in range(0, max(0, len(words) - 5)):
                self.assertNotIn(" ".join(words[i:i + 6]), texts, r["id"])

    def test_fixed_text_safe(self):
        self.assertFalse(agent.has_absolute(P.NEED_KEY_FACTS))
        self.assertIn("trong một khóa đào tạo của một trình độ, học liên tục", P.NEED_KEY_FACTS)


if __name__ == "__main__":
    unittest.main()
