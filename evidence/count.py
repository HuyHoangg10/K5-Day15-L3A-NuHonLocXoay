"""Đào data Q&A công khai — đếm pain "tạm hoãn gọi nhập ngũ vì học tập".

Chạy lại (từ thư mục gốc repo):
    python evidence/count.py              # in tóm tắt + ví dụ, ghi evidence/data-mining-ketqua.csv
    python evidence/count.py --all        # in thêm từng bài bị loại để kiểm tay

Chỉ đọc kb-nvqs/chunks/qa_chunks.jsonl (không sửa file đó), chỉ dùng thư viện chuẩn.
Luật lọc và luật gắn nhãn nằm hết ở các hằng số dưới đây; đổi luật thì ghi lại trong evidence/data-mining.md.
File kết quả chỉ chứa id · URL · ngày · nhãn — không chép nội dung bài, không có tên người hỏi.
"""
import csv
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "kb-nvqs", "chunks", "qa_chunks.jsonl")
OUT = os.path.join(ROOT, "evidence", "data-mining-ketqua.csv")

# Phần đầu `answer` dùng thay `question` khi `question` rỗng (bài báo chép câu hỏi của công dân ở đầu bài).
ANSWER_HEAD = 1500

# ---- Luật lọc (vào mẫu N) ----
# 1) loai == "hoi_dap" (công dân hỏi — kiến nghị cử tri và bài tổng hợp không tính).
# 2) Có nói đến tạm hoãn.
TOPIC = ["hoãn"]
# 3) Có dấu hiệu lý do học tập.
STUDY = ["sinh viên", "học sinh", "đại học", "cao đẳng", "trung cấp", "liên thông", "du học", "nhập học",
         "khóa học", "khóa đào tạo", "nợ môn", "chương trình đào tạo", "giáo dục thường xuyên", "thôi học",
         "đang học", "theo học"]
# 4) Loại bài mà lý do tạm hoãn là hoàn cảnh gia đình / sức khỏe (điểm khác của Đ.41), dù có nhắc chữ "học".
OTHER_REASON = ["lao động duy nhất", "hoàn cảnh kinh tế", "khuyết tật", "diop", "sức khỏe loại"]
# 5) Phải có lời người hỏi (bài phổ biến luật chung không tính) …
ASKER = ["hỏi", "tôi", "thắc mắc", "[ẩn danh]"]
# 6) … và không phải kiến nghị cử tri bị xếp nhầm vào hoi_dap.
PETITION = ["kiến nghị của cử tri", "cử tri phản ánh"]

# Cùng MỘT ca được đăng trên hai cổng (chinhphu.vn đăng lại bài của xaydungchinhsach…).
# Ghép TAY sau khi đọc cả hai bài (cùng nhân thân, năm, chi tiết); người khác cần đọc lại để kiểm.
# Đếm theo "bài" và theo "ca": một ca mang nhãn nếu bất kỳ bài nào của ca đó mang nhãn.
SAME_CASE = [("qa-q01", "qa-q28"), ("qa-q04", "qa-q05"), ("qa-q06", "qa-q07"), ("qa-q08", "qa-q38"),
             ("qa-q09", "qa-q23"), ("qa-q10", "qa-q19"), ("qa-q11", "qa-q21"), ("qa-q24", "qa-q29"),
             ("qa-q26", "qa-q31")]

# ---- Luật gắn nhãn (một bài có thể nhiều nhãn) ----
LABELS = {
    # Đã làm theo cách thông thường (nộp giấy xác nhận…) mà địa phương không nhận / trả lời chưa rõ / đòi thêm.
    "vuong_dia_phuong": ["không chấp nhận", "không được chấp nhận", "chỉ chấp nhận", "chưa được giải quyết",
                         "không giải quyết", "không được giải quyết", "chưa rõ ràng", "tiếp tục yêu cầu",
                         "vẫn yêu cầu", "yêu cầu phải", "không đồng ý", "từ chối", "vẫn gọi", "vẫn bị gọi",
                         "không xét", "không được xét", "không chấp thuận", "chưa tiếp nhận",
                         "không tiếp nhận"],
    # Hoàn cảnh học tập nằm ngoài ca "đang học khóa chính quy đầu tiên" — đọc luật không tự kết luận được.
    "tinh_huong_bien": ["nợ môn", "kéo dài", "chưa hoàn thành", "liên thông", "thôi học", "du học",
                        "giáo dục thường xuyên", "lưu ban", "ngừng học", "chuyển sang", "bảo vệ khóa luận",
                        "trễ"],
    # Hỏi cần giấy tờ / thủ tục gì.
    "hoi_thu_tuc": ["thủ tục", "hồ sơ", "giấy tờ", "trình tự", "phải làm gì", "cần làm gì"],
}
NO_PAIN = "khong_the_hien_pain"
# Luật thêm cho vuong_dia_phuong: kể đã nộp giấy tờ rồi "tuy nhiên / nhưng" (bị gọi khám, bị đòi thêm…),
# trong cùng một đoạn ≤ 400 ký tự.
SUBMIT_THEN_BUT = re.compile(r"đã nộp.{0,400}?(tuy nhiên|nhưng)")

