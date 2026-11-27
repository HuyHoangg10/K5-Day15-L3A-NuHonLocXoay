"""Kiểm đầu ra của model (bước 7) — chỉ thư viện chuẩn. agent.validate_decision gọi các hàm ở đây.

Mọi kiểm ở đây chạy trên CHỮ MODEL VIẾT (ly_do, can_lam_gi, can_hoi_them), không chạy trên câu cố định do code nối.
"""
import re

import kb

# ---------------------------------------------------------------- B1: khẳng định tuyệt đối (có nhận biết phủ định)
# Mẫu viết trên bản BỎ DẤU, chữ thường (kb.fold) → chạy được cả câu có dấu lẫn không dấu.
_ABSOLUTE = [
    r"chac\s+chan\s+(?:se\s+|la\s+)?(?:duoc|du\s+dieu\s+kien|thuoc\s+dien)",
    r"dam\s+bao\s+(?:\w+\s+){0,2}(?:se\s+)?duoc\s+(?:tam\s+)?hoan",
    r"100\s*%",
    r"giay\s+(?:cua\s+(?:ban|em)\s+)?(?:da\s+)?hop\s+le",
    r"cam\s+ket",
]
_ABSOLUTE_RX = [re.compile(r"(?<!\w)" + p) for p in _ABSOLUTE]
# Phủ định đứng NGAY TRƯỚC cụm (trong cùng mệnh đề, cách tối đa 3 từ đệm): "không thể nói 100%",
# "không thể chắc chắn được hoãn", "không có căn cứ nào để nói '100% được hoãn'", "chưa thể cam kết".
_NEGATION_TAIL = re.compile(
    r"(?<!\w)(?:khong|chua|chang|ko)\s+(?:the\s+|dam\s+|ai\s+(?:co\s+the\s+)?|co\s+(?:can\s+cu|co\s+so)\s+(?:nao\s+)?(?:de\s+)?)?"
    r"(?:\w+\s+){0,3}[\"'“”‘’«»(]*\s*$")
_CLAUSE_END = re.compile(r"[.;:!?\n,]")


def has_absolute(text: str) -> bool:
    """True nếu có cụm khẳng định tuyệt đối KHÔNG bị phủ định ngay trước nó (so trên bản bỏ dấu)."""
    folded = kb.fold(text or "")
    for rx in _ABSOLUTE_RX:
        for m in rx.finditer(folded):
            before = folded[:m.start()]
            cut = max((x.end() for x in _CLAUSE_END.finditer(before)), default=0)
            if not _NEGATION_TAIL.search(before[cut:]):
                return True
    return False


# ---------------------------------------------------------------- B3: "Điều N" (và khoản / điểm) phải có trong ngữ cảnh
_ARTICLE = re.compile(r"(?<!\w)điều\s+(\d{1,3})(?!\d)", re.IGNORECASE)
_DIEM_KHOAN_DIEU = re.compile(r"điểm\s+([a-zđ])\s+khoản\s+(\d{1,2})\s+(?:của\s+)?điều\s+(\d{1,3})(?!\d)", re.IGNORECASE)
_DIEU_KHOAN_DIEM = re.compile(r"điều\s+(\d{1,3})\s+khoản\s+(\d{1,2})\s+điểm\s+([a-zđ])(?!\w)", re.IGNORECASE)
_KHOAN_DIEU = re.compile(r"khoản\s+(\d{1,2})\s+(?:của\s+)?điều\s+(\d{1,3})(?!\d)", re.IGNORECASE)
_DIEU_KHOAN = re.compile(r"điều\s+(\d{1,3})\s+khoản\s+(\d{1,2})(?!\d)", re.IGNORECASE)
_KHOAN_NUM = re.compile(r"(?:^|\n|\s)(\d{1,2})\.\s")


def _article_index(passages, context: str):
    """→ (tập số Điều có trong ngữ cảnh, {Điều: tập khoản biết được}, {(Điều, khoản): tập điểm biết được})."""
    dieu = {str(p.get("dieu")) for p in passages if p.get("dieu")}
    dieu |= set(m.group(1) for m in _ARTICLE.finditer(context or ""))
    khoan, diem = {}, {}
    for p in passages:
        d = str(p.get("dieu") or "")
        if not d:
            continue
        ks = khoan.setdefault(d, set())
        if p.get("khoan"):
            ks.update(str(p["khoan"]).split("-"))
            if p.get("diem"):
                diem.setdefault((d, str(p["khoan"])), set()).add(str(p["diem"]).lower())
        else:                                   # chunk cả Điều: khoản là các dòng "1. …", "2. …"
            ks.update(_KHOAN_NUM.findall(p.get("text") or ""))
    return dieu, khoan, diem


