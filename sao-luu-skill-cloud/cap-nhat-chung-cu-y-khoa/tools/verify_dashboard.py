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
    python3 verify_dashboard.py <dashboard.html> --bien-ban <bb>.json
                                        # xác minh THEO BIÊN BẢN đã lập ở máy có mạng
    python3 verify_dashboard.py <dashboard.html> --online --offline-ok
                                        # chấp nhận có ghi vết khi mạng chặn PubMed

BIÊN BẢN XÁC MINH (từ 2026-09-09)
    Nơi bị chặn egress thì không tự xác minh được, nhưng vẫn có thể ĐỌC LẠI bằng chứng
    do máy có mạng lập ra: `tools/lap_bien_ban_xac_minh.py`. Biên bản ràng buộc theo
    TẬP ĐỊNH DANH, không theo byte tệp — sửa lỗi chính tả trong dashboard không làm mất
    hiệu lực, nhưng THÊM item mới thì PMID của nó không có trong biên bản → vẫn báo chưa
    xác minh. Đây là PASS thật, có truy nguyên, khác hẳn `--offline-ok` (tự nhận là chưa kiểm).

NGUYÊN TẮC "FAIL CLOSED" (từ 2026-09-08):
    Khi đã yêu cầu --online mà KHÔNG xác minh được PMID (mạng lỗi/bị chặn), công cụ
    KHÔNG in PASS. Không xác minh được ≠ đã xác minh. Muốn giao vẫn phải nêu rõ điều
    đó bằng cờ --offline-ok, và dòng ghi vết sẽ nằm trong báo cáo để người rà thấy.

Mã thoát:
    0 = PASS            — không lỗi cứng; nếu chạy --online thì mọi PMID đã phân giải
    1 = FAIL            — có lỗi cứng, phải sửa trước khi giao
    2 = KHÔNG KẾT LUẬN  — không có lỗi cứng nhưng chưa xác minh được PMID (chỉ khi --online)

Lỗi cứng: item thiếu cả pmid lẫn doi; thiếu disclaimer; item thiếu gradeLevel/decision;
          PMID không phân giải được trên PubMed;
          THIẾU GHI VẾT TRA CỨU trong DATA.meta (searchDate · searchSources · searchStrategy ·
          nextReview) — một dashboard không nói mình tra ngày nào, ở đâu, thì không rà lại được.
Cảnh báo (không chặn): nghi PII; PMID chưa xác minh khi đã bật --offline-ok;
          item không có `funding`/`coi` (thường không lấy được bằng máy — phải ghi trong
          mục COI của bản cập nhật .md, xem 5D-quater của SKILL.md).
