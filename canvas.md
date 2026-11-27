# Canvas — Nụ Hôn Lốc Xoáy · Track F

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track + lát cắt dự kiến | F · LegalTech / CivicTech. Đối chiếu căn cứ tạm hoãn gọi nhập ngũ liên quan đến tình trạng học tập. |
| 2 | Người dùng chính | Sinh viên nam trong độ tuổi gọi nhập ngũ tại Việt Nam, đang tìm hiểu trường hợp học tập của mình. |
| 3 | Pain | Sinh viên trong độ tuổi gọi nhập ngũ khó đối chiếu quy định tạm hoãn với tình trạng học tập của mình vì thông tin tra cứu phân tán, nên mất thời gian xác định bước tiếp theo. |
| 4 | Bằng chứng đầu | **Giả thuyết:** sinh viên phải tra nhiều nguồn và vẫn khó xác định dữ kiện học tập có liên quan. **Nguồn sẽ kiểm:** phỏng vấn ít nhất 3 sinh viên đúng vai ngoài nhóm và đối chiếu các hỏi đáp công khai phù hợp, ưu tiên Báo Điện tử Chính phủ. Lưu số liệu và trích dẫn ẩn danh tại `evidence/summary.md`. |
| 5 | Lát cắt một câu | Khi sinh viên nam trong độ tuổi gọi nhập ngũ tìm hiểu trường hợp học tập của mình, AI phân loại tình huống theo căn cứ đã xác minh hoặc hỏi thêm dữ kiện để đưa ra nhận định sơ bộ kèm trích dẫn và checklist bước tiếp theo khi đủ căn cứ. |
| 6 | Mức tự động | AI hỏi thêm, phân loại và giải thích dựa trên nguồn đã xác minh. Người dùng kiểm tra căn cứ và cơ quan có thẩm quyền quyết định, vì nhận định sai có thể khiến sinh viên hiểu sai nghĩa vụ hoặc chuẩn bị thiếu hồ sơ. |
| 7 | Phân công có tên | `Nhi` khám phá người dùng · `Hiếu` kiểm chứng nguồn luật · `Tùng` triển khai bản chạy thử · `Hoàng` đánh giá và chuẩn bị demo. |
| — | *(CP2)* Đã đổi gì so với CP1 | Nhóm bổ sung KB và truy xuất, kết nối model thật, các lớp guard và benchmark 27 ca; chi tiết lịch sử ở git log origin/main. Chuẩn đạt 75% và điều kiện an toàn đã chốt; bằng chứng pain đang thu thập. |

## Track F · Đối chiếu tạm hoãn gọi nhập ngũ vì lý do học tập

**Lĩnh vực.** LegalTech / CivicTech, hỗ trợ tra cứu quy định và thủ tục.

**Pain.** Sinh viên trong độ tuổi gọi nhập ngũ khó đối chiếu quy định tạm hoãn với tình trạng học tập của mình vì thông tin tra cứu phân tán, nên mất thời gian xác định bước tiếp theo.

**Insight từ người dùng thật.** Nhóm chưa có phỏng vấn đã xác thực. Sẽ kiểm tra giả thuyết ở dòng 4 và ghi kết quả có nguồn trong `evidence/summary.md`.

**Người dùng.** Sinh viên nam trong độ tuổi gọi nhập ngũ. Nhóm dự kiến tiếp cận sinh viên đúng vai từ lớp học hoặc mạng lưới quen biết ngoài đội trong hai ngày.

**Data.** Phỏng vấn và hỏi đáp công khai để xác thực pain. Dữ liệu chạy thử gồm tình huống giả lập và trích đoạn từ cổng chính thống đã xác minh hiệu lực. Nguồn đang chờ xác minh ghi `(chưa kiểm)`.

**Lát cắt.** Khi sinh viên nam trong độ tuổi gọi nhập ngũ tìm hiểu trường hợp học tập của mình, AI phân loại tình huống theo căn cứ đã xác minh hoặc hỏi thêm dữ kiện để đưa ra nhận định sơ bộ kèm trích dẫn và checklist bước tiếp theo khi đủ căn cứ.

**Công cụ của agent.** Công cụ `tra_cuu_can_cu` nhận câu hỏi đã chuẩn hóa của người dùng (đã che dữ liệu cá nhân), trả các đoạn luật trong kho kèm mã, đường dẫn và ngày kiểm tra, cùng tối đa 2 bài hỏi đáp chính thức để tham khảo. Công cụ chỉ đọc kho nội bộ và không tác động ra ngoài.

**Bộ câu thử.** Bao phủ học đúng hạn, nợ môn, bảo lưu, văn bằng hai, du học, chuyển trường và liên thông. Chấm phân loại, độ phù hợp của trích dẫn và câu hỏi bổ sung khi thiếu dữ kiện. Từ chối yêu cầu giả mạo hồ sơ hoặc bịa căn cứ.

**Persona chi phí.** Dùng ít để tra lần đầu, dùng vừa để hỏi lại khi có dữ kiện mới, dùng nhiều để theo dõi qua các bước hồ sơ. Tần suất theo tháng sẽ lấy từ bằng chứng thực tế.

**Bẫy.** Dùng nguồn chưa xác minh hiệu lực, suy đoán khi thiếu dữ kiện, hoặc diễn đạt nhận định sơ bộ như quyết định chính thức.

**An toàn.** Giữ phạm vi ở căn cứ học tập. Cơ quan có thẩm quyền quyết định trường hợp cụ thể. Không yêu cầu CCCD, địa chỉ chính xác hoặc hồ sơ cá nhân.
