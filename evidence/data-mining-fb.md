# Đào data lần 2 — bài đăng nhóm Facebook "Hỏi đáp Nghĩa Vụ Quân Sự 2027"

> Chạy lại: `python evidence/count_fb.py <raw.json>` (thêm `--vidu` để in đoạn ngắn các bài vướng địa phương / đã gặp nguồn khác).
> Bảng từng bài: `evidence/data-mining-fb-ketqua.csv` (chỉ mã băm · ngày · nhãn · từ khóa tìm, **không** chép nội dung, tên hay đường dẫn bài).
> Bản thu thập gốc (`raw.json`) **không commit**: đó là lời của người đăng, có thể nhận ra họ. Người giữ data giữ bản này trên máy.
> Nguồn này bổ sung cho `evidence/data-mining.md` (58 bài hỏi đáp trên cổng Chính phủ). Hai nguồn đếm theo cùng nhãn để so được với nhau.

## 1. Cách thu thập

- **Nguồn:** nhóm Facebook **công khai** "Hỏi đáp Nghĩa Vụ Quân Sự 2027" (khoảng 53 nghìn thành viên, hơn 90 bài/ngày theo trang nhóm). Thành viên nhóm đăng câu hỏi về trường hợp của mình.
- **Ngày thu thập:** 2026-11-27, bằng tài khoản của người giữ data đã tham gia nhóm.
- **Cách làm:** dùng ô tìm kiếm trong nhóm với **11 từ khóa** rồi cuộn hết trang kết quả, chỉ đọc chữ hiển thị trên trang. **Không** bình luận, bày tỏ cảm xúc, đăng bài, nhắn tin hay bấm "Xem thêm". Bài dài vì vậy chỉ thấy phần đầu (ghi ở cột `bi_cat`).
- **Từ khóa** (chọn trước khi đọc, theo các chỗ vướng ở `data-mining.md` và câu hỏi phỏng vấn): giấy xác nhận sinh viên · tạm hoãn sinh viên · có được hoãn không đang học · nợ môn · chưa tốt nghiệp · liên thông · bảo lưu · văn bằng 2 · du học · cao đẳng tạm hoãn · xã không nhận giấy.
- **Thu được:** 497 bài khác nhau (Facebook trả tối đa khoảng 60–70 bài cho mỗi từ khóa), đăng từ 2025 đến 2026-11-27.
- **Thông tin cá nhân:** không lưu tên tài khoản, ảnh, đường dẫn bài hay bình luận. Trích dẫn ở mục 4 đã bỏ tên trường, tên địa phương.

## 2. Cách đếm

- **Đơn vị đếm:** một **bài đăng**. Bài trùng nội dung (đăng lại, hoặc hiện ở nhiều từ khóa) chỉ tính một lần.
- **Lọc vào mẫu:**
  1. có nói đến việc học (sinh viên, đại học, cao đẳng, liên thông, bảo lưu, du học…) **và** đến tạm hoãn hoặc giấy xác nhận;
  2. không phải nữ hỏi tự nguyện nhập ngũ;
  3. không phải bài chia sẻ thông tin chung;
  4. không phải lý do khác (sức khỏe, gia đình) mà không nói gì đến giấy tờ học tập.
- **Nhãn** (một bài có thể mang nhiều nhãn; định nghĩa giống `data-mining.md` để so được):
  - `vuong_dia_phuong`: **đã nộp hoặc đưa giấy tờ học tập** mà xã/phường/Ban CHQS không nhận, đòi thêm giấy, nói không được hoãn, hoặc vẫn gọi khám. Không tính khi người hỏi tự nộp trễ, quên nộp, hay chỉ lo sẽ bị từ chối.
  - `tinh_huong_bien`: ngoài ca "đang học khóa chính quy đầu tiên, đúng hạn": nợ môn, học quá hạn, liên thông, văn bằng 2, bảo lưu, du học, chuyển trường, thôi học, thi lại, học tiếp sau tốt nghiệp, hệ không chính quy.
  - `hoi_thoi_han_thu_tuc`: hỏi nộp muộn, quên nộp, nộp ở vòng 2, nộp ở đâu, cần giấy gì.
  - `da_gap_nguon_khac`: trước khi hỏi nhóm, người hỏi **đã nghe hoặc đọc ít nhất một nguồn khác** (văn bản luật, trường, xã/phường, người quen/mạng) mà vẫn hỏi lại. Nhóm là một nguồn nữa, nên nhãn này gần với ngưỡng "tra ≥2 nguồn mà vẫn chưa chắc" ở `hypothesis.md`.
- **Kiểm tay:** đã đọc phần đầu cả 303 bài qua bước lọc chủ đề trước khi chốt luật. Sau lượt chạy đầu, đọc lại **toàn bộ** bài mang nhãn `vuong_dia_phuong` và sửa 16 bài khớp nhầm (câu giả định "nếu xã không chấp nhận", tự nộp trễ, người từ chối là trường), thêm 3 bài luật sót, loại 3 bài không phải tạm hoãn vì học. Danh sách và lý do nằm ở `SUA_TAY_VDP`, `LOAI_TAY` trong script. Nhãn `tinh_huong_bien` kiểm ngẫu nhiên 15 bài: 14 đúng.

## 3. Kết quả

**Mẫu:** N = 180 bài, đăng 2025-09-14 → 2026-11-27; 146 bài từ 2026-08-01 (đợt gọi khám cho năm 2027). Bị loại: 292 bài không nói tạm hoãn vì học, 22 bài lý do khác, 2 bài chia sẻ chung, 1 bài trùng.

