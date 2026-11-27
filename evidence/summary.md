# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).
> Cập nhật 2026-11-27: đã có hai nguồn đào data và một khảo sát (27 câu trả lời). Phỏng vấn **chưa làm**; các ô phỏng vấn ghi "chưa", không điền thay bằng data.

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ hai bộ: hỏi đáp cổng Chính phủ (N = 24) và nhóm Facebook công khai (N = 180) | `evidence/data-mining.md` · `evidence/data-mining-fb.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ chưa làm — kịch bản đã sẵn; `P1.md`… tạo sau mỗi buổi | `evidence/interviews/KICH-BAN.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☑ có điều kiện: 25 người đúng tuổi (≥ 20). Form không hỏi giới tính; kênh gửi và việc người trả lời ngoài nhóm **chưa ghi** | `evidence/survey/questions.md` · `results.csv` · `count_survey.py` |

## 2. Số chính

- **Đào data — hỏi đáp cổng Chính phủ** (`count.py`): 11/24 bài (46%), 7/15 ca, đã nộp giấy tờ mà vẫn vướng với địa phương; 21/24 bài (88%) vướng địa phương hoặc là tình huống biên.
- **Đào data — nhóm Facebook "Hỏi đáp Nghĩa Vụ Quân Sự 2027"** (`count_fb.py`, 2025-09 → 2026-11):
  - 38/180 bài (21%) đã nộp giấy xác nhận mà xã/phường không nhận, đòi thêm giấy hoặc vẫn gọi khám;
  - 117/180 (65%) là tình huống biên (nợ môn, quá hạn, liên thông, bảo lưu, chuyển trường, du học…);
  - 136/180 (76%) có ít nhất một trong hai;
  - 28/180 (16%) đã gặp ít nhất một nguồn khác (văn bản luật, trường, xã/phường, người quen) mà vẫn đăng hỏi lại nhóm — **cận dưới**, vì chỉ đếm được khi người hỏi tự kể.
- Phỏng vấn: **chưa có số** — chưa phỏng vấn ai (tính đến 2026-11-27). Khi có: x/3 người gặp pain theo ngưỡng `hypothesis.md` phần B *(n nhỏ không ghi %)*, số lần trong 12 tháng qua và thời gian mỗi lần của P1–P3.
- **Khảo sát** (`count_survey.py`, 27/11/2026): 27 câu trả lời, 25 đúng tuổi 18–27, **n = 19** người đúng tuổi đã từng tra:
  - 9/19 (47%) tra ≥ 2 cách (Google, ChatGPT, luật, bạn bè, Ban CHQS…) **mà vẫn chưa chắc** mình thuộc diện tạm hoãn và cần nộp giấy gì;
  - 13/19 (68%) phải hỏi ≥ 2 câu liên tiếp mới rõ; 13/19 (68%) tra ≥ 2 lần trong tháng gọi khám;
  - 15/19 (79%) chỉ mất dưới 15 phút mỗi lần — cái mất là **sự chắc chắn**, không phải thời gian của một lần tra.

> Nhóm đếm số lần trong **12 tháng qua** thay cho 1 tháng: tạm hoãn đi theo đợt gọi khám hằng năm, người dùng thường chỉ gặp việc này 1–2 lần mỗi năm.

Phỏng vấn nhiều vai thì đếm theo từng vai, không cộng chung.

