# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Claude Code (Hoàng) · Antigravity (Tùng) | Khung agent, RAG, guardrail, nối model: xem mục "Phần của Ngô Huy Hoàng" bên dưới. Phần của Tùng (Antigravity): rà PR, điền `cost/personas.yaml` từ khảo sát thật (PR #22), viết & chạy stress-test 100 edge cases trên `main` bằng `gpt-6.1-terra` (PR #28–#29), gắn log chat ẩn danh sang Google Sheet & siết `WEB_ALLOW_ORIGIN` cho `web/server.py` (nhánh `feat/web-sheet-log`) | Hoàng tự kiểm phần mình ở mục dưới. Tùng tự quản lý `.env` cục bộ (kiểm `.gitignore`, không commit key/link Form), tự chạy `smoke_model.py`, rà & sửa báo cáo 100 edge cases theo review ở PR #29, chạy đủ 172 unit test và `run.py check` | Ngô Huy Hoàng · Trần Thanh Tùng |
| Prompt / thiết kế lời gọi mô hình | Claude Code (Claude Opus) | Sửa `codebase/prompts.py` sau CP2: liệt kê id hợp lệ cho `can_cu`; luật 6a và giới hạn của nó (PR #24). Chạy eval lượt phát triển run-2 → run-6, đọc trace để tìm nhóm lỗi | Claude Code đề xuất nhóm lỗi "kết luận quá sớm" từ trace và output từng câu; Nhi duyệt lựa chọn, nhóm chốt ở tài liệu quyết định CP4. Mỗi lần sửa chạy 159 test và `run.py check`; không sửa `expected` hay chuẩn đạt. Phần prompt trước CP2: [người phụ trách điền] | Nguyễn Văn Nhi (sau CP2) · [người phụ trách điền] |
| Đào data (viết script đếm, gợi ý nhãn) | Claude Code (Claude Opus) | Viết `evidence/count.py`, `count_fb.py`, `survey/count_survey.py`; gắn nhãn bằng từ khóa; thu bài nhóm Facebook công khai bằng trình duyệt chỉ đọc (không bình luận, đăng bài) | Cổng Chính phủ: kiểm tay 24/24 bài trong mẫu, sửa 3 lỗi luật. Facebook: đọc lại toàn bộ bài mang nhãn vướng địa phương, sửa 19 nhãn (ghi lý do trong `SUA_TAY_VDP`), loại 3 bài; 9/9 trích dẫn khớp nguyên văn nguồn | Nguyễn Văn Nhi |
| Rà câu hỏi phỏng vấn / khảo sát | Claude Code (Claude Opus) · Antigravity | Claude Code rà câu dẫn dắt và soạn khung `evidence/interviews/KICH-BAN.md` theo Mom Test. Antigravity gợi ý bộ 8 câu hỏi khảo sát ẩn danh bám mẫu `evidence/survey/TEMPLATE.md` | Nhi duyệt kịch bản phỏng vấn. Tùng tự dựng Google Form (tắt thu email/tên), tự gửi khảo sát thực tế cho sinh viên ngoài nhóm thu phiếu thật, không dùng AI tạo câu trả lời | Nguyễn Văn Nhi · Trần Thanh Tùng |
| Viết câu thử (benchmark) | Claude Code (Claude) — phần của Hiếu | Đề xuất nhãn cho GT06/07/08/13 và nháp hai câu mới GT19 (bảo lưu), GT20 (văn bằng hai), dẫn id chunk từ `kb-nvqs`; rà `pass_criterion` cho khớp `expected` | Hiếu chọn nhãn theo văn bản luật, không theo output model; không sửa `expected` sau khi thấy kết quả. Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | Đỗ Minh Hiếu (phần GT06/07/08/13, GT19, GT20) · [người phụ trách điền phần còn lại] |
| Chạy và chấm run-1 | Claude Code (Claude) — phần của Hiếu | Viết script chấm cột `pass` bằng code theo `pass_criterion` và `nhan_dung`; đọc output từng câu để nhóm lỗi | Hiếu chạy run-1 (`--wait 4`), ghi chú từng câu và chấm lại: kết quả 18/27 (67%), chưa đạt chuẩn `nhan_dung`, ghi đúng như vậy, không đổi `expected` hay chuẩn đạt | Đỗ Minh Hiếu |
| Giao diện web demo (PR #27) | Claude Code (Claude) | Viết `web/` (máy chủ, giao diện, hai bản thiết kế) nối vào `answer()` có sẵn, không sửa agent; test với agent giả | Hiếu thiết kế luồng 5 bước và chọn hướng thiết kế (storyboard, chọn bản chính/bản cũ), duyệt và yêu cầu sửa từng phần, tự thử trên trình duyệt | Đỗ Minh Hiếu |
| Sinh data `synthetic` (nếu có) | Không dùng | — | — | — |
| Chấm cột `pass` bằng LLM (nếu có) | Không dùng LLM chấm. Claude Code viết script chấm **bằng code** theo `nhan_dung` | Điền cột `pass`, `ghi_chu` cho run-2 → run-6 | Chạy cùng script trên run-1: khớp 27/27 câu với bản nhóm chấm tay (18/27); kiểm chỉ hai cột `pass`, `ghi_chu` thay đổi | Nguyễn Văn Nhi |
| Slide, văn bản | Claude Code (Claude Opus) | Nháp `summary.md`, `data-mining*.md`, sửa câu pain ở `canvas.md` / `spec.md` §0–§2, nháp `eval/report.md`, kịch bản video CP3, nháp slide 9 trang, điền số run-7 và chi phí, xuất `demo-slides.pdf` (PR #34) | Nhi đọc lại trước khi mở PR, thành viên khác review và merge; số liệu đều chạy lại được từ script; slide còn chờ số run-7 và chi phí | Nguyễn Văn Nhi · [người phụ trách điền] |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).

## Phần của Ngô Huy Hoàng (HuyHoangg10)

**Công cụ:** Claude (claude.ai) để thảo luận, lập kế hoạch và viết prompt giao việc; Claude Code (Claude Opus / Sonnet) để code, viết test, đo và mở PR theo prompt đó. Con người (Hoàng) quyết định phạm vi, chọn nhóm lỗi và quyết định merge.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Khung agent, nối model | Claude Code | Checklist build (PR #2, `3d757c3`); khung agent + guardrail (PR #3, `4f355d9`); nối model thật vào `codebase/ai.py` (PR #4, `37e0528`) | Hoàng đọc diff, chạy thử, merge | Ngô Huy Hoàng |
| RAG và độ bền đầu vào | Claude Code | RAG với `kb-nvqs` + nhãn theo ground truth (PR #5, `8e56797`); chuẩn hóa đầu vào, guard không dấu, che dữ liệu cá nhân (PR #6, `191cf32`); siết guard + văn phong dễ hiểu (PR #9, `4d3d6cd`) | Hoàng chạy unittest với model giả, kiểm câu bị chặn nhầm, merge | Ngô Huy Hoàng |
| Tài liệu CP2 | Claude Code | Nháp chốt ngưỡng, bỏ `nvqs.md`, sửa canvas (PR #10, `3c87e78`) | Hoàng chốt ngưỡng ≥ 75%; nhóm duyệt. (PR #11 bổ sung benchmark là của Hiếu, không thuộc phần này.) | Ngô Huy Hoàng |
| Phân tích lỗi run-1 | Claude Code | Đọc 9 câu trượt của `run-1`, gom thành nhóm lỗi A/B/C (`eval/report.md` mục 2) | Hoàng chọn nhóm A ("kết luận `not_eligible` quá sớm") làm cải tiến chính thức (PR #24) vì đau nhất với người dùng; không sửa `expected` dù có nhãn tranh cãi (GT04) | Ngô Huy Hoàng |
| Thử hướng sửa khác (không vào main) | Claude Code | `fix/retrieve-before-ask` (`c1afcee`); `fix/retrieve-before-ask-lite` (`1ccc125`, PR #25 — đã đóng, không merge); `fix/citation-group` (`83a31a3`, đo không tốt hơn, không mở PR) | Hoàng quyết định không merge để giữ đúng một cải tiến cho lượt 2 | Ngô Huy Hoàng |
| So sánh ngoài mẫu #24 / #25 | Claude Code | 14 câu mới chưa ai chỉnh theo, `gpt-6.1-terra`, mỗi câu 2 lần: `main` 22/28 · PR #24 24/28 (ghi ở `eval/report.md`) · PR #25 24/28 (không có file kết quả trong repo) | Hoàng đọc kết quả, chọn #24 | Ngô Huy Hoàng |
| Bộ nhớ hội thoại | Claude Code | `codebase/session.py`, `answer(text, session=None)` và test bộ nhớ (nhánh `feat/chat-memory`, `440ef04`; vào `main` qua PR #36 sau lượt 2) | Hoàng kiểm bản chụp bất biến đường eval một lượt | Ngô Huy Hoàng |
| Nhánh `demo/final` | Claude Code | `6203ac5`, 298 test với model giả: bộ nhớ, chặn giấy tờ giả, hiển thị thân thiện, vá tấn công ngụy trang / diễn đạt lại, che dữ liệu cá nhân trong trace, giảm độ trễ câu đầu, chặn commit key (`scripts/check_secrets.py`), hướng dẫn demo (`docs/demo-guide.md`). Chưa merge vào `main` | Hoàng giao việc theo từng vòng, đọc báo cáo, kiểm trước khi push | Ngô Huy Hoàng |
| Thử nghiệm prompt sau CP4 | Claude Code | Nhánh `exp/post-cp4-prompt` (`526cebe`, 309 test với model giả): y_do riêng cho chèn lệnh, không hỏi lại dữ kiện đã trích, dữ kiện "đã nhập học". **Chưa kiểm bằng model thật**, không merge | Hoàng quyết định để sau CP4 | Ngô Huy Hoàng |

**Quyết định của con người:** chọn lát cắt tạm hoãn vì học tập; ngưỡng ≥ 75%; không sửa `expected` sau lượt 1; chọn nhóm lỗi A cho PR #24; giữ `gpt-6.1-terra` cho lượt 2 và mô phỏng chi phí; không merge nhánh demo trước CP4.

**Kiểm chứng:** unittest với model giả (`MODEL_PROVIDER=fake`); bản chụp bất biến đường eval một lượt (`tests/test_single_turn_invariance.py`, thêm ở `b07043e`); đo bằng model thật có trần số lần gọi; tập câu mới đóng băng bằng SHA-256 trước khi chạy (không có số liệu trong repo).

**Lỗi / giới hạn của AI đã phát hiện:**
- `gpt-4o-mini` chép sai mã căn cứ nên ra `safe_fallback` ở lượt phát triển run-2; sửa bằng liệt kê id hợp lệ (`3034aa7`).
- Guard `G_LEAK` từng chặn nhầm câu gợi ý nguyên văn của prompt (`7dd5aaa`).
- Một lần gọi API ngoài ý muốn khi `.env` đang trỏ model thật (không có số liệu về số lần gọi).
- Claude Code từng tự sửa `.env` (đổi `MODEL_NAME`) dù đã dặn không sửa; Hoàng phát hiện và sửa lại.
- Số "giả định offline" (đo bằng model giả) không được dùng như kết quả eval.

**An toàn:** key chỉ nằm trong `.env` (đã gitignore, chưa từng commit); quét key trước khi nộp.
