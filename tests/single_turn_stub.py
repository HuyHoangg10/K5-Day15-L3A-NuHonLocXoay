"""Model giả TẤT ĐỊNH cho test bất biến đường đo một lượt (không gọi mạng).

Trả lời chỉ phụ thuộc vào (system, user) gửi tới: prompt giống nhau → câu trả lời giống nhau. Nhờ đó nếu đường
answer(text) không có phiên vẫn gửi đúng prompt như main thì đầu ra phải giống từng byte.
Bước trích: suy dữ kiện từ từ khóa trong câu người dùng (đủ để đi qua nhiều nhánh: học tập, sức khỏe, gia đình,
lách luật, ngoài phạm vi, thiếu chủ đề). Bước quyết định: chọn nhãn theo crc32 của prompt, căn cứ là id có trong kho.
"""
import json
import re
import zlib

import kb
import prompts as P

_LABELS = ["eligible_for_review", "not_eligible", "need_more_information", "out_of_scope"]


def _user_sentence(user: str) -> str:
    m = re.findall(r"<<<NGUOI_DUNG\n(.*?)\nNGUOI_DUNG>>>", user, re.S)
    return m[-1] if m else user


def _has(t, *words):
    return any(w in t for w in words)


def extract(user: str) -> str:
    t = kb.fold(_user_sentence(user))
    y_do = "hop_phap"
    if _has(t, "lam gia", "mua giay", "kham thay", "sai lech", "lam gia giay"):
        y_do = "lach_luat"
    elif _has(t, "gia vang", "visa", "thoi tiet"):
        y_do = "ngoai_pham_vi"
    if _has(t, "lao dong duy nhat", "nuoi me", "nuoi bo"):
        chu_de = "gia_dinh"
    elif _has(t, "suc khoe", "benh", "can thi") and not _has(t, "giay xac nhan"):
        chu_de = "suc_khoe"
    elif _has(t, "duoc mien"):
        chu_de = "mien"
    elif _has(t, "hoc", "sinh vien", "truong", "dai hoc", "cao dang", "thpt", "lop ", "khoa"):
        chu_de = "hoc_tap"
    else:
        chu_de = "khac"
    n = re.search(r"nam (\d)", t)
    trinh_do = None
    for k, v in (("lien thong", "liên thông"), ("dai hoc", "đại học"), ("dh ", "đại học"), ("cao dang", "cao đẳng"),
                 ("trung cap", "trung cấp"), ("thpt", "THPT"), ("gdtx", "GDTX cấp THPT")):
        if k in t:
            trinh_do = v
            break
    d = {"chu_de": chu_de, "y_do": y_do,
         "hoi_quy_dinh_chung": _has(t, "moi sinh vien", "ai cung", "ban em bao"),
         "dang_hoc": True if _has(t, "dang hoc", "sinh vien", "nam ") else None,
         "trinh_do": trinh_do,
         "he_chinh_quy": True if "chinh quy" in t else None,
         "nam_thu": int(n.group(1)) if n and 0 < int(n.group(1)) <= 10 else None,
         "qua_han": True if _has(t, "no mon", "het khoa", "no vai hoc phan") else None,
         "bao_luu": True if "bao luu" in t else None,
         "du_hoc": True if "du hoc" in t else None,
         "da_tot_nghiep": True if "tot nghiep" in t and "chua tot nghiep" not in t else None,
         "da_tam_hoan_truoc": True if "da duoc tam hoan" in t else None}
    return json.dumps(d, ensure_ascii=False)


_LY_DO = {
    "eligible_for_review": "Theo những gì bạn kể, bạn có căn cứ để đề nghị xem xét tạm hoãn. Việc này chỉ áp dụng trong "
                           "một khóa học, tính từ ngày nhập học tới khi tốt nghiệp.",
    "not_eligible": "Theo những gì bạn kể, bạn thường không thuộc diện tạm hoãn vì học tập.",
    "need_more_information": "Mình cần thêm thông tin về việc học của bạn để đối chiếu căn cứ.",
    "out_of_scope": "Câu này nằm ngoài phạm vi tạm hoãn vì học tập mà mình hỗ trợ.",
}


def decide(user: str) -> str:
    h = zlib.crc32(user.encode("utf-8"))
    nhan = _LABELS[h % len(_LABELS)]
    if "NGOÀI lát cắt" in user:
        nhan = "out_of_scope"
    qa = re.findall(r"\[(qa-q\d+)\]", user)
    d = {"nhan": nhan,
         "can_cu": ["vbhn133-d41-k1-g"] if nhan != "out_of_scope" else [],
         "tham_khao": qa[:1] if h % 3 == 0 else [],
         "ly_do": _LY_DO[nhan],
         "can_lam_gi": ["Bạn chuẩn bị giấy xác nhận của nhà trường.",
                        "Bạn nên hỏi Ban Chỉ huy quân sự cấp xã nơi bạn cư trú để được hướng dẫn."],
         "can_hoi_them": ["Bạn đang học trình độ nào, hệ chính quy hay không?"] if nhan == "need_more_information" else []}
    return json.dumps(d, ensure_ascii=False)


def make_stub(log=None):
    """Hàm thay cho agent.call_model. `log` (list) nhận (system, user) của mọi lần gọi."""
    def fn(system, user):
        if log is not None:
            log.append((system, user))
        text = extract(user) if system == P.SYSTEM_TRICH else decide(user)
        return {"text": text, "model": "stub", "tokens_in": 0, "tokens_out": 0}
    return fn
