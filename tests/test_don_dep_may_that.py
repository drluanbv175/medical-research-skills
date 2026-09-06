#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử don_dep_may_that.py. Chạy: python3 tests/test_don_dep_may_that.py

Trọng tâm: KHÔNG BAO GIỜ xoá nhầm cache plugin ĐANG DÙNG, và MRAQ chỉ xoá khi
diff thật sự rỗng.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import don_dep_may_that as M  # noqa: E402

PASS = FAIL = 0


def kiem(nhan, thuc, mong):
    global PASS, FAIL
    if thuc == mong:
        PASS += 1
        print(f"  [PASS] {nhan}")
    else:
        FAIL += 1
        print(f"  [FAIL] {nhan}: được {thuc!r}, mong {mong!r}")


def kiem_dung(nhan, dk):
    kiem(nhan, bool(dk), True)


def tao(p: Path, noi_dung: str = "x") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung, encoding="utf-8")
    return p


# ------------------------------------------------------------ Loại 1: cache tái sinh
print("\n### Quét cache tái sinh ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp)
    tao(g / "duan" / "__pycache__" / "a.pyc")
    tao(g / "duan" / "src" / "b.py")
    tao(g / "duan" / ".pytest_cache" / "v" / "cache" / "lastfailed")
    tao(g / "duan" / ".DS_Store")
    tao(g / "duan" / "src" / "._resource")
    tao(g / "duan" / "src" / "c.pyc")
    hits = M.quet_cache_tai_sinh(g)
    ten = {p.name for p, _ in hits}
    kiem_dung("bắt __pycache__", "__pycache__" in ten)
    kiem_dung("bắt .pytest_cache", ".pytest_cache" in ten)
    kiem_dung("bắt .DS_Store", ".DS_Store" in ten)
    kiem_dung("bắt ._resource (macOS resource fork)", "._resource" in ten)
    kiem_dung("bắt c.pyc rời", "c.pyc" in ten)
    kiem("KHÔNG đụng src/b.py",
         any(p.name == "b.py" for p, _ in hits), False)
    kiem("không đi sâu vào .git",
         any(".git" in p.parts for p, _ in hits), False)

with tempfile.TemporaryDirectory() as tmp:
    tao(Path(tmp) / ".git" / "objects" / "__pycache__" / "x.pyc")
    kiem("thư mục .git bị bỏ qua hoàn toàn",
         M.quet_cache_tai_sinh(Path(tmp)), [])


# ------------------------------------------------------------ Loại 2: cache plugin cũ
print("\n### Cache plugin cũ — KHÔNG được đụng cái đang dùng ###")
with tempfile.TemporaryDirectory() as tmp:
    plugins = Path(tmp) / ".claude" / "plugins"
    cache = plugins / "cache"
    dang_dung = cache / "cho-a" / "plugin-x" / "commit-MOI"
    cu_1 = cache / "cho-a" / "plugin-x" / "commit-CU-1"
    cu_2 = cache / "cho-a" / "plugin-x" / "commit-CU-2"
    khac_plugin_dang_dung = cache / "cho-a" / "plugin-y" / "commit-Y"
    for d in (dang_dung, cu_1, cu_2, khac_plugin_dang_dung):
        tao(d / "SKILL.md", "noi dung")
    (plugins / "installed_plugins.json").write_text(json.dumps({
        "plugins": {
            "cho-a/plugin-x": [{"installPath": str(dang_dung), "gitCommitSha": "moi"}],
            "cho-a/plugin-y": [{"installPath": str(khac_plugin_dang_dung)}],
        }
    }), encoding="utf-8")

    hits = M.quet_cache_plugin_cu(plugins)
    duong_dan_hit = {p.resolve() for p, _ in hits}
    kiem_dung("bắt commit-CU-1 (không ai trỏ tới)", cu_1.resolve() in duong_dan_hit)
    kiem_dung("bắt commit-CU-2 (không ai trỏ tới)", cu_2.resolve() in duong_dan_hit)
    kiem("KHÔNG đụng commit-MOI (plugin-x đang dùng)",
         dang_dung.resolve() in duong_dan_hit, False)
    kiem("KHÔNG đụng plugin-y (đang dùng, dù khác plugin)",
         khac_plugin_dang_dung.resolve() in duong_dan_hit, False)
    kiem("đúng 2 mục bị gắn cờ (không nhiều hơn)", len(hits), 2)

with tempfile.TemporaryDirectory() as tmp:
    plugins = Path(tmp) / ".claude" / "plugins"
    kiem("thiếu installed_plugins.json -> không crash, trả rỗng",
         M.quet_cache_plugin_cu(plugins), [])

with tempfile.TemporaryDirectory() as tmp:
    plugins = Path(tmp) / ".claude" / "plugins"
    (plugins / "cache").mkdir(parents=True)
    (plugins / "installed_plugins.json").write_text("{ không phải json hợp lệ", encoding="utf-8")
    kiem("JSON hỏng -> không crash",
         isinstance(M.quet_cache_plugin_cu(plugins), list), True)


# ------------------------------------------------------------ Loại 3: MRAQ100_AUDIT/tools
print("\n### MRAQ100_AUDIT/tools — chỉ đề xuất xoá khi giống hệt ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp) / "Claude AI"
    cu = g.parent / "MRAQ100_AUDIT" / "tools"
    moi = g / "medical-ebm-automation" / "tools" / "mraq_kappa"
    tao(cu / "kappa_blind_rating.py", "noi dung giong het")
    tao(moi / "kappa_blind_rating.py", "noi dung giong het")
    kq = M.kiem_mraq_audit_tools_cu(g)
    kiem_dung("tìm thấy cặp để so", kq is not None)
    kiem_dung("giống hệt -> đề xuất xoá", kq[1].startswith("GIỐNG HỆT"))

with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp) / "Claude AI"
    cu = g.parent / "MRAQ100_AUDIT" / "tools"
    moi = g / "medical-ebm-automation" / "tools" / "mraq_kappa"
    tao(cu / "kappa_blind_rating.py", "ban CU khac noi dung")
    tao(moi / "kappa_blind_rating.py", "ban MOI khac noi dung")
    kq = M.kiem_mraq_audit_tools_cu(g)
    kiem("KHÁC nội dung -> KHÔNG đề xuất xoá",
         kq[1].startswith("GIỐNG HỆT"), False)
    kiem_dung("và nói rõ là KHÁC, không im lặng", "KHÁC" in kq[1])

with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp) / "Claude AI"
    g.mkdir(parents=True)
    kiem("không có MRAQ100_AUDIT/tools -> None, không báo nhầm",
         M.kiem_mraq_audit_tools_cu(g), None)