def unknown_article(text: str, passages, context: str = ""):
    """Cụm "Điều N" / "khoản K Điều N" / "điểm X khoản K Điều N" mà ngữ cảnh không có → trả cụm đó; không có → None."""
    t = text or ""
    dieu, khoan, diem = _article_index(passages or [], context)
    for m in _ARTICLE.finditer(t):
        if m.group(1) not in dieu:
            return m.group(0)
    for rx, order in ((_DIEM_KHOAN_DIEU, "xkd"), (_DIEU_KHOAN_DIEM, "dkx")):
        for m in rx.finditer(t):
            x, k, d = (m.group(1), m.group(2), m.group(3)) if order == "xkd" else (m.group(3), m.group(2), m.group(1))
            known = diem.get((d, k))
            if known is not None and x.lower() not in known:
                return m.group(0)
    for rx, order in ((_KHOAN_DIEU, "kd"), (_DIEU_KHOAN, "dk")):
        for m in rx.finditer(t):
            k, d = (m.group(1), m.group(2)) if order == "kd" else (m.group(2), m.group(1))
            if khoan.get(d) and k not in khoan[d]:
                return m.group(0)
    return None


# ---------------------------------------------------------------- B4: URL trong lời văn phải là URL của chunk / bài đã dùng
_URL = re.compile(r"(?:https?://|www\.)[^\s<>\"'()\[\]]+", re.IGNORECASE)


def _norm_url(u: str) -> str:
    u = u.strip().rstrip(".,;:!?)»”’").lower()
    u = re.sub(r"^https?://", "", u)
    return u[4:] if u.startswith("www.") else u


def unknown_url(text: str, passages, refs) -> str:
    """URL trong lời văn không thuộc nguồn của chunk luật / bài hỏi đáp đã đưa vào ngữ cảnh → trả URL đó."""
    allowed = {_norm_url(p.get("nguon") or "") for p in passages or []} | {_norm_url(q.get("url") or "") for q in refs or []}
    allowed.discard("")
    for m in _URL.finditer(text or ""):
        if _norm_url(m.group(0)) not in allowed:
            return m.group(0)
    return None


# ---------------------------------------------------------------- B5: số tiền / mức phạt tù / thời hạn ngày phải có trong ngữ cảnh
_UNIT = {"nghìn": 1_000, "ngàn": 1_000, "triệu": 1_000_000, "tỷ": 1_000_000_000}
_NUM = r"\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?"
_MONEY_RANGE = re.compile(r"(%s)\s*(?:đến|tới|-|–)\s*(%s)\s*(nghìn|ngàn|triệu|tỷ)?\s*(?:đồng|vnđ|vnd)?" % (_NUM, _NUM), re.IGNORECASE)
_MONEY = re.compile(r"(%s)\s*(?:(nghìn|ngàn|triệu|tỷ)\s*(?:đồng|vnđ|vnd)?|(?:đồng|vnđ|vnd))(?!\w)" % _NUM, re.IGNORECASE)
_PRISON = re.compile(r"(?:tù|cải\s+tạo)[^.;\n]{0,25}?(\d+)\s*(tháng|năm)|(\d+)\s*(tháng|năm)\s*(?:tù|cải\s+tạo)", re.IGNORECASE)
_DAYS = re.compile(r"(?<![\d/])(\d+)\s*ngày(?!\s*\d)", re.IGNORECASE)


def _to_number(s: str) -> float:
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", s):
        return float(re.sub(r"[.,]", "", s))
    return float(s.replace(",", "."))


def money_values(text: str) -> set:
    """Mọi số tiền (đồng) trong văn bản, quy về đồng: "30.000.000 đồng", "30 triệu đồng", "từ 30 đến 40 triệu đồng"."""
    out, t = set(), text or ""
    for m in _MONEY_RANGE.finditer(t):
        if m.group(3) or re.search(r"đồng|vnđ|vnd", m.group(0), re.IGNORECASE):
            mul = _UNIT.get((m.group(3) or "").lower(), 1)
            out.update({_to_number(m.group(1)) * mul, _to_number(m.group(2)) * mul})
    for m in _MONEY.finditer(t):
        out.add(_to_number(m.group(1)) * _UNIT.get((m.group(2) or "").lower(), 1))
    return out


