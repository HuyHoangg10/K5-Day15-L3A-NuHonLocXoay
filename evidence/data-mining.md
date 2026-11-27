# Đào data — cách đếm và kết quả

> Chạy lại: `python evidence/count.py` (thêm `--all` để in mọi bài bị loại). Bảng từng bài: `evidence/data-mining-ketqua.csv` (chỉ id · URL · ngày · nhãn, không chép nội dung bài).
> Repo chỉ chứa số đã tổng hợp và vài đoạn ví dụ ngắn đã ẩn danh.

## 1. Cách đếm

- **Data dùng:** `kb-nvqs/chunks/qa_chunks.jsonl` (repo tại commit `4c7b685`, chạy ngày 2026-11-27). 58 bài hỏi đáp và kiến nghị đã đăng công khai trên xaydungchinhsach.chinhphu.vn, baochinhphu.vn, chinhsachonline.chinhphu.vn và pbgdpl.cantho.gov.vn, đăng từ 2020-04-23 đến 2026-11-11.
- **Đơn vị đếm:** một **bài**, kèm một số thứ hai đếm theo **ca**. Có 9 cặp bài là cùng một câu hỏi đăng trên hai cổng, đếm hai lần sẽ làm phồng số; danh sách ghép nằm ở `SAME_CASE` trong script.
- **Lọc vào mẫu:** gồm các luật sau:
  1. `loai = hoi_dap`;
  2. có nói đến "hoãn";
  3. có dấu hiệu lý do học tập (sinh viên, đại học, cao đẳng, liên thông, du học, nợ môn…);
  4. không phải lý do gia đình hay sức khỏe (lao động duy nhất, khuyết tật, diop…);
  5. có lời người hỏi;
  6. không phải kiến nghị cử tri.
- **Văn bản để gắn nhãn:** chỉ lấy **lời người hỏi**. Ưu tiên trường `question`. Nếu `question` rỗng, dùng phần đầu `answer` khi bài báo có chép câu hỏi; không có thì dùng tiêu đề. Bỏ đoạn sapo của tòa soạn và cắt từ chỗ cơ quan bắt đầu trả lời, vì phần trả lời tự nhắc "nợ môn", "kéo dài" và làm sai nhãn.
- **Nhãn** (một bài có thể mang nhiều nhãn, so từ khóa; danh sách từ khóa đầy đủ nằm trong script):
  - `vuong_dia_phuong`: đã làm theo cách thông thường mà địa phương không chấp nhận, chưa tiếp nhận, trả lời chưa rõ hoặc đòi thêm giấy tờ. Bài cũng mang nhãn này nếu người hỏi kể "đã nộp… tuy nhiên/nhưng…".
  - `tinh_huong_bien`: hoàn cảnh học tập nằm ngoài ca "đang học khóa chính quy đầu tiên", gồm nợ môn, kéo dài, liên thông, thôi học, chuyển trường, du học, GDTX.
  - `hoi_thu_tuc`: hỏi cần giấy tờ, hồ sơ hay thủ tục gì.
  - `khong_the_hien_pain`: không khớp nhãn nào.
- **Mẫu số:** N = 24 bài (15 ca) đủ điều kiện lọc. Không lấy 58, vì 34 bài còn lại không phải câu hỏi về tạm hoãn vì học tập.

## 2. Đọc trước, đếm sau

Đã đọc trường `question` hoặc đầu `answer` của cả 58 bài trước khi chốt luật. Các kiểu hành vi thấy được:
- Đã nộp giấy xác nhận của trường, nhưng Ban CHQS xã/phường không nhận, hoặc chỉ nhận giấy đầu tiên.
- Khóa học kéo dài vì nợ môn, nên không rõ còn được tạm hoãn không.
- Học liên thông, hoặc thôi học để chuyển trường: không rõ có tính là "một khóa" không.
- Du học: không rõ cần giấy tờ gì, và địa phương đòi chứng minh thêm.
- Bài phổ biến luật chung hoặc kiến nghị cử tri: không phải hành vi của người hỏi, nên loại khỏi mẫu.

Kiểm tay sau lần chạy đầu đã sửa ba lỗi luật:
- Bỏ sapo và phần trả lời, vì chúng làm `tinh_huong_bien` bị đếm thừa.
- Thêm luật "đã nộp… tuy nhiên/nhưng" và từ khóa "không chấp thuận", "chưa tiếp nhận", vì trước đó sót q01, q07, q26, q28, q31.
- Loại q54 (bài phổ biến luật) và q36 (kiến nghị cử tri bị xếp vào `hoi_dap`).

## 3. Kết quả

| Đếm gì | x / N theo bài | x / N theo ca | Ghi chú |
|---|---|---|---|
| Đã vướng với địa phương (`vuong_dia_phuong`) | 11/24 (46%) | 7/15 (47%) | Đã nộp giấy tờ mà vẫn không được giải quyết |
| Tình huống biên (`tinh_huong_bien`) | 20/24 (83%) | 13/15 (87%) | Nợ môn, liên thông, chuyển trường, du học, GDTX |
| Hỏi thủ tục, giấy tờ (`hoi_thu_tuc`) | 18/24 (75%) | 12/15 (80%) | |
| Vướng địa phương HOẶC tình huống biên | 21/24 (88%) | 13/15 (87%) | |
| Không thể hiện pain | 1/24 (4%) | 1/15 (7%) | qa-q12: hỏi chung, không kể vướng mắc |

