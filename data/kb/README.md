# data/kb → đã chuyển sang `kb-nvqs/`

Kho giả `data/kb/dieu41.json` đã bị xoá. Kho thật của nhóm nằm ở **[`kb-nvqs/`](../../kb-nvqs/)**:

- [`kb-nvqs/README.md`](../../kb-nvqs/README.md): cấu trúc, schema chunk, cách dùng cho MVP
- [`kb-nvqs/DATA_CARD.md`](../../kb-nvqs/DATA_CARD.md): nguồn, phạm vi, giới hạn, ẩn danh
- [`kb-nvqs/SOURCES.csv`](../../kb-nvqs/SOURCES.csv): số hiệu, ngày, hiệu lực, URL, sha256 từng văn bản

Code đọc kho qua `codebase/kb.py` (chunk luật `mvp` làm căn cứ, BM25 trên câu hỏi của bài hỏi đáp làm tham khảo) và công cụ `tra_cuu_can_cu` trong `codebase/tools.py`.
Sửa nội dung kho là việc của người làm dữ liệu; PDF / text gốc và bài hỏi đáp dạng `.md` không commit (xem `.gitignore`).
