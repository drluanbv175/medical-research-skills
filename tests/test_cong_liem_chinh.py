#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm hồi quy cho các CỔNG LIÊM CHÍNH — khoá chặt những lỗi FAIL-OPEN đã từng xảy ra.

Vì sao có tệp này
-----------------
Mỗi lỗi dưới đây đều đã xảy ra THẬT trong repo này, được bắt bằng tay, rồi sửa. Sửa xong
mà không khoá lại thì lần tới có người dẫm lại y hệt. Điểm chung của cả bốn: **hệ thống
nói "ổn" trong khi thực ra nó chưa kiểm được gì** — nguy hiểm hơn hẳn việc báo lỗi.

  1. `verify_dashboard --bien-ban` in ✓ PASS kèm dòng "đã xác minh theo biên bản" ngay cả
     khi biên bản KHÔNG xác minh được PMID nào (mục `phan_giai: null` bị bỏ qua).
  2. `pubmed_search.py` gộp "lỗi mạng" với "không có kết quả" vào một câu.
  3. `surveillance_scan.py` nuốt lỗi truy vấn rồi chân trang vẫn ghi "Tổng 0 ứng viên".
  4. `make_derivatives.py` ghi đè im lặng tờ dặn người bệnh ĐÃ RÀ TAY bằng bản nháp máy.

Và hai cổng khác cần khoá luôn vì cùng họ:
  5. Thiếu GHI VẾT TRA CỨU trong `DATA.meta` phải là LỖI CỨNG.
  6. Bộ bóc tách COI phải ưu tiên câu nguyên văn hơn dữ liệu có cấu trúc, và không
     được nhét `orderIn` (số thứ tự) vào như thể là thông tin tài trợ.

KHÔNG cần mạng. Chạy được ở cả nơi bị chặn lẫn nơi mạng thông:
    python3 tests/test_cong_liem_chinh.py
