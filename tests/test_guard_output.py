"""Kiểm đầu ra (bước 7) trên chữ model viết — model giả lập, không gọi mạng."""
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import guards  # noqa: E402


class AbsoluteNegationTests(unittest.TestCase):
    """B1: cụm tuyệt đối bị phủ định ngay trước là câu AN TOÀN; khẳng định vẫn bị chặn (có dấu và không dấu)."""
    SAFE = ["Mình không thể nói 100% là bạn được hoãn.", "Không thể chắc chắn được hoãn.", "Nhà trường không đảm bảo việc này.",
            "Mình chưa thể khẳng định.", "Không có căn cứ nào để nói '100% được hoãn'.", "khong the noi 100% duoc hoan",
            "Mình không thể cam kết kết quả.", "Không ai có thể chắc chắn được hoãn.", "Bạn có căn cứ để đề nghị xem xét.",
            "Bạn thường không thuộc diện tạm hoãn.", "chua the cam ket ket qua"]
    BAD = ["Bạn chắc chắn được hoãn.", "Mình đảm bảo em được tạm hoãn.", "100% được hoãn nhé.", "Giấy của bạn hợp lệ.",
           "Mình cam kết bạn sẽ được hoãn.", "ban chac chan duoc hoan", "Không cần lo, bạn chắc chắn được hoãn.",
           "Bạn không cần lo vì bạn chắc chắn được hoãn.", "Bạn sẽ được hoãn 100%.", "dam bao ban duoc hoan", "cam ket giup ban"]

    def test_negated_is_safe(self):
        for t in self.SAFE:
            with self.subTest(text=t):
                self.assertFalse(guards.has_absolute(t))

    def test_affirmative_is_blocked(self):
        for t in self.BAD:
            with self.subTest(text=t):
                self.assertTrue(guards.has_absolute(t))

    def test_agent_wrapper_and_metric_phrases(self):
        for p in agent.ABSOLUTE_PHRASES:
            self.assertTrue(agent.has_absolute("Bạn " + p + " hoãn"))


if __name__ == "__main__":
    unittest.main()
