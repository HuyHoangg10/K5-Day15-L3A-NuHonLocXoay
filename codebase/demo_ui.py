"""Tiện ích cho giao diện demo (app.py) — NHÓM VIẾT. Không tham gia đường đo (eval / simulate không gọi module này).

- STEP_TEXT: dòng trạng thái theo bước (agent.on_step gọi), để người xem biết agent đang làm gì.
- friendly_error(): đổi lỗi kỹ thuật (đầu ra "LOI:" hoặc exception bay ra khỏi answer) thành câu thân thiện theo loại
  (khóa API, hết hạn mức, quá thời gian, phản hồi hỏng, mạng). KHÔNG BAO GIỜ trả nội dung exception / stack trace / key.
- step_timings(): đọc thời gian từng bước từ sự kiện trace (trích dữ kiện, tra cứu, quyết định, tổng).
"""
STEP_TEXT = {
    "trich": "… đang đọc câu hỏi",
    "tra_cuu": "… đang tra cứu căn cứ trong văn bản luật",
    "quyet_dinh": "… đang đối chiếu và soạn câu trả lời",
}

FRIENDLY = {
    "key": "Bản demo chưa kết nối được với model (khóa API bị từ chối hoặc thiếu cấu hình). Nhóm sẽ kiểm tra lại cấu hình.",
    "quota": "Bản demo tạm hết lượt gọi model (hạn mức của tài khoản). Bạn vui lòng thử lại sau ít phút.",
    "timeout": "Model phản hồi quá lâu nên mình dừng lại, không đoán thay. Bạn vui lòng hỏi lại, có thể ngắn gọn hơn.",
    "bad_response": "Model trả về dữ liệu không đọc được nên mình không đưa ra kết luận. Bạn vui lòng hỏi lại.",
    "network": "Mất kết nối tới model. Bạn kiểm tra mạng rồi hỏi lại giúp mình nhé.",
    "other": "Hệ thống đang gặp sự cố nên chưa trả lời được. Bạn vui lòng thử lại sau ít phút, hoặc hỏi trực tiếp "
             "Ban Chỉ huy quân sự cấp xã nơi cư trú.",
}
FOOTER = "(Bạn có thể hỏi tiếp — cuộc trò chuyện vẫn được giữ.)"

# ---------------------------------------------------------------- lệnh và trình bày dòng lệnh (app.py)
CMD_RESET = ("/moi", "/mới", "/reset")
CMD_RAW = ("/goc", "/gốc")
CMD_HELP = ("/help", "/h", "/?", "/trogiup", "/trợgiúp")
CMD_EXIT = ("/thoat", "/thoát", "/exit", "/quit", "/q")
HELP_TEXT = """Cách dùng:
  • Gõ câu hỏi về việc tạm hoãn gọi nhập ngũ vì đang đi học rồi Enter, ví dụ:
    "Em học cao đẳng chính quy năm nhất, chưa hoãn lần nào thì sao?"
  • Mình nhớ các lượt trong cuộc trò chuyện này, nên bạn có thể trả lời tiếp câu mình hỏi lại.
Lệnh:
  /moi    bắt đầu cuộc trò chuyện mới (xóa những gì mình đã nhớ)
  /goc    xem bản gốc của câu trả lời vừa rồi (có dòng NHAN / CAN_CU để chấm)
  /help   xem hướng dẫn này
  /thoat  thoát (hoặc Ctrl+C, hoặc Enter hai lần với dòng trống)"""
UNKNOWN_CMD = "Mình chưa hiểu lệnh \"%s\". Gõ /help để xem các lệnh."
TOO_LONG_CHAT = "(Cuộc trò chuyện đã khá dài; gõ /moi để bắt đầu lại cho câu trả lời gọn và chính xác hơn.)"
BYE = "Tạm biệt! (Mình không lưu gì xuống máy.)"


def term_width(default: int = 100) -> int:
    """Độ rộng để ngắt dòng: theo cửa sổ dòng lệnh, trong khoảng 40–100 ký tự."""
    import shutil
    try:
        cols = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        cols = default
    return max(40, min(cols - 2, 100))


def wrap(text: str, width: int = None) -> str:
    """Ngắt từng dòng theo độ rộng, giữ thụt lề của dòng gạch đầu dòng / đánh số (dòng tiếp thụt thẳng hàng chữ)."""
    import re
    import textwrap
    width = width or term_width()
    out = []
    for line in (text or "").split("\n"):
        if len(line) <= width:
            out.append(line)
            continue
        m = re.match(r"^(\s*(?:[•\-–*]|\d+\.)?\s*)", line)
        lead = m.group(1) if m else ""
        out.extend(textwrap.wrap(line, width=width, subsequent_indent=" " * len(lead),
                                 break_long_words=True, break_on_hyphens=False) or [""])
    return "\n".join(out)


