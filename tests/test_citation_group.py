"""Nhóm lỗi "căn cứ thiếu hoặc sai mã": chuẩn hóa căn cứ bằng code sau khi kiểm đầu ra.
W_CITE_UNIT: ưu tiên đơn vị luật nhỏ nhất (bỏ mã cả điều thừa / đổi sang điểm luật học tập khi không mơ hồ).
W_CITE_AUTHORITY: eligible_for_review dẫn thêm điều luật về thẩm quyền quyết định tạm hoãn.
Model giả lập, không gọi mạng."""
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

HQ = "vbhn133-d42"
G = "vbhn133-d41-k1-g"


def run(text, extract, decision):
    model = scripted(extract, decision)
    tracing.begin("t")
    with mock.patch.object(agent, "call_model", model):
        out = agent.answer(text)["output"]
    _, events = tracing.end()
    return out, [e["text"].split(":")[0] for e in events if e["kind"] == "note"]


def can_cu(out):
    return out.splitlines()[1][len("CAN_CU:"):].strip()


class SmallestUnitTests(unittest.TestCase):
    def test_sub_units_from_kb(self):
        subs = agent.sub_units("vbhn133-d41")
        self.assertIn(G, subs)
        self.assertIn("vbhn133-d41-k2-a", subs)
        self.assertTrue(all(s in kb.legal_ids() for s in subs))
        self.assertEqual(agent.sub_units(G), [])               # đã là điểm
        self.assertEqual(agent.sub_units(HQ), [])              # điều không có khoản/điểm riêng trong kho
        self.assertEqual(agent.sub_units("khong-co"), [])

    def test_whole_article_only_maps_to_study_point_on_study_topic(self):
        out, notes = run("Có phải ai là sinh viên cũng được miễn không?", facts_json(hoi_quy_dinh_chung=True),
                         decision_json(nhan="not_eligible", can_cu=["vbhn133-d41"]))
        self.assertEqual(first_line({"output": out}), "NHAN: not_eligible")
        self.assertEqual(can_cu(out), G)
        self.assertIn("W_CITE_UNIT", notes)

    def test_redundant_whole_article_dropped(self):
        out, notes = run("Có phải ai là sinh viên cũng được miễn không?", facts_json(hoi_quy_dinh_chung=True),
                         decision_json(nhan="not_eligible", can_cu=[G, "vbhn133-d41", "vbhn133-d41-k2-a"]))
        self.assertEqual(can_cu(out), G + ",vbhn133-d41-k2-a")
        self.assertIn("W_CITE_UNIT", notes)

    def test_no_duplicate_when_mapping(self):
        d = agent.narrow_citations(dict(nhan="not_eligible", can_cu=["vbhn133-d41", G]), "hoc_tap")
        self.assertEqual(d["can_cu"], [G])

    def test_ambiguous_whole_article_kept_outside_study_topic(self):
        d = agent.narrow_citations(dict(nhan="out_of_scope", can_cu=["vbhn133-d41"]), "gia_dinh")
        self.assertEqual(d["can_cu"], ["vbhn133-d41"])          # không biết khoản/điểm nào → không đoán

    def test_articles_without_sub_units_untouched(self):
        d = agent.narrow_citations(dict(nhan="out_of_scope", can_cu=["vbhn133-d10", "nd218-d9"]), "hoc_tap")
        self.assertEqual(d["can_cu"], ["vbhn133-d10", "nd218-d9"])

    def test_only_existing_ids_produced(self):
        for cc in (["vbhn133-d41"], [G, "vbhn133-d41"], ["vbhn133-d4", "vbhn133-d30"]):
            for topic in ("hoc_tap", "suc_khoe", None):
                d = agent.narrow_citations(dict(nhan="not_eligible", can_cu=cc), topic)
                self.assertTrue(set(d["can_cu"]) <= kb.legal_ids(), (cc, topic))


class AuthorityTests(unittest.TestCase):
    def test_eligible_gets_authority_article(self):
        out, notes = run("Em học đại học chính quy năm 2", facts_json(**STUDENT_FACTS), decision_json())
        self.assertEqual(first_line({"output": out}), "NHAN: eligible_for_review")
        self.assertEqual(can_cu(out), G + "," + HQ)
        self.assertIn("W_CITE_AUTHORITY", notes)
        self.assertIn("Chủ tịch Ủy ban nhân dân cấp tỉnh quyết định tạm hoãn", P.DISCLAIMER)   # lý do của quy tắc
        self.assertIn("Chủ tịch Ủy ban nhân dân cấp tỉnh", kb.get_chunk(HQ)["text"])

    def test_not_added_twice(self):
        out, notes = run("Em học đại học chính quy năm 2", facts_json(**STUDENT_FACTS), decision_json(can_cu=[HQ, G]))
        self.assertEqual(can_cu(out), HQ + "," + G)
        self.assertNotIn("W_CITE_AUTHORITY", notes)

    def test_other_labels_not_given_authority(self):
        for nhan, ext in (("not_eligible", facts_json(dang_hoc=True, qua_han=True)),
                          ("need_more_information", facts_json(dang_hoc=True)),
                          ("out_of_scope", facts_json(chu_de="gia_dinh"))):
            with self.subTest(nhan=nhan):
                out, notes = run("Em hỏi", ext, decision_json(nhan=nhan, can_cu=[G] if nhan != "out_of_scope" else []))
                self.assertNotIn(HQ, can_cu(out))
                self.assertNotIn("W_CITE_AUTHORITY", notes)

    def test_premature_eligible_downgraded_gets_no_authority(self):
        out, notes = run("Em là sinh viên", facts_json(dang_hoc=True), decision_json())
        self.assertEqual(first_line({"output": out}), "NHAN: need_more_information")
        self.assertEqual(can_cu(out), G)
        self.assertNotIn("W_CITE_AUTHORITY", notes)


class CodesRegisteredTests(unittest.TestCase):
    def test_new_codes_documented(self):
        for code in ("W_CITE_UNIT", "W_CITE_AUTHORITY"):
            self.assertIn(code, agent.GUARD_CODES)
            self.assertIn(code, agent.__doc__)


if __name__ == "__main__":
    unittest.main()
