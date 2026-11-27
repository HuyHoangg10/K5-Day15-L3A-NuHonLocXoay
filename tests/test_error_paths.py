"""A3: các nhánh lỗi chưa có test (đo phủ dòng bằng sys.settrace): lỗi / quá giờ ở bước quyết định, kho hỏng khi kiểm
đầu ra, ngữ cảnh quá dài, hợp đồng hàm gọi model trong tracing, dòng JSON hỏng trong kho, và các nhánh lỗi của app
(chưa nối model, Ctrl+C giữa câu, cuộc trò chuyện quá dài, lỗi nạp codebase/). Model giả, không gọi mạng."""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import app  # noqa: E402
import demo_ui  # noqa: E402
import kb  # noqa: E402
import tracing  # noqa: E402
from test_guards import STUDENT_FACTS, decision_json, facts_json, scripted  # noqa: E402

Q = "Em đang học đại học chính quy năm 2, có được tạm hoãn không?"


def extract_then(decision_effect):
    """Lần gọi trích dữ kiện trả dữ kiện sinh viên; lần gọi quyết định chạy `decision_effect` (ném lỗi…)."""
    def fn(system, user):
        if system == agent.P.SYSTEM_TRICH:
            return {"text": facts_json(**STUDENT_FACTS), "model": "t", "tokens_in": 1, "tokens_out": 1}
        return decision_effect()
    return fn


def run_traced(fn, text=Q, **patches):
    tracing.begin("t")
    try:
        with mock.patch.object(agent, "call_model", fn), contextlib.ExitStack() as st:
            for k, v in patches.items():
                st.enter_context(mock.patch.object(agent, k, v))
            out = agent.answer(text)["output"]
    finally:
        _, events = tracing.end()
    return out, [e["text"] for e in events if e["kind"] == "note"]


def boom(exc):
    def f(*a, **k):
        raise exc
    return f


class DecisionErrorTests(unittest.TestCase):
    def test_decision_model_error(self):
        out, notes = run_traced(extract_then(boom(RuntimeError("mạng"))))
        self.assertTrue(out.startswith("LOI: "))
        self.assertTrue(any(n.startswith("E_MODEL: quyết định — RuntimeError") for n in notes), notes)

    def test_decision_not_implemented_propagates(self):
        with self.assertRaises(NotImplementedError):
            run_traced(extract_then(boom(NotImplementedError("chưa nối"))))

    def test_timeout_before_decision(self):
        out, notes = run_traced(scripted(facts_json(**STUDENT_FACTS), decision_json()), DEADLINE_S=-1)
        self.assertTrue(out.startswith("LOI: "))
        self.assertTrue(any(n.startswith("E_TIMEOUT") for n in notes), notes)

    def test_kb_error_while_validating(self):
        out, notes = run_traced(scripted(facts_json(**STUDENT_FACTS), decision_json()),
                                validate_decision=boom(OSError("kho")))
        self.assertTrue(out.startswith("LOI: "))
        self.assertTrue(any(n.startswith("E_KB: kiểm đầu ra — OSError") for n in notes), notes)

    def test_long_context_only_warns(self):
        out, notes = run_traced(scripted(facts_json(**STUDENT_FACTS), decision_json()), MAX_CONTEXT_CHARS=10)
        self.assertTrue(out.startswith("NHAN: eligible_for_review"))
        self.assertTrue(any(n.startswith("W_CONTEXT") for n in notes), notes)


