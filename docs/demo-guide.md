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

## 6. Sau khi PR #24 merge vào main

Làm trên máy của một người, **không gọi API thật** (mọi lệnh đều đặt `MODEL_PROVIDER=fake`). Không rebase, không
force-push. Mỗi bước kiểm xong mới sang bước sau.

**6.1. Đưa main mới vào demo/final (merge, không rebase)**

```powershell
git fetch origin
git switch demo/final
git pull --ff-only origin demo/final
git merge --no-ff origin/main -m "Merge main (có PR #24) vào demo/final"
```

Nếu báo xung đột: `git merge --abort` (trở về như trước khi merge) rồi báo nhóm; đừng tự sửa quy tắc 6 / 6a / 16 / 17
để "cho qua".

**6.2. Sinh lại bản chụp bất biến một lượt** (PR #24 đổi quy tắc 6 / 6a / 2 và danh sách mã hợp lệ → bản chụp
đổi là ĐÚNG, có chủ đích)

```powershell
$env:MODEL_PROVIDER="fake"; python tests/make_single_turn_golden.py
git diff --stat tests/fixtures/single_turn_golden.json
```

Lần tập dượt merge trước: 68 trường hợp, phần đổi khớp byte với mã thuần của PR #24 (không có thay đổi nào từ
demo/final). Nếu `git diff` cho thấy đổi ở câu **bị chặn bằng code** (refuse / chèn lệnh / ngoài phạm vi) → dừng,
không commit: đó không phải do PR #24.

**6.3. Chạy test và kiểm**

```powershell
$env:MODEL_PROVIDER="fake"; python -m unittest discover -s tests
```

```powershell
$env:MODEL_PROVIDER="fake"; python run.py check
```

Đều phải OK. Rồi commit bản chụp:

```powershell
git add tests/fixtures/single_turn_golden.json
git commit -m "Sinh lại bản chụp một lượt sau khi merge PR #24 (model giả)"
```

**6.4. Rút gọn quy tắc 16** (chỉ khối `RULES_PHIEN` trong `codebase/prompts.py` — đường có phiên; đường eval một lượt
KHÔNG đổi). Câu cuối của luật 6a (PR #24) đã nói "đủ dữ kiện thì kết luận", nên quy tắc 16 chỉ giữ phần bổ sung. Thay
nguyên ba dòng của quy tắc 16 (từ `16. Đủ dữ kiện thì kết luận…` tới `…đã từng được tạm hoãn chưa.`) bằng đúng một
mục sau, giữ nguyên quy tắc 17:

```text
16. (Cuộc trò chuyện) Khi áp dụng phần eligible_for_review của 6a: 'không nhắc tới' gồm cả tốt nghiệp trình độ khác, liên thông, văn bằng hai, thôi học, chuyển trường, bảo lưu, nợ môn, quá hạn, du học; không hỏi về học gián đoạn; nêu điều kiện một khóa học trong ly_do.
```

Thêm test `tests/test_rule16_short.py`:

```python
import os, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "codebase"))
os.environ["MODEL_PROVIDER"] = "fake"
import prompts as P  # noqa: E402


class Rule16ShortTests(unittest.TestCase):
    def test_rule16_short_and_17_kept(self):
        self.assertIn("16. (Cuộc trò chuyện) Khi áp dụng phần eligible_for_review của 6a", P.RULES_PHIEN)
        self.assertNotIn("Đủ dữ kiện thì kết luận, không hỏi lại", P.RULES_PHIEN)
        self.assertIn("17. can_hoi_them chỉ hỏi dữ kiện còn thiếu", P.RULES_PHIEN)

    def test_single_turn_prompt_untouched(self):
        self.assertNotIn("16. (Cuộc trò chuyện)", P.SYSTEM_QUYET_DINH)
        self.assertTrue(P.SYSTEM_QUYET_DINH_PHIEN.startswith(P.SYSTEM_QUYET_DINH))


if __name__ == "__main__":
    unittest.main()
```

Kiểm lại: bản chụp một lượt **không được đổi** ở bước này (quy tắc 16 chỉ nằm ở đường có phiên):

```powershell
$env:MODEL_PROVIDER="fake"; python -m unittest discover -s tests
```

```powershell
git diff --exit-code tests/fixtures/single_turn_golden.json
```

```powershell
git add codebase/prompts.py tests/test_rule16_short.py
git commit -m "Rút gọn quy tắc 16 (đường có phiên) sau PR #24 — chưa kiểm bằng model thật"
git push origin demo/final
```

Rồi chạy thử bằng model thật 3–5 cuộc trò chuyện của mục 3 (đây là lần duy nhất gọi API, có chủ đích) trước khi dùng
để demo.

**6.5. Lùi lại nếu có lỗi**

- Chưa push, đang merge dở: `git merge --abort`.
- Chưa push, đã commit merge: `git reset --keep HEAD~1` (bỏ commit merge vừa tạo, giữ file đang sửa dở). Kiểm
  `git log --oneline -3` trước.
- Đã push: KHÔNG force-push. Lùi bằng commit mới:
  - lùi quy tắc 16: `git revert <sha-commit-quy-tắc-16>`;
  - lùi cả merge: `git revert -m 1 <sha-commit-merge>` (giữ phía demo/final), rồi sinh lại bản chụp như 6.2 và
    commit;
  - `git push origin demo/final`.
- Sau khi lùi, chạy lại 6.3; bản demo phải chạy như trước khi merge.
