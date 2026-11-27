# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp.

## Dataset 1 · Kho kb-nvqs (căn cứ pháp lý + hỏi đáp chính thức)

Bản đầy đủ: **[`kb-nvqs/DATA_CARD.md`](../kb-nvqs/DATA_CARD.md)** (nguồn, xử lý, ẩn danh, giới hạn) và **[`kb-nvqs/SOURCES.csv`](../kb-nvqs/SOURCES.csv)** (URL, sha256, ngày tải từng văn bản). Tóm tắt:

- **Luật** — `kb-nvqs/chunks/legal_chunks.jsonl`: 179 chunk (VBHN 133/2026 Luật NVQS hợp nhất, TT 148/2018, NĐ 218/2025…), mức tin cậy A. Agent chỉ dùng **23 chunk `mvp: true`** (Điều 4, 10, 30, 41 tách theo điểm, 42; NĐ 218 Đ9–10; TT 148 Đ4–5) — nạp nguyên vào ngữ cảnh, ~20,7k ký tự.
- **Hỏi đáp** — `kb-nvqs/chunks/qa_chunks.jsonl`: 58 bài BQP / Cục Quân lực trả lời công dân (47 `hoi_dap` dùng để tra BM25, lấy 2 bài/câu), mức tin cậy B. **Không phải căn cứ pháp lý**: chỉ hiện ở phần "Tham khảo", cấm ở dòng `CAN_CU:`.
- **Ẩn danh:** tên người hỏi thay `[ẩn danh]`, che email/SĐT (regex, xem kb-nvqs/DATA_CARD.md §3). Nhóm đã quét lại PII trước khi commit; bản PDF / text gốc và bài `.md` không commit (`.gitignore`).
- **Ngày kiểm tra:** 27/11/2026. **Giới hạn:** chỉ phủ đủ lát cắt tạm hoãn vì học tập (điểm g k1 Đ41); sức khỏe (TT 105 chưa OCR), gia đình, miễn, xử phạt chỉ ở mức tham chiếu → agent trả `out_of_scope`.

## Dataset 2 · Bộ câu thử `eval/benchmark.csv`

| | |
|---|---|
| Dùng để làm gì | đo agent theo `eval/metric_spec.yaml` (chấm bằng code trên dòng `NHAN:` và `CAN_CU:`) |
| Từ đâu | 18 câu từ `kb-nvqs/benchmark/ground_truth_seed.csv` (GT01–GT18: nhãn và căn cứ mong đợi lấy nguyên từ seed); 12 câu dựa trên bài hỏi đáp thật (`data_that`), 6 câu người làm dữ liệu tự viết (`tu_viet`). Cộng 7 câu `tu_viet` cũ của nhóm (B01, B04–B08, B10: tấn công, ngoài phạm vi, nghe nhạy cảm nhưng hợp lệ, thiếu dữ kiện), đã đổi sang nhãn mới; bỏ B02, B03, B09 vì trùng ý GT16, GT17, GT01/GT02 |
| Xử lý những bước gì | đổi cột seed sang cột khung (`id, input, expected, pass_criterion, type, source`); `nhom` → `type`: thong_thuong→thuong, kho→kho, tu_choi / tan_cong / ngoai_pham_vi→tu_choi. Không có dữ liệu cá nhân thật |
| Số dòng / số đoạn | 25 (7 thuong · 9 kho · 9 tu_choi) · 12/25 `data_that` |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | thật (seed do người làm dữ liệu viết từ văn bản BQP trả lời; câu cũ viết tay) |
| Giới hạn | GT08 mong đợi căn cứ `vbhn133-d17` không thuộc kho mvp → agent hiện không thể trích được (guard chặn mã ngoài mvp). Chưa có câu từ người dùng thật phỏng vấn trực tiếp |
