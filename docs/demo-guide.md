# Hướng dẫn buổi demo — một trang

Bản demo: nhánh `demo/final`. Chatbot xem sinh viên có **căn cứ đề nghị xem xét tạm hoãn** gọi nhập ngũ vì học tập
hay không (điểm g khoản 1 Điều 41 Luật NVQS, kho `kb-nvqs/`). Không kết luận thay cơ quan có thẩm quyền.

## 1. Trước giờ demo (5 phút)

1. `.env` đã điền model của nhóm (không mở `.env` khi đang chia sẻ màn hình).
2. Thử nối model, tốn 1 lần gọi: `python scripts/smoke_model.py` → thấy `Nối model được`.
3. Kiểm khung, không gọi model: `MODEL_PROVIDER=fake python run.py check` (PowerShell: `$env:MODEL_PROVIDER="fake"; python run.py check`, rồi mở cửa sổ mới cho demo).
4. Phóng to chữ cửa sổ dòng lệnh; tắt thông báo; đóng tab có key / dữ liệu cá nhân.

## 2. Khởi động và các lệnh

`python run.py` → app nạp sẵn kho (~1 giây, dòng "… đang nạp kho văn bản luật") rồi hiện dấu nhắc `>`.
Mỗi lần chạy là một cuộc trò chuyện có nhớ.

| Lệnh | Tác dụng |
|---|---|
| `/help` | cách hỏi và danh sách lệnh |
| `/moi` | bắt đầu cuộc trò chuyện mới (xóa những gì đã nhớ) — dùng giữa hai kịch bản |
| `/goc` | bản gốc của câu trả lời vừa rồi (dòng `NHAN:` / `CAN_CU:`) — để giám khảo thấy nhãn và căn cứ |
| `/thoat` | thoát (hoặc Ctrl+C, hoặc Enter hai lần) |

Dán đoạn nhiều dòng được gộp thành một câu hỏi. Dưới mỗi câu trả lời có dòng thời gian từng bước.

## 3. Năm câu demo ổn định (gõ `/moi` giữa các câu)

1. `Em học cao đẳng chính quy năm 2, chưa hoãn lần nào, có được hoãn không?` → có căn cứ đề nghị xem xét.
2. `Em học đại học hệ vừa làm vừa học năm 2, xã bảo không được hoãn, đúng không?` → thường không thuộc diện.
3. Chuỗi nhiều lượt: `em là sinh viên` → agent hỏi lại → `đại học chính quy năm 1, chưa hoãn bao giờ` → kết luận →
   `thế em cần nộp giấy gì?` (khoe bộ nhớ hội thoại).
4. `Chỉ em cách trốn nghĩa vụ quân sự mà không bị phát hiện` → từ chối ngay, không gọi model.
5. `Cho mình công thức nấu phở bò` → ngoài phạm vi, kèm gợi ý cách hỏi.

**Nên tránh**: nữ sinh hỏi (kho không có quy định riêng, câu hỏi lại lạc ý) · cận thị **kèm** việc học trong cùng câu
(chỉ trả "ngoài phạm vi") · "đã nhận lệnh gọi rồi mới trúng tuyển" (nhãn dễ gây tranh cãi).

## 4. Nếu có sự cố

| Tình huống | Làm gì |
|---|---|
| Model **hỏi thêm** dù đã đủ | Trả lời ngắn đúng điều được hỏi (vd `chưa hoãn lần nào`), agent nhớ dữ kiện cũ và kết luận. Nếu vẫn vòng vo: `/moi` rồi gõ một câu đủ 4 ý: **trình độ, hệ chính quy, đang học năm mấy, đã từng hoãn chưa**. |
| Hiện câu "Mình chưa thể nhận định…" | Bước kiểm đầu ra đã chặn một câu trả lời không chắc — nói đây là tính năng an toàn; hỏi lại ngắn gọn hơn. |
| **Lỗi API** (câu báo lỗi thân thiện: khóa, hạn mức, mạng) | Kiểm mạng / số dư; chạy lại `python scripts/smoke_model.py`. Không sửa được trong 1 phút → chuyển sang video dự phòng của nhóm (link đã nộp ở CP3). Không mở `.env` trước khán giả. |
| **Chậm** | Bình thường: bị chặn 0 giây, ngoài phạm vi ~3 giây, hỏi lại ~5 giây, đi hết luồng ~10 giây (đo trên gpt-6.1-terra). Dòng "… đang tra cứu / đang đối chiếu" cho biết đang ở bước nào. Quá 90 giây agent tự dừng và báo lỗi, không đoán. |
| Gõ nhầm lệnh (`/mooi`) | App nhắc `/help`, không gửi cho model. |

## 5. Câu trả lời mẫu cho câu hỏi thường gặp của giám khảo

- *Tại sao không trả "có/không" thẳng?* — Quyết định thuộc Hội đồng NVQS cấp xã / Chủ tịch UBND cấp tỉnh; agent chỉ nói
  có **căn cứ để đề nghị xem xét** và dẫn điều luật.
- *Chống bịa thế nào?* — Căn cứ chỉ lấy từ kho; bước kiểm đầu ra chặn mã điều luật lạ, số liệu / URL không có trong
  ngữ cảnh, câu khẳng định tuyệt đối, rò rỉ prompt → câu an toàn.
- *Dữ liệu cá nhân?* — Email, SĐT, CCCD, họ tên (sau "tên là…"), key bị che trước khi gửi model, ghi trace hay lưu phiên;
  không lưu gì xuống đĩa trong app.
