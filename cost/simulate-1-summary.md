# Tóm tắt mô phỏng simulate-1@20261128-121215

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 8 | 1 | 8182 | 485 | 1.9 | 0.9 |
| dung_vua | 27 | 2 | 13532 | 805 | 3.4 | 1.4 |
| dung_nhieu | 15 | 4 | 26938 | 1520 | 6.8 | 2.8 |

Tỉ lệ đạt dùng để tính: 23/27 (85%) — lượt run-7@20261128-120720

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-7.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (500 người) | Chi phí / tháng — cơ sở (2.000 người) | Chi phí / tháng — cao (5.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-6.1-terra (vào 1.0 · ra 5.0 $/1M) | $0.0215 (≈ 549 ₫) | $0.0253 (≈ 645 ₫) | $0.0104 (≈ 264 ₫) | $31.55 (≈ 804.419 ₫) | $126.18 (≈ 3.217.676 ₫) | $315.46 (≈ 8.044.189 ₫) | $0.0631 (≈ 1.609 ₫) |
| gpt-4o-mini (vào 0.15 · ra 0.6 $/1M) | $0.0031 (≈ 79 ₫) | $0.0036 (≈ 92 ₫) | $0.0015 (≈ 38 ₫) | $4.52 (≈ 115.248 ₫) | $18.08 (≈ 460.991 ₫) | $45.20 (≈ 1.152.477 ₫) | $0.0090 (≈ 230 ₫) |
| gpt-4o (vào 2.5 · ra 10.0 $/1M) | $0.0514 (≈ 1.311 ₫) | $0.0604 (≈ 1.539 ₫) | $0.0247 (≈ 631 ₫) | $75.33 (≈ 1.920.795 ₫) | $301.30 (≈ 7.683.181 ₫) | $753.25 (≈ 19.207.952 ₫) | $0.1507 (≈ 3.842 ₫) |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.4) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-6.1-terra. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
- Tỷ giá: 1 USD = 25.500 ₫ (tỷ giá tham khảo USD/VND tại Việt Nam (tự ước tính) · xem 27/11/2026).
