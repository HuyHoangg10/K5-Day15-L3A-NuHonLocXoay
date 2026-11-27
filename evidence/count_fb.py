"""Đếm pain trong bài đăng nhóm Facebook công khai "Hỏi đáp Nghĩa Vụ Quân Sự 2027".

Dùng:  python evidence/count_fb.py <raw.json> [--vidu]
  raw.json: bản thu thập cục bộ (KHÔNG commit vì là lời người đăng, có thể nhận ra họ).
            Dạng {khoá: {"ngay": "YYYY-MM-DD", "text": "...", "q": ["từ khóa tìm", ...]}}.
  --vidu  : in đoạn ngắn của các bài vướng địa phương / nhiều nguồn để người đọc chọn ví dụ.
Ghi: evidence/data-mining-fb-ketqua.csv (chỉ mã băm · ngày · nhãn, không chép nội dung bài).
Cách thu thập và luật đếm: evidence/data-mining-fb.md.
"""
import csv
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def norm(s):
    return unicodedata.normalize("NFC", s).lower()


def has(pat, t):
    return re.search(pat, t) is not None


# --- lọc vào mẫu -------------------------------------------------------------
HOC = (r"sinh viên|\bsv\b|svien|đại học|\bđh\b|cao đẳng|\bcđ\b|trung cấp|liên thông|văn bằng|bảo lưu|"
       r"du học|nợ môn|nợ học phần|đồ án|học kỳ|học kì|nhập học|trường|đang học|đi học|thạc sĩ|cao học|niên kho")
HOAN = r"hoãn|giấy xác nhận|xác nhận (sinh viên|svien|sv|đang học|học tập|là sinh viên)|giấy (của )?trường|chứng nhận sinh viên"
NU = r"\b(em|mình|tôi) là nữ\b|\bem nữ\b|\bmình nữ\b|bạn nữ"
# lý do khác (sức khỏe, gia đình) mà không nói giấy tờ học tập → không phải pain tạm hoãn vì học
KHAC = r"cận|loạn thị|\bbmi\b|bệnh|hen|viêm|lao động (chính|duy nhất)|hoàn cảnh|bố (em )?mất|ba (em )?mất|con nhỏ|vợ"
GIAY_HOC = r"giấy xác nhận|xác nhận (sinh viên|svien|sv)|giấy (của )?trường|chứng nhận sinh viên|giấy hoãn"
# bài chia sẻ thông tin chung, không phải người hỏi kể trường hợp của mình
KHONG_HOI = r"^(gửi cho|dưới đây|mình xin có 1 số cập nhật|đây là các bệnh|riview|đi nghĩa vụ quân sự không có nghĩa)"

# --- nhãn ----------------------------------------------------------------------
DA_NOP = (r"đã nộp|nộp rồi|có nộp|đã gửi|gửi về|có đưa|đã đưa|nộp xong|nộp xog|vừa nộp|nộp giấy|nộp cho|nộp về|"
          r"nộp lên|nộp kèm|nộp đầy đủ|nộp đủ|xin giấy|đã làm (đơn|giấy)|có giấy|giấy (của )?tr(ườn)?g|chụp giấy")
KET_QUA_XAU = (r"vẫn (bị |phải |có |kêu |bắt |gọi |gửi )|(không|ko|k|kh|chưa) (được )?(nhận|chấp nhận|chấp thuận|chịu|thèm nhận|tiếp nhận)|"
               r"từ chối|bảo (cứ |là )?(lên |đi )?khám|kêu (em |e )?(đi |lên )?khá|chỉ công nhận|bắt (đi|phải|về)|đòi thêm|"
               r"(yêu cầu|bảo|người ta bảo|ngta bảo) (phải|thêm|bổ sung)|bị yc|không được (tạm )?hoãn|ko được hoãn|"
               r"lại (bị )?(gọi|khám|gửi)|(họ|người ta|ngta|nó) (vẫn )?(gửi|kêu|gọi|bắt)|(khám|giấy|gọi) (lần|đợt|vòng|v) ?2|vẫn$")
