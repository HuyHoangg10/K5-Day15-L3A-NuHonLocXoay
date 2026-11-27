"""Luồng chính — agent xem tình trạng có CĂN CỨ XIN TẠM HOÃN gọi nhập ngũ hay không. NHÓM VIẾT.

`python run.py`, `python run.py eval`, `python run.py simulate` đều gọi answer(text).

Hợp đồng khung: answer(text: str) -> {"output": str}. Mỗi câu thử là MỘT chuỗi, MỘT lượt: "hỏi lại" là một kết quả (need_more_information).

Hình dạng: workflow cố định, 9 bước (sơ đồ ở spec.md §4):
  1 tiền xử lý (code) · 2 chặn đầu vào (code) · 3 trích dữ kiện (model→JSON) · 4 thiếu dữ kiện? (code)
  5 tra căn cứ (công cụ tra_cuu_can_cu) · 6 quyết định (model→JSON) · 7 kiểm đầu ra (code)
  8 định dạng (code) · 9 lỗi model / quá thời gian → thông báo lỗi lịch sự (code)

Tập nhãn (theo kb-nvqs): eligible_for_review · not_eligible · need_more_information · refuse · out_of_scope
Câu an toàn khi kiểm đầu ra hỏng: nhãn RIÊNG safe_fallback (không trùng need_more_information).
Sức khỏe KHÔNG phải quyết định riêng của agent: chỉ nói "kết luận do Hội đồng khám sức khỏe đưa ra".
Nội dung luật chỉ đến từ kho kb-nvqs/ (đọc qua codebase/kb.py).
note() chỉ ghi LÝ DO, không bao giờ ghi nội dung người dùng gõ (trace không được chứa dữ liệu cá nhân).
"""
import json
import re
import time
import unicodedata

import prompts as P
from ai import call_model
import kb
from tools import tra_cuu_can_cu
from tracing import note

LABELS = P.LABELS
DEADLINE_S = 90          # tổng thời gian cho cả hai lần gọi model; quá thì báo lỗi lịch sự (bước 9)

# [CHỜ người A xác nhận theo văn bản gốc] Dữ kiện bắt buộc cho từng chủ đề (bước 4).
# Thiếu dữ kiện nào thì agent hỏi lại (need_more_information) thay vì kết luận.
REQUIRED_FACTS = {
    "hoc_tap": ["dang_hoc", "trinh_do", "he_chinh_quy"],
}

BOOL_FACTS = ("dang_hoc", "he_chinh_quy", "qua_han", "bao_luu", "co_giay_kham")
Y_DO = ("hop_phap", "lach_luat", "ngoai_pham_vi")

# Cụm khẳng định tuyệt đối: model viết ra là bị chặn ở bước 7 (so cả bản bỏ dấu)
ABSOLUTE_PHRASES = ["chắc chắn được", "chắc chắn sẽ được", "đảm bảo được hoãn", "100%", "giấy hợp lệ"]

# Căn cứ cố định cho câu refuse do code chặn (có trong kho mvp): Điều 10 Luật NVQS — hành vi bị nghiêm cấm
# (k3: gian dối trong đăng ký, sơ tuyển, khám sức khỏe); NĐ 218 Điều 9 — xử phạt vi phạm về khám sức khỏe.
REFUSE_CAN_CU = "vbhn133-d10"
REFUSE_CAN_CU_KHAM = "nd218-d9"


# ================================================================ bước 1: tiền xử lý

_RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_RE_PHONE = re.compile(r"(?<!\w)(?:\+?84|0)(?:[\s.\-]?\d){9}(?!\d)")
_RE_CCCD = re.compile(r"(?<!\d)\d{12}(?!\d)")
_RE_CMND = re.compile(r"(?<!\d)\d{9}(?!\d)")


def preprocess(text: str):
    """NFKC, gộp khoảng trắng, che email / SĐT VN / CCCD (12 số) / CMND (9 số). → (văn bản đã che, danh sách loại đã che)."""
    t = unicodedata.normalize("NFKC", text or "")
    t = re.sub(r"\s+", " ", t).strip()
    kinds = []
    for kind, rx, token in (("email", _RE_EMAIL, "[EMAIL]"), ("sdt", _RE_PHONE, "[SĐT]"),
                            ("cccd", _RE_CCCD, "[CCCD]"), ("cmnd", _RE_CMND, "[CCCD]")):
        t, n = rx.subn(token, t)
        if n:
            kinds.append(kind)
    return t, kinds


