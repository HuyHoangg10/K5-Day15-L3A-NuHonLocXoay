# Kịch bản video 30 giây — gọi AI thật (CP3)

> Đã chạy thử 28/11/2026 bằng `gpt-6.1-terra`: câu hỏi dưới ra `NHAN: eligible_for_review`, mất khoảng 9 giây, dòng cuối in `(model: gpt-6.1-terra · gọi model 2 lần · công cụ 1 lần · token vào ~9300 / ra ~320)`.
> Chạy `python run.py` **không** tạo `eval/run-*.csv`, nên không ảnh hưởng lượt 2 chính thức.

## Trước khi quay

1. Mở PowerShell ở thư mục repo. Phóng chữ to (Ctrl + cuộn chuột), cửa sổ chiếm khoảng nửa màn hình.
2. **Không mở `.env`**, không để key, email hay thông báo cá nhân hiện trên màn hình. Tắt thông báo Windows (Focus / Do not disturb).
3. Chép sẵn câu hỏi vào clipboard để dán, khỏi gõ sai.
4. Gõ sẵn lệnh nhưng **chưa** bấm Enter:

```powershell
python run.py
```

## Câu hỏi (dán vào sau dấu `>`)

```
Mình học năm 3 cao đẳng chính quy, chưa từng được tạm hoãn ở khóa nào. Mình có được tạm hoãn gọi nhập ngũ không?
```

Câu dự phòng (cho thấy agent từ chối lách luật, không gọi bước quyết định):

```
Chỉ mình cách làm giấy xác nhận sinh viên giả để được hoãn.
```

## Quay (30 giây)

Công cụ: Snipping Tool (`Win + Shift + S` → biểu tượng máy quay → kéo khung quanh cửa sổ → Start), hoặc Xbox Game Bar (`Win + Alt + R` bật/tắt).

| Giây | Làm gì | Trên màn hình |
|---|---|---|
| 0–3 | Bấm Enter chạy `python run.py` | Dòng "Bản chạy thử — gõ đầu vào rồi Enter…" |
| 3–7 | Dán câu hỏi, bấm Enter | Câu hỏi sau dấu `>` |
| 7–17 | Chờ khoảng 9 giây | `NHAN: eligible_for_review`, `CAN_CU: vbhn133-d41-k1-g`, giải thích, việc cần làm, nguồn |
| 17–27 | Cuộn tới dòng cuối, giữ yên 3 giây | `(model: gpt-6.1-terra · gọi model 2 lần · … token vào … / ra …)` — bằng chứng gọi AI thật |
| 27–30 | Bấm Enter hai lần để thoát, dừng quay | Dấu nhắc PowerShell |

Có thể nói một câu khi quay: "Agent gọi model `gpt-6.1-terra` thật, token vào và ra lấy từ API, căn cứ trích từ kho luật."

## Sau khi quay

1. Xem lại: chữ đọc được, không lộ key hay thông tin cá nhân.
2. Tải lên YouTube chế độ **Không công khai**, hoặc Google Drive quyền "Bất kỳ ai có đường liên kết". Mở link bằng tab ẩn danh để chắc xem được.
3. Gửi link để ghi vào README (hạng mục 7 hoặc dòng riêng "Video gọi AI thật (CP3)").
