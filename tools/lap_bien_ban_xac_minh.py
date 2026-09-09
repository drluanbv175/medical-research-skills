#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lap_bien_ban_xac_minh.py — Chạy MỘT LẦN trên máy có mạng, sinh BIÊN BẢN XÁC MINH
để các cổng liêm chính ở phiên cloud đọc lại và ra PASS THẬT.

VẤN ĐỀ ĐANG GIẢI
----------------
Phiên cloud bị chặn toàn bộ tên miền y khoa ở tầng chính sách. Hệ quả là cổng
`verify_dashboard.py --online` không xác minh được PMID nào, chỉ ra được
`PASS CÓ ĐIỀU KIỆN` kèm ghi vết. Nhưng máy của bác sĩ thì có mạng đầy đủ.

Công cụ này bắc cầu giữa hai nơi, theo đúng mẫu `extract → gọi → report` mà
`retraction_check.py` đã dùng: việc cần mạng chạy ở nơi CÓ mạng, kết quả đóng
thành một tệp có thể commit, nơi KHÔNG có mạng đọc lại tệp đó.

    [máy có mạng]  lap_bien_ban_xac_minh.py  →  bien-ban/<chủ đề>-<ngày>.json
                            ↓ commit + push
    [phiên cloud]  verify_dashboard.py <dashboard>.html --bien-ban <tệp>.json
                                                        → ✓ PASS (theo biên bản)

BA VIỆC CẦN MẠNG, GOM VÀO MỘT LẦN CHẠY
--------------------------------------
  1. Phân giải từng PMID trên PubMed (chống trích dẫn ảo)
  2. Kiểm bài rút bằng bộ dữ liệu Retraction Watch đầy đủ (nếu đã tải)
  3. Lấy nguyên văn câu tài trợ + COI (gọi `lay_coi_tai_tro.py`)

Bước nào không chạy được thì ghi rõ là CHƯA LÀM trong biên bản — **không** bỏ trống,
**không** để cổng ở đầu kia hiểu nhầm thành đã xác minh.

BIÊN BẢN RÀNG BUỘC VÀO CÁI GÌ
-----------------------------
Ràng buộc theo **tập định danh**, không theo byte của tệp. Sửa một lỗi chính tả trong
dashboard mà mất hiệu lực cả biên bản thì không ai dùng nổi. Ngược lại, thêm một item
mới thì PMID của nó KHÔNG có trong biên bản → cổng báo chưa xác minh, đúng như phải thế.
sha256 lúc lập vẫn được ghi để người đọc biết tệp đã đổi hay chưa.

CÁCH DÙNG
    python3 tools/lap_bien_ban_xac_minh.py EBM-Dashboards/WebDashboard_EBM_*.html
    python3 tools/lap_bien_ban_xac_minh.py <dashboard>.html --ban-cap-nhat <file>.md
    python3 tools/lap_bien_ban_xac_minh.py <dashboard>.html --bo-qua-coi   # nhanh hơn

