#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử công cụ đối chiếu ba bên.

Chạy: python3 tests/test_doi_chieu_ba_ben.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import doi_chieu_ba_ben as M  # noqa: E402

PASS = FAIL = 0


def kiem(nhan, thuc, mong):
    global PASS, FAIL
    if thuc == mong:
        PASS += 1
        print(f"  [PASS] {nhan}")
    else:
        FAIL += 1
        print(f"  [FAIL] {nhan}: được {thuc!r}, mong {mong!r}")


def kiem_dung(nhan, dieu_kien):
    kiem(nhan, bool(dieu_kien), True)


def viet_skill(goc: Path, ten: str, noi_dung: str) -> Path:
    d = goc / ten
    d.mkdir(parents=True, exist_ok=True)
    f = d / "SKILL.md"
    f.write_text(noi_dung, encoding="utf-8")
    return f


FM = "---\nname: {t}\ndescription: {d}\n---\n"


# ------------------------------------------------------------------ tách frontmatter
print("\n### Tách frontmatter ###")
fm, than = M.tach_frontmatter(FM.format(t="abc", d="mô tả") + "# Thân\nnội dung\n")
kiem("lấy đúng name", fm.get("name"), "abc")
kiem("lấy đúng description", fm.get("description"), "mô tả")
kiem("thân không còn frontmatter", than.startswith("# Thân"), True)
fm2, than2 = M.tach_frontmatter("không có frontmatter\n")
kiem("thiếu frontmatter -> dict rỗng", fm2, {})
kiem("thiếu frontmatter -> giữ nguyên thân", than2, "không có frontmatter\n")
fm3, _ = M.tach_frontmatter("---\r\nname: crlf\r\n---\r\nthân\r\n")
kiem("CRLF vẫn đọc được frontmatter", fm3.get("name"), "crlf")


# ------------------------------------------------------------------ tỷ lệ tiếng Việt
print("\n### Tỷ lệ tiếng Việt ###")
kiem("chuỗi rỗng -> 0", M.ty_le_tieng_viet(""), 0.0)
kiem_dung("tiếng Việt > tiếng Anh",
          M.ty_le_tieng_viet("Tổng quan y văn có hệ thống về đái tháo đường")
          > M.ty_le_tieng_viet("A systematic review of diabetes mellitus"))
kiem("tiếng Anh thuần -> 0", M.ty_le_tieng_viet("plain english only"), 0.0)


# --------------------------------------------------- HỒI QUY: bẫy dàn phẳng
print("\n### HỒI QUY — bẫy dàn phẳng (lỗi thật, phát hiện 06/09/2026) ###")
# Bản A có cấu trúc; bản B là CÙNG nội dung nhưng gộp thành một dòng dài.
# Bản cloud của `antifacts` đúng dạng này: theo dòng 0,0% nhưng theo từ 67,1%.
co_cau_truc = (
    "# Antifacts\n"
    "## Mục tiêu\n"
    "- Gom sản phẩm EBM theo chuyên khoa\n"
    "- Bốn tab: chuyên khoa, cập nhật, thang điểm, nghiên cứu\n"
    "- Sinh bằng build_antifacts.py\n"
)
dan_phang = (
    "Antifacts gom sản phẩm EBM theo chuyên khoa. Bốn tab: chuyên khoa, "
    "cập nhật, thang điểm, nghiên cứu. Sinh bằng build_antifacts.py\n"
)
theo_dong = M.do_giong_nhau_dong(co_cau_truc, dan_phang)
theo_tu = M.do_giong_nhau_tu(co_cau_truc, dan_phang)
kiem_dung(f"theo DÒNG rơi thấp ({theo_dong*100:.1f}%) — đây là cái bẫy",
          theo_dong < M.NGUONG_KHAC_HAN)
kiem_dung(f"theo TỪ vẫn cao ({theo_tu*100:.1f}%) — nhận ra cùng skill",
          theo_tu >= M.NGUONG_KHAC_HAN)

with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp)
    a = M.Skill("x", viet_skill(g / "a", "x", FM.format(t="x", d="d") + co_cau_truc))
    b = M.Skill("x", viet_skill(g / "b", "x", FM.format(t="x", d="d") + dan_phang))
    loai, tu, dong, phang = M.phan_loai(a, b)
    kiem("dàn phẳng KHÔNG bị gọi nhầm là KHÁC HẲN", loai, "LỆCH BẢN")
    kiem("và được đánh dấu là bị dàn phẳng", phang, True)