def classify(text: str) -> str:
    """Loại lỗi từ chuỗi lỗi kỹ thuật (chỉ dùng để phân loại, không hiển thị)."""
    t = (text or "").lower()
    if any(w in t for w in ("http 401", "http 403", "key bị từ chối", "missingconfigerror", "thiếu api_key", "api_key")):
        return "key"
    if any(w in t for w in ("http 402", "http 429", "hạn mức", "quota", "số dư", "rate limit")):
        return "quota"
    if any(w in t for w in ("timeout", "timed out", "hết giờ", "e_timeout", "quá thời gian")):
        return "timeout"
    if any(w in t for w in ("không phải json", "thiếu choices", "thiếu usage", "jsondecode")):
        return "bad_response"
    if any(w in t for w in ("lỗi mạng", "urlerror", "connection", "getaddrinfo", "network")):
        return "network"
    return "other"


def friendly_error(output: str = "", events=None, exc: BaseException = None):
    """→ câu thân thiện nếu lượt này là lỗi (đầu ra "LOI:" hoặc có exception), ngược lại None."""
    if exc is None and not (output or "").startswith("LOI:"):
        return None
    clues = []
    if exc is not None:
        clues.append("%s %s" % (type(exc).__name__, exc))
    for e in events or []:
        if e.get("kind") == "model" and e.get("error"):
            clues.append(str(e["error"]))
        if e.get("kind") == "note" and str(e.get("text", "")).startswith("E_"):
            clues.append(str(e["text"]))
    return FRIENDLY[classify(" | ".join(clues))]


# ---------------------------------------------------------------- hiển thị đẹp cho người xem demo
# Chỉ đổi CÁCH TRÌNH BÀY đầu ra đã kiểm (không đổi nhãn, căn cứ, nội dung). Lệnh /goc trong app.py in bản gốc
# (dòng NHAN / CAN_CU để chấm bằng code).
LABEL_TEXT = {
    "eligible_for_review": "✅ Có căn cứ để đề nghị xem xét tạm hoãn",
    "not_eligible": "⛔ Thường không thuộc diện tạm hoãn vì học tập",
    "need_more_information": "❓ Mình cần thêm thông tin",
    "refuse": "🚫 Mình không hỗ trợ yêu cầu này",
    "out_of_scope": "↪ Ngoài phạm vi mình hỗ trợ",
    "safe_fallback": "⚠ Mình chưa thể nhận định trường hợp này",
}
SHORT_DISCLAIMER = "(Thông tin tham khảo; quyết định thuộc cơ quan có thẩm quyền.)"
OFFTOPIC_HINT = ("Bạn có thể hỏi mình về việc tạm hoãn gọi nhập ngũ vì đang đi học, ví dụ: "
                 "\"Em học cao đẳng chính quy năm nhất, chưa hoãn lần nào thì sao?\"")
# từ nội bộ của prompt lọt vào lời model viết → cách nói người dùng hiểu
_JARGON = [("văn bản trong kho", "văn bản luật mình có"), ("Ngữ cảnh", "Văn bản mình có"), ("ngữ cảnh", "văn bản mình có")]


def law_name(chunk: dict) -> str:
    """'Điểm g khoản 1 Điều 41 Luật Nghĩa vụ quân sự (133/2026/VBHN-LQ-VPQH)' từ siêu dữ liệu chunk."""
    parts = []
    if chunk.get("diem"):
        parts.append("điểm %s" % chunk["diem"])
    if chunk.get("khoan"):
        parts.append("khoản %s" % str(chunk["khoan"]).replace("-", "–"))
    parts.append("Điều %s" % chunk.get("dieu", "?"))
    name = " ".join(parts)
    doc = (chunk.get("ten_van_ban") or "").split(" (")[0]
    return "%s%s %s (%s)" % (name[0].upper(), name[1:], doc, chunk.get("so_hieu", ""))


def _sections(lines):
    sec, cur = {}, None
    for ln in lines:
        for key in ("Giải thích:", "Cần biết thêm:", "Việc cần làm:", "Nguồn:", "Tham khảo", "Lưu ý:"):
            if ln.startswith(key):
                cur = key
                sec[cur] = [ln[len(key):].strip()] if key != "Tham khảo" else []
                break
        else:
            if cur and ln.strip():
                sec[cur].append(ln.strip())
    return sec


