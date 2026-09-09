#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lay_coi_tai_tro.py — Lấy NGUYÊN VĂN câu tài trợ và câu xung đột lợi ích (COI) của
từng nguồn, để điền mục "10.x Xung đột lợi ích và tài trợ" của bản cập nhật chứng cứ.

VÌ SAO CÓ CÔNG CỤ NÀY
---------------------
Quy tắc 5D-quater của skill `cap-nhat-chung-cu-y-khoa`: COI/tài trợ phải ghi NGUYÊN VĂN
hoặc ghi rõ "chưa lấy được" — **suy đoán tài trợ từ tên thuốc hay tên tác giả là bịa dữ liệu**.

Nhưng trong phiên cloud, đo ngày 2026-09-08: connector PubMed (`get_article_metadata`)
KHÔNG có trường funding/COI, Amass BiomedCore cũng không. Trên 17 nguồn của bản sa sút
trí tuệ chỉ lấy được 3/17 — đúng 3 bài mà tạp chí đặt câu tài trợ ngay trong tóm tắt
(kiểu Lancet/NEJM). 14 nguồn còn lại phải mở toàn văn bằng tay.

Công cụ này lấy chỗ mà connector không với tới: **XML thô** của PubMed và Europe PMC,
nơi có `<CoiStatement>`, `<GrantList>`, `<funding-statement>`. Chạy trên MÁY CÓ MẠNG.

BỐN NGUỒN, THEO THỨ TỰ ƯU TIÊN (nguyên văn trước, dữ liệu có cấu trúc sau)
-------------------------------------------------------------------------
  1. PubMed efetch XML       — `<CoiStatement>` (nguyên văn), `<GrantList>` (có cấu trúc)
  2. Europe PMC fullTextXML  — `<funding-statement>`, chú thích COI (nguyên văn, chỉ bài OA)
  3. Europe PMC core JSON    — `grantsList` (có cấu trúc)
  4. Crossref                — `funder[]` (có cấu trúc, từ Funder Registry)

BA TRẠNG THÁI — KHÔNG ĐƯỢC GỘP
------------------------------
  LẤY ĐƯỢC            nguồn trả về câu/dữ liệu thật → in nguyên văn, kèm lấy từ đâu
  KHÔNG CÓ TRONG CHỈ MỤC  nguồn TRẢ LỜI nhưng bản ghi không mang trường đó
                      → **không** có nghĩa là bài không có tài trợ; vẫn phải mở toàn văn
  CHƯA TRA ĐƯỢC       lỗi mạng/HTTP → chưa biết gì cả

MÃ THOÁT
    0 = mọi định danh đều lấy được CẢ tài trợ VÀ COI
    2 = KHÔNG KẾT LUẬN — còn ô trống (chưa tra được, hoặc chỉ mục không có)
    1 = dùng sai (không thấy tệp, không rút được định danh nào)

CÁCH DÙNG
    python3 tools/lay_coi_tai_tro.py EBM-Dashboards/CapNhat_EBM_*.md
    python3 tools/lay_coi_tai_tro.py --doi 10.1056/NEJMoa2212948 10.1001/jama.2023.13239
    python3 tools/lay_coi_tai_tro.py <tệp> --luu-tho raw/     # lưu phản hồi thô để rà lại
    python3 tools/lay_coi_tai_tro.py <tệp> --tu-tho raw/      # bóc tách lại, KHÔNG gọi mạng
    python3 tools/lay_coi_tai_tro.py <tệp> --json

CẢNH BÁO VỀ ĐỘ TIN CẬY CỦA CHÍNH CÔNG CỤ NÀY
--------------------------------------------
Phần bóc tách được viết theo tài liệu của PubMed/Europe PMC/Crossref nhưng **chưa được
đối chứng với phản hồi thật** (phiên viết ra nó bị chặn egress). Lần chạy đầu tiên PHẢI
dùng `--luu-tho` rồi mở vài tệp thô, đối chiếu bằng mắt với bảng in ra. Nếu lệch, gửi
tệp thô lại để sửa bộ bóc tách — **đừng dán kết quả vào bản cập nhật khi chưa đối chiếu**.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