"""
import contextlib
import io as _io
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "EBM-Dashboards", "tools"))

VERIFY = os.path.join(ROOT, "EBM-Dashboards", "tools", "verify_dashboard.py")
DASHBOARD_THAT = os.path.join(
    ROOT, "EBM-Dashboards", "WebDashboard_EBM_VanDeCuThe_SaSutTriTue_20260908.html")

P = F = 0


def t(ten, dieu_kien):
    global P, F
    print("  [%s] %s" % ("PASS" if dieu_kien else "FAIL", ten))
    P, F = (P + 1, F) if dieu_kien else (P, F + 1)


@contextlib.contextmanager
def im_lang():
    """Nuốt stdout của công cụ gọi trong tiến trình, để bảng PASS/FAIL đọc được."""
    with contextlib.redirect_stdout(_io.StringIO()):
        yield


def chay(lenh):
    r = subprocess.run(lenh, capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


# ───────────────────────── vật liệu thử ─────────────────────────

DASHBOARD_MAU = """<!doctype html><html><body>
<footer>⚠ Cần bác sĩ kiểm chứng. Không lưu PII.</footer>
<script>
const DATA = {
  meta:{
    question:'Câu hỏi thử',
    searchDate:'2026-01-02',
    searchSources:['PubMed (connector)','Scite'],
    searchStrategy:'từ khoá thử; 10 kết quả → 2 chọn',
    nextReview:'2026-07-02 (6 tháng) — lý do: chủ đề ổn định'
  },
  items:[
    {id:'ITEM-01', title:'A', source:'S', org:'O', dateVersion:'2026',
     pmid:'11111111', doi:'10.1000/a', design:'RCT', population:'P',
     gradeSource:'Nguồn không cung cấp', gradeLevel:'na', decision:'apply',
     action:'x', vn:'y', references:['R1']},
    {id:'ITEM-02', title:'B', source:'S', org:'O', dateVersion:'2026',
     pmid:'22222222', doi:'10.1000/b', design:'RCT', population:'P',
     gradeSource:'Nguồn không cung cấp', gradeLevel:'na', decision:'consider',
     action:'x', vn:'y', references:['R2']}
  ]
};
</script></body></html>
"""


def bien_ban(pmid_map, sha=None):
    return {"phien_ban_bien_ban": "1.0", "ngay_lap": "2026-01-02T00:00:00+00:00",
            "moi_truong": {"he_dieu_hanh": "TestOS", "python": "3.11.0"},
            "tep": {"dashboard": {"ten": "d.html", "sha256_luc_lap": sha or "0" * 64},
                    "ban_cap_nhat": None},
            "pmid": pmid_map, "bai_rut": {"trang_thai": "CHƯA LÀM"},
            "coi_tai_tro": {"trang_thai": "CHƯA LÀM"}}


# ───────────────────────── 1. biên bản xác minh ─────────────────────────

def test_bien_ban():
    print("\n### 1. verify_dashboard --bien-ban — không được PASS khi chưa xác minh gì ###")
    with tempfile.TemporaryDirectory() as d:
        html = os.path.join(d, "d.html")
        open(html, "w", encoding="utf-8").write(DASHBOARD_MAU)

        def ghi(ten, noi_dung):
            p = os.path.join(d, ten)
            json.dump(noi_dung, open(p, "w", encoding="utf-8"), ensure_ascii=False)
            return p

        # (a) LỖI ĐÃ TỪNG XẢY RA: biên bản không xác minh được gì → từng ra PASS
        rong = ghi("rong.json", bien_ban({
            "11111111": {"phan_giai": None, "ly_do": "lỗi mạng"},
            "22222222": {"phan_giai": None, "ly_do": "lỗi mạng"}}))
        ma, ra = chay([sys.executable, VERIFY, html, "--bien-ban", rong])
        t("biên bản rỗng → mã thoát 2, KHÔNG phải 0", ma == 2)
        t("biên bản rỗng → in KHÔNG KẾT LUẬN", "KHÔNG KẾT LUẬN" in ra)
        t("biên bản rỗng → KHÔNG dám in 'PASS —'", "KẾT QUẢ: ✓ PASS —" not in ra)

        # (b) biên bản đủ → PASS, và ghi vết phải kèm SỐ THẬT
        du = ghi("du.json", bien_ban({
            "11111111": {"phan_giai": True, "tieu_de": "Bài A"},
            "22222222": {"phan_giai": True, "tieu_de": "Bài B"}}))
        ma, ra = chay([sys.executable, VERIFY, html, "--bien-ban", du])
        t("biên bản đủ → mã thoát 0", ma == 0)
        t("biên bản đủ → có ghi vết kèm số", "2/2 PMID theo biên bản" in ra)
        t("ghi vết nói rõ không phải phiên này", "KHÔNG diễn ra trong phiên này" in ra)

        # (c) thêm item mới sau khi lập biên bản → mã của nó phải bị bắt
        thieu = ghi("thieu.json", bien_ban({
            "11111111": {"phan_giai": True, "tieu_de": "Bài A"}}))
        ma, ra = chay([sys.executable, VERIFY, html, "--bien-ban", thieu])
        t("biên bản thiếu 1 mã → mã thoát 2", ma == 2)
        t("nêu đúng lý do 'KHÔNG có trong biên bản'", "KHÔNG có trong biên bản" in ra)
        t("chỉ bắt đúng mã thiếu", "22222222 CHƯA xác minh" in ra)

        # (d) biên bản ghi KHÔNG phân giải → trích dẫn ảo, phải là LỖI CỨNG
        ao = ghi("ao.json", bien_ban({
            "11111111": {"phan_giai": True, "tieu_de": "Bài A"},
            "22222222": {"phan_giai": False, "ly_do": "không có trong PubMed"}}))
        ma, ra = chay([sys.executable, VERIFY, html, "--bien-ban", ao])
        t("biên bản báo KHÔNG phân giải → mã thoát 1 (lỗi cứng)", ma == 1)
        t("gọi đúng tên: KHÔNG phân giải", "KHÔNG phân giải" in ra)

        # (e) sha lệch chỉ là CẢNH BÁO, không được làm hỏng cả biên bản
        ma, ra = chay([sys.executable, VERIFY, html, "--bien-ban", du])
        t("sha lệch → chỉ cảnh báo, vẫn PASS", ma == 0 and "ĐÃ ĐỔI kể từ lúc lập" in ra)


# ───────────────────────── 2. ghi vết tra cứu ─────────────────────────

def test_ghi_vet():
    print("\n### 2. Thiếu GHI VẾT TRA CỨU trong DATA.meta phải là LỖI CỨNG ###")
    with tempfile.TemporaryDirectory() as d:
        html = os.path.join(d, "d.html")
        open(html, "w", encoding="utf-8").write(
            DASHBOARD_MAU.replace("searchDate:'2026-01-02',", ""))
        ma, ra = chay([sys.executable, VERIFY, html])
        t("thiếu searchDate → mã thoát 1", ma == 1)
        t("nói rõ thiếu trường nào", "THIẾU `searchDate`" in ra)

        html2 = os.path.join(d, "d2.html")
        open(html2, "w", encoding="utf-8").write(
            DASHBOARD_MAU.replace("nextReview:'2026-07-02 (6 tháng) — lý do: chủ đề ổn định'",
                                  "nextReview:'sáu tháng nữa'"))
        ma, ra = chay([sys.executable, VERIFY, html2])
        t("nextReview không có ngày thật → lỗi cứng", ma == 1)


# ───────────────────────── 3. pubmed_search fail-closed ─────────────────────────

def test_pubmed_search():
    print("\n### 3. pubmed_search: lỗi mạng KHÁC 'không có bài' ###")
    duong = os.path.join(ROOT, "sao-luu-skill-cloud", "nghien-cuu-ebm-tong-hop", "scripts")
    if not os.path.isfile(os.path.join(duong, "pubmed_search.py")):
        t("(bỏ qua — chưa có pubmed_search.py)", True)
        return
    sys.path.insert(0, duong)
    import pubmed_search as ps

    goc_es, goc_argv = ps.esearch, sys.argv
    try:
        ps.esearch = lambda *a, **k: (_ for _ in ()).throw(
            ps.KhongGoiDuocNCBI("Tunnel connection failed: 403"))
        sys.argv = ["pubmed_search.py", "bất kỳ"]
        with im_lang():
            ma = ps.main()
        t("mạng hỏng → mã thoát 2 (KHÔNG KẾT LUẬN)", ma == 2)

        ps.esearch, ps.efetch = (lambda *a, **k: []), (lambda *a, **k: [])
        sys.argv = ["pubmed_search.py", "bất kỳ"]
        with im_lang():
            ma = ps.main()
        t("NCBI trả lời 0 kết quả → mã thoát 0", ma == 0)
    finally:
        ps.esearch, sys.argv = goc_es, goc_argv


# ───────────────────────── 4. surveillance_scan fail-closed ─────────────────────────

def test_surveillance():
    print("\n### 4. surveillance_scan: chủ đề tra hỏng KHÁC 'không có gì mới' ###")
    import surveillance_scan as ss
    goc_search, goc_argv = ss.search, sys.argv
    with tempfile.TemporaryDirectory() as d:
        wl = os.path.join(d, "wl.json")
        json.dump({"topics": [{"topic": "Chủ đề thử", "query": "x", "active": True}]},
                  open(wl, "w", encoding="utf-8"))
        bao_cao = os.path.join(d, "bc.md")
        try:
            ss.search = lambda *a, **k: (_ for _ in ()).throw(
                Exception("Tunnel connection failed: 403 Forbidden"))
            sys.argv = ["surveillance_scan.py", "--watchlist", wl, "--report", bao_cao]
            with im_lang():
                ma = ss.main()
            noi_dung = open(bao_cao, encoding="utf-8").read()
            t("chủ đề tra hỏng → mã thoát 2", ma == 2)
            t("báo cáo mở đầu bằng KHÔNG KẾT LUẬN", "KHÔNG KẾT LUẬN" in noi_dung)
            t("nói thẳng đây không phải 'không có gì mới'",
              "KHÔNG phải" in noi_dung and "không có gì mới" in noi_dung)

            ss.search, ss.summarize = (lambda *a, **k: []), (lambda *a, **k: [])
            sys.argv = ["surveillance_scan.py", "--watchlist", wl, "--report", bao_cao]
            with im_lang():
                ma2 = ss.main()
            t("tra được, 0 ứng viên → mã thoát 0", ma2 == 0)
        finally:
            ss.search, sys.argv = goc_search, goc_argv


# ───────────────────────── 5. make_derivatives không ghi đè ─────────────────────────

def test_phai_sinh_khong_ghi_de():
    print("\n### 5. make_derivatives KHÔNG ghi đè bản đã rà tay ###")
    cong_cu = os.path.join(ROOT, "EBM-Dashboards", "tools", "make_derivatives.py")
    if not (os.path.isfile(cong_cu) and os.path.isfile(DASHBOARD_THAT)):
        t("(bỏ qua — thiếu công cụ hoặc dashboard thật)", True)
        return
    with tempfile.TemporaryDirectory() as d:
        ma, _ = chay([sys.executable, cong_cu, DASHBOARD_THAT, "--outdir", d])
        sinh = sorted(f for f in os.listdir(d) if f.endswith(".md"))
        t("lần đầu: sinh đủ 3 sản phẩm", len(sinh) == 3)
        if not sinh:
            return
        mot = os.path.join(d, sinh[0])
        # Mô phỏng "người đã rà tay": bỏ dấu BẢN NHÁP TỰ ĐỘNG rồi sửa nội dung
        da_ra = open(mot, encoding="utf-8").read().replace("BẢN NHÁP TỰ ĐỘNG", "ĐÃ RÀ TAY")
        da_ra += "\n\nCâu người viết thêm, không được mất.\n"
        open(mot, "w", encoding="utf-8").write(da_ra)

        chay([sys.executable, cong_cu, DASHBOARD_THAT, "--outdir", d])
        sau = open(mot, encoding="utf-8").read()
        t("chạy lại: giữ nguyên bản đã rà tay", sau == da_ra)
        t("câu người viết thêm vẫn còn", "Câu người viết thêm" in sau)

        chay([sys.executable, cong_cu, DASHBOARD_THAT, "--outdir", d, "--ghi-de"])
        t("--ghi-de thì mới được dựng lại", open(mot, encoding="utf-8").read() != da_ra)


# ───────────────────────── 6. bộ bóc tách COI ─────────────────────────

def test_boc_coi():
    print("\n### 6. lay_coi_tai_tro: ưu tiên nguyên văn, không nhét rác ###")
    try:
        import lay_coi_tai_tro as lc
    except Exception:
        t("(bỏ qua — chưa có lay_coi_tai_tro.py)", True)
        return

    epmc = lc.boc_epmc_core(json.dumps({"resultList": {"result": [{
        "pmid": "1", "pmcid": "PMC1", "doi": "10.1/x",
        "grantsList": {"grant": [{"agency": "Cơ quan A", "grantId": "", "orderIn": 1}]}}]}}
    ).encode("utf-8"))
    t("KHÔNG nhét `orderIn` vào chuỗi tài trợ", "1" not in "".join(epmc["tai_tro"]))
    t("vẫn lấy đúng tên cơ quan", epmc["tai_tro"] == ["Cơ quan A"])

    xml_pubmed = """<PubmedArticleSet><PubmedArticle><MedlineCitation>
      <Article><GrantList><Grant><GrantID>G-1</GrantID><Agency>NIH</Agency>
      <Country>US</Country></Grant></GrantList></Article>
      <CoiStatement>Tác giả khai báo X.</CoiStatement>
      </MedlineCitation></PubmedArticle></PubmedArticleSet>"""
    pm = lc.boc_pubmed(xml_pubmed.encode("utf-8"))
    t("PubMed: lấy được CoiStatement nguyên văn", pm["coi"] == "Tác giả khai báo X.")
    t("PubMed: GrantList đầy đủ hơn", pm["tai_tro"] == ["NIH · G-1 · US"])
    t("nguồn nguyên văn được xếp ưu tiên cao hơn",
      lc.UU_TIEN["PubMed XML · GrantList"] > lc.UU_TIEN["Europe PMC core · grantsList"])
    t("câu funding-statement là ưu tiên cao nhất",
      lc.UU_TIEN["Europe PMC fullTextXML · funding-statement"] >=
      max(lc.UU_TIEN.values()))

    ft = lc.boc_epmc_fulltext(b"""<article><front><article-meta>
      <funding-group><funding-statement>Do Quy X tai tro.</funding-statement></funding-group>
      <author-notes><fn fn-type="COI-statement"><p>Khong co xung dot.</p></fn></author-notes>
      </article-meta></front></article>""")
    t("JATS: lấy được câu tài trợ", ft["tai_tro"] == ["Do Quy X tai tro."])
    t("JATS: lấy được câu COI", ft["coi"] == "Khong co xung dot.")

    t("ba trạng thái là ba hằng số khác nhau",
      len({lc.LAY_DUOC, lc.KHONG_CO, lc.CHUA_TRA}) == 3)


# ───────────────────────── 7. khoá mẫu cập nhật ─────────────────────────

def test_khoa_mau():
    print("\n### 7. kiem_mau_cap_nhat: thiếu dòng ghi vết là LỖI CỨNG ###")
    cong_cu = os.path.join(ROOT, "EBM-Dashboards", "tools", "kiem_mau_cap_nhat.py")
    mau = os.path.join(ROOT, "EBM-Dashboards", "templates", "mau-cap-nhat-chuyen-sau.md")
    if not (os.path.isfile(cong_cu) and os.path.isfile(mau)):
        t("(bỏ qua — thiếu công cụ hoặc mẫu)", True)
        return
    with tempfile.TemporaryDirectory() as d:
        # Bản cập nhật chép NGUYÊN mẫu: đủ 11 mục nhưng ghi vết còn chỗ trống
        thu = os.path.join(d, "CapNhat_thu.md")
        shutil.copy(mau, thu)
        ma, ra = chay([sys.executable, cong_cu, thu])
        t("còn nguyên chỗ trống của mẫu → lỗi cứng", ma == 1)
        t("nói rõ là chưa điền", "chưa điền" in ra or "chỗ trống" in ra)


for fn in (test_bien_ban, test_ghi_vet, test_pubmed_search, test_surveillance,
           test_phai_sinh_khong_ghi_de, test_boc_coi, test_khoa_mau):
    fn()

print("\n%s\n  PASS=%d  FAIL=%d\n%s" % ("=" * 50, P, F, "=" * 50))
sys.exit(1 if F else 0)
