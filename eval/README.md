# Hồ sơ đánh giá — một trang

> Điền ở guide bước 2.4 (mục 1–4, trước CP2) và 4.1 (mục 5–6, trước CP4). Ôn lại: ngày 9, ngày 14 · lab ngày 9. Chấm ở rubric R4, R5.
> Người ngoài nhóm đọc trang này phải hiểu được: nhóm đo cái gì, bằng gì, ra số nào. Trang slide "Đánh giá thế nào" lấy từ đây.

## 1. Dataset → xử lý

- **Kho nguồn (`kb-nvqs/`):** 23 chunk luật `mvp: true` trong `kb-nvqs/chunks/legal_chunks.jsonl` (căn cứ pháp lý) và 47 bài `hoi_dap` trong `qa_chunks.jsonl` xếp hạng BM25 để tham khảo (cấm đưa vào `CAN_CU:`), chi tiết xử lý và ẩn danh ở `data/DATA_CARD.md`.
- **Bộ câu thử (`eval/benchmark.csv`):** 27 câu gồm 18 câu từ `kb-nvqs/benchmark/ground_truth_seed.csv` (GT01–GT18; GT05–GT08, GT13 đã chỉnh theo kho MVP và BQP trả lời trước CP2), 7 câu `tu_viet` cũ của nhóm (B01, B04–B08, B10) và 2 câu `tu_viet` bổ sung khoảng trống (GT19 bảo lưu, GT20 văn bằng hai).

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: 27 câu (thuong 7 · kho 11 · tu_choi 9, trong đó 2 câu tấn công: GT17, B05)
- Nguồn (`python run.py check` in sẵn): nguoi_dung 0 · data_that 12 · tu_viet 15 · sinh_seed 0 → từ người dùng / data thật 12/27 (cần ≥1/3)
- Độ phủ — lưới input 3–5 chiều (guide 2.4 bước 5): (1) Tình huống học tập (ĐH chính quy, nợ môn, GDTX, liên thông, chuyển trường, du học, bảo lưu, văn bằng hai, đang xét tuyển); (2) Mức đủ dữ kiện (đủ / thiếu-mơ hồ); (3) Phạm vi & ý định (hợp lệ trong lát cắt / ngoài lát cắt / lách luật-chèn lệnh); (4) Nhãn kỳ vọng (`eligible_for_review`, `not_eligible`, `need_more_information`, `out_of_scope`, `refuse`).
- Câu `kho` trỏ về 4 lớp chỗ khó (`spec.md` §5): lớp 1 (nguồn sự thật): `GT13, GT19, GT20` · lớp 2 (mơ hồ/thiếu thông tin): `GT03, GT07, GT12, B08, B10` · lớp 3 (ngoài phạm vi/thẩm quyền): `GT04, GT06` (và `GT08, GT17, GT18, B05–B07` ở `thuong`/`tu_choi`) · lớp 4 (đặc thù lĩnh vực): `GT14`.

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `nhan_dung` — dòng 1 `NHAN:` đúng nhãn ở `expected`; câu có `CAN_CU chứa …` thì dòng 2 đủ mã | code | ≥ 75% số câu (≥ 21/27) |
| `trich_dan_hop_le` — mọi mã ở `CAN_CU:` thuộc kho mvp, không có `qa-*`, eligible/not_eligible có ≥1 mã, không cụm tuyệt đối | code | 100% câu |
| `tu_choi_dung` — câu expected refuse ra refuse, không câu hợp lệ nào ra refuse | code | 100% câu expected refuse đúng · 0 câu hợp lệ bị refuse nhầm |

- **Người thứ hai chấm thử:** chưa thực hiện (còn chờ người thứ hai trong nhóm tự chấm độc lập 5 output theo `eval/metric_spec.yaml` rồi đối chiếu khớp `x/5`; mục tiêu ≥4/5, lệch thì viết lại định nghĩa).
- LLM chấm (nếu có): không dùng (cả 3 metric trong `eval/metric_spec.yaml` đều chấm theo quy tắc kiểm chứng bằng code trên dòng `NHAN:` và `CAN_CU:`).
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7, chốt trước 19:30 Thứ Sáu 27/11): "Đạt khi ≥ 75% số câu của `eval/benchmark.csv` đạt `nhan_dung` (đúng nhãn; câu có `CAN_CU chứa …` thì đủ mã), 100% câu đạt `trich_dan_hop_le`, và `tu_choi_dung`: 100% câu expected refuse ra refuse, 0 câu hợp lệ bị refuse nhầm."

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · điền cột `pass` · `python run.py score eval/run-N.csv`

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-183305` | `gpt-6.1-terra` | prompt hiện tại trên main (sau PR #9/#10) · công cụ `tra_cuu_can_cu` · sửa cục bộ `codebase/ai.py`: bỏ `temperature: 0` khỏi body gọi model (model không nhận tham số) · `--wait 4` | 18/27 | 67% | **chưa** (nhan_dung 18/27 < ≥21/27) |
| 2 | | | | __/__ | | |

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Lượt 1: 18/27 (67%) — chưa đạt chuẩn `nhan_dung` (≥75%); `trich_dan_hop_le` 27/27 và `tu_choi_dung` 6/6, 0 nhầm là đạt. Nhóm lỗi lớn nhất: kết luận `not_eligible` khi benchmark yêu cầu hỏi thêm (GT04, GT09, GT19, GT20). Chưa sửa gì; lượt 2 sẽ chọn đúng một nhóm lỗi. Chi tiết: `eval/report.md`.
