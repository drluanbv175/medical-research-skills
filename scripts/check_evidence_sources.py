#!/usr/bin/env python3
"""
check_evidence_sources.py — Kiểm tra nguồn chứng cứ nào đang truy cập được.
Check which medical evidence sources are reachable from this environment.

DÙNG KHI NÀO
  - Trước khi chạy một skill tra cứu y văn, để biết đường mạng có thông không.
  - Khi một skill trả về 0 kết quả và bạn cần biết đó là "không có bài" hay
    "không tra được".

CÁCH DÙNG
    python3 scripts/check_evidence_sources.py           # dò tất cả
    python3 scripts/check_evidence_sources.py pubmed crossref
    python3 scripts/check_evidence_sources.py --json    # cho máy đọc
    python3 scripts/check_evidence_sources.py --quiet   # chỉ mã thoát

MÃ THOÁT / EXIT CODES
    0  tất cả nguồn được kiểm đều vào được
    1  có nguồn bị CHẶN bởi chính sách egress
    2  có nguồn lỗi vì lý do khác (DNS/TLS/timeout)
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import evidence_net as en  # noqa: E402

GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    ("\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")
    if sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
    else ("", "", "", "", "", "")
)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Kiểm tra khả năng truy cập các nguồn chứng cứ y khoa.")
    ap.add_argument("sources", nargs="*",
                    help=f"Tên nguồn cần kiểm ({', '.join(en.SOURCES)}). Bỏ trống = tất cả.")
    ap.add_argument("--json", action="store_true", help="Xuất JSON.")
    ap.add_argument("--quiet", "-q", action="store_true", help="Không in gì, chỉ trả mã thoát.")
    ap.add_argument("--timeout", type=float, default=15.0, help="Thời gian chờ mỗi nguồn (giây).")
    args = ap.parse_args()

    names = args.sources or list(en.SOURCES)
    unknown = [n for n in names if n not in en.SOURCES]
    if unknown:
        print(f"Nguồn không rõ: {', '.join(unknown)}", file=sys.stderr)
        print(f"Nguồn hợp lệ  : {', '.join(en.SOURCES)}", file=sys.stderr)
        return 2

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(zip(names, pool.map(lambda n: en.probe(n, args.timeout), names)))

    blocked = [n for n, (ok, d) in results.items() if not ok and d and d.blocked_by_policy]
    broken = [n for n, (ok, d) in results.items() if not ok and d and not d.blocked_by_policy]

    if args.json:
        payload = {
            "ok": not blocked and not broken,
            "blocked_by_policy": blocked,
            "other_failures": broken,
            "sources": {
                n: {
                    "reachable": ok,
                    "host": en.SOURCES[n]["host"],
                    "purpose": en.SOURCES[n]["purpose"],
                    "kind": (d.kind if d else None),
                    "detail": (d.detail if d else None),
                    "mcp_alternative": en.SOURCES[n]["mcp"],
                }
                for n, (ok, d) in results.items()
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif not args.quiet:
        _render(results, blocked, broken)

    if blocked:
        return 1
    if broken:
        return 2
    return 0


def _render(results, blocked, broken) -> None:
    width = max(len(n) for n in results)
    print()
    print(f"{BOLD}Khả năng truy cập nguồn chứng cứ y khoa{RESET}")
    print("-" * (width + 46))
    for name, (ok, diag) in results.items():
        if ok:
            mark, note = f"{GREEN}[ VÀO ĐƯỢC ]{RESET}", ""
        elif diag and diag.blocked_by_policy:
            mark, note = f"{RED}[ BỊ  CHẶN ]{RESET}", "chính sách egress"
        else:
            mark, note = f"{YELLOW}[  LỖI     ]{RESET}", (diag.kind if diag else "?")
        print(f"  {mark}  {name:<{width}}  {DIM}{en.SOURCES[name]['host']}{RESET}"
              + (f"  {DIM}({note}){RESET}" if note else ""))
    print("-" * (width + 46))

    if not blocked and not broken:
        print(f"{GREEN}Tất cả nguồn đều truy cập được.{RESET}\n")
        return

    if blocked:
        print()
        print(f"{RED}{BOLD}{len(blocked)} nguồn bị chính sách egress chặn.{RESET}")
        print("Request không rời khỏi hạ tầng (403 ở bước CONNECT).")
        print()
        print(f"{BOLD}Mở khóa:{RESET} claude.ai › Settings › Claude Code › Environments")
        print("  → nới network policy, hoặc thêm các host sau vào allowlist:")
        for n in blocked:
            print(f"      {en.SOURCES[n]['host']:<32} {DIM}{en.SOURCES[n]['purpose']}{RESET}")
        print()
        print(f"{BOLD}Dùng được ngay (MCP chạy server-side, không qua tường lửa này):{RESET}")
        for n in blocked:
            mcp = en.SOURCES[n]["mcp"]
            if mcp.startswith("KHÔNG"):
                print(f"  {YELLOW}✗{RESET} {n:<16} {mcp}")
            else:
                print(f"  {GREEN}✓{RESET} {n:<16} {mcp}")

    if broken:
        print()
        print(f"{YELLOW}{BOLD}{len(broken)} nguồn lỗi vì lý do khác:{RESET}")
        for n in broken:
            diag = results[n][1]
            print(f"  {n:<16} {diag.kind}: {diag.detail[:110]}")

    print()
    print(f"{BOLD}Nguyên tắc an toàn:{RESET} nguồn không tra được KHÁC với 'không có bằng chứng'.")
    print("Không kết luận lâm sàng và không bịa trích dẫn khi nguồn chưa xác minh được.")
    print(f"Chi tiết định tuyến nguồn: {en.ROUTING_DOC}")
    print()


if __name__ == "__main__":
    raise SystemExit(main())
