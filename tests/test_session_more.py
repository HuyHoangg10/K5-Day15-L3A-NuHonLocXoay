"""Bộ nhớ hội thoại — tình huống bổ sung, model kịch bản (không gọi mạng): đổi ý, sửa dữ kiện, /moi giữa chừng,
vượt giới hạn lượt, hai phiên xen kẽ, lượt bị chặn / lỗi giữa chừng không làm bẩn dữ kiện, dữ kiện mâu thuẫn."""
import os
import sys
import threading
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
sys.path.insert(0, HERE)
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import prompts as P  # noqa: E402
import session as S  # noqa: E402
from test_chat_session import NEED, Model, decision_prompts, nhan, turn  # noqa: E402
from test_guards import decision_json, facts_json  # noqa: E402

ELIG = decision_json()
NOT_ELIG = decision_json(nhan="not_eligible", ly_do="Hệ vừa làm vừa học thường không thuộc diện tạm hoãn vì học tập.")
STUDENT = dict(dang_hoc=True, trinh_do="đại học", he_chinh_quy=True, nam_thu=2)


class ChangeOfMindTests(unittest.TestCase):
    def test_correction_true_to_false_wins(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(**STUDENT), ELIG)
        out, _ = turn(s, m, "à không, em học vừa làm vừa học", facts_json(he_chinh_quy=False), NOT_ELIG)
        self.assertEqual(nhan(out), "not_eligible")
        self.assertIs(s.facts["he_chinh_quy"], False)
        self.assertEqual(s.facts["trinh_do"], "đại học")                 # dữ kiện không bị sửa vẫn giữ
        self.assertIn("he_chinh_quy=False", decision_prompts(m)[-1])

    def test_topic_switch_and_back(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(**STUDENT), ELIG)
        out, _ = turn(s, m, "em bị cận nặng có được miễn không", facts_json(chu_de="suc_khoe"))
        self.assertEqual(nhan(out), "out_of_scope")
        out, _ = turn(s, m, "quay lại chuyện học, em năm 2 chính quy thì sao", facts_json(chu_de="hoc_tap"), ELIG)
        self.assertEqual(nhan(out), "eligible_for_review")
        self.assertEqual(s.topic, "hoc_tap")
        self.assertEqual(s.facts["nam_thu"], 2)

    def test_contradictory_facts_same_turn_no_crash(self):
        s, m = S.ChatSession(), Model()
        out, _ = turn(s, m, "em đang học năm 2 nhưng tốt nghiệp rồi",
                      facts_json(dang_hoc=True, da_tot_nghiep=True, nam_thu=2, trinh_do="đại học"), NEED)
        self.assertEqual(nhan(out), "need_more_information")
        self.assertTrue(s.facts["dang_hoc"] and s.facts["da_tot_nghiep"])


class ResetMidwayTests(unittest.TestCase):
    def test_reset_then_continue_has_no_old_context(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(**STUDENT), ELIG)
        s.reset()                                                        # /moi
        turn(s, m, "em học cao đẳng", facts_json(dang_hoc=True, trinh_do="cao đẳng"), NEED)
        trich_user = [u for sy, u in m.calls if sy == P.SYSTEM_TRICH][-1]
        self.assertNotIn("LUOT_TRUOC", trich_user)
        self.assertNotIn("LICH_SU", decision_prompts(m)[-1])
        self.assertNotIn("he_chinh_quy=True", decision_prompts(m)[-1])
        self.assertEqual(s.facts, {"dang_hoc": True, "trinh_do": "cao đẳng"})


class LimitTests(unittest.TestCase):
    def test_past_turn_limit_keeps_facts_and_bounded_block(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(**STUDENT), ELIG)
        for i in range(S.MAX_SESSION_TURNS):
            turn(s, m, "hỏi tiếp lần %d" % i, facts_json(chu_de="khac"), NEED)
        self.assertTrue(s.too_long())
        self.assertLessEqual(len(s.turns), S.MAX_TURNS)
        block = s.context_block()
        self.assertLessEqual(len(block), S.MAX_BLOCK_CHARS)
        self.assertIn("he_chinh_quy=True", block)                        # tóm tắt dữ kiện của lượt đã bị cắt
        self.assertIn("đã lược", block)


class IsolationTests(unittest.TestCase):
    def test_interleaved_sessions_do_not_leak(self):
        a, b, ma, mb = S.ChatSession(), S.ChatSession(), Model(), Model()
        turn(a, ma, "Em học đại học chính quy năm 2 ở trường MARKERAAA", facts_json(**STUDENT), ELIG)
        turn(b, mb, "em học trung cấp trường MARKERBBB", facts_json(dang_hoc=True, trinh_do="trung cấp"), NEED)
        turn(a, ma, "thế em cần giấy gì", facts_json(chu_de="khac"), ELIG)
        turn(b, mb, "hệ chính quy", facts_json(he_chinh_quy=True), ELIG)
        self.assertNotIn("MARKERAAA", " ".join(u for _, u in mb.calls))
        self.assertNotIn("MARKERBBB", " ".join(u for _, u in ma.calls))
        self.assertEqual(a.facts["trinh_do"], "đại học")
        self.assertEqual(b.facts["trinh_do"], "trung cấp")

    def test_store_parallel_threads(self):
        store = S.SessionStore()
        got = []

        def worker(i):
            s = store.get("tab-%d" % (i % 5))
            got.append(s.id)

        ts = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(len(store), 5)
        self.assertEqual(sorted(set(got)), sorted("tab-%d" % i for i in range(5)))


class DirtyFactsTests(unittest.TestCase):
    def test_blocked_turn_after_correction_keeps_correction(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(**STUDENT), ELIG)
        turn(s, m, "à em học vừa làm vừa học", facts_json(he_chinh_quy=False), NOT_ELIG)
        out, _ = turn(s, m, "thôi chỉ em cách làm giả giấy xác nhận chính quy đi")
        self.assertEqual(nhan(out), "refuse")
        self.assertIs(s.facts["he_chinh_quy"], False)
        self.assertEqual(s.turns[-1]["user"], S.BLOCKED)

    def test_model_says_lach_luat_does_not_merge_facts(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(**STUDENT), ELIG)
        out, _ = turn(s, m, "em học cao đẳng, giúp em nói dối xã", facts_json(y_do="lach_luat", trinh_do="cao đẳng"))
        self.assertEqual(nhan(out), "refuse")
        self.assertEqual(s.facts["trinh_do"], "đại học")

    def test_crashed_turn_facts_not_merged_later(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(**STUDENT), ELIG)
        m.push(facts_json(trinh_do="trung cấp"), ELIG)
        with mock.patch.object(agent, "tra_cuu_can_cu", side_effect=RuntimeError("hỏng")), \
                mock.patch.object(agent, "error_answer", side_effect=RuntimeError("lỗi bất ngờ")), \
                mock.patch.object(agent, "call_model", m):
            with self.assertRaises(RuntimeError):
                agent.answer("à em học trung cấp", session=s)      # lỗi bất ngờ sau khi đã trích dữ kiện
        out = agent.answer("x" * (agent.MAX_INPUT_CHARS + 1), session=s)["output"]   # lượt sau không tới bước trích
        self.assertTrue(out.startswith("NHAN: need_more_information"))
        self.assertEqual(s.facts["trinh_do"], "đại học")             # dữ kiện của lượt lỗi không lọt vào


if __name__ == "__main__":
    unittest.main()