| Đếm gì | x / N | So với hỏi đáp cổng Chính phủ (`data-mining.md`) |
|---|---|---|
| Đã nộp giấy mà vẫn vướng với địa phương (`vuong_dia_phuong`) | **38/180 (21%)** | 11/24 (46%) |
| Tình huống biên (`tinh_huong_bien`) | 117/180 (65%) | 20/24 (83%) |
| Vướng địa phương HOẶC tình huống biên | 136/180 (76%) | 21/24 (88%) |
| Hỏi thời hạn, thủ tục nộp giấy | 29/180 (16%) | — (nhãn `hoi_thu_tuc` khác định nghĩa) |
| Đã gặp nguồn khác mà vẫn hỏi nhóm (`da_gap_nguon_khac`) | 28/180 (16%) | — |
| Không mang nhãn nào | 22/180 (12%) | 1/24 (4%) |

**Tách theo nhóm** (để kiểm cách giải thích khác "chỉ nhóm tình huống biên mới gặp pain"):

| Nhóm | n | Vướng địa phương | Đã gặp nguồn khác |
|---|---|---|---|
| Học bình thường (không có dấu hiệu biên) | 63 | 19 (30%) | 10 (16%) |
| Tình huống biên | 117 | 19 (16%) | 18 (15%) |

- Trong 28 bài đã gặp nguồn khác, nguồn hay gặp nhất là **chính xã/phường** (15 bài): người hỏi đã được địa phương trả lời, nhưng không tin hoặc không hiểu nên hỏi lại nhóm. Tiếp theo là văn bản luật (9), người quen/mạng (4), trường (3).
- **Kiểm độ nhạy:** từ khóa "xã không nhận giấy" có thể kéo nhãn vướng địa phương lên. Bỏ 3 bài chỉ tìm thấy qua từ khóa này, tỷ lệ vẫn là 35/177 (20%).
- 28/180 bài (16%) bị cắt, chỉ thấy phần đầu; 9 trong số đó vẫn đủ rõ để mang nhãn vướng địa phương. Các nhãn khác có thể bị đếm thiếu ở những bài này, nên các tỷ lệ trên là **cận dưới**.

## 4. Ví dụ cụ thể (đã bỏ tên trường, địa phương; mã = cột `id` trong CSV)

1. `0a70aa3901` (2026-10-28) — trễ 1 năm vì chưa đủ điều kiện làm đồ án: *"Lúc em đem giấy xác nhận còn là sinh viên ra xã đội thì người ta không chấp nhận và nói rằng là cứ đi khám."*
2. `8d713b0fa2` (2026-10-05) — hệ kỹ sư 5 năm, giấy của trường không ghi năm kết thúc: *"Em lên nộp giấy ở địa phương 3 lần nhưng họ đều từ chối."* Địa phương đã gửi công văn và trường đã xác nhận, nhưng người hỏi vẫn nhận giấy khám.
3. `8f5d4aa452` (2026-11-11) — học đến 2027: đã nộp giấy xác nhận mà vẫn phải khám vòng 2; hỏi thì *"họ bảo chỉ công nhận giấy hoãn 1 lần"*.
4. `9a023418b9` (2026-10-22) — nộp đủ giấy từ sớm nhưng xã *"Cứ bắt về khám vòng 1 nộp tận tay"*, lo bị gọi tiếp vòng 2 *"đi lại tốn kém, mất thời gian và lỡ việc"*.
5. `6ae830e218` (2026-10-18) — hệ 4,5 năm: *"Theo luật nghĩa vụ quân sự thì em tra được như điểm g"*, nhưng vẫn đăng nhóm hỏi trường hợp của mình có được hoãn không.
6. `79f9a8e68d` (2026-09-15) — thi lại sang trường khác: *"em nghe có người nói là kêu khám sức khỏe đậu là đi luôn ko đc tạm hoãn do 2 giấy xác nhận 2 năm không cùng trường"*.
7. `782007d2e5` (2026-11-23) — nhận lệnh gọi khám, xin giấy xác nhận nộp bổ sung thì *"họ bảo giờ muộn rồi ko nhận giấy. Họ bảo cứ lên khám đi rồi tính tiếp."*

## 5. Giới hạn

- **Mẫu tự chọn:** chỉ những người tìm đến nhóm và đăng hỏi. Người làm thủ tục suôn sẻ thường không đăng, nên tỷ lệ chỉ cho biết **trong các câu hỏi đã đăng**, không phải trong toàn bộ sinh viên.
- **Phụ thuộc ô tìm kiếm của Facebook:** mỗi từ khóa chỉ trả khoảng 60–70 bài theo thứ tự của Facebook, không phải toàn bộ bài trong nhóm. Đổi từ khóa thì mẫu đổi.
- **Chỉ có lời người hỏi, thường ngắn và bị cắt:** không biết kết cục (cuối cùng có được hoãn không), không biết họ mất bao lâu hay tốn bao nhiêu lần đi lại.
- **Không kiểm được người đăng:** không biết tuổi, giới tính thật; một số bài là người nhà hỏi hộ (vợ, chị, mẹ).
- **Nhãn gắn bằng từ khóa** rồi kiểm tay; nhãn `da_gap_nguon_khac` chỉ bắt được khi người hỏi tự kể nguồn, nên dễ đếm thiếu.
- **Không phải phỏng vấn:** bài đăng không thay được phần hỏi lại người dùng về tần suất, thời gian và cách xoay xở (`evidence/interviews/`).
