#!/usr/bin/env python3
"""
tai_retraction_watch.py — Tải bộ dữ liệu Retraction Watch về máy và lập chỉ mục.

VÌ SAO CÓ CÔNG CỤ NÀY
---------------------
Kiểm bài bị rút qua connector Scite hoạt động tốt nhưng chỉ mục của Scite KHÔNG
phủ 100%: một DOI có thật vẫn có thể không nằm trong đó, và khi ấy công cụ buộc
phải xếp "CHƯA KIỂM" thay vì kết luận.

Bộ dữ liệu Retraction Watch — do Crossref mua lại năm 2023 và phát hành miễn phí
— là sổ đăng ký retraction đầy đủ. Tải một lần về máy thì:
  * tra offline, không phụ thuộc mạng hay chỉ mục bên thứ ba
  * phủ đầy đủ, nên "không có trong bộ dữ liệu" mới thực sự nghĩa là
    "không có retraction nào được ghi nhận"
  * nhanh: tra hàng nghìn DOI trong vài giây

CHỈ CHẠY ĐƯỢC Ở NƠI CÓ MẠNG TỚI CROSSREF. Trong Claude Code on the web,
api.crossref.org bị chính sách egress chặn — hãy chạy trên máy cá nhân.

CÁCH DÙNG
    python3 tools/tai_retraction_watch.py tai
    python3 tools/tai_retraction_watch.py tai --via-git     # bền hơn cho file lớn
    python3 tools/tai_retraction_watch.py trangthai
    python3 tools/tai_retraction_watch.py tra 10.1016/S0140-6736(97)11096-0

Nguồn: https://gitlab.com/crossref/retraction-watch-data (cập nhật mỗi ngày làm
việc). Không cần khoá API, không cần đăng ký. Tuỳ chọn --email chỉ được đưa vào
User-Agent cho lịch sự.

MÃ THOÁT
    0 thành công · 1 không tải được · 2 lỗi tham số/dữ liệu · 3 chưa có cache
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

try:
    import evidence_net as en
except ImportError:  # chạy độc lập ngoài kho
    en = None

# Thư mục cache: theo XDG nếu có, không thì ~/.cache
CACHE = os.path.join(
    os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache"),
    "medical-research-skills", "retractionwatch",
)
CSV_PATH = os.path.join(CACHE, "retractionwatch.csv")
DB_PATH = os.path.join(CACHE, "index.sqlite3")
META_PATH = os.path.join(CACHE, "meta.json")

# Điểm tải chính thức. LƯU Ý LỊCH SỬ: endpoint cũ
# https://api.labs.crossref.org/data/retractionwatch đã NGỪNG hoạt động —
# Crossref ghi rõ nó trả về dữ liệu lỗi thời. Bộ dữ liệu hiện phát hành qua
# GitLab, cập nhật mỗi ngày làm việc.
BASE_URL = "https://gitlab.com/crossref/retraction-watch-data/-/raw/main/retraction_watch.csv"
REPO_URL = "https://gitlab.com/crossref/retraction-watch-data.git"
CSV_NAME = "retraction_watch.csv"

# Số ngày sau đó coi bộ dữ liệu là CŨ. Retraction mới xuất hiện liên tục,
# nên một bản cache cũ có thể BỎ SÓT bài vừa bị rút.
STALE_DAYS = 30

# Tên cột có thể thay đổi giữa các bản phát hành -> dò theo nhiều biến thể.
COLUMNS = {
    "doi":     ["originalpaperdoi", "original paper doi", "originaldoi"],
    "nature":  ["retractionnature", "retraction nature", "nature"],
    "rdoi":    ["retractiondoi", "retraction doi"],
    "rdate":   ["retractiondate", "retraction date"],
    "reason":  ["reason", "reasons"],
    "title":   ["title"],
    "journal": ["journal"],
}


# --------------------------------------------------------------------------
def norm_doi(doi: str) -> str:
    """Chuẩn hoá DOI để so khớp. Dùng chung logic với retraction_check.py."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        from retraction_check import norm
        return norm(doi)
    except Exception:
        d = (doi or "").strip().lower()
        for pre in ("https://doi.org/", "http://doi.org/", "doi:"):
            if d.startswith(pre):
                d = d[len(pre):]
        while d and (d[-1] in ".,;:" or (d[-1] == ")" and d.count(")") > d.count("("))):
            d = d[:-1]
        return d


def _human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024.0
    return f"{n:.1f} GB"


