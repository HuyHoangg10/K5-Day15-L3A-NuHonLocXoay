"""Công cụ của bài toán tạm hoãn NVQS — NHÓM VIẾT.

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không
Khung tự ghi mỗi lần gọi công cụ vào trace.

Kho căn cứ: data/kb/dieu41.json (hiện là kho GIẢ — xem data/kb/README.md).
"""
import json
import os

from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(ROOT, "data", "kb", "dieu41.json")
PASSAGE_KEYS = ("code", "van_ban", "hieu_luc", "ngay_tai", "url", "text")


def load_kb(path: str = KB_PATH) -> dict:
    """Đọc kho căn cứ. Trả {"la_kho_gia": bool, "doan": [đoạn…]}. Không phải công cụ (không ghi trace).
    Báo lỗi rõ nếu thiếu file hoặc đoạn thiếu khóa."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    passages = data.get("doan")
    if not isinstance(passages, list):
        raise ValueError("%s: cần khóa \"doan\" là danh sách các đoạn" % path)
    for p in passages:
        missing = [k for k in PASSAGE_KEYS if k not in p]
        if missing:
            raise ValueError("%s: đoạn %s thiếu khóa %s" % (path, p.get("code", "?"), ", ".join(missing)))
    return {"la_kho_gia": bool(data.get("la_kho_gia", False)), "doan": passages}


def all_codes(path: str = KB_PATH) -> set:
    """Mọi mã có trong kho — dùng để kiểm mã điều khoản ở bước 7. Không phải công cụ."""
    return {p["code"] for p in load_kb(path)["doan"]}


@tool
def tra_dieu_luat(chu_de: str) -> list:
    """tra_dieu_luat — tra các đoạn căn cứ trong kho văn bản theo chủ đề.
    Input: chu_de (str): "hoc_tap", "suc_khoe", hoặc "" để lấy mọi đoạn. Chủ đề lạ → danh sách rỗng.
    Output: danh sách đoạn {"code", "van_ban", "hieu_luc", "ngay_tai", "url", "text", ...}, đúng như trong kho.
    Không tác động ra ngoài (chỉ đọc data/kb/dieu41.json)."""
    kb = load_kb()
    chu_de = (chu_de or "").strip()
    if not chu_de:
        return list(kb["doan"])
    return [p for p in kb["doan"] if chu_de in (p.get("chu_de") or [])]
