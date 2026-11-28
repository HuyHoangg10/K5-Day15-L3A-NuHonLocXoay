# Web demo — Trợ lý NVQS

Giao diện web gọi **đúng agent có sẵn** (`codebase/agent.py` → `answer(text)`). Không sửa agent, tracing, `run.py`, eval hay cost. Chỉ dùng thư viện chuẩn Python 3.10+ (không cần `pip install`).

## Chạy
```
python web/server.py
```
Mở http://127.0.0.1:8765 (đổi cổng bằng biến môi trường `WEB_PORT`). Dừng: Ctrl+C. Chỉ nghe `127.0.0.1`.

Model: máy chủ đọc `.env` như `python run.py` (biến `MODEL_PROVIDER`, `MODEL_NAME`, `API_KEY`, `MODEL_BASE_URL`, `MODEL_MAX_TOKENS`; xem `docs/connect-model.md`). Khi `MODEL_PROVIDER` trống hoặc `fake`, web hiện nhãn "Model giả (chưa phải model thật)". Khóa chỉ nằm ở máy chủ.

## Kiểm thử
```
python -m unittest tests.test_web_server     # dùng STUB agent, không gọi model
python -m unittest discover -s tests
python run.py check
```

## Cách hoạt động
- `POST /api/chat` `{"message": "..."}` → `{"output", "nhan", "citations"}`. `output` là nguyên văn agent; `citations` ánh xạ đúng các id ở dòng `CAN_CU:` qua `kb.get_chunk` (không đoán thêm).
- `GET /api/sources` → danh mục nguồn chung từ `kb-nvqs/SOURCES.csv` (chỉ URL http/https hợp lệ).
- Một lúc chỉ một yêu cầu qua agent (`tracing` dùng trạng thái toàn cục); yêu cầu thứ hai chờ ≤3 giây rồi nhận "đang bận, thử lại".
- Không ghi log truy cập/nội dung ra đĩa; không trả traceback; chỉ nhận `Host` localhost (hoặc đúng 1 origin/host đầy đủ khi bật `WEB_ALLOW_ORIGIN=https://<domain>` cho tunnel).
- Tuỳ chọn ghi log thống kê ẩn danh sang Google Sheet qua Google Form: đặt `SHEET_LOG_URL=https://docs.google.com/forms/d/e/.../formResponse` trong `.env`. Câu hỏi luôn qua `agent.preprocess()` + `ai._redact()` để che PII/key trước khi gửi ngầm trong thread nền (không làm chậm chat; để trống thì tắt hoàn toàn).
- Lịch sử, mục đã lưu, giao diện, cỡ chữ lưu trong `localStorage` của trình duyệt; không gửi lên máy chủ.

## Giới hạn đã biết
- Mỗi câu hỏi được xử lý độc lập (agent không nhớ lượt trước); lịch sử chỉ để xem lại.
- Tình trạng hiệu lực hiện hành của các văn bản chưa được kiểm độc lập (ghi "chưa kiểm" trong UI).
- Chưa kiểm trên Safari/Firefox; chưa chạy kiểm thử trợ năng tự động.
