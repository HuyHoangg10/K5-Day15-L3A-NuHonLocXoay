"""Hiển thị đẹp cho demo (demo_ui.pretty): chỉ đổi cách trình bày, không đổi nhãn / căn cứ / nội dung. Không gọi mạng."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import demo_ui  # noqa: E402
import kb  # noqa: E402
import prompts as P  # noqa: E402


def sample(**kw):
    d = dict(nhan="need_more_information", giai_thich="Ngữ cảnh chưa nêu giấy tờ cần nộp.",
             viec=["Bạn hỏi nhà trường.", "Bạn nên hỏi Ban Chỉ huy quân sự cấp xã nơi bạn cư trú để được hướng dẫn."],
             passages=[kb.get_chunk("vbhn133-d41-k1-g"), kb.get_chunk("vbhn133-d41-k3-4")],
             tham_khao=[kb.get_chunk("qa-q23")], hoi_them=["Bạn học hệ chính quy không?", "Bạn đã từng được hoãn chưa?"])
    d.update(kw)
    return agent.render(d.pop("nhan"), d.pop("giai_thich"), **d)["output"]


class PrettyTests(unittest.TestCase):
    def test_layout(self):
        p = demo_ui.pretty(sample())
        self.assertTrue(p.startswith(demo_ui.LABEL_TEXT["need_more_information"]))
        self.assertNotIn("NHAN:", p)
        self.assertNotIn("CAN_CU:", p)
        self.assertIn("  • Bạn học hệ chính quy không?\n  • Bạn đã từng được hoãn chưa?", p)
        self.assertIn("  1. Bạn hỏi nhà trường.", p)
        self.assertIn("Điểm g khoản 1 Điều 41 Luật Nghĩa vụ quân sự (133/2026/VBHN-LQ-VPQH)", p)
        self.assertIn("Khoản 3–4 Điều 41 Luật Nghĩa vụ quân sự", p)
        self.assertIn(kb.get_chunk("qa-q23")["title"], p)
        self.assertNotIn("http", p)
        self.assertIn("Văn bản mình có chưa nêu", p)              # từ nội bộ "ngữ cảnh" không hiện ra
        self.assertIn(P.DISCLAIMER, p)

    def test_short_disclaimer_after_first(self):
        p = demo_ui.pretty(sample(), show_full_disclaimer=False)
        self.assertIn(demo_ui.SHORT_DISCLAIMER, p)
        self.assertNotIn(P.DISCLAIMER, p)

    def test_content_preserved(self):
        raw = sample(nhan="eligible_for_review", giai_thich="Bạn có căn cứ để đề nghị xem xét tạm hoãn.", hoi_them=None)
        p = demo_ui.pretty(raw)
        self.assertTrue(p.startswith(demo_ui.LABEL_TEXT["eligible_for_review"]))
        self.assertIn("Bạn có căn cứ để đề nghị xem xét tạm hoãn.", p)
        self.assertNotIn("Mình cần biết thêm", p)

    def test_every_label_and_refuse_without_sources(self):
        for nhan in demo_ui.LABEL_TEXT:
            self.assertTrue(demo_ui.pretty(sample(nhan=nhan)).startswith(demo_ui.LABEL_TEXT[nhan]))
        r = agent.render("refuse", "Mình không hỗ trợ.", disclaimer=False)["output"]
        p = demo_ui.pretty(r)
        self.assertNotIn("Căn cứ:", p)
        self.assertNotIn("Lưu ý", p)

    def test_safe_sentence_reads_naturally(self):
        p = demo_ui.pretty(agent.render(P.SAFE_LABEL, P.SAFE_SENTENCE)["output"])
        self.assertNotIn("văn bản trong văn bản", p)
        self.assertIn("văn bản luật mình có", p)

    def test_non_standard_output_unchanged(self):
        for s in ("LOI: " + P.ERROR_MESSAGE, "", "chuỗi lạ"):
            self.assertEqual(demo_ui.pretty(s), s)

    def test_law_names_for_all_mvp_chunks(self):
        for c in kb.legal_mvp():
            n = demo_ui.law_name(c)
            self.assertIn("Điều %s" % c["dieu"], n)
            self.assertIn(c["so_hieu"], n)


if __name__ == "__main__":
    unittest.main()
