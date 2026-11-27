"""Tầng kho văn bản kb-nvqs — chỉ đọc, chỉ dùng thư viện chuẩn.

Nguồn: kb-nvqs/chunks/legal_chunks.jsonl (văn bản quy phạm, tách theo Điều / điểm) và
       kb-nvqs/chunks/qa_chunks.jsonl (bài hỏi đáp chính thức đã ẩn danh — KHÔNG phải căn cứ pháp lý).
Mô tả dữ liệu: kb-nvqs/README.md, kb-nvqs/DATA_CARD.md, kb-nvqs/SOURCES.csv. Người làm dữ liệu sửa kho, code ở đây không sửa.

Hàm:
    legal_mvp()          các chunk luật có "mvp": true (nạp thẳng vào ngữ cảnh)
    legal_ids()          tập id chunk luật được phép trích làm căn cứ (chỉ chunk mvp)
    get_chunk(id)        một chunk luật hoặc hỏi đáp theo id, không có → None
    qa_search(query, k)  BM25 trên trường question của bài hỏi đáp (loai == "hoi_dap"), có so khớp bản bỏ dấu
"""
import json
import math
import os
import re
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS_DIR = os.path.join(ROOT, "kb-nvqs", "chunks")
LEGAL_FILE = os.path.join(CHUNKS_DIR, "legal_chunks.jsonl")
QA_FILE = os.path.join(CHUNKS_DIR, "qa_chunks.jsonl")

_cache = {}


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def _read_jsonl(path: str) -> list:
    if path not in _cache:
        rows = []
        with open(path, encoding="utf-8-sig") as f:
            for n, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    raise ValueError("%s dòng %d: không phải JSON hợp lệ" % (os.path.relpath(path, ROOT), n))
        for r in rows:
            r["id"] = nfc(r.get("id"))
        _cache[path] = rows
    return _cache[path]


def legal_all() -> list:
    return _read_jsonl(LEGAL_FILE)


def qa_all() -> list:
    return _read_jsonl(QA_FILE)


def legal_mvp() -> list:
    return [c for c in legal_all() if c.get("mvp") is True]


def legal_ids() -> frozenset:
    """Id được phép nằm trong can_cu: chỉ chunk luật mvp (đúng phần đã nạp vào ngữ cảnh)."""
    return frozenset(c["id"] for c in legal_mvp())


def get_chunk(chunk_id: str):
    cid = nfc(chunk_id).strip()
    for c in legal_all():
        if c["id"] == cid:
            return c
    for c in qa_all():
        if c["id"] == cid:
            return c
    return None


def is_qa_id(chunk_id: str) -> bool:
    return nfc(chunk_id).strip().lower().startswith("qa-")


# ================================================================ BM25 trên câu hỏi của bài hỏi đáp

def fold(s: str) -> str:
    """Hạ chữ thường, NFKC, bỏ dấu tiếng Việt (đ → d)."""
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = unicodedata.normalize("NFD", s).replace("đ", "d")
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def tokens(text: str) -> list:
    """Âm tiết có dấu + âm tiết bỏ dấu (tiền tố "~"), kèm cặp âm tiết liền nhau (tiếng Việt ghép từ theo âm tiết).
    Câu gõ không dấu chỉ khớp phần bỏ dấu; câu có dấu khớp cả hai phần."""
    low = unicodedata.normalize("NFC", unicodedata.normalize("NFKC", text or "").lower())
    words = re.findall(r"\w+", low)
    folded = [fold(w) for w in words]
    out = words + ["~" + w for w in folded]
    out += ["%s_%s" % pair for pair in zip(words, words[1:])]
    out += ["~%s_%s" % pair for pair in zip(folded, folded[1:])]
    return out


class _BM25:
    def __init__(self, docs: list, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = []
        df = {}
        for d in docs:
            counts = {}
            for t in d:
                counts[t] = counts.get(t, 0) + 1
            self.tf.append(counts)
            for t in counts:
                df[t] = df.get(t, 0) + 1
        self.len = [len(d) for d in docs]
        self.avg = (sum(self.len) / len(self.len)) if self.len else 0.0
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: list) -> list:
        out = []
        for i, counts in enumerate(self.tf):
            s = 0.0
            norm = self.k1 * (1 - self.b + self.b * self.len[i] / self.avg) if self.avg else self.k1
            for t in set(query):
                f = counts.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + norm)
            out.append(s)
        return out


def _qa_index():
    if "qa_index" not in _cache:
        docs = [c for c in qa_all() if c.get("loai") == "hoi_dap"]
        _cache["qa_index"] = (docs, _BM25([tokens(c.get("question") or "") for c in docs]))
    return _cache["qa_index"]


def qa_search(query: str, k: int = 2) -> list:
    """k bài hỏi đáp (loai == "hoi_dap") có câu hỏi gần query nhất theo BM25. Không bài nào khớp → []."""
    docs, bm25 = _qa_index()
    scored = sorted(((s, i) for i, s in enumerate(bm25.scores(tokens(query))) if s > 0), reverse=True)
    return [dict(docs[i], score=round(s, 3)) for s, i in scored[:k]]
