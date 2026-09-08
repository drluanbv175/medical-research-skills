#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_dashboard.py — Cổng kiểm liêm chính cho Web Dashboard EBM (Dark Analyst / Evidence Workbench).

Kiểm TRƯỚC KHI GIAO cho bác sĩ:
  - Mỗi item có ≥1 định danh truy nguyên (pmid hoặc doi).
  - Mỗi item có gradeLevel + decision + references.
  - Có disclaimer "Cần bác sĩ kiểm chứng".
  - Quét dấu hiệu PII (cảnh báo để người rà — không tự ý kết luận).
  - (Tùy chọn --online) Tự XÁC MINH mỗi PMID phân giải đúng qua NCBI E-utilities
    (miễn phí, không cần key) → chống trích dẫn ảo. DOI kiểm định dạng.

Cách dùng:
    python3 verify_dashboard.py <dashboard.html>                     # chỉ kiểm cấu trúc
    python3 verify_dashboard.py <dashboard.html> --online            # + xác minh PMID trên PubMed
    python3 verify_dashboard.py <dashboard.html> --online --offline-ok
                                        # chấp nhận có ghi vết khi mạng chặn PubMed

NGUYÊN TẮC "FAIL CLOSED" (từ 2026-09-08):
    Khi đã yêu cầu --online mà KHÔNG xác minh được PMID (mạng lỗi/bị chặn), công cụ
    KHÔNG in PASS. Không xác minh được ≠ đã xác minh. Muốn giao vẫn phải nêu rõ điều
    đó bằng cờ --offline-ok, và dòng ghi vết sẽ nằm trong báo cáo để người rà thấy.

Mã thoát:
    0 = PASS            — không lỗi cứng; nếu chạy --online thì mọi PMID đã phân giải
    1 = FAIL            — có lỗi cứng, phải sửa trước khi giao
    2 = KHÔNG KẾT LUẬN  — không có lỗi cứng nhưng chưa xác minh được PMID (chỉ khi --online)

Lỗi cứng: item thiếu cả pmid lẫn doi; thiếu disclaimer; item thiếu gradeLevel/decision;
          PMID không phân giải được trên PubMed.
