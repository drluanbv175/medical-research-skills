#!/usr/bin/env python3
"""
kiem_tra_plugin.py — Kiểm tra Claude Code có đang nạp BẢN MỚI của kho skill không.

VÌ SAO CẦN
----------
Kho này khai báo `source: "./"`, nên khi cài, Claude Code SAO CHÉP toàn bộ kho
vào ~/.claude/plugins/cache/<marketplace>/<plugin>/<commit>/.

Hệ quả dễ nhầm: `git pull` cập nhật thư mục làm việc của bạn, nhưng KHÔNG chạm
tới bản sao mà Claude Code đang chạy. Bạn có thể đang ở commit mới nhất trong
Terminal mà Claude Code vẫn nạp skill từ ảnh chụp cũ hàng tháng trời.

Script này CHỈ ĐỌC, không sửa gì. Nó cho biết:
  * Claude Code đang ghim commit nào
  * Kho của bạn đang ở commit nào
  * Nội dung trong cache là bản cũ hay mới
  * Cần làm gì tiếp

CÁCH DÙNG
    python3 tools/kiem_tra_plugin.py

MÃ THOÁT
    0 cache đã là bản mới · 1 cache CŨ, cần cập nhật · 2 không tìm thấy cài đặt
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

# Dấu hiệu chỉ có ở bản mới: khối định tuyến nguồn chèn vào 34 SKILL.md.
MARKER = "evidence-source-routing"
EXPECTED_MARKED = 34
PLUGINS = os.path.join(os.path.expanduser("~"), ".claude", "plugins")

TTY = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
G, R, Y, D, B, X = (("\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")
                    if TTY else ("",) * 6)


def _load(name: str) -> dict:
    try:
        with open(os.path.join(PLUGINS, name), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _repo_head() -> str:
    """Commit hiện tại của kho chứa script này."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _count_marker(path: str) -> int:
    """Đếm SKILL.md đã có khối định tuyến trong một thư mục."""
    n = 0
    for base, _dirs, files in os.walk(path):
        for f in files:
            if f != "SKILL.md":
                continue
            try:
                with open(os.path.join(base, f), encoding="utf-8", errors="ignore") as fh:
                    if MARKER in fh.read():
                        n += 1
            except Exception:
                pass
    return n


