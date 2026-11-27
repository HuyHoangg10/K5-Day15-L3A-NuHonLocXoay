# Data card — dữ liệu bản chạy thử dùng

> Điền ở guide bước 2.4 (bản đầu ở CP2, đủ ở CP3). Ôn lại: ngày 6 · lab ngày 6. Chấm ở rubric R4.
> Một trang. Mỗi dataset một mục. Dữ liệu chạy thử (bài mẫu, thông báo mẫu, đoạn transcript…) để trong thư mục `data/` này.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Kho căn cứ pháp lý (Luật Nghĩa vụ quân sự, Điều 41)

> **HIỆN LÀ KHO GIẢ.** Mọi đoạn ghi `[CHỜ VĂN BẢN GỐC vbpl.vn]`; mã (`D41.K1.a`…), chủ đề, ngày, đường dẫn đều là chỗ giữ chỗ để dựng khung, **không phải nội dung luật**. Người A thay bằng văn bản gốc (hướng dẫn: `data/kb/README.md`).

| | |
|---|---|
| Dùng để làm gì | nguồn cho công cụ `tra_dieu_luat` · kiểm mã điều khoản ở bước 7 của agent · căn cứ để người A và D viết câu thử `thuong` có `expected` từ luật gốc |
| Từ đâu | văn bản gốc trên **vbpl.vn** (cổng văn bản pháp luật). Hiện: nhóm tự viết chỗ giữ chỗ, chưa lấy văn bản thật |
| Xử lý những bước gì | chia theo **điều / khoản / điểm**, mỗi đoạn một mục `{code, van_ban, hieu_luc, ngay_tai, url, text, chu_de}`; chép nguyên văn, không tóm tắt; ghi hiệu lực và ngày tải · ẩn danh: không có dữ liệu cá nhân (chưa có script, chia bằng tay) |
| Số dòng / số đoạn | 4 đoạn giả (`D41.K1.a`, `D41.K1.b`, `D41.K1.c`, `D41.K2`) · file `data/kb/dieu41.json` |
| Phiên bản / ngày lấy | chưa có — `ngay_tai` ghi `[CHỜ]` |
| Nhãn | `synthetic` (kho giả, `la_kho_gia: true`) → đổi thành thật khi văn bản gốc vào kho |
| Giới hạn | kho giả không có nội dung luật nên mọi kết quả `co_can_cu_xem_xet` hiện chỉ để thử luồng. Khi thật: chỉ phủ Điều 41 (và văn bản nhóm đưa thêm), có thể thiếu văn bản hướng dẫn, văn bản sửa đổi; hiệu lực có thể thay đổi sau ngày tải nên phải ghi ngày tải |

**Data `synthetic` (nhóm tự sinh):** kho giả viết tay bởi nhóm (người C), không sinh bằng model, không có seed. 4 đoạn viết tay, đúng cấu trúc, không chứa nội dung luật thật; chưa có người kiểm độc lập (không cần cho kho giả). Data tự dựng **không phải bằng chứng pain**.

## Dataset 2 · Bộ câu thử `eval/benchmark.csv`

| | |
|---|---|
| Dùng để làm gì | đo agent theo `eval/metric_spec.yaml` |
| Từ đâu | nhóm tự viết (`tu_viet`): 10 câu không cần luật (5 tấn công / lách luật / chèn lệnh, 2 ngoài phạm vi, 2 nghe nhạy cảm nhưng hợp lệ, 1 thiếu dữ kiện). Còn thiếu: câu `thuong` có `expected` từ luật gốc; ≥1/3 câu từ người dùng / data thật |
| Xử lý những bước gì | không có dữ liệu cá nhân thật trong câu thử |
| Số dòng / số đoạn | 10 |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | thật (viết tay) |
| Giới hạn | chưa có câu từ người dùng thật; nhãn mong đợi của câu `thuong` phải chờ kho luật thật |
