"""Độ trễ phần code (model giả, không gọi mạng): bảng kiểm rò rỉ prompt dựng nhanh và RA ĐÚNG tập cũ; warm_up không
gọi model; câu đầu tiên sau warm_up nhanh."""
import os
import sys
import time
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import guards  # noqa: E402
import kb  # noqa: E402
import prompts as P  # noqa: E402


class PromptGramsTests(unittest.TestCase):
    def test_same_set_as_substring_check(self):
        prompts = (P.SYSTEM_TRICH, P.SYSTEM_QUYET_DINH)
        guards._PROMPT_GRAMS.pop(tuple(prompts), None)
        t0 = time.perf_counter()
        fast = guards._prompt_grams(prompts)
        self.assertLess(time.perf_counter() - t0, 2.0)
        n = guards.LEAK_MIN_CHARS
        grams = set()
        for p in prompts:
            s = guards._squash(p)
            grams.update(s[i:i + n] for i in range(len(s) - n + 1))
        corpus = " | ".join(guards._squash(" ".join(str(c.get(k) or "") for k in ("text", "title", "question", "answer")))
                            for c in kb.legal_all() + kb.qa_all())
        slow = frozenset(g for g in grams if g not in corpus)       # cách cũ (tìm chuỗi con)
        self.assertEqual(fast, slow)


class WarmUpTests(unittest.TestCase):
    def test_warm_up_no_model_call_and_first_answer_fast(self):
        with mock.patch.object(agent, "call_model", side_effect=AssertionError("không được gọi model")):
            agent.warm_up()
            t0 = time.perf_counter()
            agent.screen_input("em học đại học")
            guards.leak("abc", (P.SYSTEM_TRICH, P.SYSTEM_QUYET_DINH))
            self.assertLess(time.perf_counter() - t0, 0.5)


if __name__ == "__main__":
    unittest.main()