def main() -> int:
    print(f"\n{B}KIỂM TRA PLUGIN CLAUDE CODE — kho medical-research-skills{X}")
    print("=" * 68)

    if not os.path.isdir(PLUGINS):
        print(f"  {R}Không tìm thấy {PLUGINS}{X}")
        print("  Có vẻ bạn chưa cài kho này làm plugin Claude Code.")
        return 2

    # --- marketplace ---
    km = _load("known_marketplaces.json")
    mk_name = mk_kind = mk_loc = ""
    for k, v in km.items():
        if "aipoch" in k.lower() or "medical-research" in k.lower():
            mk_name = k
            src = (v or {}).get("source", {}) or {}
            mk_kind = src.get("source", "?")
            mk_loc = src.get("url") or src.get("path") or "?"
            print(f"\n{B}Marketplace{X}")
            print(f"  tên       : {mk_name}")
            print(f"  kiểu nguồn: {mk_kind}")
            print(f"  nguồn     : {mk_loc}")
            print(f"  cập nhật  : {(v or {}).get('lastUpdated', '?')}")
            break
    if not mk_name:
        print(f"  {Y}Không thấy marketplace nào tên chứa 'aipoch'.{X}")
        print(f"  Các marketplace đang có: {', '.join(km) or '(trống)'}")

    # --- plugin đã cài ---
    ip = _load("installed_plugins.json")
    pinned = install_path = ""
    for k, entries in (ip.get("plugins") or {}).items():
        if "aipoch" not in k.lower() and "medical-research" not in k.lower():
            continue
        print(f"\n{B}Plugin đã cài{X}")
        print(f"  khoá      : {k}")
        for e in (entries if isinstance(entries, list) else [entries]):
            print(f"  - scope   : {e.get('scope', '?')}")
            print(f"    đường dẫn: {e.get('installPath', '?')}")
            print(f"    commit   : {e.get('gitCommitSha', '(không ghi)')}")
            print(f"    cài lúc  : {e.get('installedAt', '?')}")
            pinned = pinned or (e.get("gitCommitSha") or "")
            install_path = install_path or (e.get("installPath") or "")
        break

    # --- nội dung thực sự trong cache ---
    cache = os.path.join(PLUGINS, "cache")
    roots = []
    if os.path.isdir(cache):
        for d in os.listdir(cache):
            if "aipoch" in d.lower() or "medical-research" in d.lower():
                roots.append(os.path.join(cache, d))
    if install_path and os.path.isdir(install_path):
        roots.append(install_path)

    # Khử trùng: installPath thường NẰM TRONG thư mục cache, quét cả hai sẽ
    # đếm mỗi SKILL.md hai lần. Giữ thư mục cha, bỏ thư mục con lồng bên trong.
    real = sorted({os.path.realpath(r) for r in roots})
    roots = [r for r in real
             if not any(r != o and r.startswith(o + os.sep) for o in real)]

    print(f"\n{B}Nội dung Claude Code đang nạp{X}")
    total = 0
    if not roots:
        print(f"  {Y}Không thấy thư mục cache nào của kho này.{X}")
    for r in roots:
        n = _count_marker(r)
        total += n
        snaps = []
        try:
            for base, dirs, _f in os.walk(r):
                for d in dirs:
                    if len(d) >= 8 and all(c in "0123456789abcdef" for c in d[:8]):
                        snaps.append(d)
                break
        except Exception:
            pass
        print(f"  {r}")
        if snaps:
            print(f"    ảnh chụp : {', '.join(sorted(set(snaps))[:5])}")
        print(f"    SKILL.md có định tuyến mới: {n}")

    head = _repo_head()
    print(f"\n{B}So sánh{X}")
    print(f"  Kho của bạn (HEAD)     : {head[:12] or '?'}")
    print(f"  Claude Code đang ghim  : {pinned[:12] or '(không ghi)'}")
    print(f"  SKILL.md mới trong cache: {total} / {EXPECTED_MARKED}")

    print("\n" + "=" * 68)
    if total >= EXPECTED_MARKED:
        print(f"{G}{B}KẾT LUẬN: ĐÃ CẬP NHẬT.{X}")
        print("  Claude Code đang nạp bản skill mới nhất. Không cần làm gì thêm.")
        print("=" * 68 + "\n")
        return 0

    print(f"{R}{B}KẾT LUẬN: CACHE CÒN CŨ — bản sửa CHƯA có hiệu lực.{X}")
    print(f"  Chỉ {total}/{EXPECTED_MARKED} SKILL.md có định tuyến mới.")
    print(f"\n{B}Cần làm:{X}")
    print("  1. Mở Claude Code, gõ:  /plugin")
    print(f"  2. Chọn marketplace '{mk_name or 'aipoch-medical-research'}' → Cập nhật")
    print("  3. Cập nhật tiếp plugin bên trong marketplace đó")
    print("  4. Chạy lại script này để xác nhận")
    if mk_kind == "git":
        print(f"\n  {D}Nguồn là git ({mk_loc}) — cập nhật sẽ kéo lại từ GitHub.{X}")
        print(f"  {D}Hãy chắc GitHub đã có bản mới (main = {head[:12] or '?'}).{X}")
    elif mk_kind == "directory":
        print(f"\n  {D}Nguồn là thư mục cục bộ ({mk_loc}).{X}")
        print(f"  {D}Hãy chắc thư mục đó đã `git pull` lên bản mới.{X}")
    print("=" * 68 + "\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