MÃ THOÁT
    0 = mọi PMID phân giải được (biên bản dùng được để ra PASS)
    1 = có PMID KHÔNG phân giải được → trích dẫn ảo, phải sửa dashboard
    2 = KHÔNG KẾT LUẬN — còn PMID chưa tra được (mạng hỏng giữa chừng)
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (os.path.join(ROOT, "EBM-Dashboards", "tools"), os.path.join(ROOT, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from verify_dashboard import extract_data_block, split_items, field, verify_pmid_online
except Exception:
    print("✗ Không nạp được EBM-Dashboards/tools/verify_dashboard.py — cần nó để đọc "
          "khối DATA và phân giải PMID.", file=sys.stderr)
    raise

PHIEN_BAN = "1.0"


def sha256_tep(duong_dan: str) -> str:
    return hashlib.sha256(open(duong_dan, "rb").read()).hexdigest()


def chay(lenh: list[str]) -> tuple[int, str, str]:
    """Chạy một công cụ anh em, trả (mã thoát, stdout, stderr). Không ném."""
    try:
        r = subprocess.run(lenh, capture_output=True, text=True, timeout=1800)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:                                   # công cụ thiếu, treo…
        return 127, "", str(e)


def doc_dinh_danh(html_path: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Rút (item_id, pmid) và danh sách DOI từ khối DATA của dashboard."""
    html = open(html_path, encoding="utf-8").read()
    data = extract_data_block(html)
    if not data:
        return [], []
    pmids, dois = [], []
    for ch in split_items(data):
        iid = field(ch, "id") or "(?)"
        p, d = field(ch, "pmid"), field(ch, "doi")
        if p:
            pmids.append((iid, p))
        if d:
            dois.append(d.lower())
    return pmids, dois


def buoc_pmid(pmids: list[tuple[str, str]]) -> tuple[dict, int, int]:
    """Phân giải từng PMID. Trả (bản ghi, số hỏng, số chưa tra được)."""
    ra, xong, hong, chua = {}, set(), 0, 0
    for iid, p in pmids:
        if p in ra:
            continue
        ok, tin = verify_pmid_online(p)
        if ok is True:
            ra[p] = {"phan_giai": True, "tieu_de": tin, "item": iid}
        elif ok is False:
            ra[p] = {"phan_giai": False, "ly_do": tin, "item": iid}
            hong += 1
        else:
            ra[p] = {"phan_giai": None, "ly_do": tin, "item": iid}
            chua += 1
        print("  PMID %s %s" % (p, "✓" if ok is True else ("✗" if ok is False else "⊘")),
              file=sys.stderr)
    return ra, hong, chua


def buoc_bai_rut(ban_cap_nhat: str | None) -> dict:
    """Kiểm bài rút bằng bộ dữ liệu Retraction Watch TẢI VỀ MÁY (đầy đủ hơn Scite)."""
    if not ban_cap_nhat:
        return {"trang_thai": "CHƯA LÀM", "ly_do": "không truyền --ban-cap-nhat"}
    cong_cu = os.path.join(ROOT, "EBM-Dashboards", "tools", "retraction_check.py")
    if not os.path.isfile(cong_cu):
        return {"trang_thai": "CHƯA LÀM", "ly_do": "không thấy retraction_check.py"}
    ma, ra, loi = chay([sys.executable, cong_cu, "local", ban_cap_nhat, "--json"])
    if ma == 127 or not ra.strip():
        return {"trang_thai": "CHƯA LÀM",
                "ly_do": "chưa tải bộ dữ liệu Retraction Watch — chạy "
                         "`python3 tools/tai_retraction_watch.py tai` trước",
                "stderr": loi.strip()[:400]}
    try:
        return {"trang_thai": "ĐÃ LÀM", "nguon": "Retraction Watch (bộ đầy đủ, tải về máy)",
                "ma_thoat": ma, "ket_qua": json.loads(ra)}
    except Exception:
        return {"trang_thai": "CHƯA LÀM", "ly_do": "không đọc được JSON trả về",
                "stdout": ra[:400]}


def buoc_coi(nguon_doi: str) -> dict:
    """Lấy nguyên văn câu tài trợ + COI qua tools/lay_coi_tai_tro.py."""
    cong_cu = os.path.join(HERE, "lay_coi_tai_tro.py")
    if not os.path.isfile(cong_cu):
        return {"trang_thai": "CHƯA LÀM", "ly_do": "không thấy lay_coi_tai_tro.py"}
    thu_muc_tho = os.path.join(ROOT, "tools", "mau-that-lay-coi")
    ma, ra, loi = chay([sys.executable, cong_cu, nguon_doi, "--json",
                        "--luu-tho", thu_muc_tho])
    if not ra.strip():
        return {"trang_thai": "CHƯA LÀM", "ly_do": "công cụ không trả gì",
                "stderr": loi.strip()[:400]}
    try:
        kq = json.loads(ra)
    except Exception:
        return {"trang_thai": "CHƯA LÀM", "ly_do": "không đọc được JSON trả về"}
    # "Đã chạy" KHÁC "đã lấy được". Nhãn phải nói đúng cái đã có, vì biên bản này
    # là thứ người khác đọc để tin — kể cả cổng liêm chính ở đầu bên kia.
    co = sum(1 for r in kq if r.get("tai_tro") or r.get("coi"))
    du = sum(1 for r in kq if r.get("tai_tro") and r.get("coi"))
    if not kq or co == 0:
        nhan = "ĐÃ CHẠY NHƯNG KHÔNG LẤY ĐƯỢC GÌ"
    elif du == len(kq):
        nhan = "ĐÃ LÀM"
    else:
        nhan = "ĐÃ LÀM MỘT PHẦN (%d/%d DOI có dữ liệu, %d/%d đủ cả tài trợ lẫn COI)" % (
            co, len(kq), du, len(kq))
    return {"trang_thai": nhan, "ma_thoat": ma,
            "tho_luu_tai": os.path.relpath(thu_muc_tho, ROOT),
            "ket_qua": kq}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Lập biên bản xác minh trên máy có mạng, để phiên cloud đọc lại.")
    ap.add_argument("dashboard", help="tệp WebDashboard_*.html")
    ap.add_argument("--ban-cap-nhat", dest="ban_cap_nhat",
                    help="tệp CapNhat_EBM_*.md kèm theo (để kiểm bài rút + lấy COI)")
    ap.add_argument("--ra", dest="ra", help="nơi ghi biên bản (mặc định EBM-Dashboards/bien-ban/)")
    ap.add_argument("--bo-qua-coi", dest="bo_qua_coi", action="store_true",
                    help="bỏ bước lấy COI/tài trợ cho nhanh")
    a = ap.parse_args()

    if not os.path.isfile(a.dashboard):
        print("✗ Không thấy %s" % a.dashboard, file=sys.stderr)
        return 1

    pmids, dois = doc_dinh_danh(a.dashboard)
    if not pmids:
        print("✗ Không rút được PMID nào từ khối DATA.", file=sys.stderr)
        return 1

    print("═" * 72, file=sys.stderr)
    print("LẬP BIÊN BẢN XÁC MINH — %d PMID · %d DOI" % (len(set(p for _, p in pmids)), len(dois)),
          file=sys.stderr)
    print("═" * 72, file=sys.stderr)

    print("[1/3] Phân giải PMID trên PubMed…", file=sys.stderr)
    ban_pmid, hong, chua = buoc_pmid(pmids)

    print("[2/3] Kiểm bài rút (bộ dữ liệu đầy đủ)…", file=sys.stderr)
    ban_rut = buoc_bai_rut(a.ban_cap_nhat)
    print("      %s" % ban_rut["trang_thai"], file=sys.stderr)

    nguon_coi = a.ban_cap_nhat or a.dashboard
    if a.bo_qua_coi:
        ban_coi = {"trang_thai": "CHƯA LÀM", "ly_do": "người chạy chọn --bo-qua-coi"}
        print("[3/3] Bỏ qua COI/tài trợ theo yêu cầu.", file=sys.stderr)
    else:
        print("[3/3] Lấy nguyên văn tài trợ + COI…", file=sys.stderr)
        ban_coi = buoc_coi(nguon_coi)
        print("      %s" % ban_coi["trang_thai"], file=sys.stderr)

    bien_ban = {
        "phien_ban_bien_ban": PHIEN_BAN,
        "_muc_dich": "Bằng chứng đã xác minh trên MÁY CÓ MẠNG, để cổng liêm chính ở nơi "
                     "bị chặn egress đọc lại. Ràng buộc theo TẬP ĐỊNH DANH, không theo byte tệp.",
        "ngay_lap": datetime.datetime.now(datetime.timezone.utc)
                            .replace(microsecond=0).isoformat(),
        "moi_truong": {"he_dieu_hanh": platform.system(),
                       "python": platform.python_version()},
        "tep": {
            "dashboard": {"ten": os.path.basename(a.dashboard),
                          "sha256_luc_lap": sha256_tep(a.dashboard)},
            "ban_cap_nhat": ({"ten": os.path.basename(a.ban_cap_nhat),
                              "sha256_luc_lap": sha256_tep(a.ban_cap_nhat)}
                             if a.ban_cap_nhat and os.path.isfile(a.ban_cap_nhat) else None),
        },
        "pmid": ban_pmid,
        "bai_rut": ban_rut,
        "coi_tai_tro": ban_coi,
    }

    ra_thu_muc = a.ra or os.path.join(ROOT, "EBM-Dashboards", "bien-ban")
    os.makedirs(ra_thu_muc, exist_ok=True)
    ten = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(a.dashboard).rsplit(".", 1)[0])
    duong_dan = os.path.join(ra_thu_muc, "%s.bien-ban.json" % ten)
    json.dump(bien_ban, open(duong_dan, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    n_ok = sum(1 for v in ban_pmid.values() if v["phan_giai"] is True)
    print("─" * 72, file=sys.stderr)
    print("Biên bản: %s" % os.path.relpath(duong_dan, ROOT), file=sys.stderr)
    print("PMID phân giải: %d/%d · hỏng %d · chưa tra được %d"
          % (n_ok, len(ban_pmid), hong, chua), file=sys.stderr)
    print(duong_dan)

    if hong:
        print("KẾT QUẢ: ✗ CÓ TRÍCH DẪN ẢO — %d PMID không phân giải. Sửa dashboard trước."
              % hong, file=sys.stderr)
        return 1
    if chua:
        print("KẾT QUẢ: ⊘ KHÔNG KẾT LUẬN — %d PMID chưa tra được. Chạy lại khi mạng ổn."
              % chua, file=sys.stderr)
        return 2
    print("KẾT QUẢ: ✓ Đủ. Commit biên bản, rồi ở phiên cloud chạy:\n"
          "    python3 EBM-Dashboards/tools/verify_dashboard.py %s --bien-ban %s"
          % (os.path.basename(a.dashboard), os.path.relpath(duong_dan, ROOT)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