try:                                     # dùng chung bộ rút DOI đã sửa kỹ (đếm cân bằng ngoặc)
    from retraction_check import extract_dois, norm as norm_doi
except Exception:                        # pragma: no cover
    print("✗ Không nạp được scripts/retraction_check.py — cần nó để rút DOI cho đúng.",
          file=sys.stderr)
    raise

UA = {"User-Agent": "lay-coi-tai-tro/1.0 (nghien-cuu-ebm)"}
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
CROSSREF = "https://api.crossref.org/works"

LAY_DUOC = "LẤY ĐƯỢC"
KHONG_CO = "KHÔNG CÓ TRONG CHỈ MỤC"
CHUA_TRA = "CHƯA TRA ĐƯỢC"

PMID_RE = re.compile(r"\bPMID[:\s]*([0-9]{6,9})\b", re.I)


class KhongTraDuoc(RuntimeError):
    """Không gọi được nguồn — KHÔNG phải 'nguồn không có dữ liệu'."""


# ───────────────────────────── mạng ─────────────────────────────

class Mang:
    """Gọi HTTP có retry, và ĐẾM lỗi tầng kết nối để phát hiện egress bị chặn sớm.

    Bị chặn thì 17 định danh sẽ ra 17 traceback giống nhau — vô ích. Đếm 3 lần
    hỏng liên tiếp ở tầng kết nối thì dừng hẳn và nói đúng một câu.
    """

    def __init__(self, cho: float = 0.35, lan_thu: int = 3, luu_tho: str | None = None,
                 tu_tho: str | None = None):
        self.cho, self.lan_thu = cho, lan_thu
        self.luu_tho, self.tu_tho = luu_tho, tu_tho
        self.hong_lien_tiep = 0
        self.chan = False

    def _duong_tho(self, khoa: str) -> str:
        thu_muc = self.tu_tho or self.luu_tho or "."
        return os.path.join(thu_muc, re.sub(r"[^A-Za-z0-9._-]", "_", khoa))

    def lay(self, url: str, khoa: str) -> bytes:
        if self.tu_tho:                                   # chế độ bóc tách lại, không gọi mạng
            p = self._duong_tho(khoa)
            if not os.path.isfile(p):
                raise KhongTraDuoc("không có tệp thô %s" % p)
            return open(p, "rb").read()
        if self.chan:
            raise KhongTraDuoc("đã xác định mạng bị chặn, không thử tiếp")
        cuoi = None
        for i in range(self.lan_thu):
            try:
                time.sleep(self.cho)
                with urllib.request.urlopen(
                        urllib.request.Request(url, headers=UA), timeout=30) as r:
                    du_lieu = r.read()
                self.hong_lien_tiep = 0
                if self.luu_tho:
                    os.makedirs(self.luu_tho, exist_ok=True)
                    open(self._duong_tho(khoa), "wb").write(du_lieu)
                return du_lieu
            except urllib.error.HTTPError as e:
                if e.code == 404:                          # nguồn TRẢ LỜI: không có bản ghi
                    self.hong_lien_tiep = 0
                    raise KhongTraDuoc("404 — nguồn không có bản ghi này")
                cuoi = e
            except Exception as e:                         # tầng kết nối
                cuoi = e
            time.sleep(1.5 * (2 ** i))
        self.hong_lien_tiep += 1
        if self.hong_lien_tiep >= 3:
            self.chan = True
        raise KhongTraDuoc(str(cuoi))


# ─────────────────────── bóc tách từng nguồn ───────────────────────

def _chu(node) -> str:
    """Gộp toàn bộ chữ trong một nút XML, chuẩn hoá khoảng trắng."""
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def _the(tag: str) -> str:
    """Bỏ namespace khỏi tên thẻ."""
    return tag.rsplit("}", 1)[-1].lower()


