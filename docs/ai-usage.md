# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | [người phụ trách điền] | [người phụ trách điền] | [người phụ trách điền] | Trần Thanh Tùng · Nguyễn Huy Hoàng |
| Prompt / thiết kế lời gọi mô hình | Claude Code (Claude Opus) | Sửa `codebase/prompts.py` sau CP2: liệt kê id hợp lệ cho `can_cu`; luật 6a và giới hạn của nó (PR #24). Chạy eval lượt phát triển run-2 → run-6, đọc trace để tìm nhóm lỗi | Claude Code đề xuất nhóm lỗi "kết luận quá sớm" từ trace và output từng câu; Nhi duyệt lựa chọn, nhóm chốt ở tài liệu quyết định CP4. Mỗi lần sửa chạy 159 test và `run.py check`; không sửa `expected` hay chuẩn đạt. Phần prompt trước CP2: [người phụ trách điền] | Nguyễn Văn Nhi (sau CP2) · [người phụ trách điền] |
| Đào data (viết script đếm, gợi ý nhãn) | Claude Code (Claude Opus) | Viết `evidence/count.py`, `count_fb.py`, `survey/count_survey.py`; gắn nhãn bằng từ khóa; thu bài nhóm Facebook công khai bằng trình duyệt chỉ đọc (không bình luận, đăng bài) | Cổng Chính phủ: kiểm tay 24/24 bài trong mẫu, sửa 3 lỗi luật. Facebook: đọc lại toàn bộ bài mang nhãn vướng địa phương, sửa 19 nhãn (ghi lý do trong `SUA_TAY_VDP`), loại 3 bài; 9/9 trích dẫn khớp nguyên văn nguồn | Nguyễn Văn Nhi |
| Rà câu hỏi phỏng vấn / khảo sát | Claude Code (Claude Opus) | Chỉ rà câu dẫn dắt; soạn khung `evidence/interviews/KICH-BAN.md` theo Mom Test | Nhi duyệt kịch bản. Câu hỏi khảo sát: [người phụ trách điền] | Nguyễn Văn Nhi · [người phụ trách điền] |
| Viết câu thử (benchmark) | [người phụ trách điền] | [người phụ trách điền] | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | [người phụ trách điền] |
| Sinh data `synthetic` (nếu có) | Không dùng | — | — | — |
| Chấm cột `pass` bằng LLM (nếu có) | Không dùng LLM chấm. Claude Code viết script chấm **bằng code** theo `nhan_dung` | Điền cột `pass`, `ghi_chu` cho run-2 → run-6 | Chạy cùng script trên run-1: khớp 27/27 câu với bản nhóm chấm tay (18/27); kiểm chỉ hai cột `pass`, `ghi_chu` thay đổi | Nguyễn Văn Nhi |
| Slide, văn bản | Claude Code (Claude Opus) | Nháp `summary.md`, `data-mining*.md`, sửa câu pain ở `canvas.md` / `spec.md` §0–§2, nháp `eval/report.md`, kịch bản video CP3, nháp slide 9 trang (ô chưa có số để `[__]`) | Nhi đọc lại trước khi mở PR, thành viên khác review và merge; số liệu đều chạy lại được từ script; slide còn chờ số run-7 và chi phí | Nguyễn Văn Nhi · [người phụ trách điền] |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