# ------------------------------------------------------------------ phân loại
print("\n### Phân loại ba nhóm ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp)
    y_het = FM.format(t="k", d="d") + "# Giống\nmột hai ba bốn năm\n"
    a = M.Skill("k", viet_skill(g / "a", "k", y_het))
    b = M.Skill("k", viet_skill(g / "b", "k", y_het))
    kiem("byte y hệt -> GIỐNG", M.phan_loai(a, b)[0], "GIỐNG")

    c = M.Skill("k", viet_skill(
        g / "c", "k", FM.format(t="k", d="d") + "# Giống\nmột hai ba bốn năm sáu bảy\n"))
    kiem("thêm vài từ -> LỆCH BẢN", M.phan_loai(a, c)[0], "LỆCH BẢN")

    d = M.Skill("k", viet_skill(
        g / "d", "k",
        FM.format(t="k", d="khac") + "# Hoàn toàn khác\nzebra qux frobnicate widget\n"))
    kiem("không chung từ nào -> KHÁC HẲN", M.phan_loai(a, d)[0], "KHÁC HẲN")


# ------------------------------------------------------------------ quét thư mục
print("\n### Quét thư mục ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp) / "hub"
    viet_skill(g, "that", FM.format(t="that", d="d") + "nội dung\n")
    viet_skill(g, "_noi_bo", FM.format(t="x", d="d") + "bỏ qua\n")
    (g / "khong-phai-skill").mkdir()
    kiem("chỉ nhận thư mục có SKILL.md, bỏ tiền tố _",
         sorted(M.quet_thu_muc(g)), ["that"])

try:
    M.quet_thu_muc(Path("/khong/ton/tai/that/su"))
    kiem("thư mục không tồn tại -> ném KhongDoDuoc", "không ném", "ném")
except M.KhongDoDuoc:
    kiem("thư mục không tồn tại -> ném KhongDoDuoc", "ném", "ném")


# ------------------------------------------------------------------ dò bundle cloud
print("\n### Dò bundle cloud ###")
with tempfile.TemporaryDirectory() as tmp:
    nhieu = Path(tmp) / "synced"
    (nhieu / "aaa").mkdir(parents=True)
    (nhieu / "bbb").mkdir(parents=True)
    try:
        M.tim_bundle_cloud(str(nhieu))  # chỉ định thẳng thì chấp nhận
        kiem("chỉ định thẳng đường dẫn -> nhận", True, True)
    except M.KhongDoDuoc:
        kiem("chỉ định thẳng đường dẫn -> nhận", False, True)
try:
    M.tim_bundle_cloud("/khong/co/dau/ca")
    kiem("cloud không tồn tại -> ném KhongDoDuoc", "không ném", "ném")
except M.KhongDoDuoc:
    kiem("cloud không tồn tại -> ném KhongDoDuoc", "ném", "ném")


# ------------------------------------------------------------------ đối chiếu + mã thoát
print("\n### Đối chiếu và mã thoát ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp)
    cl, rp = g / "cloud", g / "repo"
    chung = FM.format(t="chung", d="d") + "alpha beta gamma delta\n"
    viet_skill(cl, "chung", chung)
    viet_skill(rp, "chung", chung)
    viet_skill(cl, "vachua", FM.format(t="vachua", d="d") + "alpha beta gamma\n")
    viet_skill(rp, "vachua", FM.format(t="vachua", d="d") + "alpha beta gamma epsilon\n")
    viet_skill(cl, "dungten", FM.format(t="dungten", d="d") + "một hai ba bốn\n")
    viet_skill(rp, "dungten", FM.format(t="dungten", d="d") + "zebra qux frob widget\n")
    viet_skill(rp, "chiRepo", FM.format(t="chiRepo", d="d") + "chỉ repo có\n")

    kq = M.doi_chieu(M.quet_thu_muc(cl), M.quet_thu_muc(rp), {}, chi_custom=False)
    kiem("1 giống", [m["ten"] for m in kq["giong"]], ["chung"])
    kiem("1 lệch bản", [m["ten"] for m in kq["lech_ban"]], ["vachua"])
    kiem("1 khác hẳn", [m["ten"] for m in kq["khac_han"]], ["dungten"])
    kiem("1 chỉ repo", kq["chi_repo"], ["chiRepo"])
    kiem("0 chỉ cloud", kq["chi_cloud"], [])

    ma = M.main([str(rp), "--cloud", str(cl), "--json"])
    kiem("có KHÁC HẲN -> mã thoát 2", ma, 2)

with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp)
    cl, rp = g / "cloud", g / "repo"
    y = FM.format(t="a", d="d") + "alpha beta gamma\n"
    viet_skill(cl, "a", y)
    viet_skill(rp, "a", y)
    kiem("hai bên khớp hoàn toàn -> mã thoát 0",
         M.main([str(rp), "--cloud", str(cl), "--json"]), 0)

kiem("thiếu một bên -> mã thoát 3 (KHÔNG phải 0)",
     M.main(["/khong/co/that", "--cloud", "/cung/khong/co", "--json"]), 3)


# ------------------------------------------------------------------ lọc theo manifest
print("\n### Lọc theo manifest (chỉ so skill 'custom') ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp)
    cl, rp = g / "cloud", g / "repo"
    viet_skill(cl, "cua-bac-si", FM.format(t="c", d="d") + "alpha beta\n")
    viet_skill(cl, "cua-anthropic", FM.format(t="a", d="d") + "gamma delta\n")
    viet_skill(rp, "cua-bac-si", FM.format(t="c", d="d") + "alpha beta\n")
    man = {"cua-bac-si": {"source": "custom"},
           "cua-anthropic": {"source": "anthropic-example"}}
    kq = M.doi_chieu(M.quet_thu_muc(cl), M.quet_thu_muc(rp), man, chi_custom=True)
    kiem("skill Anthropic không bị tính là 'chỉ cloud'", kq["chi_cloud"], [])
    kq2 = M.doi_chieu(M.quet_thu_muc(cl), M.quet_thu_muc(rp), man, chi_custom=False)
    kiem("khi --tat-ca thì có tính", kq2["chi_cloud"], ["cua-anthropic"])


# ------------------------------------------------------- tác vụ định kỳ
print("\n### Tác vụ định kỳ: nhận diện neo máy ###")
with tempfile.TemporaryDirectory() as tmp:
    g = Path(tmp)
    tv = g / "sync" / "scheduled-tasks"
    viet_skill(tv, "neo-mac",
               FM.format(t="neo-mac", d="chạy trên máy")
               + "Thư mục: /Users/nguyenluan/Library/CloudStorage/OneDrive-Personal/x\n")
    viet_skill(tv, "neo-linux",
               FM.format(t="neo-linux", d="neo home linux")
               + "Đọc /home/bacsi/du-lieu/a.md\n")
    viet_skill(tv, "khong-neo",
               FM.format(t="khong-neo", d="chạy đâu cũng được")
               + "Tra PubMed 7 ngày qua rồi báo cáo.\n")

    ds = {t["ten"]: t for t in M.kiem_tac_vu(g, {})}
    kiem("bắt được neo /Users + OneDrive", ds["neo-mac"]["neo_may"], True)
    kiem("bắt được neo /home/<user>/", ds["neo-linux"]["neo_may"], True)
    kiem("tác vụ không neo -> không báo nhầm", ds["khong-neo"]["neo_may"], False)
    kiem("lấy được mô tả", ds["khong-neo"]["mo_ta"], "chạy đâu cũng được")
    kiem("không có trên cloud -> False", ds["neo-mac"]["co_tren_cloud"], False)

    # cùng tên tồn tại trên cloud thì phải nhận ra
    ds2 = {t["ten"]: t for t in M.kiem_tac_vu(g, {"neo-mac": None})}
    kiem("có trên cloud -> True", ds2["neo-mac"]["co_tren_cloud"], True)

with tempfile.TemporaryDirectory() as tmp:
    kiem("repo không có scheduled-tasks -> trả danh sách rỗng, KHÔNG lỗi",
         M.kiem_tac_vu(Path(tmp), {}), [])

# Bẫy: đường dẫn TƯƠNG ĐỐI không được tính là neo máy.
kiem("đường dẫn tương đối không bị tính là neo máy",
     bool(M.NEO_MAY.search("đọc sync/skills/abc/SKILL.md rồi chạy tools/x.py")), False)

print("\n" + "=" * 50)
print(f"  PASS={PASS}  FAIL={FAIL}")
print("=" * 50)
sys.exit(1 if FAIL else 0)