# ================================================================ bước 2: chặn đầu vào

def _fold(s: str) -> str:
    """Bỏ dấu tiếng Việt, hạ chữ thường — để bắt cả câu gõ không dấu."""
    s = unicodedata.normalize("NFD", s.lower()).replace("đ", "d")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# Mẫu viết CÓ dấu, chữ thường. Cố ý hẹp: "giả sử", "đóng vai trò", "mua sách" không được dính.
# Mẫu chứa chữ "giả" bỏ dấu thành "gia" (trùng "giá"), nên với câu CÓ dấu chỉ so bản có dấu; các mẫu còn lại
# so thêm bản bỏ dấu để bắt câu gõ lẫn có dấu / không dấu.
_EVASION = [
    r"giả\s*(?:mạo\s*)?(?:giấy|hồ\s*sơ|bệnh\s*án|giấy\s*tờ|con\s*dấu|xác\s*nhận)",
    r"làm\s+giả",
    r"(?:giấy|hồ\s*sơ|bệnh\s*án)\s+(?:giả|khống)",
    r"\b(?:chạy|chạy\s+chọt)\s+(?:giấy|hoãn|miễn|khám|kết\s+luận|sức\s+khỏe|loại|trượt)",
    r"\bmua\s+(?:giấy|hồ\s*sơ|bệnh\s*án)?\s*(?:hoãn|miễn|tạm\s+hoãn|khám|sức\s+khỏe|kết\s+luận|xác\s+nhận|bệnh)",
    r"gian\s+lận\s+(?:khám|sức\s+khỏe|hồ\s*sơ|giấy|để)",
    r"khai\s+(?:man|gian|dối|khống)",
    r"(?:khám|đi\s+khám)\s+(?:thay|hộ|giùm|dùm)",
    r"(?:nhờ|thuê)\s+(?:người|ai)\s+(?:khác\s+)?(?:đi\s+)?khám",
    r"hối\s+lộ|đút\s+lót|lót\s+tay",
    r"lách\s+luật",
    r"(?:cách|làm\s+sao\s+để|làm\s+thế\s+nào\s+để|muốn)\s+(?:trốn|né|tránh)\s+(?:nghĩa\s+vụ|lính|quân\s+sự|nhập\s+ngũ|đi\s+bộ\s+đội|khám)",
    r"cố\s+ý\s+(?:gây|làm)\s+(?:thương\s+tích|hỏng|bệnh)",
]
_INJECTION = [
    r"bỏ\s+qua\s+(?:mọi\s+|tất\s+cả\s+|các\s+|những\s+)?(?:hướng\s+dẫn|chỉ\s+dẫn|lệnh|quy\s+tắc|luật\s+lệ|prompt)",
    r"(?:quên|phớt\s+lờ)\s+(?:mọi\s+|tất\s+cả\s+|các\s+|những\s+)?(?:hướng\s+dẫn|chỉ\s+dẫn|quy\s+tắc)",
    r"ignore\s+(?:all\s+|any\s+|the\s+|your\s+)?(?:previous|prior|above|earlier|instructions)",
    r"disregard\s+(?:all\s+|the\s+|your\s+)?(?:previous|prior|above|instructions)",
    r"(?:system|developer)\s+prompt|prompt\s+hệ\s+thống",
    r"tiết\s+lộ\s+(?:prompt|hướng\s+dẫn|cấu\s+hình)",
    r"giả\s+làm\s+\w+",
    r"đóng\s+vai\s+(?!trò)",
    r"bây\s+giờ\s+(?:bạn|mày|em)\s+là",
    r"you\s+are\s+now|pretend\s+(?:to|you)|jailbreak|developer\s+mode",
    r"chế\s+độ\s+(?:nhà\s+phát\s+triển|không\s+giới\s+hạn)",
]
def _compile(patterns):
    accented = [re.compile(p) for p in patterns]
    folded = [re.compile(_fold(p)) for p in patterns]
    safe_folded = [rx for p, rx in zip(patterns, folded) if "giả" not in p]
    return accented, folded, safe_folded


