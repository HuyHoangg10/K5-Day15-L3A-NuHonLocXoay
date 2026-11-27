"""Che dữ liệu cá nhân ở bước tiền xử lý: không PII gốc nào vào lời gọi model, trace hay output. Không gọi model thật."""
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import tracing  # noqa: E402

# (câu, PII gốc phải biến mất, nhãn che mong đợi) — số liệu bịa, không phải dữ liệu thật
CASES = [
    ("SĐT em 0912.345.678 nhé", "0912.345.678", "[SĐT]"),
    ("sđt 091-234-5678 ạ", "091-234-5678", "[SĐT]"),
    ("liên hệ +84 912 345 678", "912 345 678", "[SĐT]"),
    ("(+84) 912-345-678 là số em", "912-345-678", "[SĐT]"),
    ("số +84-91-234-5678", "234-5678", "[SĐT]"),
    ("gọi 0912345678 nha", "0912345678", "[SĐT]"),
    ("CCCD của em là 001 203 004 567, em", "001 203 004 567", "[CCCD]"),
    ("Số CCCD: 079.203.012.345. Em", "079.203.012.345", "[CCCD]"),
    ("CCCD 0012-0300-4567 ạ", "0012-0300-4567", "[CCCD]"),
    ("CCCD 001203004567", "001203004567", "[CCCD]"),
    ("CMND 123 456 789", "123 456 789", "[CCCD]"),
    ("gửi về tranthib.nvqs+hoi@gmail.com giúp em", "tranthib.nvqs+hoi@gmail.com", "[EMAIL]"),
]
KEEP = ["khóa 2022-2026", "em 18 tuổi, lớp 10", "ngày 27/11/2026", "năm 2024 nhập học, tốt nghiệp 2028", "Điều 41 khoản 1"]


class MaskTests(unittest.TestCase):
    def test_masks_variants(self):
        for text, raw, token in CASES:
            with self.subTest(text=text):
                out, kinds = agent.preprocess(text)
                self.assertNotIn(raw, out)
                self.assertIn(token, out)
                self.assertTrue(kinds)

    def test_keeps_dates_and_numbers_that_are_not_pii(self):
        for text in KEEP:
            with self.subTest(text=text):
                self.assertEqual(agent.preprocess(text), (text, []))


class NoPiiInTraceOrOutput(unittest.TestCase):
    def _run(self, text, model):
        tracing.begin("pii")
        try:
            with mock.patch.object(agent, "call_model", model):
                out = agent.answer(text)["output"]
        finally:
            _, events = tracing.end()
        return out, json.dumps(events, ensure_ascii=False)

    def test_raw_pii_never_reaches_model_trace_or_output(self):
        seen = []

        def echo_model(system, user):          # model "nhại" lại mọi thứ nó thấy
            seen.append(user)
            if "Căn cứ pháp lý" in user:
                return {"text": json.dumps({"nhan": "eligible_for_review", "can_cu": ["vbhn133-d41-k1-g"], "tham_khao": [],
                                            "ly_do": "Bạn viết: " + user[-200:], "can_lam_gi": "", "can_hoi_them": []},
                                           ensure_ascii=False), "model": "mock", "tokens_in": 1, "tokens_out": 1}
            return {"text": json.dumps({"chu_de": "hoc_tap", "y_do": "hop_phap", "hoi_quy_dinh_chung": False,
                                        "dang_hoc": True, "trinh_do": "đại học", "he_chinh_quy": True, "nam_thu": 1}),
                    "model": "mock", "tokens_in": 1, "tokens_out": 1}

        for text, raw, _ in CASES:
            with self.subTest(text=text):
                seen.clear()
                out, trace = self._run("Em học đại học chính quy năm 1. " + text + " Em có được hoãn không?",
                                       tracing.model_call(echo_model))
                for blob in [out, trace] + seen:
                    self.assertNotIn(raw, blob)
                self.assertIn("tiền xử lý: đã che", trace)


if __name__ == "__main__":
    unittest.main()
