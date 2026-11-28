# Canvas — Nụ Hôn Lốc Xoáy · Track F

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track + lát cắt dự kiến | F · LegalTech / CivicTech. Đối chiếu căn cứ tạm hoãn gọi nhập ngũ liên quan đến tình trạng học tập. |
| 2 | Người dùng chính | Sinh viên nam trong độ tuổi gọi nhập ngũ tại Việt Nam, đang tìm hiểu trường hợp học tập của mình. |
| 3 | Pain | Sinh viên trong độ tuổi gọi nhập ngũ không chắc trường hợp học tập của mình có được tạm hoãn không dù đã tra nhiều nguồn, nhất là khi nợ môn, quá hạn, liên thông hay chuyển trường; khi nộp giấy xác nhận, xã/phường có thể không nhận, nên họ phải hỏi lại nhiều nơi hoặc vẫn bị gọi khám. *(sửa sau bằng chứng ngày 27/11; câu CP1: "…vì thông tin tra cứu phân tán, nên mất thời gian xác định bước tiếp theo")* |
| 4 | Bằng chứng đầu | **Giả thuyết:** sinh viên phải tra nhiều nguồn và vẫn khó xác định dữ kiện học tập có liên quan. **Số đầu tiên (đào data Q&A công khai, `evidence/data-mining.md`):** trên 24 bài (15 ca) đạt tiêu chí lọc, **21/24 bài (88%)** / **13/15 ca (87%)** vướng địa phương hoặc rơi vào tình huống biên; **11/24 (46%)** đã nộp giấy tờ nhưng chưa được giải quyết *(vd `qa-q02`: "Tôi đã nộp Giấy xác nhận sinh viên… tuy nhiên không được chấp nhận giải quyết chế độ tạm hoãn")*. **Đào data nhóm Facebook công khai** (`evidence/data-mining-fb.md`): **38/180 bài (21%)** đã nộp giấy xác nhận mà xã/phường không nhận hoặc vẫn gọi khám; **117/180 (65%)** là tình huống biên. **Khảo sát** (`evidence/survey/`, 27 câu trả lời, n = 19 người đúng tuổi đã từng tra): **9/19** tra ≥ 2 cách mà vẫn chưa chắc; 15/19 mất dưới 15 phút mỗi lần, nên ý "mất thời gian" của câu CP1 không đứng. **Còn thiếu:** phỏng vấn ≥3 sinh viên đúng vai ngoài nhóm. Tổng hợp: `evidence/summary.md`. |
| 5 | Lát cắt một câu | Khi sinh viên nam trong độ tuổi gọi nhập ngũ tìm hiểu trường hợp học tập của mình, AI phân loại tình huống theo căn cứ đã xác minh hoặc hỏi thêm dữ kiện để đưa ra nhận định sơ bộ kèm trích dẫn và checklist bước tiếp theo khi đủ căn cứ. |
| 6 | Mức tự động | AI hỏi thêm, phân loại và giải thích dựa trên nguồn đã xác minh. Người dùng kiểm tra căn cứ và cơ quan có thẩm quyền quyết định, vì nhận định sai có thể khiến sinh viên hiểu sai nghĩa vụ hoặc chuẩn bị thiếu hồ sơ. |
| 7 | Phân công có tên | `Nhi` khám phá người dùng · `Hiếu` kiểm chứng nguồn luật · `Tùng` triển khai bản chạy thử · `Hoàng` đánh giá và chuẩn bị demo. |
| — | *(CP2)* Đã đổi gì so với CP1 | Nhóm bổ sung KB và truy xuất, kết nối model thật, các lớp guard, benchmark 27 ca và chạy xong đào data Q&A công khai (21/24 bài / 13/15 ca có pain); chi tiết lịch sử ở git log origin/main. Chuẩn đạt 75% và điều kiện an toàn đã chốt; phỏng vấn người dùng thật đang tiếp tục thu thập. |
| — | *(sau CP2, 27/11 tối)* Đã đổi gì | Thêm hai nguồn bằng chứng (nhóm Facebook N = 180, khảo sát n = 19) và sửa câu pain dòng 3: bỏ "mất thời gian" (khảo sát: 15/19 dưới 15 phút/lần), thêm "vẫn chưa chắc dù tra nhiều nguồn" và "xã/phường có thể không nhận giấy". Lát cắt dòng 5 giữ nguyên. |

