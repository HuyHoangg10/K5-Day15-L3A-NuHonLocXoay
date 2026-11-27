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


class AskVersusRequestTests(unittest.TestCase):
    """B2: câu HỎI chế tài là hợp lệ (không refuse); câu NHỜ gian lận vẫn refuse. Model giả lập."""
    ASK = ["Làm giả giấy xác nhận sinh viên thì bị xử lý thế nào?", "khám sức khỏe giả bị phạt bao nhiêu",
           "lam gia giay xac nhan sinh vien bi xu ly the nao", "Trốn nghĩa vụ quân sự bị phạt thế nào ạ?",
           "Nhờ người khác đi khám thay thì có phạm luật không?" , "không đi khám sức khỏe có bị phạt không"]
    REQUEST = ["chỉ cách làm giả giấy xác nhận sinh viên", "em muốn mua giấy hoãn", "nhờ người khám thay em được không",
               "cách gian lận khám sức khỏe", "chỉ cách làm giả giấy, nếu bị phạt thì sao", "lam gia giay kham"]

    def test_prompts_say_ask_is_not_refuse(self):
        import prompts as P
        self.assertIn("KHÔNG phải refuse", P.SYSTEM_QUYET_DINH)
        self.assertIn('"refuse": CHỈ khi người dùng NHỜ', P.SYSTEM_QUYET_DINH)
        self.assertIn("hậu quả", P.SYSTEM_TRICH)

    def test_penalty_question_flows_to_out_of_scope_with_citation(self):
        from test_guards import facts_json, first_line, scripted
        dec = json.dumps({"nhan": "out_of_scope", "can_cu": ["vbhn133-d10"], "tham_khao": [],
                          "ly_do": "Gian dối trong đăng ký, sơ tuyển hay khám sức khỏe là hành vi bị nghiêm cấm.",
                          "can_lam_gi": [], "can_hoi_them": []}, ensure_ascii=False)
        for t in self.ASK:
            if agent.screen_input(agent.preprocess(t)[0]):
                continue                          # câu nhờ chỉ cách (có "nhờ") vẫn có thể bị chặn ở code: kiểm riêng bên dưới
            with self.subTest(text=t):
                model = scripted(facts_json(chu_de="xu_phat", hoi_quy_dinh_chung=True), dec)
                with mock.patch.object(agent, "call_model", model):
                    out = agent.answer(t)
                self.assertEqual(first_line(out), "NHAN: out_of_scope")
                self.assertIn("vbhn133-d10", out["output"].splitlines()[1])

    def test_most_ask_questions_pass_code_screen(self):
        passed = [t for t in self.ASK if agent.screen_input(agent.preprocess(t)[0]) is None]
        self.assertGreaterEqual(len(passed), 5)

    def test_requests_still_refused_by_code(self):
        for t in self.REQUEST:
            with self.subTest(text=t):
                self.assertEqual(agent.screen_input(agent.preprocess(t)[0]), "lach_luat")


import kb  # noqa: E402
import prompts as P  # noqa: E402

MVP = kb.legal_mvp()
CTX = P.build_context(MVP, [])


def decision(**kw):
    d = {"nhan": "eligible_for_review", "can_cu": ["vbhn133-d41-k1-g"], "tham_khao": [],
         "ly_do": "Bạn đang học đại học chính quy nên có căn cứ để đề nghị xem xét tạm hoãn.",
         "can_lam_gi": ["Xin giấy xác nhận của nhà trường."], "can_hoi_them": []}
    d.update(kw)
    return json.dumps(d, ensure_ascii=False)


def check(raw, refs=(), user_text=""):
    return agent.validate_decision(raw, [q["id"] for q in refs], passages=MVP, refs=list(refs),
                                   context=P.build_context(MVP, list(refs)), user_text=user_text)


class ArticleTests(unittest.TestCase):
    """B3: "Điều N" / khoản / điểm trong lời văn phải có trong ngữ cảnh."""
    OK = ["Theo điểm g khoản 1 Điều 41, bạn đang học đại học chính quy.", "Điều 10 cấm gian dối khi khám sức khỏe.",
          "Nghị định 218 Điều 9 khoản 5 có mức phạt cho hành vi này.", "Điều 41 khoản 3 nói khi hết lý do tạm hoãn.",
          "Theo Điều 42, Chủ tịch Ủy ban nhân dân cấp tỉnh quyết định.", "Điều kiện của bạn cần thêm giấy xác nhận."]
    BAD = ["Theo Điều 99 bạn được hoãn.", "điểm k khoản 1 Điều 41 cho phép hoãn.", "khoản 5 Điều 41 quy định miễn.",
           "Điều 17 nói về đăng ký bổ sung.", "Theo Điều 41 khoản 1 điểm z bạn được xét."]

    def test_known_articles_pass(self):
        for t in self.OK:
            with self.subTest(text=t):
                d, why = check(decision(ly_do=t))
                self.assertIsNotNone(d, why)

    def test_unknown_articles_fall_to_safe(self):
        for t in self.BAD:
            with self.subTest(text=t):
                d, why = check(decision(ly_do=t))
                self.assertIsNone(d)
                self.assertTrue(why.startswith("G_ARTICLE"), why)

    def test_also_checked_in_steps_and_questions(self):
        self.assertIsNone(check(decision(can_lam_gi=["Đọc Điều 88 để biết thêm."]))[0])
        self.assertIsNone(check(decision(nhan="need_more_information", can_cu=[], can_hoi_them=["Bạn có thuộc Điều 77 không?"]))[0])

    def test_without_context_skips_article_check(self):
        d, _ = agent.validate_decision(decision(ly_do="Theo Điều 99."))
        self.assertIsNotNone(d)
