"""Chuẩn hóa đầu vào dùng chung (chỉ thư viện chuẩn).

Hai mức, cố ý tách riêng:
  clean(text)          — làm sạch an toàn, KHÔNG đổi nghĩa: NFKC, bỏ ký tự zero-width / điều khiển, gộp khoảng trắng.
                         Đây là bản gửi cho model (sau khi che dữ liệu cá nhân ở agent.preprocess).
  for_matching(text)   — CHỈ để khớp từ khóa (chặn đầu vào) và làm truy vấn BM25: nối chữ bị tách ("g.i.ả m.ạ.o"),
                         mở rộng viết tắt / teencode ("sv", "nvqs", "ko", "dc"…). KHÔNG gửi bản này cho model,
                         vì mở rộng viết tắt có thể đoán sai nghĩa ("k" = "không" hay chữ k?).
"""
import re
import unicodedata

_INVISIBLE = re.compile("[­͏؜ᅟᅠ឴឵᠎​-‏‪-‮⁠-⁯﻿]")


def clean(text: str) -> str:
    """NFKC (NBSP → dấu cách, chữ full-width → thường) → NFC, bỏ zero-width / điều khiển, gộp khoảng trắng."""
    t = unicodedata.normalize("NFKC", text or "")
    t = _INVISIBLE.sub("", t)
    t = "".join(" " if unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp") else c for c in t)
    t = unicodedata.normalize("NFC", t)
    return re.sub(r"\s+", " ", t).strip()


# Chữ bị tách bằng . - _ * · hoặc dấu cách: cần ≥3 chữ cái ĐƠN liền nhau ("g.i.ả", "g i a", "m-ạ-o").
# Không nối "gi a" (2 ký tự + 1): bỏ dấu thì trùng "gì ạ" — xem báo cáo.
_SPLIT_SEP = re.compile(r"(?<![^\W\d_])(?:[^\W\d_][.\-_*·])+[^\W\d_](?![^\W\d_])")
_SPLIT_SPACE = re.compile(r"(?<![^\W\d_])(?:[^\W\d_] ){2,}[^\W\d_](?![^\W\d_])")


def join_split(text: str) -> str:
    t = _SPLIT_SEP.sub(lambda m: re.sub(r"[.\-_*·]", "", m.group(0)), text)
    return _SPLIT_SPACE.sub(lambda m: m.group(0).replace(" ", ""), t)


# Viết tắt / teencode an toàn trong ngữ cảnh NVQS. Chỉ thay nguyên TỪ (so chữ thường).
# Bỏ qua cố ý: "a" (= anh / ạ), "h" (= giờ / chữ h), "đk" (= được / đăng ký), "cd" (= cao đẳng / CD).
ABBR = {
    "sv": "sinh viên", "nvqs": "nghĩa vụ quân sự", "đhcq": "đại học chính quy", "dhcq": "đại học chính quy",
    "đh": "đại học", "dh": "đại học", "cđ": "cao đẳng", "cq": "chính quy", "ksk": "khám sức khỏe",
    "ko": "không", "k": "không", "hk": "không", "hok": "không", "khg": "không", "kh": "không", "kg": "không",
    "dc": "được", "đc": "được", "dk": "được", "j": "gì", "vs": "với", "ntn": "như thế nào", "kq": "kết quả",
    "sk": "sức khỏe", "tn": "tốt nghiệp", "lm": "làm", "mún": "muốn", "bn": "bao nhiêu", "hc": "học",
    "đg": "đang", "dg": "đang", "e": "em", "r": "rồi", "bt": "biết", "ng": "người", "bv": "bệnh viện",
    "nhập ngủ": "nhập ngũ",
}
_ABBR_RX = re.compile(r"(?<![^\W_])(%s)(?![^\W_])" % "|".join(
    re.escape(k) for k in sorted(ABBR, key=len, reverse=True)), re.IGNORECASE)


def expand_abbr(text: str) -> str:
    return _ABBR_RX.sub(lambda m: ABBR[m.group(1).lower()], text)


def for_matching(text: str) -> str:
    """Bản dùng để KHỚP (không gửi model): làm sạch → nối chữ tách → mở rộng viết tắt → chữ thường."""
    return expand_abbr(join_split(clean(text))).lower()
