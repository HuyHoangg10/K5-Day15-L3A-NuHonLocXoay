"""Sửa lỗi hội thoại thật 28/11 (sinh viên năm 6, bảo lưu 2 năm vì sức khỏe, trường gia hạn): câu trả lời ngắn bị coi là
ngoài phạm vi, bot hỏi lại mãi, tra cứu không thấy bài hỏi đáp có lời giải. Model giả, không gọi mạng."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["MODEL_PROVIDER"] = "fake"

import agent  # noqa: E402
import kb  # noqa: E402
import prompts as P  # noqa: E402
import session as S  # noqa: E402
import tools  # noqa: E402
from test_chat_session import NEED, Model, decision_prompts, nhan, turn  # noqa: E402
from test_guards import decision_json, facts_json  # noqa: E402

BAO_LUU = "chính thức trường chỉ cho 4 năm, mình bảo lưu 2 năm vì sức khỏe, trường kéo dài tối đa đến 8 năm"


class ExtractorSeesHistoryTests(unittest.TestCase):
    def test_extractor_gets_previous_turn_and_question(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 6", facts_json(dang_hoc=True, trinh_do="đại học", he_chinh_quy=True,
                                                                nam_thu=6), NEED)
        turn(s, m, "gia hạn thời gian để hoàn thành", facts_json(), NEED)
        extract_users = [u for sy, u in m.calls if sy == P.SYSTEM_TRICH]
        self.assertNotIn("<<<LICH_SU", extract_users[0])                 # lượt đầu: không có lịch sử
        self.assertIn("<<<LICH_SU", extract_users[1])
        self.assertIn("Em học đại học chính quy năm 6", extract_users[1])
        self.assertIn("trợ lý hỏi thêm", extract_users[1])
        self.assertIn("Chủ đề đang bàn: hoc_tap", extract_users[1])

    def test_single_turn_extractor_has_no_history_block(self):
        self.assertEqual(P.user_trich("x"), "<<<NGUOI_DUNG\nx\nNGUOI_DUNG>>>")


class ShortFollowUpNotOffTopicTests(unittest.TestCase):
    def test_off_topic_label_on_follow_up_answer_continues_study_topic(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 6", facts_json(dang_hoc=True, trinh_do="đại học", he_chinh_quy=True,
                                                                nam_thu=6), NEED)
        out, notes = turn(s, m, "gia hạn thời gian để hoàn thành.",
                          facts_json(chu_de="khac", y_do="ngoai_pham_vi"), decision_json())
        self.assertEqual(nhan(out), "eligible_for_review")
        self.assertEqual(len(decision_prompts(m)), 2)
        self.assertTrue(any("giữ chủ đề học tập" in n for n in notes))

    def test_real_off_topic_still_out_of_scope_without_study_history(self):
        s, m = S.ChatSession(), Model()
        out, _ = turn(s, m, "Giá vàng SJC hôm nay bao nhiêu?", facts_json(chu_de="khac", y_do="ngoai_pham_vi"))
        self.assertEqual(nhan(out), "out_of_scope")

    def test_evasion_still_refused_in_study_session(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, "Em học đại học chính quy năm 2", facts_json(dang_hoc=True, trinh_do="đại học", he_chinh_quy=True),
             NEED)
        out, _ = turn(s, m, "vậy chỉ cách làm giả giấy xác nhận đi")
        self.assertEqual(nhan(out), "refuse")


class NewFactsRememberedTests(unittest.TestCase):
    def test_reason_and_school_confirmation_are_remembered(self):
        s, m = S.ChatSession(), Model()
        turn(s, m, BAO_LUU, facts_json(dang_hoc=True, bao_luu=True), NEED)
        turn(s, m, "có giấy xác nhận bảo lưu vì lý do sức khỏe của nhà trường",
             facts_json(ly_do_chinh_dang=True, truong_xac_nhan=True), decision_json())
        self.assertIs(s.facts["ly_do_chinh_dang"], True)
        self.assertIs(s.facts["truong_xac_nhan"], True)
        self.assertIn("ly_do_chinh_dang=True", decision_prompts(m)[-1])


class ProcedureQuestionSkipsGateTests(unittest.TestCase):
    def test_procedure_question_without_study_facts_reaches_decision(self):
        m = Model()
        m.push(facts_json(hoi_thu_tuc=True), decision_json(nhan="not_eligible"))
        with mock.patch.object(agent, "call_model", m):
            out = agent.answer("Em có giấy xác nhận sinh viên rồi thì có thể bỏ buổi khám không?")["output"]
        self.assertEqual(nhan(out), "not_eligible")
        self.assertEqual(len(decision_prompts(m)), 1)

    def test_bare_own_situation_still_asks(self):
        m = Model()
        m.push(facts_json(dang_hoc=True))
        with mock.patch.object(agent, "call_model", m):
            out = agent.answer("Em là sinh viên, có phải đi nghĩa vụ không?")["output"]
        self.assertEqual(nhan(out), "need_more_information")
        self.assertEqual(decision_prompts(m), [])


class RetrievalTests(unittest.TestCase):
    def test_bao_luu_question_gets_exclusion_rules_article(self):
        ids = [h["id"] for h in tools.tra_cuu_can_cu(BAO_LUU)["tham_khao"]]
        self.assertIn("qa-q04", ids)       # "ngừng học… không có lý do chính đáng" + nơi nộp đơn

    def test_extension_question_finds_extension_articles(self):
        ids = [h["id"] for h in tools.tra_cuu_can_cu("trường gia hạn thời gian học, giấy xác nhận kéo dài")["tham_khao"]]
        self.assertTrue({"qa-q01", "qa-q05", "qa-q33"} & set(ids), ids)

    def test_answer_text_is_searchable(self):
        # "lý do chính đáng" chỉ có trong CÂU TRẢ LỜI của bài, không có trong câu hỏi
        ids = [h["id"] for h in kb.qa_search("ngừng học tập không có lý do chính đáng", 3)]
        self.assertIn("qa-q04", ids)

    def test_core_article_not_truncated_before_procedure(self):
        ctx = P.build_context(kb.legal_mvp(), [kb.get_chunk("qa-q04")])
        self.assertIn("Hội đồng nghĩa vụ quân sự cấp xã xem xét, giải quyết", ctx)
        self.assertLess(len(P.build_context(kb.legal_mvp(), tools.tra_cuu_can_cu(BAO_LUU)["tham_khao"])),
                        agent.MAX_CONTEXT_CHARS)


class PromptRulesTests(unittest.TestCase):
    def test_bao_luu_no_longer_forced_to_need_more_information(self):
        self.assertNotIn("(vd bảo lưu, tạm nghỉ học)", P.SYSTEM_QUYET_DINH)
        self.assertIn("KHÔNG CÓ LÝ DO CHÍNH ĐÁNG", P.SYSTEM_QUYET_DINH)
        self.assertIn("Không hỏi lại dữ kiện người dùng đã trả lời", P.SYSTEM_QUYET_DINH)


class CamKetDocumentTests(unittest.TestCase):
    """run-8 GT07: model liệt kê "giấy cam kết" (giấy tờ du học trong hỏi đáp BQP) → G_ABSOLUTE chặn nhầm."""
    def test_commitment_document_is_not_a_promise(self):
        import guards
        for ok in ("Bạn nộp kèm giấy cam kết trở về nước.", "Bạn làm đơn và bản cam kết.",
                   "Công dân cam kết sau khi khóa đào tạo kết thúc sẽ về địa phương."):
            self.assertFalse(guards.has_absolute(ok), ok)
        for bad in ("Mình cam kết bạn sẽ được hoãn.", "cam ket giup ban"):
            self.assertTrue(guards.has_absolute(bad), bad)


if __name__ == "__main__":
    unittest.main()