| | Vai | Gặp pain? | Số lần / 12 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | *chưa phỏng vấn* | | | | |
| P2 | *chưa phỏng vấn* | | | | |
| P3 | *chưa phỏng vấn* | | | | |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. *"Tôi đã nộp Giấy xác nhận sinh viên do nhà trường cấp cho Ban Chỉ huy Quân sự xã, tuy nhiên không được chấp nhận giải quyết chế độ tạm hoãn"* — hỏi đáp cổng Chính phủ, `qa-q02` (2026-11-11), sinh viên nợ môn.
2. Cơ quan quân sự địa phương *"không chấp thuận với lý do chương trình đào tạo… là liên thông"* — hỏi đáp cổng Chính phủ, `qa-q06` (2026-10-13).
3. *"Lúc em đem giấy xác nhận còn là sinh viên ra xã đội thì người ta không chấp nhận và nói rằng là cứ đi khám."* — nhóm Facebook, bài `0a70aa3901` (2026-10-28), trễ 1 năm vì đồ án.
4. *"Em lên nộp giấy ở địa phương 3 lần nhưng họ đều từ chối."* — nhóm Facebook, bài `8d713b0fa2` (2026-10-05), hệ kỹ sư 5 năm.
5. Nộp đủ giấy từ sớm nhưng xã *"Cứ bắt về khám vòng 1 nộp tận tay"*, lo *"đi lại tốn kém, mất thời gian và lỡ việc"* — nhóm Facebook, bài `9a023418b9` (2026-10-22).
6. *"Theo luật nghĩa vụ quân sự thì em tra được như điểm g"* — vẫn đăng nhóm hỏi mình có được hoãn không; nhóm Facebook, bài `6ae830e218` (2026-10-18), hệ 4,5 năm.
7. Đã nộp giấy mà vẫn phải khám vòng 2; hỏi thì *"họ bảo chỉ công nhận giấy hoãn 1 lần"* — nhóm Facebook, bài `8f5d4aa452` (2026-11-11).
8. *"tôi cần biết có quyết định chính xác, ko biết nguồn chuẩn, đi khám về vẫn ko biết mình đc gọi"* — khảo sát, `r02` (tra 4 cách, "vẫn mơ hồ").
9. *"những quy định mới chưa kịp cập nhật trên các trang thông tin đại chúng"* — khảo sát, `r21`.

Thêm ví dụ: `data-mining.md` mục 4, `data-mining-fb.md` mục 4, cột `q8_kho_nhat` trong `survey/results.csv`.

## 4. Các nguồn có khớp nhau không

**Data nói:** cả hai bộ đều cho thấy chỗ vướng lặp lại là hai việc sau.
- **Địa phương áp dụng khác nhau:** sinh viên đã nộp giấy xác nhận nhưng xã/phường không nhận, đòi thêm giấy hoặc vẫn gọi khám. Lý do hay gặp: "hết 4 năm / hết niên khóa", "chỉ công nhận giấy 1 lần", "không cùng khóa đào tạo", "phải có giấy chuyển trường".
- **Tình huống biên:** nợ môn, học quá hạn, liên thông, chuyển trường, bảo lưu, du học — luật chỉ nói "một khóa đào tạo", người hỏi không tự xác định được mình có thuộc diện không.

**Khớp:** tình huống biên chiếm đa số ở cả hai bộ (83% và 65%); vướng địa phương đều có mặt với những lý do giống nhau.

**Lệch:** tỷ lệ vướng địa phương ở cổng Chính phủ (46%) cao hơn nhiều so với nhóm Facebook (21%). Cách giải thích hợp lý nhất: cổng Chính phủ chọn đăng các ca khiếu nại đã qua địa phương, còn nhóm Facebook có nhiều người hỏi **trước khi** nộp (hỏi thời hạn, giấy gì, có được hoãn không). Hai con số đo hai giai đoạn khác nhau, không mâu thuẫn.

**Một điều ngược với điều nhóm nghĩ:** ở nhóm Facebook, sinh viên học bình thường bị vướng địa phương **không ít hơn** nhóm tình huống biên (19/63 so với 19/117). Vậy cách giải thích khác "chỉ nhóm biên mới gặp pain" chưa đúng với data này.

**Người dùng nói (khảo sát, n = 19):** gần một nửa (9/19) đã tra từ 2 cách trở lên mà vẫn chưa chắc. Họ dùng nhiều nguồn cùng lúc (trung vị 3 cách), và lý do vướng họ tự viết là không biết nguồn nào chuẩn, quy định mới chưa cập nhật, và tiêu chuẩn sức khỏe.