KHONG_NHAN = r"(không|ko|k|kh) (thèm )?(nhận|chấp nhận|chấp thuận|chịu)|từ chối|chỉ công nhận"
# Kiểm tay toàn bộ bài mang nhãn vuong_dia_phuong (và các bài bị sót đã thấy khi đọc). Mã = 10 ký tự đầu sha1.
# 0 = luật khớp nhầm, 1 = luật sót. Lý do ghi cạnh từng mã.
SUA_TAY_VDP = {
    # luật khớp nhầm: chưa nộp, câu giả định, tự trễ hạn, hoặc người từ chối là trường
    "e66e08dee4": 0,  # "nếu xã không chấp nhận" — câu giả định
    "852db6db86": 0,  # bài bị cắt, không thấy địa phương từ chối giấy học
    "79f9a8e68d": 0,  # chưa nộp, chỉ "nghe có người nói"
    "8bd731a98e": 0,  # chỉ nói có giấy xác nhận, hỏi về sức khỏe
    "a6bb828afc": 0,  # lo sẽ bị từ chối, chưa xảy ra
    "dbe4183add": 0,  # chưa nộp, hỏi thời hạn
    "b7332c3fe9": 0,  # tự nộp trễ
    "7d49bf0f0b": 0,  # tự nộp trễ
    "fb3d425cea": 0,  # tự nộp muộn, địa phương vẫn nhận giấy
    "1709a9ec70": 0,  # quên nộp
    "5c81d4736c": 0,  # chưa có giấy
    "498627ddfd": 0,  # chưa nộp, hỏi trước
    "d18fc1b621": 0,  # giấy gọi nghĩa vụ công an, không phải từ chối giấy học
    "bda3bc7e0a": 0,  # hỏi về sức khỏe
    "085eaca747": 0,  # hỏi cách khỏi khám vòng 2
    "a36cd00b03": 0,  # trường (không phải địa phương) không nhận bảo lưu
    # luật sót
    "fe5a1a41ad": 1,  # lên nộp giấy, "người ta bảo theo lịch học thì đến năm 2026 là hết rồi"
    "cf3ea226c5": 1,  # nộp giấy, phường "không cho hoãn" vì không chính quy
    "612c70aa59": 1,  # được bảo không cần gửi giấy, rồi bị gọi khám vòng 2
}
# loại tay: lọt luật lọc nhưng không phải tạm hoãn vì học
LOAI_TAY = {
    "401458d08a": "ly_do_khac",   # sức khỏe (mồ hôi tay)
    "fd236da801": "ly_do_khac",   # xin xác nhận trình độ học vấn lớp 7
    "3bb6d2eba5": "ly_do_khac",   # hoãn vì em trai đang tại ngũ
}

BIEN = (r"nợ môn|nợ học phần|nợ chứng chỉ|nợ \d+ môn|nợ (vài|mấy|nhiều) môn|(bị |học |ra trường |tốt nghiệp )(trễ|chậm)|chậm (tiến độ|\d|một)|kéo dài|quá hạn|học quá|lưu ban|"
        r"năm (thứ )?(5|6|năm)|4[.,]5 năm|hết (4|5) năm|hết niên kho|liên thông|văn bằng 2|\bvb2\b|bảo lưu|du học|"
        r"chuyển trường|thôi học|bỏ (học|ngang|dở)|nghỉ (học|ngang)|bị đuổi|thi lại|trường (khác|mới|b)\b|thạc sĩ|cao học|"
        r"học lên|học tiếp|vừa học vừa làm|từ xa|trung cấp|gdtx|thường xuyên|mới tốt nghiệp|vừa tốt nghiệp|chưa có bằng|chờ (bằng|visa)")
THU_TUC = (r"nộp (muộn|trễ|bổ sung|sau|kịp|ko kịp|không kịp)|quên (nộp|xin|báo)|chưa nộp|không nộp|ko nộp|k nộp|"
           r"(vòng|đợt) 2 (mới )?(nộp|lộp)|kịp không|kịp k|hạn nộp|thời hạn (để )?nộp|ở đâu|thủ tục|hồ sơ|mẫu đơn|"
           r"giấy (gì|tờ gì)|mỗi năm (phải )?nộp|nộp (khi nào|lúc nào)|cần (làm|nộp) gì")

# nguồn thông tin người hỏi đã gặp TRƯỚC khi hỏi nhóm (nhóm là một nguồn nữa)
NGUON = {
    "van_ban": r"theo luật|luật (ghi|quy định)|với luật|điều \d+|điểm g|thông tư|nghị định|tra (được|cứu)|(em|mình) (có )?tìm hiểu|theo (em|mình) (biết|tìm hiểu)",
    "truong": r"(nhà )?trường (nói|bảo|ghi|chỉ|không làm|ko làm|nhận|kêu)|\bgvcn\b|phòng (ctsv|đào tạo|công tác)",
    "dia_phuong": (r"(xã|phường|quân sự|bch|bchqs|ban chỉ huy|họ|người ta|ngta|chú|các bác|cán bộ|thôn đội|mấy ổng|ở quê|ở trên|địa phương)"
                   r" (vẫn )?(bảo|nói|kêu|báo|trả lời|yêu cầu|đòi|nhắn)"),
    "nguoi_quen_mang": r"nghe (nói|bảo)|(bạn|anh) (em|mình) (nói|bảo|làm)|người quen|trên mạng|đọc (được|báo)|họ hàng|(ba|bố) mẹ (em )?(cứ )?bảo",
}


