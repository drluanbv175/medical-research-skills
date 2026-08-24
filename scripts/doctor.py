#!/usr/bin/env python3
"""
doctor.py — Kiểm tra sức khoẻ toàn bộ hạ tầng nguồn chứng cứ.
Health check for the medical evidence stack.

Chạy được ở CẢ HAI môi trường và cho kết luận đúng cho từng nơi:
  * Máy cá nhân (không proxy)  -> chạy kiểm thử SỐNG với nguồn thật
  * Claude Code on the web     -> phát hiện egress bị chặn, chỉ đường MCP

CÁCH DÙNG
    python3 scripts/doctor.py            # kiểm tra đầy đủ
    python3 scripts/doctor.py --quick    # bỏ qua kiểm thử sống
    python3 scripts/doctor.py --json     # cho máy đọc

MÃ THOÁT
    0  mọi thứ tốt — nguồn thông, kiểm thử sống đạt
    1  nguồn bị chính sách egress chặn (dùng MCP, hoặc chạy trên máy cá nhân)
    2  vấn đề cài đặt (thiếu Python/phụ thuộc/file)
    3  nguồn thông nhưng kiểm thử sống THẤT BẠI
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import evidence_net as en  # noqa: E402

TTY = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
G, R, Y, D, B, X = (("\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")
                    if TTY else ("",) * 6)
OK, BAD, WARN = f"{G}✓{X}", f"{R}✗{X}", f"{Y}!{X}"

# Script đã được vá để thất bại ỒN ÀO thay vì trả kết quả rỗng.
PATCHED = [
    "scientific-skills/Other/search-pubmed/scripts/search_pubmed.py",
    "scientific-skills/data-analysis/meta-title-generator/scripts/search_pubmed.py",
    "scientific-skills/academic-writing/literature-review/scripts/verify_citations.py",
    "scientific-skills/evidence-insight/citation-management/scripts/validate_citations.py",
]
TOOLS = ["scripts/evidence_net.py", "scripts/check_evidence_sources.py",
         "scripts/retraction_check.py", "references/EVIDENCE-SOURCE-ROUTING.md"]


class Report:
    def __init__(self) -> None:
        self.sections: list[dict] = []
        self.problems: list[str] = []

    def add(self, name: str, rows: list[tuple[str, str, str]]) -> None:
        self.sections.append({"name": name, "rows": rows})

    def fail(self, msg: str) -> None:
        self.problems.append(msg)


def sec_environment(rep: Report) -> bool:
    """Trả True nếu đang chạy sau egress proxy."""
    proxied = bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"))
    rows = [
        ("Hệ điều hành", "info", f"{platform.system()} {platform.release()}"),
        ("Python", "ok" if sys.version_info >= (3, 10) else "bad",
         f"{platform.python_version()}" + ("" if sys.version_info >= (3, 10) else " — cần >= 3.10")),
        ("Egress proxy", "warn" if proxied else "ok",
         (f"CÓ ({os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')}) "
          "— môi trường sandbox" if proxied else "KHÔNG — mạng trực tiếp")),
    ]
    if sys.version_info < (3, 10):
        rep.fail("Python quá cũ (cần >= 3.10).")
    rep.add("Môi trường", rows)
    return proxied


def sec_deps(rep: Report) -> None:
    rows = []
    try:
        import requests  # noqa: F401
        rows.append(("requests", "ok", f"đã cài ({requests.__version__})"))
    except ImportError:
        rows.append(("requests", "warn",
                     "CHƯA cài — validate_citations/verify_citations cần. `pip install requests`"))
    rep.add("Phụ thuộc", rows)


def sec_files(rep: Report) -> None:
    rows = []
    for rel in TOOLS + PATCHED:
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            rows.append((rel, "ok", "có"))
        else:
            rows.append((rel, "bad", "THIẾU"))
            rep.fail(f"Thiếu file: {rel}")
    rep.add("Tệp hạ tầng", rows)


def sec_sources(rep: Report) -> tuple[list[str], list[str]]:
    import concurrent.futures
    names = list(en.SOURCES)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        res = dict(zip(names, pool.map(lambda n: en.probe(n, 12.0), names)))
    rows, blocked, broken = [], [], []
    for n, (ok_, diag) in res.items():
        if ok_:
            rows.append((n, "ok", en.SOURCES[n]["host"]))
        elif diag and diag.blocked_by_policy:
            blocked.append(n)
            rows.append((n, "bad", f"{en.SOURCES[n]['host']} — BỊ CHẶN (chính sách egress)"))
        else:
            broken.append(n)
            rows.append((n, "warn", f"{en.SOURCES[n]['host']} — {diag.kind if diag else '?'}"))
    rep.add("Nguồn chứng cứ", rows)
    return blocked, broken


def sec_live(rep: Report) -> bool:
    """Kiểm thử SỐNG với nguồn thật. Chỉ chạy khi đường mạng thông."""
    rows, ok_all = [], True

    # 1) PubMed phải trả về số lượng > 0 cho một truy vấn chắc chắn có bài.
    try:
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
               + urllib.parse.urlencode({"db": "pubmed", "term": "metformin",
                                         "retmode": "json", "retmax": "1"}))
        n = int(en.urlopen_json(url, 25)["esearchresult"]["count"])
        good = n > 0
        ok_all &= good
        rows.append(("PubMed esearch", "ok" if good else "bad", f"{n:,} kết quả cho 'metformin'"))
    except en.SourceUnavailable as e:
        ok_all = False
        rows.append(("PubMed esearch", "bad", f"{e.kind}: {e.detail[:80]}"))

    # 2) Crossref phải phân giải được một DOI có thật.
    try:
        d = en.urlopen_json("https://api.crossref.org/works/10.1136/bmj.n71", 25)
        title = (d.get("message", {}).get("title") or [""])[0]
        good = "PRISMA" in title.upper()
        ok_all &= good
        rows.append(("Crossref phân giải DOI", "ok" if good else "bad", title[:70] or "(rỗng)"))
    except en.SourceUnavailable as e:
        ok_all = False
        rows.append(("Crossref phân giải DOI", "bad", f"{e.kind}: {e.detail[:80]}"))

    # 3) Crossref phải đánh dấu bài Wakefield 1998 là đã bị rút.
    #    Mang tính THAM KHẢO: độ phủ Retraction Watch qua Crossref không đồng đều,
    #    nên không đạt thì cảnh báo chứ không tính là hỏng.
    try:
        d = en.urlopen_json("https://api.crossref.org/works/10.1016/S0140-6736(97)11096-0", 25)
        msg = d.get("message", {})
        blob = json.dumps(msg.get("update-to", [])) + json.dumps(msg.get("relation", {}))
        if "retraction" in blob.lower():
            rows.append(("Crossref bắt bài bị rút", "ok", "Wakefield 1998 → retraction ✓"))
        else:
            rows.append(("Crossref bắt bài bị rút", "warn",
                         "không thấy cờ retraction — dùng Scite MCP để kiểm chéo"))
    except en.SourceUnavailable as e:
        rows.append(("Crossref bắt bài bị rút", "warn", f"{e.kind}"))

    rep.add("Kiểm thử sống", rows)
    if not ok_all:
        rep.fail("Kiểm thử sống thất bại dù đường mạng thông.")
    return ok_all


def sec_behaviour(rep: Report) -> None:
    """Xác nhận script đã vá thất bại ỒN ÀO, không trả kết quả rỗng."""
    import subprocess
    rows = []
    sp = os.path.join(ROOT, PATCHED[0])
    try:
        r = subprocess.run([sys.executable, sp, "test query"], capture_output=True,
                           text=True, timeout=90)
        payload = json.loads(r.stdout.strip().splitlines()[0])
        status, total = payload.get("status"), payload.get("total")
        if status == "ok" and isinstance(total, int):
            rows.append(("search-pubmed", "ok", f"status=ok, total={total:,}"))
        elif status == "unavailable" and total is None and r.returncode == 3:
            rows.append(("search-pubmed", "warn",
                         "status=unavailable, exit 3 — thất bại ỒN ÀO, đúng thiết kế"))
        else:
            rows.append(("search-pubmed", "bad",
                         f"phản hồi bất thường: status={status} total={total} exit={r.returncode}"))
            rep.fail("search_pubmed.py trả về trạng thái không mong đợi.")
    except Exception as e:  # noqa: BLE001
        rows.append(("search-pubmed", "bad", f"không chạy được: {e}"))
        rep.fail("Không chạy được search_pubmed.py.")
    rep.add("Hành vi an toàn", rows)


def render(rep: Report, blocked, broken, live_ok, proxied) -> None:
    icon = {"ok": OK, "bad": BAD, "warn": WARN, "info": f"{D}·{X}"}
    print(f"\n{B}KIỂM TRA SỨC KHOẺ — HẠ TẦNG NGUỒN CHỨNG CỨ Y KHOA{X}")
    for s in rep.sections:
        print(f"\n{B}{s['name']}{X}")
        w = max((len(r[0]) for r in s["rows"]), default=10)
        for label, st, detail in s["rows"]:
            print(f"  {icon[st]} {label:<{w}}  {D}{detail}{X}")

    print("\n" + "=" * 74)
    if blocked:
        print(f"{R}{B}KẾT LUẬN: {len(blocked)} nguồn bị chính sách egress chặn.{X}")
        print("\nHai đường đi hợp lệ:")
        print(f"  {B}1. Dùng MCP connector{X} — chạy server-side, không qua tường lửa này.")
        print("     PubMed · Clinical Trials · Scite · Consensus · Elicit · Scholar Gateway · bioRxiv")
        print(f"     Đã nối sẵn trong 34 SKILL.md. Xem {en.ROUTING_DOC}")
        print(f"  {B}2. Chạy trên máy cá nhân{X} — không có egress proxy, mọi REST API thông.")
        print("     git pull origin main && python3 scripts/doctor.py")
        print(f"\n{Y}KHÔNG{X} tắt xác thực TLS, {Y}KHÔNG{X} bỏ HTTPS_PROXY, "
              f"{Y}KHÔNG{X} đi vòng qua mirror.")
    elif rep.problems:
        print(f"{Y}{B}KẾT LUẬN: nguồn thông nhưng có vấn đề cần xử lý.{X}")
        for p in rep.problems:
            print(f"  {BAD} {p}")
    else:
        print(f"{G}{B}KẾT LUẬN: TẤT CẢ THÔNG.{X}")
        print("  Mọi nguồn truy cập được và kiểm thử sống đều đạt.")
        print("  Toàn bộ skill REST (Europe PMC, Unpaywall, Gene/ClinVar, DailyMed, Crossref)")
        print("  dùng được đầy đủ — không cần mở khoá gì thêm.")
    if broken:
        print(f"\n{Y}Lưu ý:{X} {len(broken)} nguồn lỗi vì lý do khác: {', '.join(broken)}")
    print("=" * 74 + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra sức khoẻ hạ tầng nguồn chứng cứ.")
    ap.add_argument("--quick", action="store_true", help="Bỏ qua kiểm thử sống.")
    ap.add_argument("--json", action="store_true", help="Xuất JSON.")
    a = ap.parse_args()

    rep = Report()
    proxied = sec_environment(rep)
    sec_deps(rep)
    sec_files(rep)
    blocked, broken = sec_sources(rep)

    live_ok = None
    if not blocked and not a.quick:
        live_ok = sec_live(rep)
    sec_behaviour(rep)

    if a.json:
        print(json.dumps({
            "proxied": proxied, "blocked": blocked, "other_failures": broken,
            "live_tests_passed": live_ok, "problems": rep.problems,
            "sections": rep.sections,
        }, ensure_ascii=False, indent=2))
    else:
        render(rep, blocked, broken, live_ok, proxied)

    if blocked:
        return 1
    if live_ok is False:
        return 3
    if rep.problems:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