_RX = {"lach_luat": _compile(_EVASION), "chen_lenh": _compile(_INJECTION)}


def screen_input(text: str):
    """Trả None nếu qua, hoặc "lach_luat" / "chen_lenh". Câu hỏi về hoãn HỢP PHÁP không được chặn.
    Câu có dấu: so mẫu có dấu (tránh "giá giấy" khớp nhầm "giả giấy"). Câu gõ KHÔNG dấu: so mẫu đã bỏ dấu."""
    low = text.lower()
    folded_text = _fold(text)
    unaccented = folded_text == low
    for kind, (accented, folded, safe_folded) in _RX.items():
        if unaccented:
            if any(rx.search(low) for rx in folded):
                return kind
        elif any(rx.search(low) for rx in accented) or any(rx.search(folded_text) for rx in safe_folded):
            return kind
    return None


# ================================================================ tiện ích JSON / định dạng

def parse_json(raw: str):
    """Lấy một đối tượng JSON từ chữ model trả về (chịu được khung ```json). Không được → None."""
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    for candidate in (s, s[s.find("{"): s.rfind("}") + 1] if "{" in s and "}" in s else ""):
        try:
            data = json.loads(candidate)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def clean_facts(d: dict):
    """Chuẩn hóa dữ kiện model trích; kiểu sai → None (không biết). y_do sai / thiếu → trả None (coi là hỏng)."""
    if d.get("y_do") not in Y_DO:
        return None
    f = {k: (d.get(k) if isinstance(d.get(k), bool) else None) for k in BOOL_FACTS}
    tr = d.get("trinh_do")
    f["trinh_do"] = tr.strip() if isinstance(tr, str) and tr.strip() else None
    n = d.get("nam_thu")
    f["nam_thu"] = n if isinstance(n, int) and not isinstance(n, bool) and 0 < n <= 10 else None
    f["y_do"] = d["y_do"]
    return f


def render(nhan: str, giai_thich: str, viec: str = "", passages=None, tham_khao=None, hoi_them=None) -> dict:
    """Bước 8. Dòng đầu LUÔN là `NHAN: <nhan>` để chấm bằng code."""
    lines = ["NHAN: " + nhan, "", "Giải thích: " + giai_thich]
    if hoi_them:
        lines.append("Cần biết thêm: " + "; ".join(hoi_them))
    if viec:
        lines.append("Việc cần làm: " + viec)
    if passages:
        lines.append("Nguồn:")
        for p in passages:
            lines.append("- %s — %s; %s; kiểm tra ngày %s"
                         % (p["id"], p["so_hieu"], p["nguon"], p.get("ngay_kiem_tra") or "?"))
    else:
        lines.append("Nguồn: không dùng đoạn căn cứ nào.")
    if tham_khao:
        lines.append("Tham khảo (hỏi đáp chính thức, không phải căn cứ pháp lý):")
        for q in tham_khao:
            lines.append("- %s — %s; %s" % (q["id"], q.get("title", ""), q.get("url", "")))
    lines.append("Lưu ý: " + P.DISCLAIMER)
    return {"output": "\n".join(lines)}


def safe_answer(reason: str) -> dict:
    """CÂU AN TOÀN cố định khi kiểm đầu ra hỏng (bước 7), nhãn RIÊNG safe_fallback. Ghi lý do vào trace."""
    note("câu an toàn: " + reason)
    return render(P.SAFE_LABEL, P.SAFE_SENTENCE)


def error_answer(reason: str) -> dict:
    """Bước 9: lỗi model / quá thời gian. Không bịa, không có dòng NHAN."""
    note("lỗi: " + reason)
    return {"output": "LOI: " + P.ERROR_MESSAGE}


def refuse_answer(text: str, message: str, cite: bool = True) -> dict:
    """refuse bằng code. Câu xin gian dối dẫn Điều 10 (hành vi bị nghiêm cấm); nhắc tới khám sức khỏe thì thêm
    NĐ 218 Điều 9 (xử phạt vi phạm về khám sức khỏe). Câu chèn lệnh: không dẫn căn cứ."""
    ids = []
    if cite:
        ids = [REFUSE_CAN_CU]
        if any(w in kb.fold(text) for w in ("kham", "suc khoe")):
            ids.append(REFUSE_CAN_CU_KHAM)
    ids = [i for i in ids if i in kb.legal_ids()]
    return render("refuse", message, passages=[kb.get_chunk(i) for i in ids])


