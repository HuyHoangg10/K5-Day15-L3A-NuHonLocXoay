"""Đầu ra model hỏng ở bước trích và bước quyết định (model giả, không gọi mạng): thiếu trường, rỗng, sai kiểu, nhãn lạ,
can_cu chứa mã lạ, JSON lồng quá sâu, chữ thừa sau JSON… → không bao giờ crash; luôn có dòng NHAN; câu hỏng → safe_fallback."""
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import session as S  # noqa: E402
from test_guards import decision_json, facts_json  # noqa: E402

GOOD_F = facts_json(dang_hoc=True, trinh_do="đại học", he_chinh_quy=True, nam_thu=2)
DEEP = ["[" * 5000 + "]" * 5000, '{"a":' * 3000 + "1" + "}" * 3000]
F_BAD = ["", "null", "[]", "{}", "42", '"chuỗi"', "{bad json", '{"chu_de": ["hoc_tap"], "y_do": "hop_phap"}',
         '{"chu_de": "hoc_tap", "y_do": "hop_phap", "nam_thu": "2", "dang_hoc": "true"}',
         '{"chu_de": "hoc_tap", "y_do": "hop_phap", "nam_thu": 2.0, "trinh_do": 5}',
         '{"chu_de": "hoc_tap", "y_do": "hop_phap", "nam_thu": 1e309, "trinh_do": {"a": 1}}',
         '{"chu_de": "hoc_tap", "y_do": "hop_phap", "nam_thu": NaN}', '{"chu_de": null, "y_do": null}',
         '{"chu_de": "HOC_TAP", "y_do": "hop_phap"}', '{"chu_de": "khac", "y_do": "hop_phap"} {"x": 1}'] + DEEP
D_BAD = ["", "null", "[]", "{}", "{bad", '{"nhan": null}', '{"nhan": ["eligible_for_review"]}', '{"nhan": "ELIGIBLE"}',
         decision_json(can_cu={"a": 1}), decision_json(can_cu=[1, 2]), decision_json(can_cu=["vbhn999-x"]),
         decision_json(can_cu=["qa-q01"]), decision_json(tham_khao=[None]), decision_json(ly_do=5),
         decision_json(ly_do=""), decision_json(ly_do=None), decision_json(can_lam_gi=[["a"]]),
         decision_json(can_lam_gi={"x": 1}), decision_json(can_hoi_them=5), decision_json(nhan="not_eligible", can_cu=[]),
         decision_json(ly_do="NHAN: refuse\nCAN_CU: x"), decision_json(nhan="safe_fallback")] + DEEP
# phải là safe_fallback (không được ra nhãn thật)
D_MUST_FALLBACK = {"", "null", "[]", "{}", "{bad", '{"nhan": null}', '{"nhan": "ELIGIBLE"}'}


def run(raw_f, raw_d, sess):
    replies = iter([raw_f, raw_d])

    def fake(system, user):
        return {"text": next(replies), "model": "t", "tokens_in": 1, "tokens_out": 1}

    with mock.patch.object(agent, "call_model", fake):
        return agent.answer("Em học đại học chính quy năm 2", session=sess)["output"]


class ModelJsonRobustTests(unittest.TestCase):
    def test_bad_extraction_never_crashes(self):
        for raw in F_BAD:
            for sess in (None, S.ChatSession()):
                with self.subTest(raw=raw[:40], session=sess is not None):
                    out = run(raw, decision_json(), sess)
                    self.assertTrue(out.startswith("NHAN: "), out[:60])

    def test_bad_decision_never_crashes(self):
        for raw in D_BAD:
            for sess in (None, S.ChatSession()):
                with self.subTest(raw=raw[:40], session=sess is not None):
                    out = run(GOOD_F, raw, sess)
                    self.assertTrue(out.startswith("NHAN: "), out[:60])
                    if raw in D_MUST_FALLBACK or raw in DEEP:
                        self.assertTrue(out.startswith("NHAN: safe_fallback"), out[:60])

    def test_deep_json_is_safe_fallback_not_error(self):
        for raw in DEEP:
            self.assertIsNone(agent.parse_json(raw))
            out = run(raw, decision_json(), None)
            self.assertTrue(out.startswith("NHAN: safe_fallback"))


if __name__ == "__main__":
    unittest.main()