def prison_terms(text: str) -> set:
    return {(m.group(1) or m.group(3), (m.group(2) or m.group(4)).lower()) for m in _PRISON.finditer(text or "")}


def day_terms(text: str) -> set:
    return {m.group(1) for m in _DAYS.finditer(text or "")}


def unknown_number(text: str, allowed_text: str):
    """Số tiền / mức tù / thời hạn ngày trong lời văn không có trong allowed_text (ngữ cảnh + câu người dùng) → mô tả; ok → None."""
    money_ok = money_values(allowed_text)
    for v in money_values(text):
        if v not in money_ok:
            return "số tiền %s đồng" % format(int(v), ",")
    prison = prison_terms(text)
    if prison:
        ok = prison_terms(allowed_text) | {(n, u.lower()) for n, u in re.findall(r"(\d+)\s*(tháng|năm)", allowed_text or "")}
        for term in prison:
            if term not in ok:
                return "mức tù %s %s" % term
    for d in day_terms(text) - day_terms(allowed_text):
        return "thời hạn %s ngày" % d
    return None


# ---------------------------------------------------------------- B6: rò rỉ prompt / chèn lệnh ở đầu ra
LEAK_MIN_CHARS = 40
_LEAK_PHRASES = re.compile(
    r"(?<!\w)(?:system\s+prompt|developer\s+prompt|prompt\s+(?:he\s+thong|goc)"
    r"|bo\s+qua\s+(?:moi\s+|tat\s+ca\s+|cac\s+|nhung\s+)?(?:huong\s+dan|chi\s+dan)"
    r"|ignore\s+(?:all\s+|any\s+|the\s+|your\s+)?(?:previous\s+|prior\s+|above\s+)?instructions)(?!\w)")
# Dòng nhãn thừa: model tự viết "NHAN: …" / "CAN_CU: …" trong lời văn (so trên bản gốc, chỉ chữ ASCII viết đúng như định dạng).
_FORMAT_LINE = re.compile(r"(?<![A-Za-z_])(?:NHAN|CAN_CU)\s*:", re.IGNORECASE)


def _squash(s: str) -> str:
    """Bỏ dấu, chữ thường, gộp mọi khoảng trắng thành một dấu cách — để so đoạn trùng không phụ thuộc xuống dòng."""
    return " ".join(kb.fold(s or "").split())


_PROMPT_GRAMS = {}


def _prompt_grams(prompts) -> frozenset:
    """Mọi đoạn LEAK_MIN_CHARS ký tự liên tục của các prompt hệ thống, TRỪ đoạn cũng có trong kho (luật + hỏi đáp):
    đoạn đó là nội dung pháp lý mà model được phép nhắc lại, không phải chỉ dẫn bị lộ."""
    key = tuple(prompts)
    if key not in _PROMPT_GRAMS:
        n = LEAK_MIN_CHARS
        grams = set()
        for p in prompts:
            s = _squash(p)
            grams.update(s[i:i + n] for i in range(len(s) - n + 1))
        corpus = " | ".join(_squash(" ".join(str(c.get(k) or "") for k in ("text", "title", "question", "answer")))
                            for c in kb.legal_all() + kb.qa_all())
        _PROMPT_GRAMS[key] = frozenset(g for g in grams if g not in corpus)
    return _PROMPT_GRAMS[key]


def leak(text: str, prompts, allowed_text: str = ""):
    """Lời văn model viết có dấu hiệu rò rỉ prompt / chèn lệnh → mô tả ngắn; sạch → None.
    - cụm "system prompt", "bỏ qua hướng dẫn", "ignore previous instructions"…;
    - dòng "NHAN:" / "CAN_CU:" thừa (chỉ code được viết hai dòng này);
    - đoạn ≥ LEAK_MIN_CHARS ký tự liên tục trùng prompt hệ thống (không tính đoạn có trong ngữ cảnh / câu người dùng / kho)."""
    t = _squash(text)
    if _LEAK_PHRASES.search(t):
        return "cụm nói về prompt / bỏ qua hướng dẫn"
    if _FORMAT_LINE.search(text or ""):
        return "dòng NHAN:/CAN_CU: thừa ngoài định dạng"
    grams = _prompt_grams(prompts)
    allowed = _squash(allowed_text)
    n = LEAK_MIN_CHARS
    for i in range(len(t) - n + 1):
        w = t[i:i + n]
        if w in grams and w not in allowed:
            return "đoạn ≥%d ký tự trùng prompt hệ thống" % n
    return None
