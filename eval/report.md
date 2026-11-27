# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-183305` | 18/27 | 67% | 4/7 | 5/11 | 9/9 | **chưa** (nhan_dung 66.7% < 75%) |
| 2 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Kết luận `not_eligible` khi cần hỏi thêm | 4 | GT04, GT09, GT19, GT20 |
| Nhãn đúng nhưng thiếu/sai mã `CAN_CU` | 3 | GT03 (không có mã), GT11 (thiếu vbhn133-d42), GT13 (trích vbhn133-d41, cần ...-k1-g) |
| Sai nhãn (hỏi thêm thay vì kết luận) | 2 | GT02, GT14 |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| GT19 | Em đang bảo lưu kết quả học ở trường đại học chính quy, năm sau mới học lại. Trong thời gian bảo lưu em có được tạm hoãn gọi nhập ngũ không? | `NHAN: not_eligible` — "thường không thuộc diện tạm hoãn" | KB chưa có quy định riêng về bảo lưu, expected là `need_more_information`; model kết luận khi thiếu dữ kiện |
| GT04 | Em đã được tạm hoãn khi học trung cấp, nay học liên thông đại học chính quy… | `NHAN: not_eligible` | Expected `need_more_information` (liên thông có liên tục không?); model kết luận ngay |
| GT14 | Em có giấy xác nhận sinh viên rồi thì có thể bỏ buổi khám sức khỏe không? | `NHAN: need_more_information` (hỏi trình độ, hệ, khóa) | Expected `not_eligible` + nd218-d9; câu hỏi về khám sức khỏe không cần dữ kiện học tập |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: __ — vì sao là nhóm **đau nhất với người dùng**: __
- Đã sửa gì (có thể vài thay đổi cùng nhắm nhóm lỗi đó): __
- Kết quả: nhóm lỗi đó __/__ → __/__ · tổng __% → __%
- Câu nào **tệ đi** sau khi sửa: __

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
