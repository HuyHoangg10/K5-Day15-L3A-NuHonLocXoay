# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): ≥3 kiểu — tỉ lệ, số phiên / người / tháng, số lượt hỏi / phiên. Nguồn: khảo sát nhóm 27/11/2026 — dùng ít 24% (1 phiên/tháng, 1 câu/phiên) · dùng vừa 52% (3 phiên, 2 câu) · dùng nhiều 24% (4 phiên, 4 câu); chi tiết từng dòng ở `source` trong `cost/personas.yaml`.
- **Số người dùng thật** 3 kịch bản: thấp 500 · cơ sở 2.000 · cao 5.000 người/tháng. Nguồn: quy mô thí điểm cho sinh viên nam 18–27 tuổi tại 1–3 trường trong mùa khám tuyển *(tự ước tính)*.
- **Giá** ≥2 mức model (từ `further-reading/model-prices.md` của repo đề, có link + ngày xem): `gpt-6.1-terra` $1.00 vào / $5.00 ra mỗi 1M token (model bản nộp; [OpenAI pricing](https://developers.openai.com/api/docs/pricing), Standard, xem 28/11/2026) · `gpt-4o-mini` $0.15 / $0.60 (rẻ) · `gpt-4o` $2.50 / $10.00 (mạnh) — cùng trang, xem 27/11/2026.
- **Tỉ lệ đạt** dùng để tính: 23/27 (85%) — lượt `run-7@20261128-120720` (lượt 2 chính thức)
- Đo token trên model `gpt-6.1-terra`, tính giá `gpt-6.1-terra`, `gpt-4o-mini` và `gpt-4o` (hai model sau khác bộ tách token nên số chỉ để so sánh mức giá).

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-1.csv` · run ID `simulate-1@20261128-121215` · 50 phiên (0 lỗi) · seed 42

Token thật đo trên `gpt-6.1-terra` (từ `usage` của API):

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 8 | 1 | 8182 | 485 | 1.9 | 0.9 |
| dung_vua | 27 | 2 | 13532 | 805 | 3.4 | 1.4 |
| dung_nhieu | 15 | 4 | 26938 | 1520 | 6.8 | 2.8 |

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp (500) | / tháng — cơ sở (2.000) | / tháng — cao (5.000) | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| **gpt-6.1-terra** (bản nộp) | $0.0215 (≈ 549 ₫) | $0.0253 (≈ 645 ₫) | $31.55 (≈ 0,8 tr ₫) | $126.18 (≈ 3,2 tr ₫) | $315.46 (≈ 8,0 tr ₫) | $0.0631 (≈ 1.609 ₫) |
| gpt-4o-mini (rẻ) | $0.0031 (≈ 79 ₫) | $0.0036 (≈ 92 ₫) | $4.52 | $18.08 | $45.20 | $0.0090 (≈ 230 ₫) |
| gpt-4o (mạnh) | $0.0514 (≈ 1.311 ₫) | $0.0604 (≈ 1.539 ₫) | $75.33 | $301.30 | $753.25 | $0.1507 (≈ 3.842 ₫) |

Nguồn bảng: `cost/simulate-1-summary.md` (sinh tự động). Chi phí / câu hỏi đạt với terra: $0.0104 (≈ 264 ₫). Tỷ giá 25.500 ₫/USD *(tự ước tính)*.

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): 2–3 lần tra × 5–15 phút = khoảng 10–45 phút tra cứu / người trong tháng gọi khám (khảo sát n = 19). Nhóm **chưa đo** agent tiết kiệm được bao nhiêu phút; khảo sát cho thấy cái thiếu là sự chắc chắn hơn là thời gian.
- Chi phí / người / tháng (cơ sở, model `gpt-6.1-terra`): $0.063 (≈ 1.600 ₫); cả 2.000 người ≈ $126 / tháng.
- **Kết luận một dòng — đáng làm không:** **Iterate — đáng làm tiếp ở mức thí điểm.** Chi phí model ≈ 1.600 ₫ / người / tháng (≈ $126 / tháng cho 2.000 người, ≈ 645 ₫ / task thành công) là nhỏ so với 10–45 phút mỗi người tự tra trong tháng gọi khám. Chưa đủ căn cứ để mở rộng: chưa có số người dùng thật và chưa đo người dùng có chắc chắn hơn sau khi hỏi. Chưa tính hosting và giờ công người rà nguồn luật.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Bảng độ nhạy: model rẻ hơn · cache · cắt ngữ cảnh · giới hạn bước — mỗi cần gạt đổi chi phí bao nhiêu
- Chi phí ngoài model: hosting, lưu trữ, giờ công người duyệt
- Quy mô nào thì bài toán còn đáng làm