with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp) / "Claude AI"
    tao(g.parent / "MRAQ100_AUDIT" / "tools" / "kappa_blind_rating.py", "abc")
    kq = M.kiem_mraq_audit_tools_cu(g)
    kiem_dung("có bản cũ nhưng KHÔNG tìm thấy bản đã chuyển -> báo CÒN, không đoán",
              kq is not None and kq[1].startswith("CÒN"))


# ------------------------------------------------------------ main(): chỉ kiểm vs áp dụng
print("\n### main(): mặc định chỉ kiểm, --ap-dung mới xoá thật ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp) / "goc"
    cache_dir = g / "__pycache__"
    tao(cache_dir / "a.pyc")
    ma = M.main(["--goc", str(g), "--json"])
    kiem("có rác -> mã thoát 1 (chế độ kiểm)", ma, 1)
    kiem_dung("KHÔNG xoá gì ở chế độ kiểm", cache_dir.is_dir())

    ma2 = M.main(["--goc", str(g), "--ap-dung", "--json"])
    kiem("--ap-dung -> mã thoát 0", ma2, 0)
    kiem("ĐÃ xoá thật cache", cache_dir.exists(), False)

with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp) / "sach"
    g.mkdir()
    kiem("thư mục sạch -> mã thoát 0, không báo rác giả",
         M.main(["--goc", str(g), "--json"]), 0)


print("\n" + "=" * 50)
print(f"  PASS={PASS}  FAIL={FAIL}")
print("=" * 50)
sys.exit(1 if FAIL else 0)