Bị loại: 11 bài không phải `hoi_dap`, 14 bài không nói tạm hoãn, 5 bài có lý do khác (gia đình, sức khỏe), 2 bài không có lý do học tập, 1 bài là kiến nghị cử tri, 1 bài không có lời người hỏi.

## 4. Ví dụ cụ thể (mỗi ví dụ một ca, đã ẩn danh)

Các đoạn trích ngắn do script in ra. Trước khi chép vào bài nộp, người chọn phải mở URL đọc lại bài gốc.

1. qa-q02 (2026-11-11): sinh viên nợ môn kể *"Tôi đã nộp Giấy xác nhận sinh viên do nhà trường cấp cho Ban Chỉ huy Quân sự xã, tuy nhiên không được chấp nhận giải quyết chế độ tạm hoãn"*. [xaydungchinhsach](https://xaydungchinhsach.chinhphu.vn/co-duoc-tam-hoan-goi-nhap-ngu-voi-sinh-vien-no-mon-chua-tot-nghiep-dai-hoc-119261111152311351.htm)
2. qa-q04 (2026-10-08): giấy xác nhận các năm sau ghi đến 2027 nhưng địa phương *"không chấp nhận, vẫn yêu cầu đi khám sơ tuyển sức khoẻ"*. [baochinhphu](https://baochinhphu.vn/xac-dinh-thoi-gian-tam-hoan-goi-nhap-ngu-doi-voi-sinh-vien-102261008075934987.htm)
3. qa-q06 (2026-10-13): sinh viên liên thông nộp giấy xác nhận, cơ quan quân sự địa phương *"không chấp thuận với lý do chương trình đào tạo… là liên thông"*. [baochinhphu](https://baochinhphu.vn/hoc-lien-thong-co-tiep-tuc-duoc-tam-hoan-goi-nhap-ngu-102261013083602116.htm)
4. qa-q18 (2026-11-08): du học sinh đã gửi hộ chiếu và thẻ ngoại kiều, nhưng địa phương *"tiếp tục yêu cầu phải thực hiện việc quay video tại trường học"*. [baochinhphu](https://baochinhphu.vn/di-du-hoc-can-giay-to-gi-de-duoc-tam-hoan-nghia-vu-quan-su-10226110610542293.htm)
5. qa-q24 (2026-10-09): học sinh GDTX đã nộp giấy xác nhận và thẻ học sinh; *"nội dung trả lời của Ban Chỉ huy quân sự chưa rõ ràng"*. [baochinhphu](https://baochinhphu.vn/dang-hoc-chuong-trinh-giao-duc-thuong-xuyen-co-duoc-tam-hoan-goi-nhap-ngu-102261008075409699.htm)
6. qa-q26 (2025-12-29): sinh viên nợ môn đã nộp giấy xác nhận nợ môn theo yêu cầu, *"nhưng phường chưa tiếp nhận"*, còn đòi ghi khóa học khác với giấy trường cấp. [baochinhphu](https://baochinhphu.vn/sinh-vien-no-mon-co-duoc-tam-hoan-goi-nhap-ngu-102251225103853682.htm)
7. qa-q01 (2026-11-09): gia đình đã nộp giấy xác nhận còn đang học, nhưng Ban CHQS phường thông báo đã hết thời hạn khóa đào tạo, thuộc diện phải khám. [baochinhphu](https://baochinhphu.vn/thoi-gian-hoc-dai-hoc-keo-dai-co-duoc-tam-hoan-goi-nhap-ngu-102261106111312636.htm)

## 5. Giới hạn của data

- **Mẫu đã bị chọn lọc hai lần:** đây chỉ là những câu hỏi được cổng Chính phủ chọn đăng, rồi lại được người giữ dữ liệu chọn vào kho tri thức. Vì vậy 88% chỉ cho biết *trong các câu hỏi đã đăng* có bao nhiêu bài là tình huống biên hoặc vướng với địa phương, **không phải tỷ lệ trong toàn bộ sinh viên**.
- **Nhãn gắn bằng từ khóa:** có thể sót hoặc khớp nhầm. Đã kiểm tay cả 24 bài trong mẫu; 34 bài bị loại mới chỉ xem theo lý do loại.
- **Ghép ca trùng làm bằng tay** (9 cặp): người khác cần đọc lại từng cặp. Riêng q02 và q03 cùng chủ đề nợ môn nhưng q03 chỉ có tiêu đề, nên chưa ghép.
- **Không đo được tần suất và thời gian mất:** data cho biết người ta vướng ở đâu, không cho biết họ mất bao lâu hay xoay xở thế nào. Phần này kiểm lại bằng phỏng vấn ít nhất 3 sinh viên nam (nhóm nợ môn, liên thông, định du học), theo kịch bản `evidence/interviews/KICH-BAN.md` (câu 2–5).
- **Ẩn danh dữ liệu nguồn:** lúc chạy lần đầu, `answer` của qa-q02 còn họ tên đầy đủ của người hỏi và một bài khác còn tên riêng; script che tên khi in. Người giữ dữ liệu đã sửa `kb-nvqs/` ở PR #16. Chạy lại `count.py` sau khi sửa vẫn ra đúng các số ở mục 3.
