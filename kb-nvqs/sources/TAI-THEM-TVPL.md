# Tải thêm từ thuvienphapluat.vn — 2026-11-27

Lấy theo bảng "Bắt buộc / Nên có" (mục 1) và mục 7 "Việc còn phải làm tay" của tài liệu *Nguồn dữ liệu chatbot Nghĩa vụ quân sự*.

- **Nguồn:** thuvienphapluat.vn (TVPL) là nguồn thứ cấp, **mức B**.
- **Nơi lưu:**
  - `pdf/*_tvpl.docx`: file .docx tải về từ TVPL.
  - `text/*_tvpl.txt`: toàn văn lấy từ trang web.
  - `text/*_tvpl_docx.txt`: chữ trích từ file .docx.
  - Cả `pdf/` và `text/` đều bị `.gitignore`.
- **Việc của người giữ data:** chưa sửa `SOURCES.csv`, `legal_chunks.jsonl` hay `DATA_CARD.md`. Đề xuất cập nhật ở mục 4.

## 1. Đối chiếu danh sách văn bản (tài liệu nguồn, mục 1)

| Văn bản | Nhóm | Trước khi tải | Đã tải từ TVPL | Ghi chú |
|---|---|---|---|---|
| VBHN 133/2026/VBHN-LQ-VPQH | Bắt buộc | PDF Công báo + chunk | trang + docx | 62 Điều |
| TT 148/2018/TT-BQP (bản gốc) | Bắt buộc | PDF scan, Đ4–5 chép tay | trang + docx | 13 Điều |
| VBHN 36/VBHN-BQP (TT 148 + TT 68) | Bắt buộc | chưa có | trang + docx | 22/08/2025. **Chưa gồm TT 173/2026** |
| TT 68/2025/TT-BQP | Bắt buộc | PDF scan | trang + docx | |
| TT 173/2026/TT-BQP | Bắt buộc | PDF Công báo + chunk | **chỉ trang** (28 Điều) | TVPL báo *"Không tìm thấy file đính kèm trên server"* cho bản .docx. Toàn văn trên trang đã đủ, PDF Công báo đã có trong kho |
| TT 105/2023/TT-BQP | Nên có | PDF scan, chưa OCR | trang + docx | 34 Điều + phụ lục; **lần đầu kho có bản chữ** |
| TT 106/2025/TT-BQP | Nên có | PDF Công báo + chunk | trang + docx | |
| VBHN 88/VBHN-BQP (TT 105 + 106) | Nên có | chưa có | trang + docx + **Phụ lục I–VI** | Phụ lục nằm trong file `Phu luc.doc` nhúng trong docx (cần đăng nhập); đã trích chữ ra `text/vbhn88-2025-VBHN-BQP_phu-luc_tvpl.txt` |
| VBHN 75/VBHN-BQP (NĐ 13/2016) | Nên có | chưa có | trang + docx | 25 Điều |
| NĐ 218/2025/NĐ-CP | Nên có | PDF Công báo + chunk | trang + docx | 69 Điều |
| Luật 14/2026/QH16 | Nên có | trong VBHN 133 | trang + docx | 10 Điều |
| Luật 98/2025/QH15 | Nên có | PDF + trong VBHN 133 | trang + docx | |
| QĐ 3360/QĐ-BQP | Nên có | chưa có | trang + docx | 7 thủ tục NVQS trực tuyến, **không có thủ tục tạm hoãn** |
| HD 6544/HD-BQP | Nên có | chưa có | trang + docx | Tuyển quân 2026. TVPL **chưa có** hướng dẫn cấp Bộ cho năm 2027, mới có kế hoạch cấp tỉnh |
| TTLT 175/2011, TTLT 13/2013, TTLT 16/2016, NĐ 120/2013, VBHN 80/2025 | Không dùng | — | không tải | Hết hiệu lực hoặc đã được thay thế |

**Mục 7 "Việc còn phải làm tay"** của tài liệu nguồn:

| Việc | Kết quả |
|---|---|
| Nguyên văn Đ5 TT 148 (hoặc 36/VBHN-BQP) | Xong |
| Nguyên văn Đ9 NĐ 218/2025 | Xong: gian dối 30–40 triệu (k5 a), không chấp hành lệnh gọi khám 50–75 triệu (k6) |
| 88/VBHN-BQP và 75/VBHN-BQP | Xong, kèm phụ lục của 88 |
| Bài qdnd về nhiều khóa đào tạo | Đã tìm: <https://www.qdnd.vn/quoc-phong-an-ninh/tin-tuc/tam-hoan-nhap-ngu-khong-ap-dung-cho-nhieu-khoa-dao-tao-1063689> (07/11/2026). Là bài đăng lại của Báo Điện tử Chính phủ, cùng ca với `qa-q23` / `qa-q09`, nên không thêm. Bài còn lộ họ tên người hỏi nên không lưu bản sao |
| Chạy thử 3 đối thủ; phỏng vấn | Không phải dữ liệu tải về, ngoài phạm vi lần này |