def labels(raw):
    t = norm(raw)
    if not (has(HOC, t) and has(HOAN, t)):
        return None, "khong_noi_hoan_vi_hoc"
    if has(NU, t):
        return None, "nu_tu_nguyen"
    if has(KHONG_HOI, t):
        return None, "bai_chia_se_chung"
    if has(KHAC, t) and not has(GIAY_HOC, t):
        return None, "ly_do_khac"
    nguon = sorted(k for k, p in NGUON.items() if has(p, t))
    lab = {
        "vuong_dia_phuong": has(DA_NOP, t) and has(KET_QUA_XAU, t) or has(KHONG_NHAN, t),
        "tinh_huong_bien": has(BIEN, t),
        "hoi_thoi_han_thu_tuc": has(THU_TUC, t),
        "da_gap_nguon_khac": bool(nguon),
    }
    return {"nhan": lab, "nguon": nguon}, None


def main():
    src = Path(sys.argv[1])
    data = json.loads(src.read_text(encoding="utf-8"))
    posts = sorted(data.values(), key=lambda p: (p["ngay"], p["text"]))
    seen, rows, bo = set(), [], Counter()
    for p in posts:
        key = re.sub(r"\W+", "", norm(p["text"]))[:80]
        if key in seen:  # cùng một bài đăng lại / trùng ở nhiều từ khóa
            bo["trung_lap"] += 1
            continue
        seen.add(key)
        res, ly_do = labels(p["text"])
        if res is None:
            bo[ly_do] += 1
            continue
        pid = hashlib.sha1(key.encode()).hexdigest()[:10]
        if pid in LOAI_TAY:
            bo[LOAI_TAY[pid]] += 1
            continue
        if pid in SUA_TAY_VDP:
            res["nhan"]["vuong_dia_phuong"] = bool(SUA_TAY_VDP[pid])
        rows.append({"id": pid, "ngay": p["ngay"],
                     "bi_cat": int(p["text"].endswith("…")), **{k: int(v) for k, v in res["nhan"].items()},
                     "nguon": "+".join(res["nguon"]), "tu_khoa": "|".join(p["q"]), "_text": p["text"]})

    n = len(rows)
    print(f"Bài thu về: {len(posts)} · trong mẫu: N = {n} · khoảng ngày {rows[0]['ngay']} → {rows[-1]['ngay']}")
    print("Bị loại:", dict(bo))
    pct = lambda x: f"{x}/{n} ({100 * x / n:.0f}%)"
    for k in ("vuong_dia_phuong", "tinh_huong_bien", "hoi_thoi_han_thu_tuc", "da_gap_nguon_khac"):
        print(f"  {k:22s} {pct(sum(r[k] for r in rows))}")
    print("  vuong_dia_phuong HOẶC tinh_huong_bien", pct(sum(r["vuong_dia_phuong"] or r["tinh_huong_bien"] for r in rows)))
    print("  không nhãn nào           ", pct(sum(not any(r[k] for k in ("vuong_dia_phuong", "tinh_huong_bien", "hoi_thoi_han_thu_tuc", "da_gap_nguon_khac")) for r in rows)))
    print("  bài bị cắt (chỉ thấy phần đầu)", pct(sum(r["bi_cat"] for r in rows)))
    print("  nguồn đã gặp:", Counter(x for r in rows for x in r["nguon"].split("+") if x))
    thuong = [r for r in rows if not r["tinh_huong_bien"]]
    bien = [r for r in rows if r["tinh_huong_bien"]]
    for ten, g in (("thường", thuong), ("biên", bien)):
        print(f"  nhóm {ten}: n={len(g)} · vướng địa phương {sum(r['vuong_dia_phuong'] for r in g)} · gặp nguồn khác {sum(r['da_gap_nguon_khac'] for r in g)}")
    gan = [r for r in rows if r["ngay"] >= "2026-08-01"]
    print(f"  từ 2026-08-01 (đợt gọi khám 2027): n={len(gan)} · vướng địa phương {sum(r['vuong_dia_phuong'] for r in gan)}")

    out = Path(__file__).with_name("data-mining-fb-ketqua.csv")
    cols = ["id", "ngay", "bi_cat", "vuong_dia_phuong", "tinh_huong_bien", "hoi_thoi_han_thu_tuc", "da_gap_nguon_khac", "nguon", "tu_khoa"]
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("Đã ghi", out.name, f"({n} dòng)")

    if "--vidu" in sys.argv:
        for r in rows:
            if r["vuong_dia_phuong"] or r["da_gap_nguon_khac"]:
                print(f"\n[{r['id']} · {r['ngay']} · VDP={r['vuong_dia_phuong']} nguồn={r['nguon']}] {r['_text'][:320]}")


if __name__ == "__main__":
    main()
