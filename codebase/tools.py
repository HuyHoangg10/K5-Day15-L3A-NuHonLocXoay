"""Công cụ của bài toán tạm hoãn gọi nhập ngũ vì học tập — NHÓM VIẾT.

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không
Khung tự ghi mỗi lần gọi công cụ vào trace.

Kho: kb-nvqs/ (đọc qua codebase/kb.py). Tên công cụ khớp canvas.md: tra_cuu_can_cu.
"""
import kb
import text_norm
from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký)

QA_K = 3
# Bài hỏi đáp NỀN, luôn đưa vào ngữ cảnh (nếu BM25 chưa lấy): lời giải chính thức của BQP liệt kê ĐỦ các trường hợp
# sinh viên KHÔNG thuộc diện tạm hoãn (bị buộc thôi học; tự bỏ / ngừng học ≥ 6 tháng không có lý do chính đáng;
# hết thời hạn khóa học; chỉ ghi danh…) và cách tính thời gian tạm hoãn. Thiếu bài này thì model không có căn cứ
# nào để phân biệt "bảo lưu có lý do chính đáng" với "bỏ học", và cứ hỏi lại mãi.
QA_CORE = ("qa-q04",)

# Từ người dùng hay nói ↔ chữ trong văn bản chính thức. Chỉ dùng để MỞ RỘNG truy vấn BM25 (không gửi model,
# không đổi câu người dùng). Khóa so trên bản bỏ dấu (kb.fold).
QUERY_SYNONYMS = {
    "bao luu": "ngừng học tập tạm dừng học nghỉ học lý do chính đáng",
    "nghi hoc": "ngừng học tập tạm dừng học lý do chính đáng",
    "tam dung": "ngừng học tập lý do chính đáng",
    "gia han": "kéo dài thời gian khóa học nhà trường xác định khóa học kéo dài",
    "keo dai": "nhà trường xác định khóa học kéo dài giấy xác nhận",
    "8 nam": "thời gian tối đa hoàn thành chương trình kéo dài",
    "ra truong muon": "kéo dài thời gian học chưa tốt nghiệp",
    "tre han": "kéo dài thời gian học chưa tốt nghiệp",
    "no mon": "nợ môn lưu ban kéo dài chưa tốt nghiệp",
    "van bang 2": "văn bằng hai khóa đào tạo khác trình độ",
    "bang 2": "văn bằng hai khóa đào tạo khác trình độ",
    "thoi hoc": "buộc thôi học chuyển trường khóa đào tạo khác",
}


def expand_query(q: str) -> str:
    """Câu gốc + bản mở rộng viết tắt (text_norm.for_matching) + từ đồng nghĩa trong văn bản chính thức."""
    norm = text_norm.for_matching(q)
    if norm != q.lower():
        q = q + " " + norm
    folded = kb.fold(q)
    extra = [v for k, v in QUERY_SYNONYMS.items() if k in folded]
    return q + (" " + " ".join(extra) if extra else "")


@tool
def tra_cuu_can_cu(cau_hoi: str) -> dict:
    """tra_cuu_can_cu — lấy căn cứ cho một câu hỏi về tạm hoãn gọi nhập ngũ vì học tập.
    Input: cau_hoi (str) — câu của người dùng đã che thông tin cá nhân (bản demo nhiều lượt: kèm vài lượt trước).
    Output: {"luat": mọi chunk luật "mvp" của kb-nvqs (văn bản quy phạm, dùng làm căn cứ),
             "tham_khao": QA_K bài hỏi đáp chính thức gần câu hỏi nhất theo BM25 trên câu hỏi + câu trả lời,
                          cộng bài nền QA_CORE nếu chưa có (KHÔNG phải căn cứ pháp lý)}.
    Không tác động ra ngoài (chỉ đọc kb-nvqs/chunks/*.jsonl).
    Truy vấn BM25 = câu gốc + bản mở rộng viết tắt + từ đồng nghĩa (expand_query), để "sv", "bảo lưu", "gia hạn" vẫn khớp."""
    hits = kb.qa_search(expand_query(cau_hoi or ""), QA_K)
    have = {h["id"] for h in hits}
    for cid in QA_CORE:
        c = kb.get_chunk(cid)
        if c is not None and cid not in have:
            hits.append(dict(c, score=0.0))
    return {"luat": kb.legal_mvp(), "tham_khao": hits}