def boc_pubmed(xml_bytes: bytes) -> dict:
    """PubMed efetch XML → CoiStatement (nguyên văn) + GrantList (có cấu trúc)."""
    goc = ET.fromstring(xml_bytes)
    coi, tai_tro = "", []
    for n in goc.iter():
        t = _the(n.tag)
        if t == "coistatement" and not coi:
            coi = _chu(n)
        elif t == "grant":
            phan = {_the(c.tag): (c.text or "").strip() for c in n}
            mo_ta = " · ".join(x for x in (phan.get("agency"), phan.get("grantid"),
                                           phan.get("country")) if x)
            if mo_ta:
                tai_tro.append(mo_ta)
    return {"tai_tro": tai_tro, "coi": coi}


# Nhãn nhận diện trong JATS: khớp theo *chứa*, vì tạp chí đặt tên rất khác nhau.
JATS_TAI_TRO = ("funding-statement", "funding-information", "funding-source")
JATS_COI = ("coi-statement", "conflict", "competing", "coi")


def boc_epmc_fulltext(xml_bytes: bytes) -> dict:
    """Europe PMC fullTextXML (JATS) → câu tài trợ và câu COI nguyên văn."""
    goc = ET.fromstring(xml_bytes)
    tai_tro, coi = [], []
    for n in goc.iter():
        t = _the(n.tag)
        thuoc = " ".join(str(v).lower() for v in n.attrib.values())
        van = _chu(n)
        if not van:
            continue
        if t in JATS_TAI_TRO or any(k in thuoc for k in ("funding", "fund")):
            tai_tro.append(van)
        elif any(k in thuoc for k in JATS_COI):
            coi.append(van)
    # Nút cha chứa lại chữ của nút con → bỏ chuỗi nào là con của chuỗi đã có.
    def gon(ds):
        ds = sorted(set(ds), key=len, reverse=True)
        giu = []
        for s in ds:
            if not any(s in g for g in giu):
                giu.append(s)
        return giu
    return {"tai_tro": gon(tai_tro), "coi": " ".join(gon(coi))}


def boc_epmc_core(json_bytes: bytes) -> dict:
    """Europe PMC resultType=core → grantsList + định danh chéo (pmid/pmcid)."""
    d = json.loads(json_bytes.decode("utf-8", "replace"))
    kq = (((d.get("resultList") or {}).get("result")) or [])
    if not kq:
        return {"tai_tro": [], "coi": "", "pmid": "", "pmcid": ""}
    r = kq[0]
    grants = ((r.get("grantsList") or {}).get("grant")) or []
    ds = []
    for g in grants:
        # KHÔNG lấy `orderIn`: đó là số thứ tự trong danh sách, không phải thông tin tài trợ.
        mo_ta = " · ".join(str(x) for x in (g.get("agency"), g.get("grantId")) if x)
        if mo_ta:
            ds.append(mo_ta)
    return {"tai_tro": ds, "coi": "",
            "pmid": str(r.get("pmid") or r.get("id") or ""),
            "pmcid": str(r.get("pmcid") or "")}


def boc_crossref(json_bytes: bytes) -> dict:
    """Crossref /works/{DOI} → funder[] (tên nhà tài trợ + số hiệu tài trợ)."""
    d = json.loads(json_bytes.decode("utf-8", "replace"))
    ds = []
    for f in (d.get("message") or {}).get("funder") or []:
        ten = str(f.get("name") or "").strip()
        giai = ", ".join(str(a) for a in (f.get("award") or []))
        if ten:
            ds.append(ten + (" · " + giai if giai else ""))
    return {"tai_tro": ds, "coi": ""}


# ───────────────────────── điều phối một DOI ─────────────────────────

