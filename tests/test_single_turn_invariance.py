"""BẤT BIẾN ĐƯỜNG ĐO: answer(text) không phiên phải cho đầu ra GIỐNG TỪNG BYTE và gửi model ĐÚNG các prompt như
main 5ac7fb5 (bản chụp tests/fixtures/single_turn_golden.json), với mọi input của eval/benchmark.csv + input biên,
dưới hai model giả. Lượt 2 chính thức (`python run.py eval`) gọi đúng đường này. Không gọi mạng."""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import make_single_turn_golden as G  # noqa: E402


class SingleTurnInvarianceTests(unittest.TestCase):
    def test_outputs_and_prompts_byte_identical_to_main(self):
        with open(G.GOLDEN, encoding="utf-8") as f:
            golden = json.load(f)
        now = G.run_all()
        self.assertEqual(sorted(now), sorted(golden))
        for key in sorted(golden):
            with self.subTest(case=key):
                self.assertEqual(now[key]["output"], golden[key]["output"])
                self.assertEqual(now[key]["prompts"], golden[key]["prompts"])

    def test_golden_covers_every_benchmark_input(self):
        with open(G.GOLDEN, encoding="utf-8") as f:
            golden = json.load(f)
        ids = [cid for cid, _ in G.inputs()]
        for mode in ("fake", "stub"):
            self.assertEqual({k for k in golden if k.startswith(mode + "/")}, {"%s/%s" % (mode, i) for i in ids})


if __name__ == "__main__":
    unittest.main()