def _map_columns(header: list[str]) -> dict[str, int]:
    """Ánh xạ tên cột thật -> chỉ số, chấp nhận biến thể tên."""
    lower = [h.strip().lower().replace("_", "").replace("-", "") for h in header]
    out: dict[str, int] = {}
    for key, alts in COLUMNS.items():
        for alt in alts:
            a = alt.replace(" ", "").replace("_", "").replace("-", "")
            if a in lower:
                out[key] = lower.index(a)
                break
    return out


# --------------------------------------------------------------------------
def tai(email: str = "", url: str | None = None, force: bool = False) -> int:
    os.makedirs(CACHE, exist_ok=True)
    src = url or BASE_URL

    if os.path.isfile(CSV_PATH) and not force:
        age = (time.time() - os.path.getmtime(CSV_PATH)) / 86400
        if age < 1:
            print(f"Đã có bản tải hôm nay ({_human(os.path.getsize(CSV_PATH))}). "
                  f"Dùng --force để tải lại.")
            return dung_chi_muc()

    print(f"Tải từ : {src}")
    if email:
        print(f"Liên hệ: {email}")
    print("(Bộ dữ liệu vài chục MB — có thể mất một lúc)\n")

    ua = f"medical-research-skills/1.0" + (f" (mailto:{email})" if email else "")
    req = urllib.request.Request(src, headers={
        "User-Agent": ua,
        "Accept": "text/csv, application/csv, */*",
    })
    tmp = CSV_PATH + ".part"
    sha = hashlib.sha256()
    try:
        with urllib.request.urlopen(req, timeout=180) as resp, open(tmp, "wb") as fh:
            total = int(resp.headers.get("Content-Length") or 0)
            got = moc = 0
            while True:
                chunk = resp.read(1 << 16)
                if not chunk:
                    break
                fh.write(chunk)
                sha.update(chunk)
                got += len(chunk)
                # Chỉ vẽ thanh tiến độ khi xuất ra terminal. Khi bị chuyển hướng
                # (log, pipe), ký tự \r không xoá dòng nên sẽ sinh hàng nghìn dòng rác.
                if sys.stdout.isatty():
                    if total:
                        print(f"\r  {_human(got)} / {_human(total)}  "
                              f"({got * 100 // total}%)", end="", flush=True)
                    else:
                        print(f"\r  {_human(got)}", end="", flush=True)
                elif total and got * 10 // total > moc:
                    moc = got * 10 // total
                    print(f"  {moc * 10}% ({_human(got)})", flush=True)
        if sys.stdout.isatty():
            print()
    except Exception as exc:  # noqa: BLE001
        if os.path.exists(tmp):
            os.remove(tmp)
        if en is not None:
            diag = en.classify(exc, src)
            print(diag.report(), file=sys.stderr)
            if diag.blocked_by_policy:
                print("  gitlab.com bị chặn trong môi trường này.", file=sys.stderr)
                print("  → Chạy lệnh này trên MÁY CÁ NHÂN, nơi không có egress proxy.",
                      file=sys.stderr)
        else:
            print(f"\nTải thất bại: {exc}", file=sys.stderr)
        return 1

    # Kiểm tra thứ tải về đúng là CSV Retraction Watch, không phải trang lỗi HTML.
    with open(tmp, "r", encoding="utf-8", errors="replace") as fh:
        head = fh.readline()
    if not head or "," not in head:
        os.remove(tmp)
        print(f"Nội dung tải về không phải CSV. Dòng đầu: {head[:120]!r}", file=sys.stderr)
        return 2
    cols = _map_columns(next(csv.reader(io.StringIO(head))))
    if "doi" not in cols or "nature" not in cols:
        os.remove(tmp)
        print("CSV thiếu cột bắt buộc (OriginalPaperDOI / RetractionNature).", file=sys.stderr)
        print(f"Cột đọc được: {head[:300]}", file=sys.stderr)
        return 2

    os.replace(tmp, CSV_PATH)
    with open(META_PATH, "w", encoding="utf-8") as fh:
        json.dump({
            "source": BASE_URL,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "bytes": os.path.getsize(CSV_PATH),
            "sha256": sha.hexdigest(),
        }, fh, ensure_ascii=False, indent=2)
    print(f"✓ Đã tải {_human(os.path.getsize(CSV_PATH))}\n")
    return dung_chi_muc()


