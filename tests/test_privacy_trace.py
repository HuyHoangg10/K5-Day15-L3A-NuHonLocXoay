"""Riêng tư (model kịch bản CHÉP LẠI câu người dùng, không gọi mạng): email, SĐT, CCCD, họ tên mẫu, key, token Bearer
không xuất hiện ở dạng gốc trong trace (mọi sự kiện), bản ghi phiên, khối ngữ cảnh, đầu ra, câu báo lỗi."""
import json
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import demo_ui  # noqa: E402
import session as S  # noqa: E402
import tracing  # noqa: E402
from test_guards import decision_json, facts_json  # noqa: E402

SECRETS = {"email": "an.nguyen99@gmail.com", "sdt": "0912 345 678", "cccd": "001203004567", "ten": "Nguyễn Văn An",
           "key": "sk-proj-AbCdEf1234567890GhIjKlMnOpQr", "bearer": "abcDEF1234567890xyzXYZ7777"}
TEXTS = ["Em tên là Nguyễn Văn An, email an.nguyen99@gmail.com, sđt 0912 345 678, CCCD 001203004567, học ĐH chính quy năm 2",
         "key của em sk-proj-AbCdEf1234567890GhIjKlMnOpQr, header Bearer abcDEF1234567890xyzXYZ7777, em học cao đẳng"]


def echo_model(system, user):
    if system == agent.P.SYSTEM_TRICH:
        return {"text": facts_json(dang_hoc=True, trinh_do="đại học", he_chinh_quy=True), "model": "t",
                "tokens_in": 1, "tokens_out": 1}
    return {"text": decision_json(ly_do="Bạn nói: " + user[-200:]), "model": "t", "tokens_in": 1, "tokens_out": 1}


def boom(system, user):
    raise RuntimeError("HTTP 400: invalid content: " + user[-150:])


class PrivacyTests(unittest.TestCase):
    def assertClean(self, where, blob):
        for k, v in SECRETS.items():
            self.assertNotIn(v, blob, "%s lộ %s" % (where, k))

    def run_turn(self, model, text, sess):
        tracing.begin("privacy")
        with mock.patch.object(agent, "call_model", tracing.model_call(model)):
            out = agent.answer(text, session=sess)["output"]
        _, ev = tracing.end()
        return out, ev

    def test_trace_session_output_clean(self):
        for sess in (None, S.ChatSession()):
            for t in TEXTS:
                out, ev = self.run_turn(echo_model, t, sess)
                self.assertClean("đầu ra", out)
                self.assertClean("trace", json.dumps(ev, ensure_ascii=False))
            if sess is not None:
                self.assertClean("phiên", json.dumps(sess.turns, ensure_ascii=False) + json.dumps(sess.facts, ensure_ascii=False))
                self.assertClean("khối ngữ cảnh", sess.context_block() + sess.extract_context())

    def test_error_path_clean(self):
        out, ev = self.run_turn(boom, TEXTS[0], S.ChatSession())
        self.assertTrue(out.startswith("LOI:"))
        self.assertClean("trace lỗi", json.dumps(ev, ensure_ascii=False))
        self.assertClean("câu báo lỗi", demo_ui.friendly_error(out, ev) or "")

    def test_masks(self):
        cases = {"Em tên là Nguyễn Văn An, học ĐH": "Em tên là [TÊN], học ĐH",
                 "Họ và tên: Trần Thị Bình": "Họ và tên: [TÊN]", "Tên em là Phạm Đức": "Tên em là [TÊN]",
                 "tôi là Lê Minh Châu": "tôi là [TÊN]", "key sk-ant-api03-AbCdEf1234567890 nhé": "key [KEY] nhé",
                 "Authorization: Bearer abcDEF1234567890xyz=": "Authorization: [KEY]", "api_key = abc123def456ghi": "[KEY]"}
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(agent.preprocess(raw)[0], want)

    def test_no_false_mask(self):
        for t in ("em là SV năm 2", "em là sinh viên", "Em là Sinh viên Bách Khoa", "tên trường là Đại học Bách khoa",
                  "Em học khóa 2022-2026", "Ban Chỉ huy quân sự cấp xã", "token: xyz"):
            with self.subTest(t=t):
                self.assertEqual(agent.preprocess(t), (t, []))

    def test_note_lists_kinds_not_values(self):
        tracing.begin("privacy")
        agent.answer(TEXTS[0])
        _, ev = tracing.end()
        notes = " ".join(e["text"] for e in ev if e["kind"] == "note")
        self.assertIn("tên", notes)
        self.assertClean("note", notes)


if __name__ == "__main__":
    unittest.main()
