# Kho căn cứ pháp lý — hướng dẫn cho người A (kho luật)

**Hiện kho là GIẢ** (`la_kho_gia: true`): mã, chủ đề, ngày, URL đều là chỗ giữ chỗ, ghi `[CHỜ VĂN BẢN GỐC vbpl.vn]`. Khung agent chạy được nhờ nó, nhưng **không được dùng nội dung này làm luật**. Không viết nội dung luật từ trí nhớ.

## Việc cần làm

1. Mở văn bản gốc trên **vbpl.vn** (Luật Nghĩa vụ quân sự, Điều 41 và văn bản hướng dẫn nếu nhóm dùng). Ghi lại: tên văn bản, hiệu lực (đang có hiệu lực hay không, từ ngày nào), URL, **ngày tải**.
2. Chia văn bản theo **điều / khoản / điểm**, mỗi đoạn một mục trong `doan` của `dieu41.json`.
3. Đổi `la_kho_gia` thành `false` khi toàn bộ đoạn đã là văn bản gốc. (Khi còn `true`, đầu ra của agent in cảnh báo kho giả.)
4. Chạy `python -m unittest discover tests` và `python run.py check`, rồi mở PR vào `main`.

## Định dạng một đoạn

```json
{
  "code": "D41.K1.a",
  "van_ban": "tên văn bản + số hiệu",
  "hieu_luc": "còn hiệu lực từ dd/mm/yyyy",
  "ngay_tai": "dd/mm/yyyy",
  "url": "https://vbpl.vn/...",
  "chu_de": ["suc_khoe"],
  "text": "nguyên văn điểm đó, chép đúng từng chữ, không tóm tắt"
}
```

| Khóa | Quy ước |
|---|---|
| `code` | `D<điều>.K<khoản>.<điểm>`, duy nhất. Không có điểm thì `D41.K2`. Mã này là thứ agent trích dẫn; bước 7 chặn mọi mã không có trong kho |
| `van_ban`, `hieu_luc`, `ngay_tai`, `url` | bắt buộc, in ra phần "Căn cứ" của câu trả lời |
| `text` | nguyên văn một khoản / điểm; khoản có nhiều điểm thì tách từng điểm, để model trích đúng mã |
| `chu_de` | *(thêm ngoài 6 khóa chuẩn)* danh sách nhãn chủ đề để công cụ `tra_dieu_luat(chu_de)` lọc: `hoc_tap`, `suc_khoe`. Một đoạn có thể thuộc nhiều chủ đề. Muốn thêm chủ đề mới thì báo người C để thêm vào bảng `REQUIRED_FACTS` trong `codebase/agent.py` |

## Cần người A xác nhận cùng người C / D

- **Chủ đề của từng đoạn** (hiện chỉ là giữ chỗ).
- **Dữ kiện bắt buộc cho từng chủ đề** (`REQUIRED_FACTS` trong `codebase/agent.py`): thiếu dữ kiện nào thì agent hỏi lại thay vì kết luận.
- Câu "nên hỏi cơ quan nào" ở `codebase/prompts.py` (`SAFE_SENTENCE`, `ERROR_MESSAGE`) có đúng không.

Không commit tệp có dữ liệu cá nhân thật. Chỉ chép nguyên văn điều luật công khai.