class TracingContractTests(unittest.TestCase):
    def call(self, ret=None, exc=None):
        @tracing.model_call
        def fake(system, user):
            if exc:
                raise exc
            return ret
        tracing.begin("t")
        try:
            try:
                fake("s", "u")
                err = None
            except Exception as e:
                err = e
        finally:
            _, events = tracing.end()
        return err, events[-1]

    def test_non_dict(self):
        err, ev = self.call("chuỗi")
        self.assertIsInstance(err, TypeError)
        self.assertIn("phải trả dict", ev["error"])

    def test_missing_keys_and_bad_tokens(self):
        err, ev = self.call({"text": "x", "tokens_in": True, "tokens_out": -1})
        self.assertIsInstance(err, TypeError)
        for part in ("thiếu khoá model", "tokens_in phải là số nguyên", "tokens_out phải là số nguyên"):
            self.assertIn(part, ev["error"])
        self.assertEqual(ev["model"], "")

    def test_exception_recorded_and_reraised(self):
        err, ev = self.call(exc=ConnectionError("đứt"))
        self.assertIsInstance(err, ConnectionError)
        self.assertIn("ConnectionError: đứt", ev["error"])

    def test_tool_error_recorded(self):
        @tracing.tool
        def cong_cu_hong(x):
            raise KeyError("k")
        tracing.begin("t")
        try:
            with self.assertRaises(KeyError):
                cong_cu_hong(1)
        finally:
            _, events = tracing.end()
        tracing.TOOLS.pop("cong_cu_hong", None)
        self.assertTrue(events[-1]["error"].startswith("KeyError"))


class KbJsonlTests(unittest.TestCase):
    def test_bad_line_reports_line_number_and_blank_lines_skipped(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "x.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                f.write('{"id": "a"}\n\n{hỏng\n')
            with mock.patch.object(kb, "ROOT", d), mock.patch.dict(kb._cache, clear=False):
                with self.assertRaises(ValueError) as cm:
                    kb._read_jsonl(p)
            self.assertIn("x.jsonl dòng 3", str(cm.exception))
            with open(p, "w", encoding="utf-8") as f:
                f.write('{"id": "a"}\n\n')
            with mock.patch.dict(kb._cache, clear=False):
                self.assertEqual([r["id"] for r in kb._read_jsonl(p)], ["a"])
                kb._cache.pop(p, None)
        finally:
            shutil.rmtree(d, ignore_errors=True)


def run_app(inputs, **patches):
    buf = io.StringIO()
    with mock.patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(buf), \
            contextlib.ExitStack() as st:
        for target, kw in patches.items():
            st.enter_context(mock.patch(target.replace("__", "."), **kw))
        code = app.main()
    return code, buf.getvalue()


class AppErrorBranchTests(unittest.TestCase):
    def test_not_connected_model(self):
        code, out = run_app([Q], agent__answer=dict(side_effect=NotImplementedError("chưa có khóa")))
        self.assertEqual(code, 1)
        self.assertIn("Chưa nối model: chưa có khóa", out)

    def test_ctrl_c_during_answer_keeps_chatting(self):
        code, out = run_app([Q, "/thoat"], agent__answer=dict(side_effect=KeyboardInterrupt))
        self.assertEqual(code, 0)
        self.assertIn("Đã dừng câu này", out)
        self.assertIn(demo_ui.BYE, out)

    def test_too_long_chat_hint(self):
        code, out = run_app([Q, "/thoat"], session__ChatSession__too_long=dict(return_value=True))
        self.assertEqual(code, 0)
        self.assertIn(demo_ui.TOO_LONG_CHAT, out)

    def test_import_error_friendly(self):
        with mock.patch.dict(sys.modules, {"agent": None}):
            code, out = run_app([])
        self.assertEqual(code, 1)
        self.assertIn("Không nạp được codebase/", out)
        self.assertNotIn("Traceback", out)

    def test_where_names_file(self):
        base = os.path.dirname(HERE)
        e = SyntaxError("x")
        e.filename = os.path.join(base, "codebase", "prompts.py")
        self.assertEqual(app._where(e), "codebase/prompts.py")
        self.assertEqual(app._where(RuntimeError("không traceback")), "codebase/")
        e2 = SyntaxError("y")
        e2.filename = os.path.join(os.path.dirname(os.path.dirname(base)), "ngoai_repo.py")   # file ngoài repo: in nguyên
        self.assertEqual(app._where(e2), e2.filename)


if __name__ == "__main__":
    unittest.main()
