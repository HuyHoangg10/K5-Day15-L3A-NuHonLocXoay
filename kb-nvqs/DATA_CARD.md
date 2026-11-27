# DATA CARD – Knowledge Base Nghĩa vụ quân sự

## 1. Mục đích
Làm căn cứ cho chatbot hỗ trợ sinh viên đối chiếu điều kiện **tạm hoãn gọi nhập ngũ vì lý do học tập** (điểm g khoản 1 Điều 41 Luật NVQS) và hướng dẫn bước tiếp theo. Dữ liệu chỉ phục vụ tra cứu, không thay thế quyết định của cơ quan có thẩm quyền.

## 2. Nguồn

### 2.1. Văn bản quy phạm (mức tin cậy A, bản gốc)

| Văn bản | Ngày ban hành | Hiệu lực | Ghi chú |
|---|---|---|---|
| VBHN 133/2026/VBHN-LQ-VPQH – Luật NVQS hợp nhất | 18/9/2026 | Hợp nhất Luật 78/2015 + 48/2019 + 98/2025 + 14/2026 | Văn bản chính |
| Luật 98/2025/QH15 | 27/6/2025 | 01/7/2025 | Đã nằm trong VBHN 133 |
| TT 148/2018/TT-BQP – tuyển chọn, gọi nhập ngũ | 04/10/2018 | 20/11/2018 | Scan; Đ4–5 chép tay, đã áp sửa đổi; đã đối chiếu 36/VBHN-BQP (khớp nội dung) |
| TT 68/2025/TT-BQP – sửa TT 148 | 03/7/2025 | 01/7/2025 | Scan |
| TT 173/2026/TT-BQP – Chương III sửa TT 148 | 28/10/2026 | 28/10/2026 | Không sửa Đ5 (tạm hoãn) |
| TT 105/2023/TT-BQP – tiêu chuẩn sức khỏe | 06/12/2023 | 01/01/2024 | Bản gốc scan; đã có bản chữ từ thuvienphapluat (mục 2.3), chưa tách chunk, ngoài MVP |
| TT 106/2025/TT-BQP – sửa TT 105 | 30/9/2025 | — | Bản Công báo có chữ |
| NĐ 218/2025/NĐ-CP – xử phạt quốc phòng, cơ yếu | 05/8/2025 | 05/8/2025 | Dùng cho ca từ chối |

URL và sha256 của từng file nằm trong `SOURCES.csv`.

### 2.3. Bản đối chiếu từ nguồn thứ cấp (mức B, không làm căn cứ)
Tải ngày 27/11/2026 từ thuvienphapluat.vn, gồm bản .docx và toàn văn trang:
- VBHN 133/2026, TT 148/2018, VBHN 36/VBHN-BQP (TT 148 + TT 68), TT 68/2025.
- TT 173/2026: chỉ toàn văn trang vì TVPL không có .docx; có thêm bản in trang luatvietnam.vn (mức C).
- TT 105/2023, TT 106/2025, VBHN 88/VBHN-BQP (TT 105 + 106, kèm Phụ lục I–VI).
- VBHN 75/VBHN-BQP (NĐ 13/2016), NĐ 218/2025, Luật 14/2026, Luật 98/2025, QĐ 3360/QĐ-BQP, HD 6544/HD-BQP.

File lưu ở `sources/` (không commit), sha256 trong `SOURCES.csv`.

Kết quả đối chiếu với `legal_chunks.jsonl`:
- 23/23 chunk `mvp` khớp nguyên văn. Các chunk điểm Đ41 chỉ khác ở tiền tố "Điều 41 khoản … – điểm …" do kho thêm.
- Đ4–5 TT 148 chép tay khớp nội dung với 36/VBHN-BQP. Đ4 khác đúng ở các chỗ TT 173/2026 đã sửa.
- Đã sửa lỗi trích PDF ngoài `mvp` (không đổi id, không đổi nội dung quy phạm):
  - `vbhn133-d3`, `vbhn133-d18`, `vbhn133-d20`: bỏ số chú thích dính chữ ("nhân dân2.", "trách nhiệm:17") và lời chú thích lọt vào thân điều.
  - `vbhn133-d62`, `nd218-d69`, `tt173-d28`, `tt106-d4`: cắt phần nơi nhận, chữ ký và phụ lục. Phụ lục mẫu biểu của TT 173 và TT 106 vẫn còn trong `sources/text/`.
  - `ghi_chu_sua_doi` của `vbhn133-d3`, `d18`, `d20`, `d61`, `d62` được gán lại theo vị trí dấu chú thích trong văn bản. Trước đây chú thích của Đ15–Đ18 bị gán nhầm sang Đ3, Đ61, Đ62. Kho vẫn gộp các chú thích trùng nhau.
  - Sau khi sửa, 163/163 chunk theo Điều của VBHN 133, NĐ 218, TT 173, TT 106 khớp ≥ 99% với bản đối chiếu.

