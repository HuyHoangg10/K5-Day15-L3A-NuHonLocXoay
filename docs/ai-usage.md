# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | | | | |
| Prompt / thiết kế lời gọi mô hình | | | | |
| Đào data (viết script đếm, gợi ý nhãn) | | | Kiểm tay __ dòng, khớp __ | |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | | | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản | | | | |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).

## Phần của Nguyễn Huy Hoàng (HuyHoangg10)

**Công cụ:** Claude (claude.ai) để thảo luận, lập kế hoạch và viết prompt giao việc; Claude Code (Claude Opus / Sonnet) để code, viết test, đo và mở PR theo prompt đó. Con người (Hoàng) quyết định phạm vi, chọn nhóm lỗi và quyết định merge.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Khung agent, nối model | Claude Code | Checklist build (PR #2, `3d757c3`); khung agent + guardrail (PR #3, `4f355d9`); nối model thật vào `codebase/ai.py` (PR #4, `37e0528`) | Hoàng đọc diff, chạy thử, merge | Nguyễn Huy Hoàng |
| RAG và độ bền đầu vào | Claude Code | RAG với `kb-nvqs` + nhãn theo ground truth (PR #5, `8e56797`); chuẩn hóa đầu vào, guard không dấu, che dữ liệu cá nhân (PR #6, `191cf32`); siết guard + văn phong dễ hiểu (PR #9, `4d3d6cd`) | Hoàng chạy unittest với model giả, kiểm câu bị chặn nhầm, merge | Nguyễn Huy Hoàng |
| Tài liệu CP2 | Claude Code | Nháp chốt ngưỡng, bỏ `nvqs.md`, sửa canvas (PR #10, `3c87e78`) | Hoàng chốt ngưỡng ≥ 75%; nhóm duyệt. (PR #11 bổ sung benchmark là của Hiếu, không thuộc phần này.) | Nguyễn Huy Hoàng |
| Phân tích lỗi run-1 | Claude Code | Đọc 9 câu trượt của `run-1`, gom thành nhóm lỗi A/B/C (`eval/report.md` mục 2) | Hoàng chọn nhóm A ("kết luận `not_eligible` quá sớm") làm cải tiến chính thức (PR #24) vì đau nhất với người dùng; không sửa `expected` dù có nhãn tranh cãi (GT04) | Nguyễn Huy Hoàng |
| Thử hướng sửa khác (không vào main) | Claude Code | `fix/retrieve-before-ask` (`c1afcee`); `fix/retrieve-before-ask-lite` (`1ccc125`, PR #25 — đã đóng, không merge); `fix/citation-group` (`83a31a3`, đo không tốt hơn, không mở PR) | Hoàng quyết định không merge để giữ đúng một cải tiến cho lượt 2 | Nguyễn Huy Hoàng |
| So sánh ngoài mẫu #24 / #25 | Claude Code | 14 câu mới chưa ai chỉnh theo, `gpt-6.1-terra`, mỗi câu 2 lần: `main` 22/28 · PR #24 24/28 (ghi ở `eval/report.md`) · PR #25 24/28 (không có file kết quả trong repo) | Hoàng đọc kết quả, chọn #24 | Nguyễn Huy Hoàng |
| Bộ nhớ hội thoại | Claude Code | `codebase/session.py`, `answer(text, session=None)` và test bộ nhớ (nhánh `feat/chat-memory`, `440ef04`; vào `main` qua PR #36 sau lượt 2) | Hoàng kiểm bản chụp bất biến đường eval một lượt | Nguyễn Huy Hoàng |
| Nhánh `demo/final` | Claude Code | `6203ac5`, 298 test với model giả: bộ nhớ, chặn giấy tờ giả, hiển thị thân thiện, vá tấn công ngụy trang / diễn đạt lại, che dữ liệu cá nhân trong trace, giảm độ trễ câu đầu, chặn commit key (`scripts/check_secrets.py`), hướng dẫn demo (`docs/demo-guide.md`). Chưa merge vào `main` | Hoàng giao việc theo từng vòng, đọc báo cáo, kiểm trước khi push | Nguyễn Huy Hoàng |
| Thử nghiệm prompt sau CP4 | Claude Code | Nhánh `exp/post-cp4-prompt` (`526cebe`, 309 test với model giả): y_do riêng cho chèn lệnh, không hỏi lại dữ kiện đã trích, dữ kiện "đã nhập học". **Chưa kiểm bằng model thật**, không merge | Hoàng quyết định để sau CP4 | Nguyễn Huy Hoàng |

**Quyết định của con người:** chọn lát cắt tạm hoãn vì học tập; ngưỡng ≥ 75%; không sửa `expected` sau lượt 1; chọn nhóm lỗi A cho PR #24; giữ `gpt-6.1-terra` cho lượt 2 và mô phỏng chi phí; không merge nhánh demo trước CP4.

**Kiểm chứng:** unittest với model giả (`MODEL_PROVIDER=fake`); bản chụp bất biến đường eval một lượt (`tests/test_single_turn_invariance.py`, thêm ở `b07043e`); đo bằng model thật có trần số lần gọi; tập câu mới đóng băng bằng SHA-256 trước khi chạy (không có số liệu trong repo).

**Lỗi / giới hạn của AI đã phát hiện:**
- `gpt-4o-mini` chép sai mã căn cứ nên ra `safe_fallback` ở lượt phát triển run-2; sửa bằng liệt kê id hợp lệ (`3034aa7`).
- Guard `G_LEAK` từng chặn nhầm câu gợi ý nguyên văn của prompt (`7dd5aaa`).
- Một lần gọi API ngoài ý muốn khi `.env` đang trỏ model thật (không có số liệu về số lần gọi).
- Claude Code từng tự sửa `.env` (đổi `MODEL_NAME`) dù đã dặn không sửa; Hoàng phát hiện và sửa lại.
- Số "giả định offline" (đo bằng model giả) không được dùng như kết quả eval.

**An toàn:** key chỉ nằm trong `.env` (đã gitignore, chưa từng commit); quét key trước khi nộp.