Cảnh báo (không chặn): nghi PII; PMID chưa xác minh khi đã bật --offline-ok.
"""
import sys, re, json, argparse

DISCLAIMER = "Cần bác sĩ kiểm chứng"
VALID_GRADE = {"high", "mod", "low", "vlow", "na"}
VALID_DECISION = {"apply", "consider", "notyet"}


def extract_data_block(html):
    """Lấy đoạn từ 'const DATA' tới hết khối (marker hoặc cân bằng ngoặc)."""
    i = html.find("const DATA")
    if i == -1:
        return None
    end = html.find("HẾT KHỐI DATA", i)
    return html[i:end] if end != -1 else html[i:i + 60000]


def split_items(data_block):
    """Tách từng object item theo mốc bắt đầu {id:'...' hoặc {id:"..."."""
    items_pos = data_block.find("items:")
    seg = data_block[items_pos:] if items_pos != -1 else data_block
    starts = [m.start() for m in re.finditer(r"\{\s*id\s*:\s*['\"]", seg)]
    chunks = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(seg)
        chunks.append(seg[s:e])
    return chunks


def field(chunk, name):
    m = re.search(name + r"\s*:\s*['\"]([^'\"]*)['\"]", chunk)
    return m.group(1) if m else None


def verify_pmid_online(pmid):
    import urllib.request
    url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
           "?db=pubmed&retmode=json&id=" + pmid)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            j = json.loads(r.read().decode("utf-8"))
        res = j.get("result", {})
        if pmid in res and "title" in res[pmid]:
            return True, res[pmid].get("title", "")[:90]
        return False, "không có trong PubMed"
    except Exception as e:
        return None, "lỗi mạng: %s" % e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--online", action="store_true", help="xác minh PMID/DOI trên mạng")
    ap.add_argument("--offline-ok", dest="offline_ok", action="store_true",
                    help="chấp nhận giao khi mạng chặn PubMed — hạ PMID chưa xác minh "
                         "từ LỖI xuống cảnh báo, có ghi vết trong báo cáo")
    a = ap.parse_args()
    unresolved = []

    html = open(a.file, encoding="utf-8").read()
    errors, warns, oks = [], [], []

    # 1) Disclaimer
    if DISCLAIMER in html:
        oks.append("Có disclaimer \"%s\"." % DISCLAIMER)
    else:
        errors.append("THIẾU disclaimer \"%s\"." % DISCLAIMER)

    data = extract_data_block(html)
    if not data:
        errors.append("Không tìm thấy khối const DATA.")
        return report(errors, warns, oks, [], a.offline_ok)

    items = split_items(data)
    if not items:
        errors.append("Không tách được item nào trong items[].")
    oks.append("Số item: %d." % len(items))

    pmids = []
    for ch in items:
        iid = field(ch, "id") or "(?)"
        pmid = field(ch, "pmid")
        doi = field(ch, "doi")
        url = field(ch, "url")
        grade = field(ch, "gradeLevel")
        dec = field(ch, "decision")
        if not (pmid or doi or url):
            errors.append("[%s] THIẾU định danh truy nguyên (pmid/doi/url)." % iid)
        if pmid:
            pmids.append((iid, pmid))
        if grade not in VALID_GRADE:
            errors.append("[%s] gradeLevel không hợp lệ: %r (cần %s)." % (iid, grade, VALID_GRADE))
        if dec not in VALID_DECISION:
            errors.append("[%s] decision không hợp lệ: %r (cần %s)." % (iid, dec, VALID_DECISION))
        if "references" not in ch:
            warns.append("[%s] không thấy references[]." % iid)

    # 2) PII (heuristic — chỉ cảnh báo)
    pii = []
    pii += re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", html)            # ngày sinh dạng dd/mm/yyyy
    pii += re.findall(r"\b0\d{9}\b", html)                            # SĐT VN
    pii += re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", html)              # email
    pii += re.findall(r"\bCCCD|CMND|số\s*BHYT|mã\s*BN|MRN\b", html, re.I)
    if pii:
        warns.append("Nghi PII (RÀ TAY): %s" % ", ".join(sorted(set(pii))[:8]))
    else:
        oks.append("Không thấy mẫu PII rõ ràng.")

    # 3) Xác minh PMID/DOI online
    if a.online and pmids:
        oks.append("Đang xác minh %d PMID trên PubMed…" % len(set(p for _, p in pmids)))
        seen = {}
        for iid, p in pmids:
            if p in seen:
                ok, info = seen[p]
            else:
                ok, info = verify_pmid_online(p)
                seen[p] = (ok, info)
            if ok is True:
                oks.append("[%s] PMID %s ✓ %s" % (iid, p, info))
            elif ok is False:
                errors.append("[%s] PMID %s KHÔNG phân giải: %s" % (iid, p, info))
            else:
                unresolved.append((iid, p, info))
        n_ok = sum(1 for _, p in pmids if seen.get(p, (None, ""))[0] is True)
        n_all = len(set(p for _, p in pmids))
        oks.append("ĐÃ XÁC MINH %d/%d PMID trên PubMed." % (n_ok, n_all))
        for iid, p, info in unresolved:
            msg = "[%s] PMID %s CHƯA xác minh được (%s)." % (iid, p, info)
            (warns if a.offline_ok else errors).append(msg)
    elif pmids:
        warns.append("CHƯA xác minh phân giải %d PMID — mới kiểm cấu trúc. "
                     "Chạy --online trước khi giao." % len(set(p for _, p in pmids)))

    return report(errors, warns, oks, unresolved, a.offline_ok)


def report(errors, warns, oks, unresolved=(), offline_ok=False):
    print("=" * 64)
    print("CỔNG KIỂM LIÊM CHÍNH — Web Dashboard EBM")
    print("=" * 64)
    for o in oks:
        print("  ✓ " + o)
    for w in warns:
        print("  ⚠ " + w)
    for e in errors:
        print("  ✗ " + e)
    print("-" * 64)
    # PMID chưa xác minh được đã nằm trong `errors` khi không bật --offline-ok;
    # tách ra để LỖI THẬT luôn được ưu tiên báo trước.
    n_unres_as_err = len(unresolved) if not offline_ok else 0
    n_hard = len(errors) - n_unres_as_err
    if n_hard > 0:
        print("KẾT QUẢ: ✗ FAIL — %d lỗi cứng, %d cảnh báo. Sửa trước khi giao." % (n_hard, len(warns)))
        if n_unres_as_err:
            print("         (kèm %d PMID chưa xác minh được — xem bên trên)" % n_unres_as_err)
        return 1
    if unresolved and not offline_ok:
        print("KẾT QUẢ: ⊘ KHÔNG KẾT LUẬN — %d PMID chưa xác minh được (mạng chặn PubMed)."
              % len(unresolved))
        print("         KHÔNG in PASS: CHƯA xác minh KHÁC với ĐÃ xác minh.")
        print("         → Chạy lại trên máy có mạng, HOẶC dùng --offline-ok để giao có ghi vết.")
        return 2
    if unresolved and offline_ok:
        print("KẾT QUẢ: ✓ PASS CÓ ĐIỀU KIỆN — 0 lỗi cứng, %d cảnh báo." % len(warns))
        print("         ⚑ GHI VẾT: %d PMID CHƯA được xác minh trên PubMed; người giao chủ động"
              % len(unresolved))
        print("           chấp nhận bằng --offline-ok. PHẢI xác minh lại khi có mạng.")
        return 0
    print("KẾT QUẢ: ✓ PASS — 0 lỗi cứng, %d cảnh báo (rà tay nếu có)." % len(warns))
    return 0


if __name__ == "__main__":
    sys.exit(main())
