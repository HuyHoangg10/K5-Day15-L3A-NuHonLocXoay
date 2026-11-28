"""Kiểm tầng kho văn bản kb-nvqs (codebase/kb.py) và công cụ tra_cuu_can_cu. Không gọi model, không gọi mạng.
Chạy: python -m unittest discover tests
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import kb  # noqa: E402
import tools  # noqa: E402


class KbLoadTests(unittest.TestCase):
    def test_reads_both_files(self):
        self.assertGreater(len(kb.legal_all()), 0)
        self.assertGreater(len(kb.qa_all()), 0)

    def test_mvp_chunks_exist_and_ids_match(self):
        mvp = kb.legal_mvp()
        self.assertGreater(len(mvp), 0)
        self.assertTrue(all(c["mvp"] is True for c in mvp))
        self.assertEqual(kb.legal_ids(), frozenset(c["id"] for c in mvp))
        self.assertIn("vbhn133-d41-k1-g", kb.legal_ids())

    def test_ids_unique(self):
        for rows in (kb.legal_all(), kb.qa_all()):
            ids = [c["id"] for c in rows]
            self.assertEqual(len(ids), len(set(ids)))

    def test_legal_ids_exclude_qa(self):
        self.assertFalse(any(kb.is_qa_id(i) for i in kb.legal_ids()))

    def test_get_chunk(self):
        self.assertEqual(kb.get_chunk("vbhn133-d41-k1-g")["dieu"], "41")
        self.assertIsNotNone(kb.get_chunk("qa-q01"))
        self.assertIsNone(kb.get_chunk("khong-co-id-nay"))

    def test_chunks_have_fields_for_citation(self):
        for c in kb.legal_mvp():
            for k in ("id", "so_hieu", "text", "nguon"):
                self.assertTrue(c.get(k), "%s thiếu %s" % (c.get("id"), k))


class QaSearchTests(unittest.TestCase):
    @staticmethod
    def about_no_mon(hits):
        return any("nợ môn" in (h.get("title", "") + h.get("question", "")).lower() for h in hits)

    def test_finds_no_mon_article(self):
        hits = kb.qa_search("em nợ môn chưa tốt nghiệp", k=2)
        self.assertEqual(len(hits), 2)
        self.assertTrue(self.about_no_mon(hits), [h["id"] for h in hits])

    def test_finds_without_diacritics(self):
        hits = kb.qa_search("em no mon chua tot nghiep", k=2)
        self.assertTrue(self.about_no_mon(hits), [h["id"] for h in hits])

    def test_only_hoi_dap(self):
        for q in ("du học", "liên thông đại học", "nợ môn"):
            self.assertTrue(all(h["loai"] == "hoi_dap" for h in kb.qa_search(q, k=5)))

    def test_no_match_returns_empty(self):
        self.assertEqual(kb.qa_search("zzqxw", k=2), [])

    def test_fold(self):
        self.assertEqual(kb.fold("Đại Học NỢ MÔN"), "dai hoc no mon")


class ToolTests(unittest.TestCase):
    def test_tra_cuu_can_cu_shape(self):
        out = tools.tra_cuu_can_cu("em nợ môn chưa tốt nghiệp")
        self.assertEqual({c["id"] for c in out["luat"]}, kb.legal_ids())
        ids = [h["id"] for h in out["tham_khao"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(set(tools.QA_CORE) <= set(ids))               # bài nền luôn có
        self.assertLessEqual(len(ids), tools.QA_K + len(tools.QA_CORE))
        self.assertTrue(all(kb.is_qa_id(h["id"]) for h in out["tham_khao"]))

    def test_registered_as_tool(self):
        self.assertIn("tra_cuu_can_cu", tools.TOOLS)


if __name__ == "__main__":
    unittest.main()
