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


# ---------------------------------------------------------------- CHỈ cho bước chặn đầu vào (không dùng cho BM25 / model)
# Tách riêng khỏi for_matching để truy vấn tra cứu (và đường đo) không đổi.

# Chữ Kirin / Hy Lạp / Armenia trông giống chữ Latin ("ѕуѕtеm", "іgnоrе", "mսa") → chữ Latin tương ứng.
_HOMOGLYPH = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "ї": "i", "ј": "j", "ѕ": "s",
    "ԁ": "d", "ӏ": "l", "к": "k", "т": "t", "м": "m", "н": "h", "в": "b", "г": "r", "п": "n",
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X",
    "І": "I", "Ј": "J", "Ѕ": "S", "У": "Y",
    "α": "a", "ο": "o", "ρ": "p", "ε": "e", "ι": "i", "κ": "k", "ν": "v", "τ": "t", "υ": "u", "χ": "x", "ϲ": "c",
    "Α": "A", "Β": "B", "Ε": "E", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T", "Χ": "X",
    "ս": "u", "օ": "o", "ո": "n", "հ": "h", "ց": "g", "ɡ": "g", "ı": "i",
})
# Leetspeak: chỉ đổi số / ký hiệu NẰM TRONG một từ có cả chữ ("g1ả", "tr0n", "syst3m"); "2024", "lớp 12" giữ nguyên.
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "8": "b", "9": "g", "@": "a", "$": "s"})
_WORDISH = re.compile(r"[\w@$]+")          # tách từ một lượt (tuyến tính); kiểm "có cả chữ và số" bằng Python


def _leet_word(m) -> str:
    w = m.group(0)
    if any(c.isalpha() for c in w) and any(c.isdigit() or c in "@$" for c in w):
        return w.translate(_LEET)
    return w


def deobfuscate(text: str) -> str:
    """Ký tự vô hình → dấu cách (để "bỏ qua\\u200bhướng dẫn" không dính thành một từ), chữ giống Latin → Latin, leetspeak."""
    t = unicodedata.normalize("NFKC", text or "")
    t = _INVISIBLE.sub(" ", t).translate(_HOMOGLYPH)
    return _WORDISH.sub(_leet_word, t)


def for_screening(text: str) -> str:
    """Bản dùng cho bước chặn: bỏ ngụy trang (deobfuscate) rồi chuẩn hóa như for_matching."""
    return for_matching(deobfuscate(text))


def fold(text: str) -> str:
    """Bỏ dấu tiếng Việt, chữ thường."""
    s = unicodedata.normalize("NFD", (text or "").lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def squash(text: str) -> str:
    """Chỉ giữ chữ cái a–z sau khi bỏ dấu và bỏ ngụy trang: "b*ỏ q*ua h-ướng d.ẫn", "s y s t e m" → "boquahuongdan", "system".
    Mất ranh giới từ nên CHỈ được so với danh sách từ khóa rất đặc trưng (agent._SQUASHED_INJECTION)."""
    return re.sub(r"[^a-z]", "", fold(deobfuscate(text)))


_B64_TOKEN = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")


def decoded_payloads(text: str) -> list:
    """Đoạn base64 (≥16 ký tự) giải mã ra chữ đọc được, và bản rot13 của câu — để kiểm lệnh bị mã hóa."""
    import base64
    import binascii
    out = []
    for tok in _B64_TOKEN.findall(text or ""):
        try:
            raw = base64.b64decode(tok + "=" * (-len(tok) % 4), validate=True)
            s = raw.decode("utf-8")
        except (binascii.Error, ValueError, UnicodeDecodeError):
            continue
        if s and sum(c.isprintable() for c in s) / len(s) > 0.9 and sum(c.isalpha() for c in s) >= 8:
            out.append(s)
    import codecs
    out.append(codecs.encode(text or "", "rot13"))
    return out