## 2. Đối chiếu từng chunk trong `chunks/legal_chunks.jsonl` với TVPL

So từng từ theo Điều, sau khi bỏ chú thích "(sửa bởi …)" kho tự thêm, số chú thích `[n]`, và tiêu đề Chương/Mục.

| Văn bản | Số Điều so | Khớp ≥ 99% |
|---|---|---|
| VBHN 133/2026 | 62 | 58 |
| NĐ 218/2025 | 69 | 68 |
| TT 173/2026 | 28 | 27 |
| TT 106/2025 | 4 | 3 |
| TT 148 Đ4–5 (chép tay) so với 36/VBHN-BQP | 2 | Đ5 khớp 100% nội dung (chỉ khác dấu câu); Đ4 khác đúng ở các chỗ TT 173 đã sửa |

- **Tất cả chunk `mvp: true` khớp ≥ 99%.**
- Các chỗ lệch còn lại đều là **lỗi trích PDF của kho**, không phải thiếu nội dung:
  - `vbhn133-d3`, `vbhn133-d18`, `vbhn133-d20`: số chú thích dính vào chữ ("dân2", "dân15"). Lời chú thích của VBHN (vd. "Câu dẫn này được sửa đổi… Luật số 98…") lọt vào thân điều.
  - `vbhn133-d62`, `nd218-d69`, `tt173-d28`, `tt106-d4` là Điều cuối của mỗi văn bản: chunk dính cả nơi nhận, chữ ký và phụ lục.
  - `tt148-d4`: dòng "(phần còn lại của khoản 4 nằm ở trang 3 bản scan, chưa chép)" là thừa. Khoản 4 chỉ có điểm a, b và đã chép đủ.

## 3. Không lấy được / bổ sung tay

- **TT 173/2026: không có file .docx** (máy chủ TVPL báo không có file đính kèm). Toàn văn trên trang thì đã lấy đủ.
- **Bổ sung tay:** người dùng lưu thêm `pdf/tt173-2026-TT-BQP_luatvietnam-in-web.pdf`.
  - **Bản gốc là gì:** bản in trang web luatvietnam.vn bằng Firefox (Skia/PDF), 26 trang, tạo 27/11/2026. Không phải bản ký số. Nguồn thứ cấp, **mức C**.
  - **Text:** `text/tt173-2026-TT-BQP_luatvietnam.txt` (đã bỏ đầu/chân trang trình duyệt).
  - **Đối chiếu:** đủ 28 Điều kèm phụ lục mẫu. Nội dung khớp từng từ với chunk trong kho (bản Công báo) và với bản TVPL, kể cả Điều 6 (sửa Đ4 TT 148, dùng cho MVP). Hai chỗ lệch do công cụ cắt, không phải do nội dung: Điều 9 trích nguyên văn "Điều 8…" ở đầu dòng; chunk `tt173-d28` dính phụ lục.
  - **Kết luận:** không bổ sung nội dung mới. Chỉ dùng làm bản đối chiếu thứ ba; **không thay** PDF Công báo trong `SOURCES.csv`.

## 4. Đề xuất cho người giữ data

1. Thêm các file ở mục 5 vào `SOURCES.csv`, cột nguồn ghi thuvienphapluat (mức B).
2. `tt148-d4` / `tt148-d5`: bỏ dòng "phần còn lại của khoản 4…". Đổi `tin_cay` thành "A (chép tay, đã đối chiếu 36/VBHN-BQP)".
3. Làm sạch `vbhn133-d3`, `vbhn133-d18`, `vbhn133-d20`: bỏ số và lời chú thích lọt vào thân. Với Điều cuối mỗi văn bản, cắt phần nơi nhận, chữ ký, phụ lục.
4. `qa_chunks.jsonl` / `qa/`: `answer` của qa-q02 còn họ tên đầy đủ người hỏi, qa-q04 còn tên riêng. Cần ẩn danh.
5. TT 105/2023 nay đã có bản chữ, cùng Phụ lục I của 88/VBHN-BQP. Nếu cần tra phân loại sức khỏe thì tách chunk (ngoài MVP: kết luận sức khỏe do Hội đồng khám sức khỏe đưa ra).

## 5. Manifest (sha256)

