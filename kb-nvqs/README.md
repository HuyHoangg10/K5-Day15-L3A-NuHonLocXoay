# Knowledge Base – Chatbot Nghĩa vụ quân sự (lát cắt: sinh viên tạm hoãn vì học tập)

Kho dữ liệu này được tải và kiểm tra ngày 27/11/2026. Mọi văn bản pháp luật đều lấy từ cổng chính thống (Công báo, datafiles.chinhphu.vn). Danh sách nguồn kèm mã hash nằm trong `SOURCES.csv`.

## Cấu trúc

```
kb-nvqs/
├── README.md                  ← file này
├── DATA_CARD.md               ← nguồn, phạm vi, giới hạn (nộp cho CP2)
├── SOURCES.csv                ← manifest: số hiệu, ngày, hiệu lực, URL, sha256
├── sources/
│   ├── pdf/                   ← 8 bản PDF gốc + bản .docx đối chiếu từ thuvienphapluat (*_tvpl.docx)
│   └── text/                  ← text trích từ PDF + bản chép tay TT 148 (Đ4–5) + toàn văn thuvienphapluat (*_tvpl.txt)
├── chunks/
│   ├── legal_chunks.jsonl     ← 179 chunk (165 theo Điều + 14 chunk Đ41 tách theo điểm/khoản), có metadata
│   └── qa_chunks.jsonl        ← 58 bài hỏi đáp/kiến nghị chính thức (đã ẩn danh), tách question/answer
├── qa/                        ← 58 bài dạng .md (đã ẩn danh) + INDEX.csv
└── benchmark/
    └── ground_truth_seed.csv  ← 18 ca mẫu có nhãn status + căn cứ + nguồn
```

## Dùng nhanh cho MVP

- **Nạp thẳng vào context LLM:** lọc `legal_chunks.jsonl` với `"mvp": true` (23 chunk, khoảng 17k ký tự). Gồm Đ4, Đ10, Đ30, Đ41 (cả điều và từng điểm), Đ42 Luật NVQS; Đ4–5 TT 148 (bản hiện hành); Đ9–10 NĐ 218/2025.
- **Ví dụ minh họa / few-shot:** `qa_chunks.jsonl`, lọc `loai == "hoi_dap"`.
- **Benchmark:** mở rộng `ground_truth_seed.csv` lên 25 ca. Cột `status_ky_vong` gồm: `eligible_for_review`, `not_eligible`, `need_more_information`, `refuse`, `out_of_scope`.

```python
import json
law = [json.loads(l) for l in open("chunks/legal_chunks.jsonl", encoding="utf-8")]
mvp = [c for c in law if c["mvp"]]
context = "\n\n".join(f"[{c['id']}] {c['so_hieu']} – {c['text']}" for c in mvp)
```

Yêu cầu chatbot trích `id` chunk (ví dụ `vbhn133-d41-k1-g`) để chấm tự động metric "trích dẫn đúng".

## Schema `legal_chunks.jsonl`

| Trường | Ý nghĩa |
|---|---|
| `id` | `<doc>-d<điều>[-k<khoản>-<điểm>]` |
| `so_hieu`, `ten_van_ban`, `loai` | Số hiệu, tên, loại văn bản |
| `dieu`, `khoan`, `diem`, `tieu_de` | Vị trí, tiêu đề điều |
| `text` | Nội dung (đã bỏ số chú thích, nối dòng) |
| `ghi_chu_sua_doi` | Chú thích của VBHN: điều/khoản này được sửa bởi luật nào, hiệu lực khi nào |
| `ngay_ban_hanh`, `hieu_luc_tu`, `nguon`, `tin_cay`, `ngay_kiem_tra` | Metadata |
| `mvp` | `true` nếu thuộc lát cắt MVP |

## Cảnh báo

- Text trích tự động từ PDF có thể lẫn lỗi ngắt dòng hoặc chú thích. Trước khi demo, đối chiếu lại các chunk `mvp` với PDF.
- TT 148/2018 và TT 68/2025 là bản scan, nên Đ4–5 TT 148 được **chép tay**. Ngày 27/11/2026 đã đối chiếu với 36/VBHN-BQP: khớp nội dung.
- TT 105/2023 (105 trang scan) chưa được OCR. Đã có bản chữ từ thuvienphapluat trong `sources/text/`, chưa tách chunk.
- Bài hỏi đáp là **văn bản trả lời của cơ quan nhà nước, không phải văn bản quy phạm**. Không trích chúng như "căn cứ pháp lý".
