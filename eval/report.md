# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-183305` | 18/27 | 67% | 4/7 | 5/11 | 9/9 | **chưa** (nhan_dung 66.7% < 75%) |
| 2 | `run-7@20261128-120720` | 23/27 | 85% | 6/7 | 8/11 | 9/9 | **đạt** (nhan_dung 85.2% ≥ 75%; trich_dan_hop_le 27/27; tu_choi_dung 6/6, 0 nhầm) |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-7.csv`. Trace: `traces/run-1.jsonl`, `traces/run-7.jsonl`.

> **Lượt 2 chính thức = `run-7`**, chạy **một lần** bằng `gpt-6.1-terra` (cùng model lượt 1) sau khi merge PR #24; SHA `main` lúc chạy: `01b27e5` (28/11/2026 12:07, sau merge #24–#28; #25–#28 không đổi `codebase/` hay KB), `--wait 4`, 0 lỗi, trung bình 1.3 lần gọi model và 5.025 token vào / 288 ra mỗi câu.
> `run-2` → `run-6` là **lượt phát triển** chạy trên chính bộ 27 câu trong lúc chỉnh prompt (bảng ở `eval/README.md` mục 5). Không dùng số của chúng làm lượt 2.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| **A. Kết luận `not_eligible` quá sớm** (khi cần hỏi thêm) | 4 | GT04, GT09, GT19, GT20 |
| **B. Nhãn đúng nhưng thiếu/sai mã `CAN_CU`** | 3 | GT03 (không có mã), GT11 (thiếu vbhn133-d42), GT13 (trích vbhn133-d41, cần ...-k1-g) |
| **C. Thoát sớm ở bước chặn thiếu dữ kiện** (hỏi thêm thay vì kết luận, không trích căn cứ) | 2 | GT02, GT14 |

Đối chiếu: bộ chấm code theo `nhan_dung` cho đúng 9 câu trượt này, khớp từng câu với bản nhóm chấm tay (18/27).

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| GT19 | Em đang bảo lưu kết quả học ở trường đại học chính quy, năm sau mới học lại. Trong thời gian bảo lưu em có được tạm hoãn gọi nhập ngũ không? | `NHAN: not_eligible` — "thường không thuộc diện tạm hoãn" | KB chưa có quy định riêng về bảo lưu, expected là `need_more_information`; model kết luận khi thiếu dữ kiện |
| GT04 | Em đã được tạm hoãn khi học trung cấp, nay học liên thông đại học chính quy… | `NHAN: not_eligible` | Expected `need_more_information` (liên thông có liên tục không?); model kết luận ngay |
| GT14 | Em có giấy xác nhận sinh viên rồi thì có thể bỏ buổi khám sức khỏe không? | `NHAN: need_more_information` (hỏi trình độ, hệ, khóa) | Expected `not_eligible` + nd218-d9; câu hỏi về khám sức khỏe không cần dữ kiện học tập |

## 3. Một lần cải tiến

- **Nhắm vào nhóm lỗi:** A — kết luận `not_eligible` quá sớm (GT04, GT09, GT19, GT20).
- **Vì sao đau nhất với người dùng:** báo sai "không thuộc diện tạm hoãn" khiến sinh viên có thể bỏ cuộc một quyền hợp pháp, hoặc không nộp giấy đúng hạn. Sai kiểu này nặng hơn nhóm B (nhãn đúng, thiếu mã) và nhóm C (hỏi lại thừa): hai nhóm đó vẫn để người dùng đi hỏi tiếp, nhóm A thì đóng cửa. Nhóm A cũng nhiều câu nhất (4/9).
- **Đã sửa gì** (`codebase/prompts.py`, PR #24):
  1. Luật 6a: chỉ chọn `not_eligible` khi chính người dùng **đã nói** dữ kiện loại trừ (đã được tạm hoãn ở khóa trước, kéo dài vì nợ môn, đã thôi học…). Kết luận "không" phải dựa vào dữ kiện chưa nói (đã từng tạm hoãn chưa, đã nhập học chưa) hoặc tình huống ngữ cảnh không có quy định riêng (bảo lưu, tạm nghỉ) thì chọn `need_more_information`, hỏi đúng dữ kiện thiếu, vẫn ghi điểm luật vào `can_cu`.
  2. Giới hạn 6a: không dùng để hoãn kết luận `eligible_for_review` khi người dùng đã nói đủ trình độ và hệ chính quy (thêm sau khi run-5 làm GT10, GT11 bị hỏi lại thừa).
- **Ghi thật — PR #24 còn một thay đổi khác nhóm:** ngữ cảnh liệt kê nguyên văn các id hợp lệ cho `can_cu` (luật 2). Thay đổi này làm để sửa lỗi chép sai mã của `gpt-4o-mini` ở lượt phát triển run-2 (14 câu `G_CITE_MVP`), không nhắm nhóm A, nhưng có thể đổi kết quả nhóm B. Ở run-6, GT13 (nhóm B) từ trượt thành đạt nhiều khả năng do thay đổi này, không phải do luật 6a.
- **Kết quả lượt 2 chính thức (`run-7`):** nhóm A 0/4 → 3/4 (GT09, GT19, GT20 đạt; GT04 vẫn trượt) · tổng 18/27 → 23/27 (67% → 85%), cao hơn lượt phát triển run-6 (22/27).
  - Tham khảo lượt phát triển `run-6` (đã chỉnh trên chính bộ thử, nên lượt 2 có thể thấp hơn): nhóm A 0/4 → 3/4 (GT09, GT19, GT20 đạt; GT04 vẫn trượt) · tổng 18/27 → 22/27 (67% → 81%).
- **Kiểm chứng ngoài mẫu:** 14 câu mới chưa ai chỉnh theo, `gpt-6.1-terra`, mỗi câu 2 lần: `main` 22/28 · PR #24 24/28. Câu thắng thêm (tạm nghỉ một học kỳ) đổi từ `not_eligible` sang `need_more_information`. *(Nguồn: tài liệu quyết định CP4 của nhóm, 27/11; 2 nhãn trong 14 câu là nhóm tự suy.)*
- **Câu nào tệ đi sau khi sửa:** không câu nào — mọi câu đạt ở run-1 vẫn đạt ở run-7. Ngoài nhóm A còn thêm GT02 (nhóm C) và GT13 (nhóm B) chuyển sang đạt; GT13 nhiều khả năng do thay đổi liệt kê id ở luật 2, GT02 chưa rõ nguyên nhân (một lần chạy, có thể do biến động của model). Ở lượt phát triển: run-5 làm GT10 và GT11 bị hỏi lại thừa (GT10 trượt); run-6 sửa lại, so với run-1 không câu nào tệ đi.

## 4. Còn lại

- **Lỗi chưa sửa + nguy hiểm thế nào** *(theo run-7: còn trượt GT03, GT04, GT11, GT14)*:
  - **Nhóm C — GT14 (và GT03 ở nhóm B; GT02 đạt ở run-7):** bước chặn `G_ASK_STUDY` trả `need_more_information` mà không tra luật, nên không có căn cứ. Nguy hiểm nhất ở GT14: người dùng hỏi có bỏ buổi khám được không, agent chỉ hỏi lại trình độ mà không cảnh báo giấy xác nhận không phải quyết định tạm hoãn và bỏ khám có thể bị phạt (NĐ 218 Đ9). Hướng sửa (luôn tra luật trước khi hỏi thêm) đã thử ở PR #25, chưa merge để giữ một cải tiến cho lượt 2.
  - **GT11:** đúng nhãn nhưng thiếu `vbhn133-d42` (ai quyết định tạm hoãn). Người dùng không biết quyết định cuối thuộc Chủ tịch UBND cấp tỉnh — mức nguy hiểm thấp, phần miễn trừ vẫn nêu điều này.
  - **GT04 — nhãn tranh cãi:** model vẫn ra `not_eligible`. Input gần giống GT05 (đã tạm hoãn ở trình độ trước, nay học liên thông) mà GT05 có expected `not_eligible`; GT04 khác ở chỗ địa phương không nhận giấy và ghi "liên thông phải liên tục không gián đoạn". Nhóm giữ nguyên `expected` theo hướng dẫn BQP đã dùng khi dựng bộ thử, **không sửa** để khớp output, và không viết luật riêng cho câu này.
- **Nếu có thêm 1 tuần:**
  - Sửa nhóm C: tra luật trước khi hỏi thêm, để câu hỏi lại vẫn kèm căn cứ (PR #25).
  - Thêm 20–30 câu thử ngoài mẫu, ưu tiên tình huống biên từ data Facebook (bảo lưu, liên thông, chuyển trường), và cho người thứ hai gán nhãn độc lập các câu tranh cãi.
  - Hỏi người dùng thật xem họ hiểu và làm gì với kết quả "cần hỏi thêm".
