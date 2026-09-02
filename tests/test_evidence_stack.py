#!/usr/bin/env python3
"""Kiểm thử hạ tầng nguồn chứng cứ.

Chạy được ở CẢ môi trường bị chặn lẫn môi trường mạng thông:
nhánh "mạng thông" của doctor.py được kiểm bằng phản hồi mô phỏng,
nên không phụ thuộc việc nguồn thật có truy cập được hay không.

    python3 tests/test_evidence_stack.py
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import evidence_net as en
import doctor
import retraction_check as rc

P = F = 0
def t(name, cond):
    global P, F
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    P, F = (P + 1, F) if cond else (P, F + 1)


def test_classify():
    print("\n### Phân loại lỗi mạng ###")
    t("tunnel 403 -> egress_blocked",
      en.classify(Exception("Tunnel connection failed: 403 Forbidden")).kind == en.EGRESS_BLOCKED)
    t("tunnel 407 -> proxy_auth",
      en.classify(Exception("Tunnel connection failed: 407 Proxy Auth")).kind == en.PROXY_AUTH)
    t("cert -> tls_untrusted",
      en.classify(Exception("certificate verify failed")).kind == en.TLS_UNTRUSTED)
    t("reset KHÔNG phải bị chặn",
      not en.classify(Exception("connection reset by peer")).blocked_by_policy)


def test_probe():
    print("\n### probe() ###")
    ok, _ = en.probe("https://github.com/")
    t("host được allowlist -> reachable", ok is True)
    # 403/404 THẬT từ máy chủ nghĩa là tunnel đã mở -> vẫn tính là thông.
    ok2, _ = en.probe("https://api.github.com/repos/anthropics/___khong-ton-tai___")
    t("origin trả 4xx vẫn tính là thông", ok2 is True)


def test_fetch():
    print("\n### urlopen_json trên mạng thật ###")
    try:
        d = en.urlopen_json("https://api.github.com/", 20)
        t("lấy + parse JSON trả về dict", isinstance(d, dict))
    except en.SourceUnavailable as e:
        t(f"lấy + parse JSON (bỏ qua: {e.kind})", e.blocked_by_policy)
    try:
        en.urlopen_json("https://api.github.com/repos/anthropics/___khong-ton-tai___", 20)
        t("403 thật phải ném lỗi", False)
    except en.SourceUnavailable as e:
        t("403 thật -> http_error, KHÔNG phải egress_blocked",
          e.kind == en.HTTP_ERROR and not e.blocked_by_policy)


def test_doi_regex():
    print("\n### Rút DOI (DOI Lancet có dấu ngoặc) ###")
    cases = [
        ("(10.1136/bmj.n71).", "10.1136/bmj.n71"),
        ("doi: 10.1016/S0140-6736(20)31180-6).", "10.1016/s0140-6736(20)31180-6"),
        ("https://doi.org/10.1016/S0140-6736(97)11096-0", "10.1016/s0140-6736(97)11096-0"),
        ("[10.61882/zwq4sh57]", "10.61882/zwq4sh57"),
    ]
    for text, want in cases:
        got = rc.extract_dois(text)
        t(f"{text[:40]:<40} -> {want[:34]}", got and got[0] == want)


def test_retraction_report():
    print("\n### Phán định bài bị rút ###")
    scite = {"hits": [
        {"doi": "10.1016/s0140-6736(97)11096-0", "title": "RETRACTED: ...",
         "editorialNotices": [{"status": "retracted", "noticeDoi": "10.x", "date": "2010-2-6"},
                              {"status": "comment", "noticeDoi": "10.y", "date": "1998-2"}]},
        {"doi": "10.1136/bmj.n71", "title": "PRISMA 2020"},
    ]}
    rep = rc.build_report(scite, ["10.1016/S0140-6736(97)11096-0", "10.1136/bmj.n71",
                                  "10.9999/khong-co"])
    s = rep["thong_ke"]
    t("bắt đúng 1 bài bị rút", s[rc.RETRACTED] == 1)
    t("PRISMA sạch", s[rc.CLEAN] == 1)
    t("DOI thiếu -> CHUA_KIEM (không phải sạch)", s[rc.UNCHECKED] == 1)
    t("khớp DOI không phân biệt hoa/thường",
      not any(r["phan_dinh"] == rc.UNCHECKED and "11096" in r["doi"] for r in rep["chi_tiet"]))
    t("'comment' không bị tính là tì vết",
      all(n["loai"] != rc.CORRECTED for r in rep["chi_tiet"] for n in r["notices"]))


def test_doctor_live():
    print("\n### doctor.sec_live (mô phỏng nhánh mạng thông) ###")
    real = en.urlopen_json

    def ok(url, timeout=20, headers=None):
        if "esearch.fcgi" in url:
            return {"esearchresult": {"count": "84213", "idlist": ["1"]}}
        if "bmj.n71" in url:
            return {"message": {"title": ["The PRISMA 2020 statement"]}}
        return {"message": {"update-to": [{"type": "retraction"}], "relation": {}}}

    def bad(url, timeout=20, headers=None):
        if "esearch.fcgi" in url:
            return {"esearchresult": {"count": "0"}}
        return {"message": {"title": ["Sai hoàn toàn"]}}

    def blocked(url, timeout=20, headers=None):
        raise en.SourceUnavailable(kind=en.EGRESS_BLOCKED, url=url, host="x", detail="chặn")

    try:
        en.urlopen_json = ok
        r = doctor.Report(); res = doctor.sec_live(r)
        t("mọi thứ tốt -> True", res is True)
        t("không dòng nào 'bad'", not any(x[1] == "bad" for x in r.sections[-1]["rows"]))

        en.urlopen_json = bad
        r2 = doctor.Report(); res2 = doctor.sec_live(r2)
        t("dữ liệu sai -> False (không lặng lẽ pass)", res2 is False)
        t("có ghi nhận problem", len(r2.problems) > 0)

        en.urlopen_json = blocked
        r3 = doctor.Report()
        t("bị chặn giữa chừng -> False, không vỡ", doctor.sec_live(r3) is False)
    finally:
        en.urlopen_json = real



def test_local_retraction_watch():
    print("\n### Bộ dữ liệu Retraction Watch cục bộ ###")
    found = {
        "10.1016/s0140-6736(97)11096-0": [
            {"nature": "Retraction", "retraction_doi": "10.1016/s0140-6736(10)60175-4",
             "retraction_date": "2/6/2010", "reason": "+Falsification", "title": "Wakefield"}],
        "10.5555/reinstated.paper": [
            {"nature": "Retraction", "retraction_doi": "10.9999/r1",
             "retraction_date": "2019", "reason": "", "title": "Reinstated"},
            {"nature": "Reinstatement", "retraction_doi": "10.9999/i1",
             "retraction_date": "2020", "reason": "", "title": "Reinstated"}],
        "10.7777/concern.only": [
            {"nature": "Expression of concern", "retraction_doi": "10.9999/e1",
             "retraction_date": "2021", "reason": "", "title": "Concern"}],
        "10.1136/bmj.n71": [],
    }
    rep = rc.build_report_local(
        ["10.1016/S0140-6736(97)11096-0", "10.5555/reinstated.paper",
         "10.7777/concern.only", "10.1136/bmj.n71"], found, dataset_age=3.0)
    st = rep["thong_ke"]
    t("retraction -> RUT_BAI", st[rc.RETRACTED] == 1)
    t("expression of concern -> QUAN_NGAI", st[rc.CONCERN] == 2)
    t("không có bản ghi -> SACH (RW là sổ đầy đủ)", st[rc.CLEAN] == 1)
    t("không có ca CHUA_KIEM ở chế độ local", st[rc.UNCHECKED] == 0)

    reins = [r for r in rep["chi_tiet"] if "reinstated" in r["doi"]][0]
    t("bị rút RỒI phục hồi -> KHÔNG tự hạ thành sạch", reins["phan_dinh"] == rc.CONCERN)
    t("có ghi chú yêu cầu kiểm tay", "thủ công" in (reins["ghi_chu"] or ""))
    t("báo cáo ghi rõ nguồn", "Retraction Watch" in rep.get("nguon", ""))
    t("báo cáo ghi tuổi dữ liệu", rep.get("tuoi_du_lieu_ngay") == 3.0)

    out = rc.render(rep)
    t("render hiện tuổi dữ liệu", "Tuổi dữ liệu" in out)
    rep_old = rc.build_report_local(["10.1136/bmj.n71"], {"10.1136/bmj.n71": []},
                                    dataset_age=90.0)
    t("dữ liệu cũ -> cảnh báo trong render", "CŨ" in rc.render(rep_old))


for fn in (test_classify, test_probe, test_fetch, test_doi_regex,
           test_retraction_report, test_local_retraction_watch, test_doctor_live):
    fn()

print(f"\n{'=' * 50}\n  PASS={P}  FAIL={F}\n{'=' * 50}")
sys.exit(1 if F else 0)
