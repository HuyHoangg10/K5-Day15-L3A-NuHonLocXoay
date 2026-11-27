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