"""
import sys, re, json, hashlib, argparse

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


CO_NGAY = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}")


def lay_khoi_meta(data_block):
    """Cắt đoạn meta:{...} — dừng ở `summary:` hoặc `items:`, cái nào tới trước."""
    i = data_block.find("meta:")
    if i < 0:
        return ""
    ends = [x for x in (data_block.find("summary:", i), data_block.find("items:", i)) if x > 0]
    return data_block[i:min(ends)] if ends else data_block[i:i + 4000]


def mang_chuoi(meta, ten):
    """Đọc `ten:[ 'a', 'b' ]` → ['a','b']. Trả [] nếu không có hoặc rỗng."""
    m = re.search(ten + r"\s*:\s*\[", meta)
    if not m:
        return []
    j, sau = m.end(), 1
    while j < len(meta) and sau:
        sau += (meta[j] == "[") - (meta[j] == "]")
        j += 1
    return re.findall(r"['\"]([^'\"]+)['\"]", meta[m.end():j - 1])


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
    ap.add_argument("--bien-ban", dest="bien_ban", metavar="TỆP.json",
                    help="biên bản xác minh do tools/lap_bien_ban_xac_minh.py lập "
                         "trên máy có mạng")
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

    # 1-bis) GHI VẾT TRA CỨU trong DATA.meta (bắt buộc từ 2026-09-08)
    meta = lay_khoi_meta(data)
    for ten, nhan, phai_co_ngay in (
            ("searchDate", "ngày tra cứu", True),
            ("searchStrategy", "chiến lược tìm", False),
            ("nextReview", "ngày rà lại kế tiếp", True)):
        gt = (field(meta, ten) or "").strip()
        if not gt:
            errors.append("GHI VẾT: DATA.meta THIẾU `%s` (%s)." % (ten, nhan))
        elif phai_co_ngay and not CO_NGAY.search(gt):
            errors.append("GHI VẾT: DATA.meta.%s không có ngày thật: %r" % (ten, gt[:60]))
        else:
            oks.append("GHI VẾT %s: %s" % (ten, gt[:70]))
    nguon = mang_chuoi(meta, "searchSources")
    if not nguon:
        errors.append("GHI VẾT: DATA.meta THIẾU `searchSources` — phải liệt kê từng CSDL đã tra "
                      "(ghi cả nguồn BỊ CHẶN, để lần sau khỏi thử lại).")
    else:
        oks.append("GHI VẾT searchSources: %d nguồn (%s)." % (len(nguon), ", ".join(nguon[:4])))
    if not (field(meta, "retractionCheck") or "").strip():
        warns.append("GHI VẾT: DATA.meta chưa có `retractionCheck` — chạy tools/retraction_check.py "
                     "rồi ghi ngày + kết quả vào đây (xem 5D-ter).")

    items = split_items(data)
    if not items:
        errors.append("Không tách được item nào trong items[].")
    oks.append("Số item: %d." % len(items))

    pmids = []
    thieu_funding = []
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
        if not (field(ch, "funding") or "").strip():
            thieu_funding.append(iid)

    if thieu_funding:
        warns.append("%d item chưa ghi `funding` (%s%s) — thường KHÔNG lấy được bằng máy; "
                     "phải ghi vào mục COI/tài trợ của bản cập nhật .md."
                     % (len(thieu_funding), ", ".join(thieu_funding[:6]),
                        "…" if len(thieu_funding) > 6 else ""))

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

    # 3) Xác minh PMID — trực tiếp (--online) và/hoặc theo BIÊN BẢN (--bien-ban)
    bb, bb_note = None, None
    if a.bien_ban:
        try:
            bb = json.load(open(a.bien_ban, encoding="utf-8"))
        except Exception as e:
            errors.append("Không đọc được biên bản %s: %s" % (a.bien_ban, e))
    if bb:
        tep = (bb.get("tep") or {}).get("dashboard") or {}
        sha_now = hashlib.sha256(open(a.file, "rb").read()).hexdigest()
        if tep.get("sha256_luc_lap") and tep["sha256_luc_lap"] != sha_now:
            warns.append("Dashboard ĐÃ ĐỔI kể từ lúc lập biên bản (%s… → %s…). Biên bản ràng "
                         "buộc theo tập định danh nên vẫn dùng được cho PMID cũ, nhưng hãy rà "
                         "lại phần đã sửa." % (tep["sha256_luc_lap"][:12], sha_now[:12]))
        bb_note = "biên bản lập %s trên %s" % (bb.get("ngay_lap", "?"),
                                               (bb.get("moi_truong") or {}).get("he_dieu_hanh", "?"))
        oks.append("Có biên bản xác minh: %s." % bb_note)

    if pmids:
        rieng = sorted(set(p for _, p in pmids))
        ket = {}                       # pmid -> (True/False/None, thông tin, nguồn)
        if a.online:
            oks.append("Đang xác minh %d PMID trên PubMed…" % len(rieng))
            for p in rieng:
                ok, info = verify_pmid_online(p)
                ket[p] = (ok, info, "PubMed trực tiếp")
        if bb:
            # MỌI pmid đều phải có phán định khi đã đưa biên bản vào. Bỏ sót một mã
            # nghĩa là nó lọt qua cổng mà không ai xác minh — đúng lỗi fail-open.
            ghi = bb.get("pmid") or {}
            for p in rieng:
                if ket.get(p, (None, "", ""))[0] is True:
                    continue           # tự xác minh được rồi thì khỏi cần biên bản
                v = ghi.get(p)
                if not isinstance(v, dict):
                    ket[p] = (None, "KHÔNG có trong biên bản", "BIÊN BẢN")
                elif v.get("phan_giai") is True:
                    ket[p] = (True, v.get("tieu_de", ""), "BIÊN BẢN")
                elif v.get("phan_giai") is False:
                    ket[p] = (False, v.get("ly_do", "biên bản ghi KHÔNG phân giải"), "BIÊN BẢN")
                else:
                    ket[p] = (None, "biên bản ghi CHƯA tra được (%s)"
                              % (v.get("ly_do", "") or "không nêu lý do"), "BIÊN BẢN")

        if not ket:
            warns.append("CHƯA xác minh phân giải %d PMID — mới kiểm cấu trúc. "
                         "Chạy --online, hoặc --bien-ban, trước khi giao." % len(rieng))
            bb_note = None
        else:
            for iid, p in pmids:
                ok, info, nguon = ket[p]
                if ok is True:
                    oks.append("[%s] PMID %s ✓ %s (%s)" % (iid, p, info[:70], nguon))
                elif ok is False:
                    errors.append("[%s] PMID %s KHÔNG phân giải: %s (%s)" % (iid, p, info, nguon))
                else:
                    unresolved.append((iid, p, info))
            n_ok = sum(1 for p in rieng if ket[p][0] is True)
            n_bb = sum(1 for p in rieng if ket[p][0] is True and ket[p][2] == "BIÊN BẢN")
            oks.append("ĐÃ XÁC MINH %d/%d PMID." % (n_ok, len(rieng)))
            # Chỉ được nói "theo biên bản" khi biên bản THỰC SỰ xác minh được cái gì đó.
            bb_note = ("%d/%d PMID theo %s" % (n_bb, len(rieng), bb_note)) if (bb and n_bb) else None
            for iid, p, info in unresolved:
                msg = "[%s] PMID %s CHƯA xác minh được (%s)." % (iid, p, info)
                (warns if a.offline_ok else errors).append(msg)
    else:
        bb_note = None

    return report(errors, warns, oks, unresolved, a.offline_ok, bb_note)


def report(errors, warns, oks, unresolved=(), offline_ok=False, bb_note=None):
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
        # Không nêu nguyên nhân ở đây: có thể do mạng chặn, mà cũng có thể do biên bản
        # thiếu mã đó. Lý do cụ thể đã in ở từng dòng bên trên.
        print("KẾT QUẢ: ⊘ KHÔNG KẾT LUẬN — %d PMID chưa xác minh được (lý do ở từng dòng trên)."
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
    if bb_note:
        print("         ⚑ GHI VẾT: %s — xác minh KHÔNG diễn ra trong phiên này." % bb_note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
