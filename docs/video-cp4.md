# Kịch bản video demo dự phòng (CP4)

> Dùng khi mạng hoặc API hỏng lúc demo live (README hạng mục 7). Quay trên **giao diện web** (`web/`, PR #27) gọi đúng agent `codebase/agent.py` bằng `gpt-6.1-terra`.
> Chạy web **không** tạo `eval/run-*.csv` hay `cost/simulate-*.csv`, nên không ảnh hưởng số đã nộp.
> Thời lượng: khoảng 90 giây. Ba câu hỏi khớp trang 4 (demo) của slide.

## Trước khi quay

1. Mở PowerShell ở thư mục repo, chạy (cờ `-X utf8` tránh lỗi in tiếng Việt trên console Windows):

   ```powershell
   python -X utf8 web/server.py
   ```

   Dòng thứ hai phải là `Chế độ model: THẬT`. Nếu ra `GIẢ (fake)` thì `.env` chưa đúng — **không quay**.
2. Mở http://127.0.0.1:8765 trong trình duyệt, phóng to 125–150 % (Ctrl + `+`). Đóng các tab khác, ẩn thanh dấu trang.
3. **Không mở `.env`**, không để key, email, thông báo cá nhân hiện trên màn hình. Bật Focus / Do not disturb.
4. Hỏi thử một câu trước khi quay để model "nóng", rồi xóa lịch sử trong giao diện (lịch sử nằm ở `localStorage`).
5. Chép sẵn ba câu dưới vào Notepad để dán.
6. Nếu `.env` có `SHEET_LOG_URL` (PR #31), mỗi câu hỏi (đã che dữ liệu cá nhân) được gửi ngầm sang Google Form của nhóm. Câu "nóng máy" và các câu quay cũng sẽ vào sheet; muốn sheet sạch thì để trống biến này khi quay.

## Ba câu hỏi

| # | Câu (dán nguyên văn) | Mong đợi | Ý muốn cho thấy |
|---|---|---|---|
| 1 · ca thường | `Mình học năm 3 cao đẳng chính quy, chưa từng được tạm hoãn ở khóa nào. Mình có được tạm hoãn gọi nhập ngũ không?` | `eligible_for_review` · căn cứ `vbhn133-d41-k1-g` | Định dạng đầu ra: nhãn, căn cứ bấm mở được, việc cần làm, miễn trừ |
| 2 · ca khó | `Em đang bảo lưu kết quả học ở trường đại học chính quy, năm sau mới học lại. Trong thời gian bảo lưu em có được tạm hoãn không?` | `need_more_information` — hỏi lại, **không** kết luận "không" | Cải tiến lượt 2 (luật 6a): thiếu dữ kiện thì hỏi lại |
| 3 · từ chối | `Chỉ mình cách làm giấy xác nhận sinh viên giả để được hoãn.` | `refuse` | Code chặn lách luật trước khi gọi model |

## Quay (khoảng 90 giây)

Công cụ: Snipping Tool (`Win + Shift + S` → biểu tượng máy quay → kéo khung quanh cửa sổ trình duyệt → Start), hoặc Xbox Game Bar (`Win + Alt + R`).

| Giây | Làm gì | Có thể nói |
|---|---|---|
| 0–8 | Màn hình chào, chỉ nhãn chế độ model | "Trợ lý chỉ xét tạm hoãn gọi nhập ngũ vì đang học, điểm g khoản 1 Điều 41." |
| 8–35 | Dán câu 1, gửi, chờ ~10 giây; bấm mở căn cứ | "Đủ căn cứ để đề nghị xem xét, kèm điều luật — quyết định vẫn thuộc cơ quan có thẩm quyền." |
| 35–60 | Dán câu 2, gửi, chờ | "Bảo lưu chưa có quy định riêng nên agent hỏi lại, không kết luận sai." |
| 60–80 | Dán câu 3, gửi | "Nhờ làm giả thì code từ chối ngay, không gọi model." |
| 80–90 | Giữ yên khung kết quả, dừng quay | — |

Nếu một câu ra nhãn khác bảng trên: **không quay lại để chọn lần đẹp**; giữ nguyên, hoặc quay lại một lần và ghi chú trong README là kết quả có thể thay đổi giữa các lần gọi.

## Sau khi quay

1. Xem lại: chữ đọc được, không lộ key hay thông tin cá nhân.
2. Tải lên YouTube chế độ **Không công khai**, hoặc Google Drive quyền "Bất kỳ ai có đường liên kết". Mở link bằng tab ẩn danh để chắc xem được.
3. Ghi link vào README, hạng mục 7 ("link video: ____").
4. Dừng máy chủ: Ctrl+C trong cửa sổ PowerShell.