# Nguồn nào cũng "có dữ liệu", nhưng chất lượng rất khác nhau. Câu nguyên văn của
# chính bài báo > danh mục tài trợ có cấu trúc > sổ đăng ký của bên thứ ba.
# Không có bảng này thì nguồn chạy TRƯỚC giành mất chỗ của nguồn TỐT hơn chạy sau.
UU_TIEN = {
    "Europe PMC fullTextXML · funding-statement": 3,   # nguyên văn, của chính bài
    "Europe PMC fullTextXML · chú thích COI": 3,       # nguyên văn
    "PubMed XML · CoiStatement": 3,                    # nguyên văn, do nhà xuất bản nộp
    "PubMed XML · GrantList": 2,                       # có cấu trúc, đầy đủ agency+mã
    "Europe PMC core · grantsList": 1,                 # có cấu trúc, thường rút gọn
    "Crossref · funder[]": 1,                          # Funder Registry, hay thiếu
}

def mot_nguon(m: Mang, doi: str) -> dict:
    """Chạy lần lượt 4 nguồn cho một DOI. Dừng sớm khi đã có CẢ tài trợ lẫn COI."""
    ra = {"doi": doi, "pmid": "", "pmcid": "",
          "tai_tro": "", "tai_tro_tu": "", "tai_tro_trang_thai": CHUA_TRA,
          "coi": "", "coi_tu": "", "coi_trang_thai": CHUA_TRA,
          "tat_ca": {"tai_tro": {}, "coi": {}},   # giữ MỌI nguồn, để đối chiếu chéo
          "loi": [], "da_hoi": []}
    ut = {"tai_tro": 0, "coi": 0}

    def ghi(khoa_tt, khoa_tu, khoa_tr, gia_tri, nguon):
        """Ghi nếu nguồn mới TỐT HƠN nguồn đang giữ chỗ; giá trị cũ vẫn lưu ở `tat_ca`."""
        if not gia_tri:
            return
        ra["tat_ca"][khoa_tt][nguon] = gia_tri
        diem = UU_TIEN.get(nguon, 0)
        if diem > ut[khoa_tt]:
            ut[khoa_tt] = diem
            ra[khoa_tt] = gia_tri
            ra[khoa_tu] = nguon
            ra[khoa_tr] = LAY_DUOC

    def da_tra_loi(khoa_tr):
        if ra[khoa_tr] == CHUA_TRA:
            ra[khoa_tr] = KHONG_CO

    # (1) Europe PMC core — vừa lấy grantsList vừa phân giải pmid/pmcid cho bước sau
    q = urllib.parse.quote('DOI:"%s"' % doi)
    try:
        b = m.lay("%s/search?query=%s&resultType=core&format=json" % (EPMC, q),
                  "%s.epmc-core.json" % doi.replace("/", "_"))
        d = boc_epmc_core(b)
        ra["pmid"], ra["pmcid"] = d["pmid"], d["pmcid"]
        ghi("tai_tro", "tai_tro_tu", "tai_tro_trang_thai",
            " · ".join(d["tai_tro"]), "Europe PMC core · grantsList")
        da_tra_loi("tai_tro_trang_thai")
        ra["da_hoi"].append("Europe PMC core")
    except KhongTraDuoc as e:
        ra["loi"].append("Europe PMC core: %s" % e)

    # (2) PubMed efetch XML — CoiStatement là nguồn COI nguyên văn tốt nhất
    if ra["pmid"]:
        try:
            b = m.lay("%s/efetch.fcgi?db=pubmed&retmode=xml&id=%s" % (EUTILS, ra["pmid"]),
                      "%s.pubmed.xml" % doi.replace("/", "_"))
            d = boc_pubmed(b)
            ghi("coi", "coi_tu", "coi_trang_thai", d["coi"], "PubMed XML · CoiStatement")
            ghi("tai_tro", "tai_tro_tu", "tai_tro_trang_thai",
                " · ".join(d["tai_tro"]), "PubMed XML · GrantList")
            da_tra_loi("coi_trang_thai")
            da_tra_loi("tai_tro_trang_thai")
            ra["da_hoi"].append("PubMed efetch")
        except KhongTraDuoc as e:
            ra["loi"].append("PubMed efetch: %s" % e)

    # (3) Europe PMC fullTextXML — chỉ bài truy cập mở, nhưng cho câu NGUYÊN VĂN
    if ra["pmcid"]:                       # luôn thử: đây là nguồn NGUYÊN VĂN tốt nhất
        try:
            b = m.lay("%s/%s/fullTextXML" % (EPMC, ra["pmcid"]),
                      "%s.epmc-fulltext.xml" % doi.replace("/", "_"))
            d = boc_epmc_fulltext(b)
            ghi("tai_tro", "tai_tro_tu", "tai_tro_trang_thai",
                " · ".join(d["tai_tro"]), "Europe PMC fullTextXML · funding-statement")
            ghi("coi", "coi_tu", "coi_trang_thai", d["coi"],
                "Europe PMC fullTextXML · chú thích COI")
            da_tra_loi("tai_tro_trang_thai")
            da_tra_loi("coi_trang_thai")
            ra["da_hoi"].append("Europe PMC fullTextXML")
        except KhongTraDuoc as e:
            ra["loi"].append("Europe PMC fullTextXML: %s" % e)

    # (4) Crossref — Funder Registry, dự phòng cho tài trợ
    if not ra["tai_tro"]:
        try:
            b = m.lay("%s/%s" % (CROSSREF, urllib.parse.quote(doi)),
                      "%s.crossref.json" % doi.replace("/", "_"))
            d = boc_crossref(b)
            ghi("tai_tro", "tai_tro_tu", "tai_tro_trang_thai",
                " · ".join(d["tai_tro"]), "Crossref · funder[]")
            da_tra_loi("tai_tro_trang_thai")
            ra["da_hoi"].append("Crossref")
        except KhongTraDuoc as e:
            ra["loi"].append("Crossref: %s" % e)

    return ra