def tai_bang_git(force: bool = False) -> int:
    """Tải bằng `git clone/pull` thay vì HTTP.

    Bền hơn cho file lớn, và các lần sau chỉ kéo phần thay đổi thay vì tải lại
    toàn bộ. Cần có `git` trên máy.
    """
    import shutil
    import subprocess

    if shutil.which("git") is None:
        print("Không tìm thấy `git`. Dùng cách tải HTTP (bỏ --via-git).", file=sys.stderr)
        return 2

    os.makedirs(CACHE, exist_ok=True)
    repo = os.path.join(CACHE, "repo")
    try:
        if os.path.isdir(os.path.join(repo, ".git")) and not force:
            print(f"Cập nhật kho sẵn có: {repo}")
            r = subprocess.run(["git", "-C", repo, "pull", "--ff-only"],
                               capture_output=True, text=True, timeout=600)
        else:
            if os.path.isdir(repo):
                shutil.rmtree(repo)
            print(f"Clone {REPO_URL}\n(bộ dữ liệu vài chục MB — có thể mất một lúc)")
            r = subprocess.run(["git", "clone", "--depth", "1", REPO_URL, repo],
                               capture_output=True, text=True, timeout=1800)
        if r.returncode != 0:
            print(f"git thất bại:\n{(r.stderr or r.stdout)[:800]}", file=sys.stderr)
            return 1
    except subprocess.TimeoutExpired:
        print("git quá thời gian chờ.", file=sys.stderr)
        return 1

    src_csv = os.path.join(repo, CSV_NAME)
    if not os.path.isfile(src_csv):
        found = [f for f in os.listdir(repo) if f.lower().endswith(".csv")]
        if not found:
            print(f"Không thấy CSV nào trong {repo}", file=sys.stderr)
            return 2
        src_csv = os.path.join(repo, found[0])
        print(f"Dùng {found[0]} (tên file khác mặc định).")

    import shutil as _sh
    _sh.copyfile(src_csv, CSV_PATH)
    with open(META_PATH, "w", encoding="utf-8") as fh:
        json.dump({"source": REPO_URL,
                   "downloaded_at": datetime.now(timezone.utc).isoformat(),
                   "bytes": os.path.getsize(CSV_PATH), "sha256": None,
                   "via": "git"}, fh, ensure_ascii=False, indent=2)
    print(f"✓ Đã lấy {_human(os.path.getsize(CSV_PATH))}\n")
    return dung_chi_muc()


