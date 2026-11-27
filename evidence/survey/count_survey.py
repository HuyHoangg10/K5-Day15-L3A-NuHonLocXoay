"""Đếm kết quả khảo sát "Khảo sát tìm hiểu quy định tạm hoãn nghĩa vụ quân sự" (Google Form, 27/11/2026).

Dùng:  python evidence/survey/count_survey.py evidence/survey/raw-khao-sat-2026-11-27.csv
  raw-*.csv: bản xuất CSV của Google Sheet (gitignore; không commit vì còn dấu thời gian đến giây).
Ghi:  evidence/survey/results.csv — chỉ giữ ngày (bỏ giờ), mã dòng r01…, câu trả lời đã rút gọn tên cột.
Câu hỏi nguyên văn và cách tính: evidence/survey/questions.md.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

COLS = ["q1_tuoi_18_27", "q2_lan_gan_nhat", "q3_so_lan_1_thang", "q4_so_cau_lien_tiep",
        "q5_cach_tim", "q6_thoi_gian", "q7_da_chac", "q8_kho_nhat"]
CHUA_CHAC = {"Vẫn mơ hồ, chưa chắc", "Mới rõ một phần, vẫn phân vân"}
CACH = ["Tìm Google / đọc bài báo", "Đọc thẳng văn bản luật", "Hỏi bạn bè / anh chị",
        "Hỏi phòng đào tạo / Ban CHQS phường", "Hỏi nhóm Facebook / TikTok / Reddit", "Hỏi ChatGPT"]


def cach(r):
    return [c for c in CACH if c in r["q5_cach_tim"]]


def main():
    raw = list(csv.reader(open(sys.argv[1], encoding="utf-8-sig")))
    head, body = raw[0], [x for x in raw[1:] if any(x)]
    assert len(head) == 9, head
    rows = []
    for i, x in enumerate(body, 1):
        r = {"id": f"r{i:02d}", "ngay": x[0].split()[0]}
        r.update({c: v.strip() for c, v in zip(COLS, x[1:])})
        rows.append(r)

    out = Path(__file__).with_name("results.csv")
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "ngay"] + COLS)
        w.writeheader()
        w.writerows(rows)

    n_all = len(rows)
    vai = [r for r in rows if r["q1_tuoi_18_27"] == "Có"]
    da_tra = [r for r in vai if r["q2_lan_gan_nhat"] != "Chưa bao giờ" and r["q3_so_lan_1_thang"] != "Chưa từng tra"]
    n = len(da_tra)
    pct = lambda x, m: f"{x}/{m} ({100 * x / m:.0f}%)"
    print(f"Tổng câu trả lời: {n_all} · đúng tuổi (câu 1 = Có): {len(vai)} · đã từng tra (câu 2 ≠ Chưa bao giờ, câu 3 ≠ Chưa từng tra): {n}")
    print("Mẫu số các số dưới = người đúng tuổi đã từng tra, n =", n)

    chua_chac = [r for r in da_tra if r["q7_da_chac"] in CHUA_CHAC]
    nhieu_nguon = [r for r in da_tra if len(cach(r)) >= 2]
    nn_chua_chac = [r for r in nhieu_nguon if r["q7_da_chac"] in CHUA_CHAC]
    print("  Sau khi tra vẫn chưa chắc (câu 7)            ", pct(len(chua_chac), n))
    print("  Tra ≥2 cách (câu 5)                           ", pct(len(nhieu_nguon), n))
    print("  Tra ≥2 cách MÀ vẫn chưa chắc                  ", pct(len(nn_chua_chac), n))
    print("  Phải hỏi ≥2 câu liên tiếp mới rõ (câu 4)      ", pct(sum(r["q4_so_cau_lien_tiep"] != "1 câu" for r in da_tra), n))
    print("  Tra ≥2 lần/tháng vào đợt gọi khám (câu 3)     ", pct(sum(r["q3_so_lan_1_thang"] != "1 lần" for r in da_tra), n))
    print("  Lần gần nhất mất ≥15 phút (câu 6)             ", pct(sum(r["q6_thoi_gian"] in ("15–30 phút", "Trên 30 phút") for r in da_tra), n))
    print("  Lần gần nhất trong 1 tháng qua (câu 2)        ", pct(sum(r["q2_lan_gan_nhat"] == "Trong 1 tháng qua" for r in da_tra), n))
    print("Phân bố:")
    for c in COLS[1:7]:
        print(f"  {c}: {dict(Counter(r[c] for r in da_tra))}")
    print("  cách tìm (chọn nhiều):", dict(Counter(x for r in da_tra for x in cach(r))))
    print("  số cách mỗi người:", dict(sorted(Counter(len(cach(r)) for r in da_tra).items())))
    print("Câu 8 (người đã tra):")
    for r in da_tra:
        print(f"  {r['id']} [{r['q7_da_chac']}] {r['q8_kho_nhat']}")
    print("Đã ghi", out.name, f"({n_all} dòng)")


if __name__ == "__main__":
    main()
