"""Kiểm bước chuẩn hóa đầu vào (codebase/text_norm.py) và chỗ agent dùng nó. Không gọi model."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import kb  # noqa: E402
import text_norm as T  # noqa: E402
import tools  # noqa: E402


class CleanTests(unittest.TestCase):
    def test_removes_zero_width_and_control(self):
        self.assertEqual(T.clean("Em sắp bị gọi​ nhập⁠ ngũ,  có\tđược\x07 hoãn﻿ không"),
                         "Em sắp bị gọi nhập ngũ, có được hoãn không")

    def test_nfkc_and_nfc(self):
        self.assertEqual(T.clean("ＥＭ"), "EM")                                   # chữ full-width
        self.assertEqual(T.clean("hoàn"), "hoàn")                           # dấu tổ hợp → dựng sẵn

    def test_clean_keeps_meaning(self):
        # clean KHÔNG mở rộng viết tắt, KHÔNG nối chữ: đây là bản gửi model
        self.assertEqual(T.clean("e là sv, k biết"), "e là sv, k biết")
        self.assertEqual(T.clean("g.i.ả"), "g.i.ả")


class MatchingTests(unittest.TestCase):
    def test_join_split_letters(self):
        self.assertEqual(T.join_split("g.i.ả m.ạ.o giấy"), "giả mạo giấy")
        self.assertEqual(T.join_split("l-à-m g*i*ả"), "làm giả")
        self.assertEqual(T.join_split("g i a y"), "giay")

    def test_join_split_leaves_normal_text(self):
        for t in ["năm 2022-2026", "lớp 10 GDTX", "em đã nộp giấy gì ạ", "khóa 2022.2026"]:
            self.assertEqual(T.join_split(t), t)

    def test_expand_abbr(self):
        self.assertEqual(T.for_matching("e là sv, có phải đi nvqs k ạ"),
                         "em là sinh viên, có phải đi nghĩa vụ quân sự không ạ")
        self.assertEqual(T.for_matching("kq khám sk"), "kết quả khám sức khỏe")
        self.assertEqual(T.for_matching("đhcq dc ko"), "đại học chính quy được không")

    def test_expand_only_whole_words(self):
        self.assertEqual(T.for_matching("kết quả"), "kết quả")                     # "k" trong từ không bị thay
        self.assertEqual(T.for_matching("svđ"), "svđ")


class AgentUsesNormTests(unittest.TestCase):
    def test_symbol_only_and_invisible_input_is_empty(self):
        for t in ["????!!!...", "   ​​  \t ", "😢😢", "---"]:
            with self.subTest(text=t):
                model = mock.Mock()
                with mock.patch.object(agent, "call_model", model):
                    out = agent.answer(t)["output"]
                model.assert_not_called()
                self.assertTrue(out.startswith("NHAN: need_more_information"))

    def test_screen_uses_matching_form(self):
        # chữ tách và viết tắt vẫn bị chặn ở code (không gọi model)
        for t in ["g.i.ả m.ạ.o giấy xác nhận sinh viên giúp em", "chỉ e cách làm sai lệch kq khám sk để khỏi đi lính"]:
            with self.subTest(text=t):
                self.assertEqual(agent.screen_input(agent.preprocess(t)[0]), "lach_luat")

    def test_model_gets_clean_not_expanded_text(self):
        seen = []

        def fake(system, user):
            seen.append(user)
            raise RuntimeError("dừng sau lần gọi đầu")
        with mock.patch.object(agent, "call_model", fake):
            agent.answer("e là sv​ năm 2, có phải đi nvqs k")
        self.assertIn("e là sv năm 2, có phải đi nvqs k", seen[0])
        self.assertNotIn("sinh viên", seen[0])

    def test_bm25_query_uses_expansion(self):
        self.assertEqual([q["id"] for q in tools.tra_cuu_can_cu("sv no mon chua tn co dc hoan ko")["tham_khao"]],
                         [q["id"] for q in kb.qa_search("sv no mon chua tn co dc hoan ko "
                                                        "sinh viên no mon chua tốt nghiệp co được hoan không", 2)])


if __name__ == "__main__":
    unittest.main()