# ───────────────────────────── in ra ─────────────────────────────

def o_bang(giatri: str, trang_thai: str, tu: str, dai: int) -> str:
    if trang_thai == LAY_DUOC:
        s = giatri.replace("|", "\\|")
        if len(s) > dai:
            s = s[:dai].rstrip() + "… **[CẮT BỚT — xem tệp thô]**"
        return s
    if trang_thai == KHONG_CO:
        return "**CHƯA LẤY ĐƯỢC** — chỉ mục không mang trường này; phải mở toàn văn"
    return "**CHƯA TRA ĐƯỢC** — lỗi mạng, chưa biết gì"


def in_bang(ket: list[dict], dai: int) -> None:
    print()
    print("Dán vào mục *10.x Xung đột lợi ích và tài trợ* của bản cập nhật:")
    print()
    print("| Nguồn (DOI) | Tài trợ | COI của nhóm tác giả | Vai trò nhà tài trợ | Lấy từ đâu |")
    print("|---|---|---|---|---|")
    for r in ket:
        tu = " + ".join(x for x in (r["tai_tro_tu"], r["coi_tu"]) if x) or "—"
        print("| %s | %s | %s | **[CẦN KIỂM CHỨNG]** — phải đọc toàn văn | %s |"
              % (r["doi"],
                 o_bang(r["tai_tro"], r["tai_tro_trang_thai"], r["tai_tro_tu"], dai),
                 o_bang(r["coi"], r["coi_trang_thai"], r["coi_tu"], dai),
                 tu))
    print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Lấy nguyên văn câu tài trợ và COI cho mục 10.x của bản cập nhật.")
    ap.add_argument("file", nargs="?", help="bản cập nhật .md / dashboard .html / .bib")
    ap.add_argument("--doi", nargs="+", default=[], help="DOI rời, thay cho tệp")
    ap.add_argument("--json", action="store_true", help="xuất JSON thay vì bảng")
    ap.add_argument("--luu-tho", dest="luu_tho", metavar="THƯ_MỤC",
                    help="lưu phản hồi thô để rà lại — NÊN dùng ở lần chạy đầu")
    ap.add_argument("--tu-tho", dest="tu_tho", metavar="THƯ_MỤC",
                    help="bóc tách lại từ phản hồi đã lưu, KHÔNG gọi mạng")
    ap.add_argument("--dai-toi-da", type=int, default=1200, metavar="N",
                    help="cắt bớt ô quá dài trong bảng (mặc định 1200 ký tự)")
    a = ap.parse_args()

    if a.doi:
        dois = [norm_doi(d) for d in a.doi]
    elif a.file:
        if not os.path.isfile(a.file):
            print("✗ Không thấy %s" % a.file, file=sys.stderr)
            return 1
        dois = extract_dois(open(a.file, encoding="utf-8", errors="replace").read())
    else:
        ap.error("cần một tệp, hoặc --doi")
        return 1

    if not dois:
        print("✗ Không rút được DOI nào từ %s." % a.file, file=sys.stderr)
        return 1

    # Banner và tiến độ ra stderr, để stdout chỉ chứa ĐÚNG sản phẩm (bảng hoặc JSON)
    # — có vậy mới pipe được sang tệp/công cụ khác.
    print("═" * 72, file=sys.stderr)
    print("LẤY COI / TÀI TRỢ — %d DOI%s" % (len(dois), "  (chế độ --tu-tho, không gọi mạng)"
                                            if a.tu_tho else ""), file=sys.stderr)
    print("═" * 72, file=sys.stderr)

    m = Mang(luu_tho=a.luu_tho, tu_tho=a.tu_tho)
    ket = []
    for i, d in enumerate(dois, 1):
        print("  [%2d/%d] %s" % (i, len(dois), d), file=sys.stderr)
        ket.append(mot_nguon(m, d))
        if m.chan:
            print("\n⊘ MẠNG BỊ CHẶN — 3 lần liên tiếp không gọi được nguồn nào.\n"
                  "   Dừng ở đây thay vì in %d lỗi giống nhau.\n"
                  "   Đây KHÔNG phải 'các bài không có tài trợ'. Chưa tra được thì chưa biết gì.\n"
                  "   Chạy lại trên máy có mạng bình thường (không qua proxy chặn egress)."
                  % (len(dois) - i), file=sys.stderr)
            break

    # Dừng sớm vì mạng chặn thì các DOI CHƯA ĐỘNG ĐẾN vẫn phải có mặt trong bảng.
    # Thiếu dòng = dán vào bản cập nhật là âm thầm mất nguồn — đúng thứ hệ thống này chống.
    da_co = {r["doi"] for r in ket}
    for d in dois:
        if d not in da_co:
            ket.append({"doi": d, "pmid": "", "pmcid": "",
                        "tai_tro": "", "tai_tro_tu": "", "tai_tro_trang_thai": CHUA_TRA,
                        "coi": "", "coi_tu": "", "coi_trang_thai": CHUA_TRA,
                        "tat_ca": {"tai_tro": {}, "coi": {}},
                        "loi": ["chưa gọi tới — đã dừng vì mạng bị chặn"], "da_hoi": []})

    if a.json:
        print(json.dumps(ket, ensure_ascii=False, indent=2))
    else:
        in_bang(ket, a.dai_toi_da)

    du = [r for r in ket if r["tai_tro_trang_thai"] == LAY_DUOC and r["coi_trang_thai"] == LAY_DUOC]
    thieu = [r for r in ket if r not in du]
    print("─" * 72, file=sys.stderr)
    print("Đủ CẢ tài trợ và COI : %d/%d" % (len(du), len(dois)), file=sys.stderr)
    for r in thieu:
        print("  · %s — tài trợ: %s · COI: %s"
              % (r["doi"], r["tai_tro_trang_thai"], r["coi_trang_thai"]), file=sys.stderr)
    if a.luu_tho:
        print("Phản hồi thô đã lưu ở %s/ — MỞ VÀI TỆP ĐỐI CHIẾU trước khi dán kết quả."
              % a.luu_tho, file=sys.stderr)
    if thieu:
        print("KẾT QUẢ: ⊘ KHÔNG KẾT LUẬN — còn ô trống. Mở toàn văn cho các DOI trên.",
              file=sys.stderr)
        return 2
    print("KẾT QUẢ: ✓ Đủ cho mọi DOI. Vẫn phải người đọc điền cột 'vai trò nhà tài trợ'.",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