# Che tên người nếu bài gốc chưa ẩn danh ("Tôi là Nguyễn Văn A, …").
_UP = "A-ZÀ-ỸĐ"
_NAME = re.compile(r"(Tôi là|tôi tên là|Tôi tên|Em là|em tên là)\s+(?:[%s][^\s,.;:]*\s*){2,4}" % _UP)


def norm(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text or "")).strip()


# "Sinh viên <Tên> hỏi", "Ông <Tên> đã…" → "Sinh viên [ẩn danh] hỏi".
_ROLE_NAME = re.compile(r"\b(Sinh viên|sinh viên|Học sinh|học sinh|Ông|ông|Bà|bà|Anh|anh|Chị|chị)\s+"
                        r"(?:[%s][^\s,.;:]*\s+){1,3}(?=hỏi|đã|có|cho|đang|được|nộp)" % _UP)


def mask(text):
    text = _NAME.sub(lambda m: m.group(1) + " [ẩn danh] ", text)
    return _ROLE_NAME.sub(lambda m: m.group(1) + " [ẩn danh] ", text)


def has_any(text, words):
    return [w for w in words if w in text]


# Chỉ chấm trên LỜI NGƯỜI HỎI:
#  - bỏ đoạn sapo đầu bài "(Chinhphu.vn) - …" nếu đoạn đó là lời tòa soạn (không có "[ẩn danh]", "hỏi", "tôi");
#  - cắt từ chỗ cơ quan bắt đầu trả lời (phần trả lời tự nhắc "nợ môn", "kéo dài"… và làm sai nhãn).
REPLY_MARKERS = ["Về vấn đề này", "Cục Quân lực", "Bộ Quốc phòng trả lời như sau", "Trả lời vấn đề này",
                 "Bộ Chỉ huy Quân sự", "Luật sư"]
ASKER_HINTS = ["[ẩn danh]", "hỏi", "tôi"]


def asker_part(raw):
    paras = [p for p in re.split(r"\n+|\s{2,}", raw or "") if p.strip()]
    if paras and paras[0].lstrip().startswith("(Chinhphu.vn)") and not any(h in paras[0].lower() or h in paras[0]
                                                                            for h in ASKER_HINTS):
        paras = paras[1:]
    text = norm(" ".join(paras))
    cut = [text.find(m) for m in REPLY_MARKERS if text.find(m) > 0]
    return text[:min(cut)] if cut else text


def label_text(r):
    """Trả (văn bản để gắn nhãn, nguồn của văn bản đó)."""
    q = r.get("question") or ""
    if norm(q) and not norm(q).startswith("Chi tiết câu hỏi"):
        return asker_part(q), "question"
    a = r.get("answer") or ""
    if norm(a).startswith("(Chinhphu.vn)"):  # bài báo: đầu bài chép câu hỏi của công dân
        return asker_part(a)[:ANSWER_HEAD], "answer_dau_bai"
    return norm(r.get("title")), "title"  # chỉ có lời trả lời → chấm theo tiêu đề


def classify(r):
    text, src = label_text(r)
    low = (norm(r.get("title")) + " " + text).lower()
    row = {"id": r["id"], "url": r.get("url", ""), "ngay_dang": r.get("ngay_dang") or "",
           "loai": r.get("loai", ""), "nguon_nhan": src}
    if r.get("loai") != "hoi_dap":
        row["vao_mau"], row["ly_do_loai"] = 0, "khong_phai_hoi_dap"
    elif not has_any(low, TOPIC):
        row["vao_mau"], row["ly_do_loai"] = 0, "khong_noi_tam_hoan"
    elif not has_any(low, STUDY):
        row["vao_mau"], row["ly_do_loai"] = 0, "khong_ly_do_hoc_tap"
    elif has_any(low, OTHER_REASON):
        row["vao_mau"], row["ly_do_loai"] = 0, "ly_do_khac:" + "|".join(has_any(low, OTHER_REASON))
    elif not has_any(low, ASKER):
        row["vao_mau"], row["ly_do_loai"] = 0, "khong_co_loi_nguoi_hoi"
    elif has_any(low, PETITION):
        row["vao_mau"], row["ly_do_loai"] = 0, "thuc_chat_kien_nghi"
    else:
        row["vao_mau"], row["ly_do_loai"] = 1, ""
    tl = text.lower()
    hits = {name: has_any(tl, words) for name, words in LABELS.items()}
    if SUBMIT_THEN_BUT.search(tl):
        hits["vuong_dia_phuong"].append("đã nộp…tuy nhiên/nhưng")
    for name in LABELS:
        row[name] = int(bool(hits[name])) if row["vao_mau"] else ""
    row["tu_khop"] = "; ".join(f"{k}:{'|'.join(v)}" for k, v in hits.items() if v) if row["vao_mau"] else ""
    row[NO_PAIN] = int(row["vao_mau"] and not any(hits.values())) if row["vao_mau"] else ""
    return row, text


