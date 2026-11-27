# Nối model thật — hướng dẫn nhanh cho nhóm NuHonLocXoay

Chi tiết chung của khung: [connect-model.md](connect-model.md). File này chỉ là phần nhóm đã làm trong `codebase/ai.py` (provider `deepseek` và `openai`).

1. Chép file mẫu: PowerShell `copy .env.example .env` (macOS/Linux `cp .env.example .env`). `.env` đã nằm trong `.gitignore`.
2. Mở `.env`, điền 3 dòng, **không dấu ngoặc kép, không thừa dấu cách**: `MODEL_PROVIDER=deepseek` · `MODEL_NAME=deepseek-flash` · `API_KEY=<key của bạn>`.
3. Thử nối model (gọi API thật đúng 1 lần, vài chục token): `python scripts/smoke_model.py`. Thấy `Nối model được` là xong. Key trống thì script chỉ in hướng dẫn, không báo lỗi.
4. Đổi sang OpenAI: trong `.env` đổi `MODEL_PROVIDER=openai`, `MODEL_NAME=gpt-4o-mini`, và **đổi `API_KEY` sang key của OpenAI** (mỗi nhà cung cấp một key). Thử nhanh không sửa `.env`: `python scripts/smoke_model.py --provider openai`.
5. Tuỳ chọn trong `.env` (để trống = mặc định): `MODEL_MAX_TOKENS` (mặc định 700) · `MODEL_BASE_URL` (đổi địa chỉ API, vd cổng trung gian tương thích OpenAI).
6. Mỗi lần gọi: `temperature=0`, tối đa 30 giây, thử lại **1 lần** (chờ 2 giây) khi lỗi mạng / HTTP 429 / 5xx. Sai key, hết số dư thì báo lỗi ngay. Prompt có chữ "JSON" thì `ai.py` tự bật chế độ ép JSON.
7. Với `deepseek-flash`, `ai.py` **tắt chế độ suy nghĩ** (`thinking: disabled`) để rẻ và ra JSON đều; token vào / ra lấy từ trường `usage` của phản hồi.
8. Lỗi hay gặp: `Thiếu API_KEY trong .env` (chưa điền) · `HTTP 401` (key sai) · `HTTP 402` hoặc `quota` (hết số dư) · `HTTP 429` kéo dài (gọi quá nhanh, thêm `--wait 4` sau `eval`).
9. ⚠️ **KHÔNG chạy `python run.py eval` hoặc `python run.py simulate` bằng model thật trước CP3**: chúng tạo lượt chấm thật (`eval/run-1.csv`), bị tính và tốn tiền. Chỉ thử bằng `eval --try` hoặc `scripts/smoke_model.py`.
10. ⚠️ **Không đưa key lên repo**: không commit `.env`, không dán key vào chat, code, slide, ảnh chụp. Trước khi commit chạy `git check-ignore -v .env` (phải in ra dòng của `.gitignore`) và `git diff --cached`. Lỡ lộ key thì thu hồi key trên trang nhà cung cấp ngay.