def _fold(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", (s or "").lower()).replace("đ", "d")
    return " ".join("".join(c for c in s if unicodedata.category(c) != "Mn").split())


# A1: dấu hiệu câu đòi đổi vai / lộ prompt / bỏ quy định (so trên bản bỏ dấu) và dấu hiệu gian lận giấy tờ / trốn tránh.
# Chỉ dùng để CHỌN CÂU TỪ CHỐI hiển thị cho đúng loại; nhãn (refuse) và bản gốc không đổi.
_INJECTION_HINTS = ("prompt", "prompts", "instruction", "instructions", "system", "chi dan", "huong dan cua ban", "huong dan he thong",
                    "huong dan dau tien", "huong dan goc", "cau hinh", "nhap vai", "dong vai", "gia vo", "pretend",
                    "roleplay", "role play", "act as", "jailbreak", "bo qua", "ignore", "khong bi gioi han",
                    "khong co gioi han", "khong co quy dinh", "khong can theo quy dinh", "khong co dao duc",
                    "unrestricted", "no rules", "without rules", "no restrictions", "developer mode", "che do",
                    "tu gio ban la", "ban la mot", "you are now", "from now on")
_EVASION_HINTS = ("gia giay", "lam gia", "giay gia", "mua giay", "mua hoan", "kham thay", "kham ho", "chay hoan",
                  "chay chot", "hoi lo", "dut lot", "tron", "lach luat", "fake", "gian lan", "khai man", "khai gian")


def refusal_is_injection(user_text: str) -> bool:
    """Câu bị từ chối là chèn lệnh / đòi lộ prompt (không phải nhờ gian lận giấy tờ)?"""
    import re
    t = _fold(user_text)

    def has(hints):
        return re.search(r"(?<!\w)(?:%s)(?!\w)" % "|".join(re.escape(h) for h in hints), t) is not None
    return has(_INJECTION_HINTS) and not has(_EVASION_HINTS)


def pretty(output: str, show_full_disclaimer: bool = True, user_text: str = None) -> str:
    """Đầu ra đã định dạng (NHAN / CAN_CU / Giải thích / …) → bản dễ đọc cho người xem. "LOI:" và chuỗi lạ: giữ nguyên.
    user_text (tùy chọn, chỉ app truyền): câu người dùng vừa gõ — để chọn câu từ chối đúng loại (A1)."""
    import kb   # nạp trễ: demo_ui dùng được cả khi chưa nạp kho (friendly_error)
    import prompts as P
    lines = (output or "").splitlines()
    if len(lines) < 2 or not lines[0].startswith("NHAN:") or not lines[1].startswith("CAN_CU:"):
        return output
    nhan = lines[0][5:].strip()
    ids = [c for c in lines[1][7:].strip().split(",") if c]
    sec = _sections(lines[2:])
    out = [LABEL_TEXT.get(nhan, nhan), ""]
    expl = " ".join(sec.get("Giải thích:", [])).strip()
    for a, b in _JARGON:
        expl = expl.replace(a, b)
    if nhan == "refuse" and expl == P.REFUSE_EVASION and user_text and refusal_is_injection(user_text):
        # Model gắn y_do=lach_luat cho câu đòi đổi vai / lộ prompt → câu từ chối về chèn lệnh, không dẫn Điều 10 (làm giả)
        expl, ids = P.REFUSE_INJECTION, []
    if expl:
        out.append(expl)
    hoi = " ".join(sec.get("Cần biết thêm:", [])).strip()
    if hoi:
        out += ["", "Mình cần biết thêm:"] + ["  • " + q.strip() for q in hoi.split(";") if q.strip()]
    viec = [x for x in sec.get("Việc cần làm:", []) if x]
    offtopic = nhan == "out_of_scope" and not ids and expl == P.OUT_OF_SCOPE and viec == [P.REDIRECT_OTHER]
    if offtopic:
        # Câu không liên quan nghĩa vụ quân sự (nấu ăn, bóng đá…): không bảo người dùng hỏi Ban Chỉ huy quân sự, không
        # kèm lưu ý về Hội đồng nghĩa vụ quân sự — chỉ nói mình giúp được gì. Bản gốc (/goc, đường eval) không đổi.
        viec = []
        sec.pop("Lưu ý:", None)
        out += ["", OFFTOPIC_HINT]
    if viec:
        out += ["", "Việc bạn nên làm:"] + ["  " + (x if x[:1].isdigit() else "• " + x) for x in viec]
    names = []
    for c in ids:
        ch = kb.get_chunk(c)
        if ch:
            names.append(law_name(ch))
    if names:
        out += ["", "Căn cứ:"] + ["  • " + n for n in names]
    refs = [x[2:].split(" — ", 1) for x in sec.get("Tham khảo", []) if x.startswith("- ")]
    titles = [r[1].split(";")[0].strip() for r in refs if len(r) > 1]
    if titles:
        out += ["", "Tham khảo (hỏi đáp chính thức của Bộ Quốc phòng, không phải văn bản luật):"] + \
               ["  • " + t for t in titles]
    if sec.get("Lưu ý:"):
        out += ["", ("Lưu ý: " + " ".join(sec["Lưu ý:"])) if show_full_disclaimer else SHORT_DISCLAIMER]
    return "\n".join(out)


def step_timings(events, total_s: float) -> dict:
    """Thời gian (giây) theo bước từ trace: lần gọi model đầu = trích dữ kiện, công cụ = tra cứu, lần gọi sau = quyết định."""
    models = [e for e in events or [] if e.get("kind") == "model"]
    tools = [e for e in events or [] if e.get("kind") == "tool"]
    t = {"trich": models[0].get("latency_s", 0.0) if models else 0.0,
         "tra_cuu": sum(e.get("latency_s", 0.0) or 0.0 for e in tools),
         "quyet_dinh": sum(e.get("latency_s", 0.0) or 0.0 for e in models[1:]),
         "tong": round(total_s, 2)}
    return {k: round(v, 2) for k, v in t.items()}
