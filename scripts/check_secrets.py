"""Quét chuỗi giống KEY / dữ liệu cá nhân trước khi commit / push. Chạy offline, không gọi mạng, không in giá trị đầy đủ.

    python scripts/check_secrets.py              # quét mọi file git đang theo dõi
    python scripts/check_secrets.py --staged     # quét nội dung SẮP commit (git diff --cached) — dùng trong hook
    python scripts/check_secrets.py a.py b.md    # quét các file chỉ định

Mã thoát: 0 = sạch (có thể có CẢNH BÁO dữ liệu cá nhân) · 1 = có chuỗi giống key/secret (CHẶN) · 2 = lỗi chạy.
--strict: coi cả cảnh báo dữ liệu cá nhân (email, SĐT VN, CCCD) là chặn.

Phát hiện (CHẶN): sk-… (OpenAI / DeepSeek / Anthropic sk-ant-…), "Bearer <token>", ghp_/github_pat_, AKIA…, AIza…,
xox…-, khóa riêng PEM, và chuỗi dài ngẫu nhiên gán cho biến tên *KEY* / *TOKEN* / *SECRET* / *PASSWORD*.
Phát hiện (CẢNH BÁO): email, SĐT Việt Nam, CCCD 12 số.
Cho phép: key GIẢ trong tests/ có dấu hiệu giả rõ ràng (FAKE_MARKERS, vd sk-TESTKEY-…); email miền ví dụ
(ALLOWED_EMAIL_DOMAINS); dòng có chú thích "check-secrets: allow" (dùng dè dặt, người review phải thấy).
.env không bao giờ được theo dõi; nếu có trong danh sách quét thì CHẶN ngay.
"""
import argparse
import math
import os
import re
import subprocess
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_BYTES = 2_000_000
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".pptx", ".docx", ".xlsx", ".ico", ".mp4", ".woff", ".woff2"}
FAKE_MARKERS = ("testkey", "khongphaikey", "0123456789", "1234567890", "abcdef", "example", "fake", "dummy", "xxxx")
ALLOWED_EMAIL_DOMAINS = ("example.com", "example.org", "example.net", "test", "localhost", "users.noreply.github.com",
                         "anthropic.com")
PRAGMA = "check-secrets: allow"

KEY_RULES = [
    ("sk-key", re.compile(r"(?<![\w-])sk-(?:ant-|proj-)?[A-Za-z0-9_\-]{20,}")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/\-]{20,}=*")),
    ("github", re.compile(r"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}")),
    ("aws", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
    ("google", re.compile(r"\bAIza[A-Za-z0-9_\-]{30,}")),
    ("slack", re.compile(r"\bxox[abpr]-[A-Za-z0-9\-]{10,}")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("assigned-secret", re.compile(r"(?i)\b[\w.]*(?:api_?key|secret|token|password|passwd)[\w.]*\s*[:=]\s*['\"]?"
                                   r"(?P<val>[A-Za-z0-9_\-+/=.]{20,})")),
]
PII_RULES = [
    ("email", re.compile(r"(?<![\w.+-])[\w.+-]+@([\w-]+(?:\.[\w-]+)+)")),
    ("sdt", re.compile(r"(?<![\w+\-])(?:\+?84|0)(?:[\s.\-]?\d){9}(?!\d)")),
    ("cccd", re.compile(r"(?<!\d)\d{12}(?!\d)")),
]


def entropy(s: str) -> float:
    """Entropy Shannon theo ký tự (bit/ký tự): chuỗi ngẫu nhiên ~4+, tên biến / câu chữ thấp hơn."""
    if not s:
        return 0.0
    freq = {c: s.count(c) for c in set(s)}
    return -sum(n / len(s) * math.log2(n / len(s)) for n in freq.values())


def is_fake(value: str, path: str) -> bool:
    low = value.lower()
    return path.replace("\\", "/").startswith("tests/") and any(m in low for m in FAKE_MARKERS)


def mask(value: str) -> str:
    """Không bao giờ in giá trị đầy đủ: 4 ký tự đầu + độ dài."""
    return "%s…(%d ký tự)" % (value[:4], len(value))


def scan_text(path: str, text: str):
    """→ danh sách (mức, loại, số dòng, giá trị đã che). mức: 'CHẶN' hoặc 'CẢNH BÁO'."""
    found = []
    for no, line in enumerate(text.splitlines(), 1):
        if PRAGMA in line:
            continue
        for kind, rx in KEY_RULES:
            for m in rx.finditer(line):
                val = m.group("val") if "val" in rx.groupindex else m.group(0)
                # gán cho biến tên *KEY*/*TOKEN*…: chỉ chặn chuỗi trông ngẫu nhiên (entropy cao, có cả chữ và số),
                # không chặn tên biến / câu chữ dài
                if kind == "assigned-secret" and (entropy(val) < 3.5 or not any(c.isdigit() for c in val)
                                                  or not any(c.isalpha() for c in val) or "os.environ" in line):
                    continue
                if is_fake(val, path):
                    continue
                found.append(("CHẶN", kind, no, mask(val)))
        for kind, rx in PII_RULES:
            for m in rx.finditer(line):
                if kind == "email" and m.group(1).lower().endswith(ALLOWED_EMAIL_DOMAINS):
                    continue
                if kind == "email" and is_fake(m.group(0), path):
                    continue
                found.append(("CẢNH BÁO", kind, no, mask(m.group(0))))
    return found


def git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8", "replace")


def targets(staged: bool, paths):
    """→ danh sách (đường dẫn, nội dung)."""
    if paths:
        return [(p, open(os.path.join(ROOT, p) if not os.path.isabs(p) else p, encoding="utf-8", errors="replace").read())
                for p in paths]
    if staged:
        names = [n for n in git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines() if n]
        return [(n, git("show", ":" + n)) for n in names if os.path.splitext(n)[1].lower() not in SKIP_EXT]
    out = []
    for n in git("ls-files").splitlines():
        full = os.path.join(ROOT, n)
        if not n or os.path.splitext(n)[1].lower() in SKIP_EXT or not os.path.isfile(full):
            continue
        if os.path.getsize(full) > MAX_BYTES:
            continue
        out.append((n, open(full, encoding="utf-8", errors="replace").read()))
    return out


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Quét chuỗi giống key / dữ liệu cá nhân (offline)")
    ap.add_argument("--staged", action="store_true", help="quét nội dung sắp commit")
    ap.add_argument("--strict", action="store_true", help="cảnh báo dữ liệu cá nhân cũng chặn")
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args(argv)
    try:
        files = targets(args.staged, args.paths)
    except (subprocess.CalledProcessError, OSError) as e:
        print("Không quét được: %s" % type(e).__name__)
        return 2
    block = warn = 0
    for path, text in files:
        if os.path.basename(path) == ".env":
            print("CHẶN  %s: file .env không được commit (đã có trong .gitignore)" % path)
            block += 1
            continue
        for level, kind, no, val in scan_text(path, text):
            print("%-8s %s:%d  %s  %s" % (level, path, no, kind, val))
            block += level == "CHẶN"
            warn += level == "CẢNH BÁO"
    print("Đã quét %d file: %d chặn, %d cảnh báo." % (len(files), block, warn))
    if block or (args.strict and warn):
        print("DỪNG: gỡ chuỗi trên (key thật: thu hồi ngay trên trang nhà cung cấp). Key giả trong tests/ cần dấu hiệu giả "
              "rõ ràng (vd sk-TESTKEY-…), hoặc thêm chú thích '%s' nếu chắc chắn." % PRAGMA)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
