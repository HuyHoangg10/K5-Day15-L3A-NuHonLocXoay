"""Công cụ của bài toán tạm hoãn gọi nhập ngũ vì học tập — NHÓM VIẾT.

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không
Khung tự ghi mỗi lần gọi công cụ vào trace.

Kho: kb-nvqs/ (đọc qua codebase/kb.py). Tên công cụ khớp canvas.md: tra_cuu_can_cu.
"""
import kb
import text_norm
from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký)

QA_K = 2


@tool
def tra_cuu_can_cu(cau_hoi: str) -> dict:
    """tra_cuu_can_cu — lấy căn cứ cho một câu hỏi về tạm hoãn gọi nhập ngũ vì học tập.
    Input: cau_hoi (str) — câu của người dùng đã che thông tin cá nhân.
    Output: {"luat": mọi chunk luật "mvp" của kb-nvqs (văn bản quy phạm, dùng làm căn cứ),
             "tham_khao": 2 bài hỏi đáp chính thức gần câu hỏi nhất theo BM25 (KHÔNG phải căn cứ pháp lý)}.
    Không tác động ra ngoài (chỉ đọc kb-nvqs/chunks/*.jsonl).
    Truy vấn BM25 = câu gốc + bản mở rộng viết tắt (text_norm.for_matching) nếu khác, để "sv", "nvqs", "ko" vẫn khớp."""
    q = cau_hoi or ""
    norm = text_norm.for_matching(q)
    if norm != q.lower():
        q = q + " " + norm
    return {"luat": kb.legal_mvp(), "tham_khao": kb.qa_search(q, QA_K)}
