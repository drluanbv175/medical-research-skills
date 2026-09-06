#!/usr/bin/env python3
"""
lam_moi_plugin.py — Làm mới thủ công cache plugin Claude Code.

CẢNH BÁO — ĐỌC TRƯỚC KHI CHẠY
-----------------------------
Đây KHÔNG phải cách chính thức. Cách chính thức là lệnh /plugin trong Claude Code
hoặc giao diện quản lý plugin của ứng dụng Claude. Chỉ dùng script này khi cả hai
đường đó không dùng được.

Script can thiệp vào trạng thái nội bộ của Claude Code:
  * chép kho vào một thư mục cache mới đặt tên theo commit hiện tại
  * cập nhật installPath và gitCommitSha trong installed_plugins.json

Nó KHÔNG xoá gì. Cache cũ giữ nguyên, mọi file JSON được sao lưu trước khi sửa,
và script in sẵn lệnh hoàn tác. Nếu Claude Code còn bookkeeping khác mà script
chưa biết (ví dụ .install-manifests), plugin có thể lỗi — khi đó hãy hoàn tác
rồi cài lại marketplace.

CÁCH DÙNG
    python3 tools/lam_moi_plugin.py --thu        # chạy thử, không sửa gì
    python3 tools/lam_moi_plugin.py --that       # thực hiện
    python3 tools/lam_moi_plugin.py --hoan-tac   # phục hồi từ sao lưu gần nhất

MÃ THOÁT
    0 thành công · 1 lỗi · 2 không tìm thấy cài đặt
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

PLUGINS = os.path.join(os.path.expanduser("~"), ".claude", "plugins")
BACKUP = os.path.join(PLUGINS, "backup-truoc-khi-lam-moi")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "evidence-source-routing"

# Không chép những thứ này vào cache: nặng, vô nghĩa, hoặc là dữ liệu cục bộ.
BO_QUA = shutil.ignore_patterns(
    ".git", "__pycache__", "*.pyc", ".DS_Store", "node_modules",
    "*.sqlite3", "retraction_watch.csv", "backup-*",
)


def _head() -> str:
    r = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                       capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        raise RuntimeError(f"Không đọc được commit của kho: {r.stderr.strip()}")
    return r.stdout.strip()


def _sach() -> bool:
    r = subprocess.run(["git", "-C", REPO, "status", "--porcelain"],
                       capture_output=True, text=True, timeout=20)
    return r.returncode == 0 and not r.stdout.strip()


def _tim_plugin(ip: dict):
    for khoa, ds in (ip.get("plugins") or {}).items():
        if "aipoch" in khoa.lower() or "medical-research" in khoa.lower():
            return khoa, (ds if isinstance(ds, list) else [ds])
    return None, []


def _sao_luu() -> str:
    os.makedirs(BACKUP, exist_ok=True)
    dau = datetime.now().strftime("%Y%m%d-%H%M%S")
    thu_muc = os.path.join(BACKUP, dau)
    os.makedirs(thu_muc, exist_ok=True)
    for ten in ("installed_plugins.json", "known_marketplaces.json"):
        goc = os.path.join(PLUGINS, ten)
        if os.path.isfile(goc):
            shutil.copy2(goc, os.path.join(thu_muc, ten))
    return thu_muc


def hoan_tac() -> int:
    if not os.path.isdir(BACKUP):
        print("Không có bản sao lưu nào.", file=sys.stderr)
        return 1
    ban = sorted(os.listdir(BACKUP))
    if not ban:
        print("Thư mục sao lưu trống.", file=sys.stderr)
        return 1
    moi_nhat = os.path.join(BACKUP, ban[-1])
    for ten in os.listdir(moi_nhat):
        shutil.copy2(os.path.join(moi_nhat, ten), os.path.join(PLUGINS, ten))
        print(f"  phục hồi {ten}")
    print(f"\n✓ Đã phục hồi từ {moi_nhat}")
    print("  Khởi động lại Claude Code để nó đọc lại cấu hình.\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--thu", action="store_true", help="Chạy thử, không sửa gì.")
    g.add_argument("--that", action="store_true", help="Thực hiện thật.")
    g.add_argument("--hoan-tac", action="store_true", help="Phục hồi sao lưu gần nhất.")
    a = ap.parse_args()

    if a.hoan_tac:
        return hoan_tac()

    if not os.path.isdir(PLUGINS):
        print(f"Không tìm thấy {PLUGINS} — chưa cài plugin Claude Code.", file=sys.stderr)
        return 2

    ip_path = os.path.join(PLUGINS, "installed_plugins.json")
    try:
        with open(ip_path, encoding="utf-8") as fh:
            ip = json.load(fh)
    except Exception as e:
        print(f"Không đọc được {ip_path}: {e}", file=sys.stderr)
        return 2

    khoa, entries = _tim_plugin(ip)
    if not khoa:
        print("Không thấy plugin nào tên chứa 'aipoch' trong installed_plugins.json.",
              file=sys.stderr)
        return 2

    # Chỉ chặn khi THỰC HIỆN thật. Chạy thử chỉ đọc nên luôn cho phép,
    # để người dùng xem được tình trạng ngay cả khi kho đang dở dang.
    if a.that and not _sach():
        print("Kho còn thay đổi chưa commit — commit hoặc stash trước cho chắc chắn.",
              file=sys.stderr)
        print("(Dùng --thu để xem trước mà không cần kho sạch.)", file=sys.stderr)
        return 1

    head = _head()
    cu = entries[0].get("installPath", "")
    goc_cache = os.path.dirname(cu) if cu else ""
    if not goc_cache or not os.path.isdir(os.path.dirname(goc_cache)):
        print(f"installPath bất thường: {cu!r}", file=sys.stderr)
        return 1
    moi = os.path.join(goc_cache, head[:12])

    print(f"\n  Plugin        : {khoa}")
    print(f"  Cache hiện tại: {cu}")
    print(f"  Cache sẽ tạo  : {moi}")
    print(f"  Commit kho    : {head[:12]}")
    print(f"  Commit đang ghim: {(entries[0].get('gitCommitSha') or '?')[:12]}")

    if a.thu:
        print("\n  [CHẠY THỬ] Không sửa gì. Dùng --that để thực hiện.\n")
        return 0

    thu_muc_bak = _sao_luu()
    print(f"\n  ✓ Đã sao lưu JSON vào {thu_muc_bak}")

    if os.path.isdir(moi):
        shutil.rmtree(moi)
    shutil.copytree(REPO, moi, ignore=BO_QUA, symlinks=False)
    n = 0
    for base, _d, files in os.walk(moi):
        for f in files:
            if f == "SKILL.md":
                try:
                    with open(os.path.join(base, f), encoding="utf-8", errors="ignore") as fh:
                        if MARKER in fh.read():
                            n += 1
                except Exception:
                    pass
    print(f"  ✓ Đã chép kho vào cache ({n} SKILL.md có định tuyến mới)")

    for e in entries:
        e["installPath"] = moi
        e["gitCommitSha"] = head
        e["lastUpdated"] = datetime.now().astimezone().isoformat()
    with open(ip_path, "w", encoding="utf-8") as fh:
        json.dump(ip, fh, indent=2, ensure_ascii=False)
    print("  ✓ Đã cập nhật installed_plugins.json")

    print(f"\n  Cache cũ vẫn còn ở {cu} (không xoá, để hoàn tác được).")
    print("  KHỞI ĐỘNG LẠI Claude Code, rồi kiểm tra:")
    print("      python3 tools/kiem_tra_plugin.py")
    print("  Nếu plugin lỗi, hoàn tác:")
    print("      python3 tools/lam_moi_plugin.py --hoan-tac\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
