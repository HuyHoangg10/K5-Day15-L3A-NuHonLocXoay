# Checklist build agent — NuHonLocXoay (L3A · Track F)

> Nộp mọi checkpoint qua **Form 2**. Đội trưởng nộp bằng mã học viên ở dòng 1 của `TEAMS.md`.
> Người: **A** kho luật · **B** bằng chứng · **C** code · **D** prompt + spec + eval. (Đội trưởng nộp, không thay ai làm việc.)

## 1. Mốc và yêu cầu từng checkpoint

### CP1 · 17:00 Thứ Sáu 27/11
- [ ] Repo **Public**; mở bằng tab ẩn danh không bị 404
- [ ] `TEAMS.md` đủ 4 người, đội trưởng ở dòng 1, đúng format
- [ ] `python run.py check`: phần "Kiểm TEAMS.md" không báo gì
- [ ] `canvas.md` đủ 7 dòng: bài toán 1–2 câu **không dùng chữ AI** · lát cắt 1 câu · track

### CP2 · 19:30 Thứ Sáu 27/11
- [ ] `spec.md` §4 có sơ đồ
- [ ] `eval/benchmark.csv` ≥10 câu
- [ ] `eval/metric_spec.yaml` ≥3 metric điền đủ
- [ ] `data/DATA_CARD.md`
- [ ] `python run.py` chạy hết luồng (model giả được)
- [ ] Chuẩn "đạt" ghi ở `spec.md` §7. **KHÔNG SỬA SAU 19:30.**

### CP3 · 10:00 Thứ Bảy 28/11
- [ ] `evidence/summary.md`: ≥1 nguồn đạt ngưỡng + ≥5 trích dẫn nguyên văn đã ẩn tên
- [ ] 20–30 câu thử: ≥5 câu khó, ≥2 câu từ chối, ≥1/3 câu từ người dùng / data thật
- [ ] Video 30 giây, gọi AI **thật**
- [ ] `python run.py eval` lượt 1 (đã nối model thật, `eval --try` thấy token > 0)

### CP4 · 14:30 Thứ Bảy 28/11
- [ ] Chọn **1** cải tiến từ câu trượt, chạy lượt 2, ghi so sánh vào `eval/report.md`
- [ ] `python run.py simulate --rate-from eval/run-2.csv` ≥50 phiên
- [ ] `demo-slides.pdf` ở gốc repo + link video dự phòng (README, hạng mục 7)
- [ ] Tick 4 điều kiện cứng: (1) bản chạy thử gọi AI thật · (2) bằng chứng pain ≥1 nguồn đạt ngưỡng · (3) ≥20 câu thử + % đạt · (4) slide PDF

## 2. Bảng việc

Trạng thái: `[ ]` chưa · `[~]` đang làm · `[x]` xong. Cột "Cần data?" = có thì phải chờ văn bản gốc hoặc người dùng thật.

| Việc | Người | Mốc | Cần data? | File | Trạng thái |
|---|---|---|---|---|---|
| Repo Public, mở được bằng tab ẩn danh | Đội trưởng | CP1 | không | (repo) | [~] |
| Điền `TEAMS.md` (4 người, đội trưởng dòng 1) | Đội trưởng | CP1 | không | `TEAMS.md` | [~] |
| Điền `canvas.md` 7 dòng | D | CP1 | không | `canvas.md` | [~] |
| Chia **văn bản gốc** (vbpl.vn) theo điều / khoản / điểm vào kho | A | CP2 | **có** | `data/kb/dieu41.json` (xem `data/kb/README.md`) | [ ] |
| Xác nhận bảng "dữ kiện bắt buộc theo chủ đề" và nhãn chủ đề của từng đoạn | A | CP2 | **có** | `codebase/agent.py` (`REQUIRED_FACTS`), `data/kb/dieu41.json` | [ ] |
| Soát prompt hệ thống theo văn bản gốc | D (+A) | CP2 | **có** | `codebase/prompts.py` | [ ] |
| Sơ đồ + danh sách công cụ + hình dạng | D | CP2 | không | `spec.md` §4 | [ ] |
| Bộ câu thử ≥10 (10 câu `tu_viet` không cần luật) | D | CP2 | không | `eval/benchmark.csv` | [ ] |
| Thêm câu `thuong` có `expected` lấy từ luật gốc | D (+A) | CP3 | **có** | `eval/benchmark.csv` | [ ] |
| Chốt `nhan_dung.threshold` sau khi thử tay | D | **trước 19:30** | không | `eval/metric_spec.yaml` | [ ] |
| Mô tả kho văn bản | A + D | CP2 | **có** | `data/DATA_CARD.md` | [ ] |
| Khung chạy hết luồng bằng model giả | C | CP2 | không | `codebase/` · `python run.py` | [ ] |
| Chốt chuẩn "đạt" | D (cả nhóm duyệt) | **19:30** | không | `spec.md` §7 | [ ] |
| Phỏng vấn / hỏi đáp công khai, ẩn danh | B | CP3 | **có** | `evidence/` | [ ] |
| Tổng hợp: ≥1 nguồn đạt ngưỡng, ≥5 trích dẫn nguyên văn | B | CP3 | **có** | `evidence/summary.md` | [ ] |
| Câu thử từ người dùng thật (≥1/3 bộ) | B + D | CP3 | **có** | `eval/benchmark.csv` | [ ] |
| Nối model thật, **không commit key** | C | tối T6 | không (cần key) | `codebase/ai.py`, `.env` | [ ] |
| Video 30 giây gọi AI thật | C | CP3 | không | link trong README | [ ] |
| `run.py eval` lượt 1, chấm cột `pass`, `score` | D (C chạy) | CP3 | không | `eval/run-1.csv`, `traces/run-1.jsonl` | [ ] |
| Chọn cải tiến, lượt 2, so sánh | C + D | CP4 | không | `eval/report.md`, `spec.md` §10 | [ ] |
| Persona, giá model, mô phỏng ≥50 phiên | C (+B) | CP4 | **có** (số người dùng thật) | `cost/personas.yaml`, `cost/cost-estimate.md` | [ ] |
| Slide PDF + video dự phòng | cả nhóm | CP4 | không | `demo-slides.pdf`, `slides/outline.md` | [ ] |
| Reflection mỗi người | từng người | 23:59 T7 | không | `reflection/<ten>.md` | [ ] |