```
file,bytes,sha256
pdf/vbhn133-2026-VBHN-LQ-VPQH_tvpl.docx,28166,a0d84b85c07954ee1efc9ff8e041caa93fe3788e281f891ad7c9a1a4348031d8
pdf/tt148-2018-TT-BQP_tvpl.docx,13537,2308867d111cf695d40b67b479a632d014758d391395b4cdf67f7c3063fe2244
pdf/vbhn36-2025-VBHN-BQP_tvpl.docx,14807,c99500c099e3b57d602658a2be88e2a498264843f0b72910fcf4d67182402306
pdf/tt68-2025-TT-BQP_tvpl.docx,12225,916283fd30d5f5455e1a36c237d7f80be9ad280be3d8efa0971212755e381d11
pdf/tt105-2023-TT-BQP_tvpl.docx,183362,018468af037efccb278f56bdefa7c5da5d8a924b384906ccee29a45bae3c44b2
pdf/tt106-2025-TT-BQP_tvpl.docx,86201,dd218928530a30a9e28d1b81e22321692a7b1331343dee5c1ed3501ab82137f2
pdf/vbhn88-2025-VBHN-BQP_tvpl.docx,503400,135c242eb5f879af18de37ee7118b43f70d67d96a1d1ea932f41c5eec2d631b0
pdf/vbhn75-2025-VBHN-BQP_tvpl.docx,14998,33dd9d2d6aaed22f520cea52b131560b76df330abe60b4b11bb70384e56f610b
pdf/nd218-2025-ND-CP_tvpl.docx,36552,537e3adf3372f9f6908040615e5e99316f4d891bc112ff517095e6b3fed717ac
pdf/luat14-2026-QH16_tvpl.docx,14663,bc5ad518aae8f9fec46d2f7f6031d66a92870de5f5e3a848af507d59eec551e3
pdf/luat98-2025-QH15_tvpl.docx,30472,eab3e77ff0aaa8a642c65674d418d23c7833ad259dfca650c0a5b72076ee1456
pdf/qd3360-2026-QD-BQP_tvpl.docx,8611,db9ccee3337c051a59963ae4f454a805a6574bf0228b2fdad3eeca9a4cfa7410
pdf/hd6544-2025-HD-BQP_tvpl.docx,14645,69bf90d80c0b30bb20d90175f44b12cfc43f7ffa10935fe27fc89d094c3a240d
text/vbhn133-2026-VBHN-LQ-VPQH_tvpl.txt,78567,b0a50aec3cec0417ca7e278e92a1c6df3daed41338ef9f94a12471461a4002e4
text/tt148-2018-TT-BQP_tvpl.txt,25259,3c498815b5baab850394ed569358c9f255a417e45b4403ba7b60ef2da089c203
text/vbhn36-2025-VBHN-BQP_tvpl.txt,33478,fab60c882635ea9c53566bf25bca610b6bab4c3ee28e2c58621c6eabfa1e8512
text/tt68-2025-TT-BQP_tvpl.txt,19255,095ec06e9dbf898fbeb6265ddd68bdc45b2db9ab977eb47de711941b3074cda4
text/tt173-2026-TT-BQP_tvpl.txt,57248,3a385958606ea43802e4e7e26f58e244cc7baf8fab1af1feef3d4c47955fffc6
text/tt105-2023-TT-BQP_tvpl.txt,228210,09332f401c9b07d4adc3691a2b31fb07b44e6106c3246a8a78c11d986cbbc39a
text/tt106-2025-TT-BQP_tvpl.txt,80633,0b3a00283618f6092d293f478b529e6c8b6616dc1f26f8b1746b365ab406187f
text/vbhn88-2025-VBHN-BQP_tvpl.txt,98590,80ee0659c43040bc7dd36c0304d2522498195c93b06ccc10611909c3f7afecbe
text/vbhn88-2025-VBHN-BQP_phu-luc_tvpl.txt,161536,dd76d0b73fcc3d333663894a92e63f384d8869c325391495b4150da351d93028
text/vbhn75-2025-VBHN-BQP_tvpl.txt,42339,df3cf78902119289b119344520fac95f48b31bb6fa97294d850d88430a6b275d
text/nd218-2025-ND-CP_tvpl.txt,139637,069741148debfe38896da892a05a07ce2f84db194673dbddcd3c2158acd2f3e3
text/luat14-2026-QH16_tvpl.txt,24092,648f4ccfdb844616c1d8446183b929fc0b4a3edafb2717e3e7f9981b5a373417
text/luat98-2025-QH15_tvpl.txt,76682,9d6c66ea0a55ec7fd00d3daae54a672a9a984d83238f876d2775b3bc55f5694c
text/qd3360-2026-QD-BQP_tvpl.txt,6200,73ce4043af7a3a307a76d6bf2c6077124713c9ef421e1872647154d5fd7daa13
pdf/tt173-2026-TT-BQP_luatvietnam-in-web.pdf,563251,e89caa143167268d6f763860de418043488a6049bf833263f43c9b08b0f74356
text/hd6544-2025-HD-BQP_tvpl.txt,21351,b8b2e90d685987a42a2bfc6dec15aa05984ace39234ab82754a345fa50254a72
```