# ================================================================ bước 4: dữ kiện / chủ đề

def detect_topics(f: dict) -> list:
    topics = []
    if f["dang_hoc"] is not None or any(f[k] is not None for k in ("trinh_do", "he_chinh_quy", "nam_thu", "qua_han", "bao_luu")):
        topics.append("hoc_tap")
    if f["co_giay_kham"] is not None:
        topics.append("suc_khoe")
    return topics


def missing_facts(f: dict, topics: list) -> list:
    need = []
    for t in topics:
        req = REQUIRED_FACTS.get(t, [])
        if t == "hoc_tap" and f["dang_hoc"] is False:   # không đi học: chỉ cần biết điều đó
            req = ["dang_hoc"]
        for k in req:
            if f[k] is None and k not in need:
                need.append(k)
    return need


# ================================================================ bước 7: kiểm đầu ra

def has_absolute(text: str) -> bool:
    """Cụm khẳng định tuyệt đối, so cả bản có dấu và bản bỏ dấu."""
    low = unicodedata.normalize("NFC", unicodedata.normalize("NFKC", text or "")).lower()
    folded = kb.fold(text)
    return any(p in low for p in ABSOLUTE_PHRASES) or any(kb.fold(p) in folded for p in ABSOLUTE_PHRASES)


def _str_list(v):
    """None → []; chuỗi → [chuỗi]; danh sách chuỗi → danh sách đã bỏ trống / trùng. Sai kiểu → None."""
    if v is None:
        return []
    if isinstance(v, str):
        v = [v]
    if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
        return None
    return list(dict.fromkeys(kb.nfc(x).strip() for x in v if x.strip()))


def validate_decision(raw: str, qa_allowed=()):
    """→ (quyết định đã chuẩn hóa, None) nếu đạt; (None, lý do) nếu hỏng.
    qa_allowed: id hỏi đáp đã đưa vào ngữ cảnh — tham_khao chỉ được chứa các id này."""
    d = parse_json(raw)
    if d is None:
        return None, "JSON không hợp lệ"
    nhan = d.get("nhan")
    if nhan not in LABELS:
        return None, "nhãn ngoài tập nhãn"
    can_cu, tham_khao, hoi_them = _str_list(d.get("can_cu")), _str_list(d.get("tham_khao")), _str_list(d.get("can_hoi_them"))
    if can_cu is None or tham_khao is None or hoi_them is None:
        return None, "can_cu / tham_khao / can_hoi_them sai kiểu"
    if any(kb.is_qa_id(c) for c in can_cu):
        return None, "mã hỏi đáp nằm trong can_cu (hỏi đáp không phải văn bản quy phạm)"
    known = kb.legal_ids()
    if any(c not in known for c in can_cu):
        return None, "mã trong can_cu không có trong kho luật mvp"
    allowed = set(qa_allowed)
    if any((not kb.is_qa_id(q)) or q not in allowed for q in tham_khao):
        return None, "tham_khao chứa id không phải bài hỏi đáp đã đưa vào ngữ cảnh"
    if nhan in ("eligible_for_review", "not_eligible") and not can_cu:
        return None, nhan + " nhưng không có căn cứ"
    ly_do = d.get("ly_do")
    if not isinstance(ly_do, str) or not ly_do.strip():
        return None, "thiếu ly_do"
    viec = d.get("can_lam_gi", "")
    if isinstance(viec, list):
        viec = "; ".join(str(x) for x in viec)
    if not isinstance(viec, str):
        return None, "can_lam_gi sai kiểu"
    if has_absolute(" ".join([ly_do, viec] + hoi_them)):
        return None, "chứa cụm tuyệt đối"
    return {"nhan": nhan, "can_cu": can_cu, "tham_khao": tham_khao, "ly_do": ly_do.strip(),
            "can_lam_gi": viec.strip(), "can_hoi_them": hoi_them}, None


# ================================================================ answer