### 2.2. Văn bản trả lời của cơ quan nhà nước (mức B)
58 bài từ baochinhphu.vn, xaydungchinhsach.chinhphu.vn, chinhsachonline.chinhphu.vn (Bộ Quốc phòng / Cục Quân lực trả lời công dân và cử tri, 2022–11/2026), cộng bộ 14 tình huống của Sở Tư pháp TP Cần Thơ. Đây là cách hiểu chính thức nhưng **không phải văn bản quy phạm**.

## 3. Xử lý
- Trích text bằng `pdftotext -layout`. Bỏ chữ ký số, số trang, header Công báo.
- Tách theo Điều. Chú thích sửa đổi của VBHN được tách ra trường `ghi_chu_sua_doi`. Điều 41 được tách thêm theo từng điểm.
- Bài hỏi đáp: trích nội dung chính, bỏ link "Tham khảo thêm", tách câu hỏi và câu trả lời.
- **Ẩn danh:** tên người hỏi (sau "ông/bà/anh/chị/công dân/sinh viên…") được thay bằng `[ẩn danh]` bằng regex. Email và số điện thoại cũng được che. Địa danh cấp tỉnh còn giữ.
- **Rà tay ngày 27/11/2026:**
  - Regex đã sót: họ tên đầy đủ (qa-q02, dạng "Tôi là …"), tên một chữ (qa-q04), ngày sinh đầy đủ (qa-q29), địa chỉ cấp thôn/xã (qa-q39, qa-q41). Đã thay bằng `[ẩn danh]`, giữ năm sinh và tỉnh.
  - Quét lại `qa_chunks.jsonl`, `qa/INDEX.csv`, `benchmark/ground_truth_seed.csv`: không còn tên người hỏi, ngày sinh, địa chỉ chi tiết, số điện thoại, email. Tên còn lại là của người ký văn bản (công khai).
  - Bản `qa/*.md` (không commit) cần sửa tương ứng.

## 4. Phạm vi và giới hạn
- Chỉ bao phủ đầy đủ lát cắt sinh viên tạm hoãn. Sức khỏe, hoàn cảnh gia đình và xử phạt chỉ có ở mức tham chiếu.
- **Chưa tách chunk:** VBHN 36/VBHN-BQP, VBHN 88/VBHN-BQP, VBHN 75/VBHN-BQP, QĐ 3360/QĐ-BQP, HD 6544/HD-BQP. Đã có toàn văn từ thuvienphapluat (mục 2.3) để đối chiếu.
  - QĐ 3360 gồm 7 thủ tục NVQS trực tuyến, không có thủ tục tạm hoãn.
  - Chưa có hướng dẫn tuyển quân năm 2027 cấp Bộ.
- Không có định nghĩa quy phạm cho "thời gian một khóa đào tạo". Cách hiểu (tính từ ngày nhập học đến khi tốt nghiệp, không tính nợ môn/lưu ban, chỉ một khóa đầu tiên) lấy từ văn bản trả lời của BQP.
- Văn bản hết hiệu lực **không** đưa vào: TTLT 175/2011, TTLT 13/2013, TTLT 16/2016, NĐ 120/2013.
- Dữ liệu cập nhật đến 27/11/2026. Quy định có thể thay đổi sau ngày này.

## 5. Dữ liệu cá nhân
Không thu thập dữ liệu người dùng. Bài hỏi đáp công khai đã được ẩn danh tên người hỏi. Không lưu CCCD, địa chỉ hay hồ sơ y tế.