## 3. Hợp đồng agent

Một lượt vào, một lượt ra: `answer(text) -> {"output": str}`. Không hội thoại nhiều lượt, nên "hỏi lại" là một **kết quả** (`can_hoi_them`). Mọi chữ trong ngoặc `[CHỜ …]` là chờ người A.

**Luồng 9 bước**

| # | Bước | Ai làm | Ghi chú |
|---|---|---|---|
| 1 | Tiền xử lý: NFKC, gộp khoảng trắng, che CCCD (9/12 số), SĐT VN, email | code | che **trước** khi gửi model và trước khi ghi trace |
| 2 | Chặn đầu vào: từ khóa lách luật, chèn lệnh → `tu_choi`, không gọi model | code | câu "hoãn **hợp pháp**" không được chặn |
| 3 | Trích dữ kiện → JSON | model | `y_do` = `lach_luat` → `tu_choi`; `ngoai_pham_vi` → `ngoai_pham_vi` |
| 4 | Thiếu dữ kiện bắt buộc → `can_hoi_them`, nêu cần thêm gì | code | |
| 5 | Tra căn cứ: công cụ `tra_dieu_luat(chu_de)` đọc `data/kb/dieu41.json` | code | |
| 6 | Quyết định → JSON `{nhan, ma_dieu_khoan[], ly_do, can_lam_gi}` | model | chỉ dùng căn cứ được đưa vào |
| 7 | Kiểm đầu ra; hỏng → **câu an toàn** cố định + `note()` lý do | code | |
| 8 | Định dạng: dòng đầu `NHAN: <nhan>`, giải thích, việc cần làm, nguồn (url + ngày tải), 1 câu miễn trừ | code | để chấm bằng code |
| 9 | Lỗi model / quá thời gian → thông báo lỗi lịch sự, không bịa | code | `NotImplementedError` vẫn bay ra cho khung |

**Tập nhãn:** `co_can_cu_xem_xet` · `khong_thuoc_dien_nay` · `can_hoi_them` · `tu_choi` · `ngoai_pham_vi`

**Schema JSON**

```json
// Bước 3 — trích dữ kiện (không biết thì null)
{"dang_hoc": true, "trinh_do": "…", "he_chinh_quy": true, "nam_thu": 2,
 "qua_han": false, "bao_luu": false, "co_giay_kham": true,
 "y_do": "hop_phap"}            // hop_phap | lach_luat | ngoai_pham_vi

// Bước 6 — quyết định
{"nhan": "co_can_cu_xem_xet", "ma_dieu_khoan": ["D41.K1.a"],
 "ly_do": "…", "can_lam_gi": "…"}
```

**3 lớp guardrail**

| Lớp | Ở đâu | Chặn gì |
|---|---|---|
| 1 · Đầu vào | code, bước 1–2 | thông tin cá nhân; từ khóa lách luật; chèn lệnh |
| 2 · Prompt | `codebase/prompts.py` | chỉ dùng căn cứ được đưa vào; không đủ căn cứ thì `can_hoi_them`; **không bao giờ** kết luận sức khỏe hay xác minh giấy tờ |
| 3 · Đầu ra | code, bước 7 | JSON hỏng; nhãn lạ; mã điều khoản không có trong kho; `co_can_cu_xem_xet` mà không có mã; cụm tuyệt đối ("chắc chắn được", "100%", "giấy hợp lệ", "đảm bảo") |

Sức khỏe **không** phải quyết định riêng của agent: chỉ nói "kết luận do Hội đồng khám sức khỏe đưa ra".

## 4. Quy ước git

- [ ] Mỗi người **một nhánh** riêng, tên `loai/ten-viec` (vd `feat/agent-skeleton`, `docs/build-checklist`, `findings/<ten>`).
- [ ] Mở **PR vào `main`**, mô tả ngắn: đổi gì, file nào, cần ai xem.
- [ ] **Không force-push**, không xóa nhánh của người khác, không commit thẳng vào `main`.
- [ ] Mỗi người chỉ sửa file thuộc phần mình (bảng mục 2); cần sửa file người khác thì báo trong nhóm trước.
- [ ] **Không commit** `.env`, API key, dữ liệu cá nhân thật, export khảo sát còn tên / SĐT.
- [ ] Kết quả chạy thử (`run-try`, `run-mock`, `run-fake`) đã nằm trong `.gitignore`; **chỉ lượt thật** `eval/run-N.csv` + `traces/run-N.jsonl` mới commit, do **một người** (C) chạy; trong lúc đang chạy không ai sửa `eval/benchmark.csv`.
- [ ] Sau CP2 19:30: không sửa `spec.md` §7 và `eval/metric_spec.yaml`; mọi thay đổi khác ghi vào `spec.md` §10.
