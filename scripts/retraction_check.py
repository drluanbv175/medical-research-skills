#!/usr/bin/env python3
"""
retraction_check.py — Kiểm tra trích dẫn bị RÚT / đính chính, KHÔNG cần mạng.

VÌ SAO
------
Dữ liệu Retraction Watch đầy đủ nằm ở Crossref (`api.crossref.org`), thường bị
chính sách egress chặn. Nhưng connector Scite chạy server-side và trả trường
`editorialNotices` với đúng thông tin đó — đã đối chứng trên Mehra 2020 và
Wakefield 1998 (cả hai đều nhận diện `retracted` kèm DOI thông báo và ngày).

Script này lo hai đầu; lời gọi Scite ở giữa do agent thực hiện:

    1) extract  — rút DOI từ bản thảo/.bib  ->  danh sách dán vào Scite
    2) [agent gọi mcp__Scite__search_literature với dois=[...]]
    3) report   — đọc JSON Scite trả về      ->  bảng phán định

NGUYÊN TẮC AN TOÀN
------------------
DOI mà Scite KHÔNG trả về được xếp loại `CHUA_KIEM`, tuyệt đối không mặc định
là sạch. "Không tra được" khác "không bị rút".

CÁCH DÙNG
    python3 scripts/retraction_check.py extract manuscript.md
    python3 scripts/retraction_check.py extract refs.bib --json
    python3 scripts/retraction_check.py report scite_response.json --dois-from refs.bib
    cat scite.json | python3 scripts/retraction_check.py report -

MÃ THOÁT
    0  tất cả đã kiểm và sạch
    1  CÓ bài bị rút  (nghiêm trọng)
    2  có quan ngại / đính chính cần xem
    3  có DOI CHƯA kiểm được
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Iterable

# DOI theo khuyến nghị Crossref.
# LƯU Ý: DOI của Elsevier/Lancet CHỨA dấu ngoặc — 10.1016/S0140-6736(20)31180-6.
# Vì vậy regex phải NHẬN ngoặc, rồi mới cắt dấu câu thừa ở bước _trim().
# Loại ngoặc ra khỏi lớp ký tự sẽ cắt cụt DOI và làm lọt bài bị rút.
DOI_RE = re.compile(r'10\.\d{4,9}/[^\s"<>,;\]}]+', re.IGNORECASE)


def _trim(d: str) -> str:
    """Cắt dấu câu bám đuôi, giữ nguyên ngoặc thuộc về DOI.

    Chỉ bỏ ')' khi nó KHÔNG có '(' tương ứng — tức là ngoặc của câu văn,
    ví dụ '(10.1136/bmj.n71)' -> '10.1136/bmj.n71', trong khi
    '10.1016/S0140-6736(20)31180-6' được giữ nguyên vẹn.
    """
    while d:
        if d[-1] in '.,;:':
            d = d[:-1]
        elif d[-1] == ')' and d.count(')') > d.count('('):
            d = d[:-1]
        else:
            break
    return d

RETRACTED = "RUT_BAI"
CONCERN   = "QUAN_NGAI"
CORRECTED = "DINH_CHINH"
CLEAN     = "SACH"
UNCHECKED = "CHUA_KIEM"

# Ánh xạ chuỗi status của Scite -> phân loại của ta.
_STATUS = {
    "retracted": RETRACTED,
    "has retraction": RETRACTED,
    "has expression of concern": CONCERN,
    "expression of concern": CONCERN,
    "has correction": CORRECTED,
    "has erratum": CORRECTED,
    "correction": CORRECTED,
    "erratum": CORRECTED,
    # "comment" cố ý bỏ qua: bình luận học thuật KHÔNG phải tì vết.
}

SEVERITY = {RETRACTED: 4, UNCHECKED: 3, CONCERN: 2, CORRECTED: 1, CLEAN: 0}

# Giá trị cột RetractionNature trong bộ dữ liệu Retraction Watch.
_RW_NATURE = {
    "retraction": RETRACTED,
    "expression of concern": CONCERN,
    "correction": CORRECTED,
    "erratum": CORRECTED,
    # "reinstatement" xử lý riêng bên dưới: bài từng bị rút rồi được phục hồi.
}


def norm(doi: str) -> str:
    """Chuẩn hoá DOI để so khớp: bỏ tiền tố URL, hạ chữ thường, bỏ dấu cuối."""
    d = _trim(doi.strip())
    for pre in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/",
                "http://dx.doi.org/", "doi:", "DOI:"):
        if d.lower().startswith(pre.lower()):
            d = d[len(pre):]
    return d.lower()


def extract_dois(text: str) -> list[str]:
    """Rút DOI duy nhất, giữ thứ tự xuất hiện."""
    seen, out = set(), []
    for m in DOI_RE.findall(text):
        n = norm(m)
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def classify(notices: Iterable[dict]) -> tuple[str, list[dict]]:
    """Quy các editorialNotices về một phán định + danh sách notice liên quan."""
    verdict, hits = CLEAN, []
    for n in notices or []:
        kind = _STATUS.get(str(n.get("status", "")).strip().lower())
        if not kind:
            continue
        hits.append({"loai": kind, "status": n.get("status"),
                     "noticeDoi": n.get("noticeDoi"), "date": n.get("date")})
        if SEVERITY[kind] > SEVERITY[verdict]:
            verdict = kind
    return verdict, hits


def build_report(scite: dict, expected: list[str]) -> dict:
    """Ghép phản hồi Scite với danh sách DOI mong đợi."""
    by_doi = {}
    for hit in scite.get("hits", []) or []:
        d = norm(str(hit.get("doi", "")))
        if d:
            by_doi[d] = hit

    rows = []
    for doi in expected or list(by_doi):
        hit = by_doi.get(norm(doi))
        if hit is None:
            rows.append({"doi": doi, "phan_dinh": UNCHECKED, "tieu_de": None,
                         "notices": [], "ghi_chu": "Scite không trả về bản ghi cho DOI này."})
            continue
        verdict, hits = classify(hit.get("editorialNotices"))
        rows.append({"doi": doi, "phan_dinh": verdict,
                     "tieu_de": hit.get("title"), "notices": hits, "ghi_chu": None})

    tally = {k: sum(1 for r in rows if r["phan_dinh"] == k)
             for k in (RETRACTED, CONCERN, CORRECTED, CLEAN, UNCHECKED)}
    return {"tong": len(rows), "thong_ke": tally, "chi_tiet": rows}


def build_report_local(expected: list[str], found: dict, dataset_age=None) -> dict:
    """Dựng báo cáo từ bộ dữ liệu Retraction Watch TẢI VỀ MÁY.

    Khác biệt then chốt so với chế độ Scite: Retraction Watch là sổ đăng ký
    ĐẦY ĐỦ, nên một DOI không có trong đó thực sự nghĩa là "không có retraction
    nào được ghi nhận" — kết luận SACH, chứ không phải CHUA_KIEM.

    Điều đó chỉ đúng khi bộ dữ liệu còn mới. Bản cache cũ có thể bỏ sót bài vừa
    bị rút, nên tuổi dữ liệu luôn được ghi vào báo cáo.
    """
    rows = []
    for doi in expected:
        recs = found.get(norm(doi), [])
        if not recs:
            rows.append({"doi": doi, "phan_dinh": CLEAN, "tieu_de": None,
                         "notices": [], "ghi_chu": "Không có retraction nào được ghi nhận."})
            continue

        verdict, notices, reinstated = CLEAN, [], False
        title = None
        for r in recs:
            nature = (r.get("nature") or "").strip()
            title = title or (r.get("title") or None)
            if nature.lower().startswith("reinstatement"):
                reinstated = True
            kind = _RW_NATURE.get(nature.lower())
            if not kind:
                continue
            notices.append({"loai": kind, "status": nature,
                            "noticeDoi": r.get("retraction_doi"),
                            "date": r.get("retraction_date"),
                            "reason": (r.get("reason") or "")[:160]})
            if SEVERITY[kind] > SEVERITY[verdict]:
                verdict = kind

        note = None
        if reinstated and verdict == RETRACTED:
            # Bài từng bị rút rồi được phục hồi -> KHÔNG tự hạ xuống "sạch",
            # bắt buộc người đọc tự kiểm tra.
            verdict = CONCERN
            note = ("Có bản ghi REINSTATEMENT (phục hồi) bên cạnh retraction — "
                    "phải kiểm tra thủ công tình trạng hiện hành.")
        elif reinstated:
            note = "Có bản ghi REINSTATEMENT (phục hồi)."

        rows.append({"doi": doi, "phan_dinh": verdict, "tieu_de": title,
                     "notices": notices, "ghi_chu": note})

    tally = {k: sum(1 for r in rows if r["phan_dinh"] == k)
             for k in (RETRACTED, CONCERN, CORRECTED, CLEAN, UNCHECKED)}
    return {"tong": len(rows), "thong_ke": tally, "chi_tiet": rows,
            "nguon": "Retraction Watch (bộ dữ liệu cục bộ)",
            "tuoi_du_lieu_ngay": dataset_age}


def render(rep: dict) -> str:
    t, lines = rep["thong_ke"], []
    lines.append("")
    lines.append("=" * 72)
    lines.append(f"  KIỂM TRA TRÍCH DẪN BỊ RÚT / ĐÍNH CHÍNH")
    lines.append(f"  Nguồn: {rep.get('nguon', 'Scite MCP')}")
    age = rep.get("tuoi_du_lieu_ngay")
    if age is not None:
        warn = "  ← CŨ, nên tải lại" if age > 30 else ""
        lines.append(f"  Tuổi dữ liệu: {age:.0f} ngày{warn}")
    lines.append("=" * 72)
    lines.append(f"  Tổng số DOI      : {rep['tong']}")
    lines.append(f"  BỊ RÚT           : {t[RETRACTED]}")
    lines.append(f"  Quan ngại        : {t[CONCERN]}")
    lines.append(f"  Có đính chính    : {t[CORRECTED]}")
    lines.append(f"  Sạch             : {t[CLEAN]}")
    lines.append(f"  CHƯA kiểm được   : {t[UNCHECKED]}")
    lines.append("-" * 72)

    order = {RETRACTED: 0, UNCHECKED: 1, CONCERN: 2, CORRECTED: 3, CLEAN: 4}
    mark = {RETRACTED: "[!! RÚT BÀI !!]", UNCHECKED: "[?  CHƯA KIỂM ]",
            CONCERN: "[!  QUAN NGẠI]", CORRECTED: "[~  ĐÍNH CHÍNH]", CLEAN: "[   sạch     ]"}
    for r in sorted(rep["chi_tiet"], key=lambda x: order[x["phan_dinh"]]):
        lines.append(f"  {mark[r['phan_dinh']]}  {r['doi']}")
        if r["tieu_de"]:
            lines.append(f"        {r['tieu_de'][:96]}")
        for n in r["notices"]:
            lines.append(f"        → {n['status']} | notice {n['noticeDoi']} | {n['date']}")
        if r["ghi_chu"]:
            lines.append(f"        → {r['ghi_chu']}")

    lines.append("-" * 72)
    if t[RETRACTED]:
        lines.append("  HÀNH ĐỘNG: GỠ NGAY các trích dẫn bị rút khỏi bản thảo,")
        lines.append("  hoặc nếu buộc phải nhắc tới thì ghi rõ '(đã bị rút)'.")
    if t[UNCHECKED]:
        lines.append("  CẢNH BÁO: các DOI 'CHƯA KIỂM' KHÔNG được coi là sạch.")
        lines.append("  Phải nêu rõ trong báo cáo là chưa xác minh được tình trạng rút bài.")
    if not t[RETRACTED] and not t[UNCHECKED] and not t[CONCERN]:
        lines.append("  Không phát hiện bài bị rút hay bị nêu quan ngại.")
    lines.append("=" * 72)
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("extract", help="Rút DOI từ file, xuất danh sách cho Scite.")
    e.add_argument("file")
    e.add_argument("--json", action="store_true", help="Xuất mảng JSON.")

    l = sub.add_parser("local", help="Tra bằng bộ dữ liệu Retraction Watch TẢI VỀ MÁY "
                                     "(đầy đủ, không cần mạng).")
    l.add_argument("file", help="Bản thảo / .bib chứa DOI.")
    l.add_argument("--json", action="store_true", help="Xuất JSON.")

    r = sub.add_parser("report", help="Đọc JSON Scite trả về, in bảng phán định.")
    r.add_argument("scite_json", help="Đường dẫn file JSON, hoặc '-' để đọc stdin.")
    r.add_argument("--dois-from", help="File gốc, để phát hiện DOI mà Scite bỏ sót.")
    r.add_argument("--json", action="store_true", help="Xuất JSON thay vì bảng.")

    a = ap.parse_args()

    if a.cmd == "extract":
        dois = extract_dois(open(a.file, encoding="utf-8", errors="replace").read())
        if a.json:
            print(json.dumps(dois, ensure_ascii=False, indent=2))
        else:
            if not dois:
                print("Không tìm thấy DOI nào.", file=sys.stderr)
                return 0
            print(f"# {len(dois)} DOI — dán vào tham số `dois` của mcp__Scite__search_literature")
            print(json.dumps(dois, ensure_ascii=False))
        return 0

    if a.cmd == "local":
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "tools"))
        try:
            import tai_retraction_watch as rw
        except ImportError:
            print("Không nạp được tools/tai_retraction_watch.py", file=sys.stderr)
            return 2

        dois = extract_dois(open(a.file, encoding="utf-8", errors="replace").read())
        if not dois:
            print("Không tìm thấy DOI nào trong file.", file=sys.stderr)
            return 0
        try:
            found = rw.tra_cuu(dois)
        except FileNotFoundError as exc:
            print(f"\n{exc}\n", file=sys.stderr)
            return 3

        rep = build_report_local(dois, found, rw.tuoi_cache())
        print(json.dumps(rep, ensure_ascii=False, indent=2) if a.json else render(rep))
        t = rep["thong_ke"]
        if t[RETRACTED]:
            return 1
        if t[CONCERN] or t[CORRECTED]:
            return 2
        return 0

    raw = sys.stdin.read() if a.scite_json == "-" else \
        open(a.scite_json, encoding="utf-8", errors="replace").read()
    try:
        scite = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"JSON không hợp lệ: {exc}", file=sys.stderr)
        return 2

    expected = []
    if a.dois_from:
        expected = extract_dois(open(a.dois_from, encoding="utf-8", errors="replace").read())

    rep = build_report(scite, expected)
    print(json.dumps(rep, ensure_ascii=False, indent=2) if a.json else render(rep))

    t = rep["thong_ke"]
    if t[RETRACTED]:
        return 1
    if t[UNCHECKED]:
        return 3
    if t[CONCERN] or t[CORRECTED]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
