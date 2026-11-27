# Rào chắn chống commit key — `scripts/check_secrets.py`

Quét **offline** (không gọi mạng) để không lỡ đưa key / dữ liệu cá nhân lên GitHub. Không bao giờ in giá trị đầy đủ
(chỉ 4 ký tự đầu + độ dài).

## Chạy tay

```
python scripts/check_secrets.py            # quét mọi file git đang theo dõi
python scripts/check_secrets.py --staged   # quét nội dung SẮP commit (sau git add)
python scripts/check_secrets.py --strict   # coi cả cảnh báo dữ liệu cá nhân là chặn
```

Mã thoát: `0` sạch (có thể còn CẢNH BÁO) · `1` có chuỗi giống key → **không commit** · `2` lỗi chạy (vd không phải repo git).

| Mức | Phát hiện |
|---|---|
| CHẶN | `sk-…` (OpenAI / DeepSeek / Anthropic `sk-ant-…`), `Bearer <token>`, `ghp_…` / `github_pat_…`, `AKIA…`, `AIza…`, `xox…-`, khóa riêng PEM, chuỗi dài ngẫu nhiên gán cho biến tên *KEY* / *TOKEN* / *SECRET* / *PASSWORD*, file `.env` |
| CẢNH BÁO | email, số điện thoại Việt Nam, CCCD 12 số |

**Được phép** (không báo):
- key GIẢ trong `tests/` có dấu hiệu giả rõ ràng: `TESTKEY`, `KHONGPHAIKEY`, `0123456789`, `abcdef`, `fake`, `dummy`… (vd `sk-TESTKEY-…`). Cùng chuỗi đó nằm ngoài `tests/` vẫn bị chặn.
- email miền ví dụ (`example.com`, `users.noreply.github.com`…).
- dòng có chú thích `check-secrets: allow` — dùng dè dặt, người review phải thấy lý do.

Cảnh báo hiện có trong repo đều là dữ liệu mẫu của test (số điện thoại, CCCD, email giả để kiểm bước che) và hai chú
thích trong code; không phải dữ liệu thật.

## Cài hook (mỗi máy một lần — script KHÔNG tự cài)

```
git config core.hooksPath .githooks
```

Từ đó mỗi `git commit` chạy `python scripts/check_secrets.py --staged`; có chuỗi bị CHẶN thì commit dừng lại.
Gỡ: `git config --unset core.hooksPath`. Trên Windows, Git for Windows chạy được hook `sh` này (cần `python` hoặc `py`
trong PATH; thiếu thì hook chỉ nhắc, không chặn).

## Nếu lỡ commit key thật

1. **Thu hồi key ngay** trên trang nhà cung cấp (xóa commit KHÔNG đủ: key đã nằm trong lịch sử / bản sao).
2. Tạo key mới, chỉ đặt trong `.env` (đã có trong `.gitignore`: `.env`, `.env.*`, trừ `.env.example`).
3. Báo nhóm để không ai dùng key cũ.
