"""Thử nối model: gọi model thật ĐÚNG 1 LẦN với một câu ngắn. Không nằm trong luồng chấm, không ghi file nào.

    python scripts/smoke_model.py                       # dùng MODEL_PROVIDER / MODEL_NAME / API_KEY trong .env
    python scripts/smoke_model.py --provider openai     # thử openai (key trong .env phải là key của openai)
    python scripts/smoke_model.py --provider openai --model gpt-4o-mini

API_KEY trống: in hướng dẫn rồi thoát mã 0 (không lỗi). Không bao giờ in key.
Mỗi lần chạy tốn một lượt gọi API thật (rất rẻ: vài chục token).
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import ai  # noqa: E402  (nạp .env)

DEFAULT_MODELS = {"deepseek": "deepseek-flash", "openai": "gpt-4o-mini"}
SYSTEM = "Bạn là trợ lý. Trả lời ngắn gọn bằng tiếng Việt."
USER = "Hai cộng ba bằng mấy? Trả lời một câu."


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Gọi model thật 1 lần để kiểm tra .env")
    ap.add_argument("--provider", help="deepseek | openai (mặc định: MODEL_PROVIDER trong .env)")
    ap.add_argument("--model", help="mã model (mặc định: MODEL_NAME trong .env, hoặc model rẻ gợi ý của provider)")
    args = ap.parse_args(argv)

    if args.provider:
        ai.MODEL_PROVIDER = args.provider.strip().lower()
        if not args.model and ai.MODEL_PROVIDER in DEFAULT_MODELS:
            ai.MODEL_NAME = DEFAULT_MODELS[ai.MODEL_PROVIDER]
    if args.model:
        ai.MODEL_NAME = args.model.strip()

    print("provider: %s · model: %s" % (ai.MODEL_PROVIDER or "(trống)", ai.MODEL_NAME or "(trống)"))
    if ai.MODEL_PROVIDER in ("", "fake"):
        print("MODEL_PROVIDER đang trống hoặc fake nên chưa gọi model thật.")
        print("Mở .env, đặt MODEL_PROVIDER=deepseek (hoặc openai), MODEL_NAME, API_KEY rồi chạy lại.")
        return 0
    if not ai.API_KEY:
        print("API_KEY trong .env đang TRỐNG, nên chưa gọi model.")
        print("Cách làm: mở file .env ở gốc repo, điền API_KEY=<key của bạn> (không dấu ngoặc kép, không thừa dấu cách), lưu file,")
        print("rồi chạy lại: python scripts/smoke_model.py")
        print("Không dán key vào chat, code, ảnh chụp màn hình; .env đã nằm trong .gitignore.")
        return 0

    t0 = time.perf_counter()
    try:
        res = ai.call_model(SYSTEM, USER)
    except Exception as e:  # thông báo lỗi của ai.py đã che key
        print("Lỗi: %s: %s" % (type(e).__name__, e))
        return 1
    dt = time.perf_counter() - t0
    print("model: %s" % res["model"])
    print("tokens_in: %d · tokens_out: %d" % (res["tokens_in"], res["tokens_out"]))
    print("độ trễ: %.2f giây" % dt)
    print("trả lời (80 ký tự đầu): %s" % res["text"].strip().replace("\n", " ")[:80])
    if res["tokens_in"] <= 0 or res["tokens_out"] <= 0:
        print("⚠️ Token bằng 0: khung sẽ coi là chưa gọi model thật. Kiểm lại MODEL_PROVIDER / MODEL_NAME.")
        return 1
    print("Nối model được. KHÔNG chạy `python run.py eval` bằng model thật trước CP3.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
