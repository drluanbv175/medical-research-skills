#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""don_dep_may_that.py — Dọn rác trên MÁY THẬT của bác sĩ (không phải phiên cloud này).

VÌ SAO CÓ
=========
Bác sĩ hỏi có thể dọn bớt gì trong thư mục "Claude AI" (OneDrive, máy Mac/Windows)
không. Phiên cloud này KHÔNG có quyền truy cập máy đó — không đọc, không xoá,
không kiểm được gì ở đó từ xa. Công cụ này được VIẾT SẴN để bác sĩ tự chạy trên
chính máy mình.

BỐN LOẠI RÁC — chỉ động vào loại có thể XÁC MINH ĐƯỢC là an toàn
==================================================================
  1. CACHE TÁI SINH — __pycache__/, *.pyc, .pytest_cache/, .mypy_cache/,
     .ruff_cache/, .DS_Store, ._* — an toàn tuyệt đối, tự sinh lại khi cần.
  2. CACHE PLUGIN CŨ — ~/.claude/plugins/cache/<chợ>/<plugin>/<commit>/ — Claude
     Code KHÔNG BAO GIỜ tự xoá bản cache cũ khi plugin cập nhật (đã xác nhận
     bằng cách đọc chính tools/lam_moi_plugin.py: "Cache cũ vẫn còn... không
     xoá, để hoàn tác được"). Qua nhiều lần cập nhật, các commit cũ chất đống.
     Công cụ này CHỈ xoá commit KHÔNG còn được installed_plugins.json trỏ tới
     — tức không plugin nào đang thật sự dùng.
  3. MRAQ100_AUDIT/tools/ — theo tools/mraq_kappa/BLIND_RATING_GUIDE.md (trong
     medical-ebm-automation): bộ công cụ κ đã CHUYỂN vào git tại
     medical-ebm-automation/tools/mraq_kappa/ từ 15/07/2026. Bản cũ ở
     MRAQ100_AUDIT/tools/ (ngoài git) có thể còn sót lại. CHỈ đề xuất xoá nếu
     diff xác nhận giống hệt bản đã chuyển — khác một byte cũng dừng, không đoán.
  4. CONFLICT-COPY ONEDRIVE — KHÔNG tự kiểm ở đây để tránh hai bản logic trôi
     nhau; dùng thẳng `python3 tools/sync_safety_check.py` đã có sẵn và được
     kiểm kỹ trong ebm-drluanbv175 (làn ① của dong_bo_tat_ca.py).

AN TOÀN
=======
- Mặc định CHỈ KIỂM, in ra sẽ xoá gì + giải phóng bao nhiêu, KHÔNG xoá gì.
- Chỉ xoá thật khi có `--ap-dung`.
- KHÔNG BAO GIỜ xoá: bất kỳ thứ gì không khớp chính xác một trong 3 loại có thể
  xác minh ở trên. Nghi ngờ → bỏ qua, in ra để người xem, không đoán.
- Loại 2 (cache plugin) chỉ xoá commit không được TRỎ TỚI bởi bất kỳ entry nào
  trong installed_plugins.json của BẤT KỲ plugin nào (không riêng plugin của
  dự án này) — tránh xoá nhầm cache của plugin khác đang dùng.

CÁCH DÙNG
    python3 tools/don_dep_may_that.py                       # chỉ kiểm
    python3 tools/don_dep_may_that.py --goc "~/OneDrive/Claude AI"  # chỉ định gốc quét loại 1+3
    python3 tools/don_dep_may_that.py --ap-dung              # xoá thật

MÃ THOÁT
    0 không có gì để dọn (hoặc đã dọn xong)  ·  1 có thứ để dọn (chế độ kiểm)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

CACHE_TEN = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
CACHE_HAU_TO = (".pyc", ".pyo")
CACHE_TEN_FILE = {".DS_Store"}


def _kich_thuoc(p: Path) -> int:
    if p.is_file():
        try:
            return p.stat().st_size
        except OSError:
            return 0
    tong = 0
    for f in p.rglob("*"):
        if f.is_file():
            try:
                tong += f.stat().st_size
            except OSError:
                pass
    return tong


def _doc_dep(n: int) -> str:
    for don, ky in ((1024**3, "GB"), (1024**2, "MB"), (1024, "KB")):
        if n >= don:
            return f"{n / don:.1f} {ky}"
    return f"{n} B"


# --------------------------------------------------------- Loại 1: cache tái sinh
def quet_cache_tai_sinh(goc: Path) -> list[tuple[Path, int]]:
    """Trả [(đường_dẫn, byte)] cho từng thư mục/file cache tìm thấy dưới `goc`."""
    ket: list[tuple[Path, int]] = []
    if not goc.is_dir():
        return ket
    for base, dirs, files in os.walk(goc):
        basep = Path(base)
        # Đừng đi sâu vào .git — quét cache bên trong .git là vô nghĩa và chậm.
        dirs[:] = [d for d in dirs if d != ".git"]
        for d in list(dirs):
            if d in CACHE_TEN:
                p = basep / d
                ket.append((p, _kich_thuoc(p)))
                dirs.remove(d)  # không đi sâu thêm vào trong cache đã bắt
        for f in files:
            if f in CACHE_TEN_FILE or f.startswith("._") or f.endswith(CACHE_HAU_TO):
                p = basep / f
                ket.append((p, _kich_thuoc(p)))
    return ket


# --------------------------------------------------------- Loại 2: cache plugin cũ
def duong_dan_plugin_claude() -> Path:
    return Path.home() / ".claude" / "plugins"


def doc_installed_plugins(goc_plugin: Path) -> dict:
    f = goc_plugin / "installed_plugins.json"
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def duong_dan_dang_dung(du_lieu: dict) -> set[str]:
    """Tập realpath các installPath đang được installed_plugins.json trỏ tới."""
    dung: set[str] = set()
    for entries in (du_lieu.get("plugins") or {}).values():
        for e in (entries if isinstance(entries, list) else [entries]):
            ip = (e or {}).get("installPath")
            if ip:
                dung.add(str(Path(ip).resolve()))
    return dung


def quet_cache_plugin_cu(goc_plugin: Path) -> list[tuple[Path, int]]:
    """Mỗi thư mục <chợ>/<plugin>/<commit>/ dưới cache/ mà KHÔNG có installPath
    nào (của bất kỳ plugin nào) trỏ vào — tức là ảnh chụp cũ, không ai dùng."""
    cache = goc_plugin / "cache"
    if not cache.is_dir():
        return []
    dang_dung = duong_dan_dang_dung(doc_installed_plugins(goc_plugin))
    ket: list[tuple[Path, int]] = []
    for cho in sorted(p for p in cache.iterdir() if p.is_dir()):
        for plugin in sorted(p for p in cho.iterdir() if p.is_dir()):
            for commit in sorted(p for p in plugin.iterdir() if p.is_dir()):
                if str(commit.resolve()) in dang_dung:
                    continue
                # Phòng hờ: nếu chính plugin cha (không phải commit con) được
                # trỏ tới trực tiếp (source: "./" không lồng theo commit ở vài
                # bản Claude Code), bỏ qua toàn bộ plugin đó cho an toàn.
                if str(plugin.resolve()) in dang_dung:
                    continue
                ket.append((commit, _kich_thuoc(commit)))
    return ket


# --------------------------------------------------------- Loại 3: MRAQ100_AUDIT/tools cũ
def kiem_mraq_audit_tools_cu(goc: Path) -> tuple[Path, str] | None:
    """Tìm `<goc>/../MRAQ100_AUDIT/tools/` và bản đã chuyển
    `medical-ebm-automation/tools/mraq_kappa/`. Chỉ đề xuất xoá nếu diff RỖNG.
    Trả (đường_dẫn_cu, ghi_chú) hoặc None nếu không áp dụng được."""
    ung_vien = goc.parent / "MRAQ100_AUDIT" / "tools"
    if not ung_vien.is_dir():
        return None
    moi = None
    for ten in ("medical-ebm-automation", "EBM-drluanbv175", "ebm-drluanbv175"):
        thu = goc / ten / "tools" / "mraq_kappa"
        if thu.is_dir():
            moi = thu
            break
    if moi is None:
        return (ung_vien, "CÒN — không tìm thấy tools/mraq_kappa/ đã chuyển ở cạnh để so sánh")

    khac = shutil.which("diff")
    if not khac:
        return (ung_vien, "CÒN — máy không có lệnh diff để so sánh, không đoán")
    import subprocess
    r = subprocess.run(["diff", "-rq", str(ung_vien), str(moi)],
                        capture_output=True, text=True)
    if r.returncode == 0:
        return (ung_vien, f"GIỐNG HỆT {moi} — an toàn để xoá bản cũ")
    return (ung_vien, f"KHÁC bản đã chuyển ({moi}) — DỪNG, xem tay:\n{r.stdout.strip()}")


def _goc_mac_dinh() -> list[Path]:
    ung_vien = [
        Path.home() / "OneDrive" / "Claude AI",
        Path.home() / "Library" / "CloudStorage" / "OneDrive-Personal" / "Claude AI",
        Path.home() / "Documents" / "GitHub",
    ]
    return [p for p in ung_vien if p.is_dir()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Dọn rác an toàn trên máy thật. Mặc định CHỈ KIỂM, không xoá gì.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--goc", action="append", default=None,
                     help="thư mục gốc để quét loại 1 (cache) và loại 3 (MRAQ). "
                          "Có thể lặp lại để quét nhiều gốc. Bỏ trống thì tự dò "
                          "vài vị trí quen thuộc.")
    ap.add_argument("--ap-dung", action="store_true", help="xoá thật (mặc định chỉ kiểm)")
    ap.add_argument("--json", action="store_true", help="xuất JSON máy đọc")
    a = ap.parse_args(argv)

    goc_list = [Path(g).expanduser() for g in a.goc] if a.goc else _goc_mac_dinh()
    if not goc_list:
        print("KHÔNG dò được thư mục gốc nào — chỉ định bằng --goc \"<đường dẫn>\"",
              file=sys.stderr)
        return 1

    cache_hits: list[tuple[Path, int]] = []
    for g in goc_list:
        cache_hits += quet_cache_tai_sinh(g)

    plugin_root = duong_dan_plugin_claude()
    plugin_hits = quet_cache_plugin_cu(plugin_root)

    mraq_hits = []
    for g in goc_list:
        kq = kiem_mraq_audit_tools_cu(g)
        if kq:
            mraq_hits.append(kq)

    if a.json:
        print(json.dumps({
            "goc_quet": [str(g) for g in goc_list],
            "cache_tai_sinh": [{"duong_dan": str(p), "byte": n} for p, n in cache_hits],
            "cache_plugin_cu": [{"duong_dan": str(p), "byte": n} for p, n in plugin_hits],
            "mraq_audit_tools": [{"duong_dan": str(p), "ghi_chu": gc} for p, gc in mraq_hits],
        }, ensure_ascii=False, indent=2))
    else:
        print("=" * 70)
        print("  DỌN RÁC MÁY THẬT" + ("" if not a.ap_dung else " — CHẾ ĐỘ XOÁ THẬT"))
        print("=" * 70)
        print(f"  Gốc quét: {', '.join(str(g) for g in goc_list)}")
        print(f"  Plugin cache: {plugin_root}")

        t1 = sum(n for _, n in cache_hits)
        print(f"\n① Cache tái sinh — {len(cache_hits)} mục, {_doc_dep(t1)}")
        for p, n in cache_hits[:20]:
            print(f"    {p}  ({_doc_dep(n)})")
        if len(cache_hits) > 20:
            print(f"    ... và {len(cache_hits) - 20} mục khác")

        t2 = sum(n for _, n in plugin_hits)
        print(f"\n② Cache plugin cũ (không plugin nào còn trỏ tới) — "
              f"{len(plugin_hits)} mục, {_doc_dep(t2)}")
        for p, n in plugin_hits:
            print(f"    {p}  ({_doc_dep(n)})")

        print(f"\n③ MRAQ100_AUDIT/tools/ cũ — {len(mraq_hits)} vị trí")
        an_toan_xoa_mraq = []
        for p, gc in mraq_hits:
            print(f"    {p}\n      {gc}")
            if gc.startswith("GIỐNG HỆT"):
                an_toan_xoa_mraq.append(p)

        print(f"\n④ Conflict-copy OneDrive — KHÔNG tự kiểm ở đây.")
        print(f"    Chạy: python3 tools/sync_safety_check.py  (trong ebm-drluanbv175)")

        tong = t1 + t2 + sum(_kich_thuoc(p) for p in an_toan_xoa_mraq)
        print(f"\nTổng có thể giải phóng (①+②+③ an toàn): {_doc_dep(tong)}")

    if a.ap_dung:
        da_xoa = 0
        for p, _ in cache_hits + plugin_hits:
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
                da_xoa += 1
            except OSError as e:
                print(f"  LỖI xoá {p}: {e}", file=sys.stderr)
        for p, gc in mraq_hits:
            if gc.startswith("GIỐNG HỆT"):
                try:
                    shutil.rmtree(p)
                    da_xoa += 1
                except OSError as e:
                    print(f"  LỖI xoá {p}: {e}", file=sys.stderr)
        print(f"\nĐã xoá {da_xoa} mục.")
        return 0

    tong_muc = len(cache_hits) + len(plugin_hits) + sum(
        1 for _, gc in mraq_hits if gc.startswith("GIỐNG HỆT"))
    if tong_muc == 0:
        print("\nKhông có gì để dọn.")
        return 0
    print(f"\nChỉ mới KIỂM — chưa xoá gì. Chạy lại kèm --ap-dung để xoá thật.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