def answer(text: str) -> dict:
    t0 = time.monotonic()

    # 1. Tiền xử lý
    clean, masked = preprocess(text if isinstance(text, str) else "")
    if masked:
        note("tiền xử lý: đã che " + ", ".join(masked))
    if not clean:
        note("đầu vào rỗng")
        return render("need_more_information", "Mình chưa nhận được nội dung nào.", hoi_them=[P.TOPIC_QUESTION])

    # 2. Chặn đầu vào (không gọi model)
    hit = screen_input(clean)
    if hit:
        note("chặn đầu vào: " + hit + " — không gọi model")
        if hit == "lach_luat":
            return refuse_answer(clean, P.REFUSE_EVASION)
        return refuse_answer(clean, P.REFUSE_INJECTION, cite=False)

    # 3. Trích dữ kiện (model → JSON)
    try:
        res = call_model(P.SYSTEM_TRICH, P.user_trich(clean))
    except NotImplementedError:
        raise                     # khung báo "chưa nối model"
    except Exception as e:        # hết lượt, mất mạng, quá thời gian…: lỗi đã được @model_call ghi vào trace
        return error_answer("trích dữ kiện — " + type(e).__name__)
    parsed = parse_json(res.get("text"))
    facts = clean_facts(parsed) if parsed is not None else None
    if facts is None:
        return safe_answer("trích dữ kiện: JSON hỏng hoặc y_do không hợp lệ")
    if facts["y_do"] == "lach_luat":
        note("model đánh dấu y_do=lach_luat — không tra căn cứ")
        return refuse_answer(clean, P.REFUSE_EVASION)
    if facts["y_do"] == "ngoai_pham_vi":
        note("model đánh dấu y_do=ngoai_pham_vi — không tra căn cứ")
        return render("out_of_scope", P.OUT_OF_SCOPE, P.REDIRECT_OTHER)

    # 4. Chủ đề ngoài lát cắt / thiếu dữ kiện bắt buộc (code)
    topics = detect_topics(facts)
    if "suc_khoe" in topics:
        note("chủ đề sức khỏe — ngoài lát cắt học tập")
        return render("out_of_scope", P.OUT_OF_SCOPE, P.REDIRECT_HEALTH)
    if not topics:
        note("thiếu dữ kiện: chưa rõ chủ đề")
        return render("need_more_information", "Mình chưa biết tình trạng học tập của bạn.", hoi_them=[P.TOPIC_QUESTION])
    need = missing_facts(facts, topics)
    if need:
        note("thiếu dữ kiện: " + ", ".join(need))
        return render("need_more_information", "Chưa đủ dữ kiện để nhận định.",
                      hoi_them=[P.FACT_QUESTIONS[k] for k in need])

    # 5. Tra căn cứ (công cụ)
    try:
        found = tra_cuu_can_cu(clean)
    except Exception as e:        # thiếu / hỏng kho
        return error_answer("tra căn cứ — " + type(e).__name__)
    passages, refs = found["luat"], found["tham_khao"]
    note("tra căn cứ: %d chunk luật, %d bài hỏi đáp" % (len(passages), len(refs)))

    # 6. Quyết định (model → JSON)
    if time.monotonic() - t0 > DEADLINE_S:
        return error_answer("quá thời gian trước bước quyết định")
    try:
        res = call_model(P.SYSTEM_QUYET_DINH, P.user_quyet_dinh(clean, facts, passages))
    except NotImplementedError:
        raise
    except Exception as e:
        return error_answer("quyết định — " + type(e).__name__)

    # 7. Kiểm đầu ra (code)
    try:
        decision, why = validate_decision(res.get("text"), [q["id"] for q in refs])
    except Exception as e:        # không đọc được kho để kiểm mã → không dám tin đầu ra
        return error_answer("kiểm đầu ra — " + type(e).__name__)
    if decision is None:
        return safe_answer(why)

    # 8. Định dạng đầu ra
    note("quyết định: " + decision["nhan"])
    return render(decision["nhan"], decision["ly_do"], decision["can_lam_gi"],
                  [kb.get_chunk(c) for c in decision["can_cu"]],
                  [kb.get_chunk(q) for q in decision["tham_khao"]], decision["can_hoi_them"])
