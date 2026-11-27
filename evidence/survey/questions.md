# Khảo sát — "Khảo sát tìm hiểu quy định tạm hoãn nghĩa vụ quân sự"

> Google Form của nhóm, câu trả lời ngày **27/11/2026 từ 17:38 đến 19:21** (27 câu trả lời).
> Chạy lại: `python evidence/survey/count_survey.py evidence/survey/raw-khao-sat-2026-11-27.csv`.
> `results.csv` = toàn bộ 27 câu trả lời, giữ ngày, bỏ giờ, mã dòng `r01`…`r27`. Form **không** thu tên, email hay số điện thoại. Bản xuất gốc (`raw-*.csv`) bị gitignore.

## Thông tin gửi

- Kênh gửi và danh sách người nhận: **chưa ghi** — người gửi form (cùng người làm PR #22) bổ sung, kèm xác nhận người trả lời là người ngoài nhóm.
- Giờ mở / chốt: câu trả lời đầu 17:38, cuối 19:21 ngày 27/11/2026.

## Câu hỏi (nguyên văn trên form)

| # | Câu hỏi | Lựa chọn thấy trong câu trả lời | Cột `results.csv` |
|---|---|---|---|
| 1 | Bạn có phải trong độ tuổi gọi nhập ngũ (18–27 tuổi) không? | Có · Không | `q1_tuoi_18_27` |
| 2 | Lần gần nhất bạn tìm hiểu quy định hoặc thủ tục tạm hoãn nghĩa vụ quân sự là khi nào? | Trong 1 tháng qua · Trong 6 tháng qua · Hơn 6 tháng trước · Chưa bao giờ | `q2_lan_gan_nhat` |
| 3 | Vào đợt gọi khám/nộp giấy xác nhận, trong 1 tháng bạn thường tra cứu hoặc hỏi về tạm hoãn NVQS mấy lần? | Chưa từng tra · 1 lần · 2–3 lần · 4 lần trở lên | `q3_so_lan_1_thang` |
| 4 | Mỗi lần tìm hiểu, bạn thường phải tra/hỏi khoảng bao nhiêu câu liên tiếp mới rõ trường hợp của mình? | 1 câu · 2–3 câu · 4 câu trở lên | `q4_so_cau_lien_tiep` |
| 5 | Lần gần nhất đó, bạn đã tìm thông tin bằng cách nào? *(chọn nhiều)* | Tìm Google / đọc bài báo · Đọc thẳng văn bản luật · Hỏi bạn bè / anh chị · Hỏi phòng đào tạo / Ban CHQS phường · Hỏi nhóm Facebook / TikTok / Reddit · Hỏi ChatGPT · Khác | `q5_cach_tim` |
| 6 | Lần gần nhất đó bạn mất khoảng bao lâu để tìm hiểu? | Dưới 5 phút · 5–15 phút · 15–30 phút · Trên 30 phút | `q6_thoi_gian` |
| 7 | Sau lần tìm đó, bạn có chắc chắn mình thuộc diện được tạm hoãn và cần nộp giấy gì chưa? | Rõ rồi · Mới rõ một phần, vẫn phân vân · Vẫn mơ hồ, chưa chắc | `q7_da_chac` |
| 8 | Điều gì làm bạn khó chịu/vướng nhất lần đó, hoặc bạn đang có câu hỏi thực tế nào về tạm hoãn NVQS không? | Đoạn văn | `q8_kho_nhat` |

Form không hỏi giới tính, việc có đang đi học hay không, và lý do tạm hoãn. Vì vậy "đúng người dùng" ở đây chỉ kiểm được theo **tuổi**.

## Cách tính (chạy bằng `count_survey.py`)

- **Đúng vai:** câu 1 = Có → 25/27. Hai người trả lời "Không" (một người ghi ở câu 8 là nữ) bị loại.
- **Mẫu số các số về pain:** người đúng tuổi **đã từng tra**, tức câu 2 khác "Chưa bao giờ" và câu 3 khác "Chưa từng tra" → **n = 19**. Sáu người đúng tuổi bị loại vì chưa từng tìm hiểu, hoặc tự trả lời mâu thuẫn ở câu 2 và câu 3.
- **"Tra ≥ 2 cách mà vẫn chưa chắc"** (gần nhất với ngưỡng ở `hypothesis.md` phần B): câu 5 có ≥ 2 cách **và** câu 7 = "Mới rõ một phần" hoặc "Vẫn mơ hồ".

## Kết quả (n = 19 người đúng tuổi đã từng tra)

| Số | x / 19 |
|---|---|
| Sau khi tra vẫn chưa chắc (câu 7) | 9 (47%) |
| Tra ≥ 2 cách (câu 5) | 17 (89%) |
| **Tra ≥ 2 cách mà vẫn chưa chắc** | **9 (47%)** |
| Phải hỏi ≥ 2 câu liên tiếp mới rõ (câu 4) | 13 (68%) |
| Tra ≥ 2 lần/tháng vào đợt gọi khám (câu 3) | 13 (68%) |
| Lần gần nhất trong 1 tháng qua (câu 2) | 13 (68%) |
| Lần gần nhất mất ≥ 15 phút (câu 6) | 4 (21%) |

- **Cách tìm (chọn nhiều):** Google/báo 17 · ChatGPT 10 · văn bản luật 9 · bạn bè 8 · nhóm Facebook/TikTok/Reddit 8 · phòng đào tạo/Ban CHQS 7. Trung vị: 3 cách mỗi người.
- **Câu 8:** 11/19 người viết nội dung thật (còn lại "không", "khum"…). Chủ đề lặp nhiều nhất là **sức khỏe và xếp loại khám** (4 người), kế đến **thông tin không biết nguồn nào chuẩn hoặc chưa cập nhật** (3 người).

## Giới hạn

- Không kiểm được giới tính, việc đang đi học, và người trả lời có ngoài nhóm hay không.
- Câu hỏi về tạm hoãn NVQS **nói chung**, không riêng lý do học tập; nhiều câu trả lời ở câu 8 nói về sức khỏe.
- Mẫu nhỏ, gửi trong khoảng 2 giờ, kênh gửi chưa ghi → không suy ra cho toàn bộ sinh viên.