def dung_chi_muc() -> int:
    """Dựng chỉ mục SQLite từ CSV để tra nhanh theo DOI."""
    if not os.path.isfile(CSV_PATH):
        print("Chưa có CSV. Chạy: tai_retraction_watch.py tai --email ...", file=sys.stderr)
        return 3

    print("Đang dựng chỉ mục...")
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
        DROP TABLE IF EXISTS retraction;
        CREATE TABLE retraction (
            doi TEXT NOT NULL, nature TEXT, retraction_doi TEXT,
            retraction_date TEXT, reason TEXT, title TEXT, journal TEXT
        );
    """)
    n = skipped = 0
    with open(CSV_PATH, "r", encoding="utf-8", errors="replace", newline="") as fh:
        rdr = csv.reader(fh)
        cols = _map_columns(next(rdr))
        get = lambda row, k: (row[cols[k]].strip() if k in cols and cols[k] < len(row) else "")
        rows = []
        for row in rdr:
            doi = norm_doi(get(row, "doi"))
            if not doi:
                skipped += 1
                continue
            rows.append((doi, get(row, "nature"), get(row, "rdoi"), get(row, "rdate"),
                         get(row, "reason"), get(row, "title"), get(row, "journal")))
            if len(rows) >= 5000:
                con.executemany("INSERT INTO retraction VALUES (?,?,?,?,?,?,?)", rows)
                n += len(rows); rows = []
        if rows:
            con.executemany("INSERT INTO retraction VALUES (?,?,?,?,?,?,?)", rows)
            n += len(rows)
    con.execute("CREATE INDEX idx_doi ON retraction(doi)")
    con.commit()
    con.close()
    print(f"✓ Chỉ mục xong: {n:,} bản ghi"
          + (f" ({skipped:,} dòng thiếu DOI, bỏ qua)" if skipped else ""))
    print(f"  {DB_PATH}\n")
    return 0


# --------------------------------------------------------------------------
def _meta() -> dict:
    try:
        with open(META_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def tuoi_cache() -> float | None:
    """Số ngày kể từ lần tải gần nhất; None nếu chưa có."""
    m = _meta()
    if not m.get("downloaded_at"):
        return None
    try:
        dl = datetime.fromisoformat(m["downloaded_at"])
        return (datetime.now(timezone.utc) - dl).total_seconds() / 86400
    except Exception:
        return None


def san_sang() -> bool:
    return os.path.isfile(DB_PATH)


def tra_cuu(dois: list[str]) -> dict[str, list[dict]]:
    """Tra một loạt DOI trong bộ dữ liệu cục bộ.

    Trả dict: doi_chuẩn_hoá -> danh sách bản ghi (rỗng nghĩa là KHÔNG có
    retraction nào được ghi nhận trong bộ dữ liệu).
    """
    if not san_sang():
        raise FileNotFoundError(
            f"Chưa có chỉ mục cục bộ tại {DB_PATH}. "
            "Chạy: python3 tools/tai_retraction_watch.py tai --email ban@vidu.com")
    con = sqlite3.connect(DB_PATH)
    out: dict[str, list[dict]] = {}
    for raw in dois:
        d = norm_doi(raw)
        cur = con.execute(
            "SELECT nature, retraction_doi, retraction_date, reason, title, journal "
            "FROM retraction WHERE doi = ?", (d,))
        out[d] = [dict(zip(("nature", "retraction_doi", "retraction_date",
                            "reason", "title", "journal"), r)) for r in cur.fetchall()]
    con.close()
    return out


def trangthai() -> int:
    m, age = _meta(), tuoi_cache()
    print("\nTrạng thái bộ dữ liệu Retraction Watch")
    print("-" * 56)
    print(f"  Thư mục   : {CACHE}")
    if not os.path.isfile(CSV_PATH):
        print("  Trạng thái: CHƯA TẢI")
        print("\n  Chạy: python3 tools/tai_retraction_watch.py tai --email ban@vidu.com\n")
        return 3
    print(f"  CSV       : {_human(os.path.getsize(CSV_PATH))}")
    print(f"  Chỉ mục   : {'có' if san_sang() else 'CHƯA DỰNG'}")
    if san_sang():
        con = sqlite3.connect(DB_PATH)
        n = con.execute("SELECT COUNT(*) FROM retraction").fetchone()[0]
        u = con.execute("SELECT COUNT(DISTINCT doi) FROM retraction").fetchone()[0]
        con.close()
        print(f"  Bản ghi   : {n:,}  ({u:,} DOI duy nhất)")
    print(f"  Tải lúc   : {m.get('downloaded_at', '?')}")
    if age is not None:
        if age > STALE_DAYS:
            print(f"  Tuổi      : {age:.0f} ngày — CŨ, nên tải lại "
                  f"(bài mới bị rút có thể chưa có)")
        else:
            print(f"  Tuổi      : {age:.0f} ngày — còn dùng tốt")
    print("-" * 56 + "\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("tai", help="Tải bộ dữ liệu và dựng chỉ mục.")
    d.add_argument("--email", default=os.environ.get("CROSSREF_MAILTO", ""),
                   help="Email liên hệ (TUỲ CHỌN, chỉ đưa vào User-Agent).")
    d.add_argument("--via-git", action="store_true",
                   help="Tải bằng git clone/pull thay vì HTTP (bền hơn, cập nhật tăng dần).")
    d.add_argument("--url", help="Ghi đè URL nguồn (dùng khi Crossref đổi điểm tải).")
    d.add_argument("--force", action="store_true", help="Tải lại dù đã có bản hôm nay.")

    sub.add_parser("chimuc", help="Dựng lại chỉ mục từ CSV đã tải.")
    sub.add_parser("trangthai", help="Xem trạng thái cache.")

    q = sub.add_parser("tra", help="Tra thử một hoặc nhiều DOI.")
    q.add_argument("dois", nargs="+")

    a = ap.parse_args()

    if a.cmd == "tai":
        if a.via_git:
            return tai_bang_git(a.force)
        if a.email and "@" not in a.email:
            print("Email không hợp lệ. Bỏ --email hoặc nhập đúng dạng.", file=sys.stderr)
            return 2
        return tai(a.email, a.url, a.force)
    if a.cmd == "chimuc":
        return dung_chi_muc()
    if a.cmd == "trangthai":
        return trangthai()
    if a.cmd == "tra":
        try:
            res = tra_cuu(a.dois)
        except FileNotFoundError as e:
            print(e, file=sys.stderr)
            return 3
        age = tuoi_cache()
        if age is not None and age > STALE_DAYS:
            print(f"! Bộ dữ liệu đã {age:.0f} ngày tuổi — nên tải lại.\n", file=sys.stderr)
        for doi, recs in res.items():
            if not recs:
                print(f"  [ sạch ]  {doi}  — không có retraction nào được ghi nhận")
            for r in recs:
                print(f"  [{r['nature'] or '?'}]  {doi}")
                print(f"        ngày {r['retraction_date'] or '?'} | "
                      f"notice {r['retraction_doi'] or '?'}")
                if r["reason"]:
                    print(f"        lý do: {r['reason'][:110]}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
