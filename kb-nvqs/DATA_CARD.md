# DATA CARD – Knowledge Base Nghĩa vụ quân sự

## 1. Mục đích
Làm căn cứ cho chatbot hỗ trợ sinh viên đối chiếu điều kiện **tạm hoãn gọi nhập ngũ vì lý do học tập** (điểm g khoản 1 Điều 41 Luật NVQS) và hướng dẫn bước tiếp theo. Dữ liệu chỉ phục vụ tra cứu, không thay thế quyết định của cơ quan có thẩm quyền.

## 2. Nguồn

### 2.1. Văn bản quy phạm (mức tin cậy A, bản gốc)

| Văn bản | Ngày ban hành | Hiệu lực | Ghi chú |
|---|---|---|---|
| VBHN 133/2026/VBHN-LQ-VPQH – Luật NVQS hợp nhất | 18/9/2026 | Hợp nhất Luật 78/2015 + 48/2019 + 98/2025 + 14/2026 | Văn bản chính |
| Luật 98/2025/QH15 | 27/6/2025 | 01/7/2025 | Đã nằm trong VBHN 133 |
| TT 148/2018/TT-BQP – tuyển chọn, gọi nhập ngũ | 04/10/2018 | 20/11/2018 | Scan; Đ4–5 chép tay, đã áp sửa đổi |
| TT 68/2025/TT-BQP – sửa TT 148 | 03/7/2025 | 01/7/2025 | Scan |
| TT 173/2026/TT-BQP – Chương III sửa TT 148 | 28/10/2026 | 28/10/2026 | Không sửa Đ5 (tạm hoãn) |
| TT 105/2023/TT-BQP – tiêu chuẩn sức khỏe | 06/12/2023 | 01/01/2024 | Scan, chưa OCR, ngoài MVP |
| TT 106/2025/TT-BQP – sửa TT 105 | 30/9/2025 | — | Bản Công báo có chữ |
| NĐ 218/2025/NĐ-CP – xử phạt quốc phòng, cơ yếu | 05/8/2025 | 05/8/2025 | Dùng cho ca từ chối |

URL và sha256 của từng file nằm trong `SOURCES.csv`.

### 2.2. Văn bản trả lời của cơ quan nhà nước (mức B)
58 bài từ baochinhphu.vn, xaydungchinhsach.chinhphu.vn, chinhsachonline.chinhphu.vn (Bộ Quốc phòng / Cục Quân lực trả lời công dân và cử tri, 2022–11/2026), cộng bộ 14 tình huống của Sở Tư pháp TP Cần Thơ. Đây là cách hiểu chính thức nhưng **không phải văn bản quy phạm**.

## 3. Xử lý
- Trích text bằng `pdftotext -layout`. Bỏ chữ ký số, số trang, header Công báo.
- Tách theo Điều. Chú thích sửa đổi của VBHN được tách ra trường `ghi_chu_sua_doi`. Điều 41 được tách thêm theo từng điểm.
- Bài hỏi đáp: trích nội dung chính, bỏ link "Tham khảo thêm", tách câu hỏi và câu trả lời.
- **Ẩn danh:** tên người hỏi (sau "ông/bà/anh/chị/công dân/sinh viên…") được thay bằng `[ẩn danh]` bằng regex. Email và số điện thoại cũng được che. Địa danh cấp tỉnh còn giữ. Quy trình tự động, cần rà lại trước khi công khai repo.

## 4. Phạm vi và giới hạn
- Chỉ bao phủ đầy đủ lát cắt sinh viên tạm hoãn. Sức khỏe, hoàn cảnh gia đình và xử phạt chỉ có ở mức tham chiếu.
- **Chưa có:** VBHN 36/VBHN-BQP (hợp nhất TT 148), VBHN 88/VBHN-BQP, VBHN 75/VBHN-BQP (Nghị định 13/2016 hợp nhất), Quyết định 3360/QĐ-BQP về thủ tục hành chính, Hướng dẫn 6544/HD-BQP. vbpl.vn trả 404 cho các link tải.
- Không có định nghĩa quy phạm cho "thời gian một khóa đào tạo". Cách hiểu (tính từ ngày nhập học đến khi tốt nghiệp, không tính nợ môn/lưu ban, chỉ một khóa đầu tiên) lấy từ văn bản trả lời của BQP.
- Văn bản hết hiệu lực **không** đưa vào: TTLT 175/2011, TTLT 13/2013, TTLT 16/2016, NĐ 120/2013.
- Dữ liệu cập nhật đến 27/11/2026. Quy định có thể thay đổi sau ngày này.

## 5. Dữ liệu cá nhân
Không thu thập dữ liệu người dùng. Bài hỏi đáp công khai đã được ẩn danh tên người hỏi. Không lưu CCCD, địa chỉ hay hồ sơ y tế.