**Khớp và lệch giữa data và khảo sát:**
- **Khớp:** người dùng phải hỏi nhiều nơi (89% tra ≥ 2 cách; trên Facebook, người hỏi đã hỏi xã/phường hoặc đọc luật rồi vẫn hỏi lại).
- **Lệch:** khảo sát ủng hộ ý "thông tin phân tán, khó kiểm chứng" mạnh hơn data (47% so với 16% cận dưới). Lý do có thể: khảo sát hỏi thẳng, còn bài đăng hiếm khi kể đã tra ở đâu.
- **Khảo sát không đo được vướng địa phương:** form không hỏi chuyện nộp giấy ở xã/phường, và hỏi tạm hoãn **nói chung** (nhiều câu trả lời nói về sức khỏe), không riêng lý do học tập.

**Người dùng nói (qua phỏng vấn):** chưa có. Phỏng vấn sẽ kiểm lại điều cả data và khảo sát chưa đo: đi lại mấy lần, có bị địa phương từ chối không, cuối cùng có được hoãn không.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **phải đổi — mở rộng** (hai bộ data N = 24 và N = 180, khảo sát n = 19). Ý "thông tin phân tán" có khảo sát ủng hộ một phần (9/19, dưới mức 2/3 mà phần B đặt cho phỏng vấn); ý "địa phương áp dụng khác nhau" có data ủng hộ nhưng khảo sát chưa hỏi. Phỏng vấn sẽ chốt.

- **Phần được data ủng hộ:** sinh viên khó đối chiếu quy định tạm hoãn với tình trạng học tập của mình, nhất là khi lệch khỏi ca "khóa chính quy đầu tiên, đúng hạn" (65–83% câu hỏi).
- **Phần được ủng hộ một phần:** "vì thông tin tra cứu phân tán". Khảo sát: 9/19 tra ≥ 2 cách mà vẫn chưa chắc, người trả lời tự viết "ko biết nguồn chuẩn". Data Facebook: chỉ 16% bài (cận dưới) kể đã tra nguồn khác, và nguồn hay gặp nhất lại là **chính xã/phường**.
- **Phần ngược giả thuyết:** "mất thời gian". 15/19 người mất dưới 15 phút mỗi lần tra; cái thiếu là sự chắc chắn và việc địa phương chấp nhận giấy.
- **Đề xuất câu pain sửa** (nhóm duyệt sau phỏng vấn): sinh viên có tình trạng học tập không chuẩn (nợ môn, quá hạn, liên thông, chuyển trường…) không biết mình có thuộc diện tạm hoãn không, và khi nộp giấy xác nhận thì bị địa phương từ chối với lý do họ không kiểm được, nên phải hỏi khắp nơi, đi lại nhiều lần hoặc phải đi khám.
- **Ý nghĩa cho sản phẩm:** công cụ đúng hướng ở chỗ giúp sinh viên đối chiếu tình huống biên với căn cứ có trích dẫn, mang theo khi làm việc với địa phương. Công cụ **không** giải quyết được việc địa phương áp dụng sai; phần này chỉ hỗ trợ được bằng gợi ý bước tiếp theo (đề nghị xem xét, hỏi lại cơ quan có thẩm quyền).

**Điều vẫn chưa biết:**
- Đi lại bao nhiêu lần, cuối cùng có được hoãn không (data không cho biết kết cục; khảo sát không hỏi).
- Người không đăng hỏi có gặp pain không — mẫu data chỉ gồm người đã gặp chuyện.
- Pain chính là thiếu thông tin hay là địa phương — cần ≥3 phỏng vấn theo ngưỡng ở `hypothesis.md` phần B.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| *chưa hẹn — tìm người theo `interviews/KICH-BAN.md` mục 1* | | |
