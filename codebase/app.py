"""Khung chạy bản chạy thử tối thiểu (dòng lệnh): gõ đầu vào → answer() trong agent.py → in kết quả.

Chạy bằng: python run.py   (macOS/Linux có thể là python3, Windows có thể là py)
Nhóm thay bằng giao diện của mình (web, bot…) nhưng giữ `python run.py` là lệnh duy nhất
để chạy bản chạy thử (sửa hàm run_app() trong run.py nếu cần).

Bộ nhớ hội thoại (codebase/session.py): mỗi lần chạy app là MỘT cuộc trò chuyện riêng (một phiên), agent nhớ dữ kiện
và vài lượt gần nhất trong cuộc đó. Gõ /moi (hoặc /reset) để xóa và bắt đầu lại. Không lưu gì xuống đĩa.
"""
import os
import sys
import time

for _stream in (sys.stdout, sys.stderr, sys.stdin):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _where(e):
    """File (trong codebase/) gây lỗi khi nạp: SyntaxError có e.filename, lỗi khác lấy khung cuối của traceback."""
    import traceback
    path = getattr(e, "filename", None) or (traceback.extract_tb(e.__traceback__)[-1].filename if e.__traceback__ else "")
    if not path:
        return "codebase/"
    p = os.path.abspath(path)
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.relpath(p, base).replace(os.sep, "/") if p.startswith(base) else path

def main() -> int:
    try:
        import tracing
        import agent
        import demo_ui
        from agent import answer
        from session import ChatSession
    except Exception as e:  # lỗi cú pháp, thiếu thư viện… trong codebase/
        print("Không nạp được codebase/ — lỗi ở %s: %s: %s" % (_where(e), type(e).__name__, e))
        print("Sửa lỗi rồi chạy lại. Cách nối model: docs/connect-model.md")
        return 1
    print("Bản chạy thử — gõ đầu vào rồi Enter. Thoát: Ctrl+C (hoặc Enter 2 lần với dòng trống).")
    session = ChatSession()
    print("(%s Gõ /moi để bắt đầu lại.)" % session.status())
    agent.on_step = lambda name: print("   " + demo_ui.STEP_TEXT.get(name, "…"), flush=True)
    print("(Lệnh: /moi bắt đầu lại · /goc xem bản gốc của câu trả lời vừa rồi, có dòng NHAN / CAN_CU.)")
    shown_disclaimer, last_raw = False, ""
    blank = 0
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not text:
            blank += 1
            if blank >= 2:
                return 0
            continue
        blank = 0
        if text.lower() in ("/moi", "/mới", "/reset"):
            session.reset()
            shown_disclaimer, last_raw = False, ""
            print("(Đã xóa cuộc trò chuyện. %s)" % session.status())
            continue
        if text.lower() in ("/goc", "/gốc"):
            print(last_raw or "(Chưa có câu trả lời nào.)")
            continue
        tracing.begin("app")
        t0 = time.perf_counter()
        try:
            result = answer(text, session=session)
        except NotImplementedError as e:
            tracing.end()
            print("Chưa nối model: %s" % e)
            return 1
        except KeyboardInterrupt:
            tracing.end()
            print("\n(Đã dừng câu này. Bạn có thể hỏi tiếp.)")
            continue
        except Exception as e:  # lỗi bất ngờ: câu thân thiện, KHÔNG in nội dung lỗi / stack trace
            _, events = tracing.end()
            print(demo_ui.friendly_error(events=events, exc=e))
            print("   " + demo_ui.FOOTER)
            continue
        s, events = tracing.end()
        output = result.get("output", "") if isinstance(result, dict) else str(result)
        last_raw = output
        nice = demo_ui.friendly_error(output, events)
        print(nice if nice else demo_ui.pretty(output, show_full_disclaimer=not shown_disclaimer))
        shown_disclaimer = shown_disclaimer or "Lưu ý:" in output
        t = demo_ui.step_timings(events, time.perf_counter() - t0)
        print("   (model: %s · gọi model %d lần · công cụ %d lần · token vào %d / ra %d · %.1f s: trích %.1f, tra cứu %.1f, "
              "quyết định %.1f)" % (", ".join(s["models"]) or "—", s["model_calls"], s["tool_calls"], s["tokens_in"],
                                    s["tokens_out"], t["tong"], t["trich"], t["tra_cuu"], t["quyet_dinh"]))
        print("   (%s)" % session.status())


if __name__ == "__main__":
    sys.exit(main())