def pct(x, n):
    return f"{x}/{n} ({100 * x / n:.0f}%)" if n else f"{x}/0"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = [json.loads(line) for line in open(SRC, encoding="utf-8") if line.strip()]
    out, texts = [], {}
    case_of = {b: a for a, b in SAME_CASE}
    for r in rows:
        row, text = classify(r)
        row["ca"] = case_of.get(row["id"], row["id"])
        out.append(row)
        texts[row["id"]] = text

    cols = ["id", "ca", "url", "ngay_dang", "loai", "vao_mau", "ly_do_loai", "nguon_nhan",
            *LABELS, NO_PAIN, "tu_khop"]
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)

    sample = [o for o in out if o["vao_mau"]]
    n = len(sample)
    print(f"Nguồn: {os.path.relpath(SRC, ROOT)} · tổng {len(rows)} bài")
    print(f"Mẫu N (hoi_dap + tạm hoãn + lý do học tập, trừ lý do khác) = {n}")
    dates = sorted(o["ngay_dang"] for o in sample if o["ngay_dang"])
    if dates:
        print(f"  ngày đăng: {dates[0]} → {dates[-1]} · {n - len(dates)} bài không có ngày")
    print("  nguồn văn bản gắn nhãn:", {s: sum(o['nguon_nhan'] == s for o in sample)
                                       for s in ("question", "answer_dau_bai", "title")})
    cases = {}
    for o in sample:
        cases.setdefault(o["ca"], []).append(o)
    m = len(cases)
    print(f"  {n} bài = {m} ca (ghép {n - m} bài trùng ca, xem SAME_CASE)")

    def case_has(arts, name):
        return any(o[name] == 1 for o in arts)

    print("\nKết quả (một bài có thể nhiều nhãn)          theo BÀI          theo CA")
    for name in LABELS:
        print(f"  {name:22s} {pct(sum(o[name] == 1 for o in sample), n):>22s} {pct(sum(case_has(a, name) for a in cases.values()), m):>16s}")
    no_pain_cases = sum(not any(case_has(a, k) for k in LABELS) for a in cases.values())
    print(f"  {NO_PAIN:22s} {pct(sum(o[NO_PAIN] == 1 for o in sample), n):>22s} {pct(no_pain_cases, m):>16s}")
    any_b = sum(o["vuong_dia_phuong"] == 1 or o["tinh_huong_bien"] == 1 for o in sample)
    any_c = sum(case_has(a, "vuong_dia_phuong") or case_has(a, "tinh_huong_bien") for a in cases.values())
    print(f"  {'vuong_dp HOẶC bien':22s} {pct(any_b, n):>22s} {pct(any_c, m):>16s}")

    print("\nBài bị loại:")
    reasons = {}
    for o in out:
        if not o["vao_mau"]:
            reasons.setdefault(o["ly_do_loai"].split(":")[0], []).append(o["id"])
    for k, ids in reasons.items():
        print(f"  {k}: {len(ids)}" + (f" — {', '.join(ids)}" if "--all" in sys.argv or len(ids) <= 8 else ""))

    print("\nỨng viên ví dụ (đoạn ngắn, đã che tên — người chọn phải đọc lại bài gốc qua URL):")
    shown = set()
    for o in sample:
        if o["vuong_dia_phuong"] == 1 and o["ca"] not in shown:
            shown.add(o["ca"])
            t = mask(texts[o["id"]])
            pos = [t.lower().find(w) for w in LABELS["vuong_dia_phuong"] if w in t.lower()]
            mt = SUBMIT_THEN_BUT.search(t.lower())
            k = min(pos) if pos else mt.start(1)
            s = max(0, k - 160)
            print(f"  [{o['id']} · {o['ngay_dang'] or 'không ngày'}] …{t[s:k + 80]}…\n      {o['url']}")
    print(f"\nĐã ghi {os.path.relpath(OUT, ROOT)} ({len(out)} dòng).")


if __name__ == "__main__":
    main()