## Track F · Đối chiếu tạm hoãn gọi nhập ngũ vì lý do học tập

**Lĩnh vực.** LegalTech / CivicTech, hỗ trợ tra cứu quy định và thủ tục.

**Pain.** Sinh viên trong độ tuổi gọi nhập ngũ không chắc trường hợp học tập của mình có được tạm hoãn không dù đã tra nhiều nguồn, nhất là khi nợ môn, quá hạn, liên thông hay chuyển trường; khi nộp giấy xác nhận, xã/phường có thể không nhận, nên họ phải hỏi lại nhiều nơi hoặc vẫn bị gọi khám.

**Insight từ người dùng thật.** Khảo sát 27 người: gần một nửa người đã tra (9/19) dùng từ 2 cách trở lên mà vẫn chưa chắc mình thuộc diện và cần nộp giấy gì; một người viết *"ko biết nguồn chuẩn, đi khám về vẫn ko biết mình đc gọi"*. Bài đăng trong nhóm Facebook cho thấy thêm chỗ vướng khảo sát chưa hỏi: đã nộp giấy mà xã/phường không nhận với lý do "hết 4 năm", "chỉ công nhận 1 lần". Chưa có phỏng vấn; chi tiết `evidence/summary.md`.

**Người dùng.** Sinh viên nam trong độ tuổi gọi nhập ngũ. Nhóm dự kiến tiếp cận sinh viên đúng vai từ lớp học hoặc mạng lưới quen biết ngoài đội trong hai ngày.

**Data.** Hỏi đáp công khai trên cổng Chính phủ (N = 24), bài đăng nhóm Facebook công khai (N = 180), khảo sát (27 câu trả lời) để xác thực pain; phỏng vấn đang thu thập. Dữ liệu chạy thử gồm tình huống giả lập và trích đoạn từ cổng chính thống đã xác minh hiệu lực. Nguồn đang chờ xác minh ghi `(chưa kiểm)`.

**Lát cắt.** Khi sinh viên nam trong độ tuổi gọi nhập ngũ tìm hiểu trường hợp học tập của mình, AI phân loại tình huống theo căn cứ đã xác minh hoặc hỏi thêm dữ kiện để đưa ra nhận định sơ bộ kèm trích dẫn và checklist bước tiếp theo khi đủ căn cứ.

**Công cụ của agent.** Công cụ `tra_cuu_can_cu` nhận câu hỏi đã chuẩn hóa của người dùng (đã che dữ liệu cá nhân), trả các đoạn luật trong kho kèm mã, đường dẫn và ngày kiểm tra, cùng tối đa 3 bài hỏi đáp chính thức gần nhất (và một bài nền liệt kê các trường hợp không được tạm hoãn) để tham khảo. Công cụ chỉ đọc kho nội bộ và không tác động ra ngoài.

**Bộ câu thử.** Bao phủ học đúng hạn, nợ môn, bảo lưu, văn bằng hai, du học, chuyển trường và liên thông. Chấm phân loại, độ phù hợp của trích dẫn và câu hỏi bổ sung khi thiếu dữ kiện. Từ chối yêu cầu giả mạo hồ sơ hoặc bịa căn cứ.

**Persona chi phí.** Dùng ít để tra lần đầu, dùng vừa để hỏi lại khi có dữ kiện mới, dùng nhiều để theo dõi qua các bước hồ sơ. Tần suất theo tháng sẽ lấy từ bằng chứng thực tế.

**Bẫy.** Dùng nguồn chưa xác minh hiệu lực, suy đoán khi thiếu dữ kiện, hoặc diễn đạt nhận định sơ bộ như quyết định chính thức.

**An toàn.** Giữ phạm vi ở căn cứ học tập. Cơ quan có thẩm quyền quyết định trường hợp cụ thể. Không yêu cầu CCCD, địa chỉ chính xác hoặc hồ sơ cá nhân.
