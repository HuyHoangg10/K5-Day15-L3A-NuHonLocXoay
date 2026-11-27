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


def step_timings(events, total_s: float) -> dict:
    """Thời gian (giây) theo bước từ trace: lần gọi model đầu = trích dữ kiện, công cụ = tra cứu, lần gọi sau = quyết định."""
    models = [e for e in events or [] if e.get("kind") == "model"]
    tools = [e for e in events or [] if e.get("kind") == "tool"]
    t = {"trich": models[0].get("latency_s", 0.0) if models else 0.0,
         "tra_cuu": sum(e.get("latency_s", 0.0) or 0.0 for e in tools),
         "quyet_dinh": sum(e.get("latency_s", 0.0) or 0.0 for e in models[1:]),
         "tong": round(total_s, 2)}
    return {k: round(v, 2) for k, v in t.items()}
