#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_derivatives.py — TỰ ĐỘNG sinh 3 sản phẩm phái sinh từ một dashboard đã PASS cổng liêm chính.

Đầu ra (vào derivatives/):
  <slug>_to-dan-nguoi-benh.md   — BẢN NHÁP tờ dặn người bệnh (model/bác sĩ rà ngôn ngữ phổ thông, BỎ liều)
  <slug>_slide-outline.md       — dàn ý slide (FAITHFUL: giữ hiệu số + GRADE + PMID) → nạp skill slide ra .pptx
  <slug>_kich-ban-tiktok.md     — BẢN NHÁP kịch bản TikTok (rà ngôn ngữ; video thật: skill tao-video-tiktok)

Cách dùng (trong EBM-Dashboards/):
    python3 tools/make_derivatives.py WebDashboard_EBM_<...>.html

LƯU Ý LIÊM CHÍNH: tờ dặn & TikTok là BẢN NHÁP — rà lại để bỏ liều/thuật ngữ trước khi phát/đăng.
"""
import sys, os, re, argparse

DEC = {"apply": "Áp dụng ngay", "consider": "Cân nhắc", "notyet": "Chưa đủ"}

# Chuỗi JS: chỉ dấu GIỐNG dấu mở mới kết thúc chuỗi. Regex cũ dùng ['\"] ở cả hai đầu nên
# một dấu " bên trong chuỗi 'nháy đơn' làm cắt nhầm — đã gây gạch đầu dòng cụt trong tờ dặn.
STR_RE = re.compile(r"'((?:\\.|[^'\\])*)'|\"((?:\\.|[^\"\\])*)\"", re.S)


def _first_string(text):
    """Lấy giá trị chuỗi JS đầu tiên trong `text` (đã tôn trọng dấu mở)."""
    m = STR_RE.search(text)
    if not m:
        return ""
    return m.group(1) if m.group(1) is not None else m.group(2)


def _all_strings(text):
    out = []
    for m in STR_RE.finditer(text):
        out.append(m.group(1) if m.group(1) is not None else m.group(2))
    return out


def _slice_bracket(text, start):
    """Cắt đúng nội dung trong [...] bắt đầu tại `start`, bỏ qua ngoặc nằm trong chuỗi."""
    i, depth, n = start, 0, len(text)
    while i < n:
        c = text[i]
        if c in "'\"":
            m = STR_RE.match(text, i)
            i = m.end() if m else i + 1
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
        i += 1
    return ""


def block(html):
    i = html.find("const DATA")
    return html[i:html.find("HẾT KHỐI DATA", i)] if i != -1 else html


def meta(b, name):
    m = re.search(name + r"\s*:\s*(?=['\"])", b)
    return _first_string(b[m.end():]) if m else ""


def arr(b, name):
    m = re.search(name + r"\s*:\s*\[", b, re.S)
    if not m:
        return []
    return _all_strings(_slice_bracket(b, m.end() - 1))


def items(b):
    ipos = b.find("items:")
    seg = b[ipos:] if ipos != -1 else b
    starts = [m.start() for m in re.finditer(r"\{\s*id\s*:\s*['\"]", seg)]
    out = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(seg)
        ch = seg[s:e]
        def f(n, _ch=ch):
            m = re.search(n + r"\s*:\s*(?=['\"])", _ch)
            return _first_string(_ch[m.end():]) if m else ""
        out.append({
            "title": f("title"), "source": f("source"), "pmid": f("pmid"),
            "effectText": f("effectText"), "gradeSource": f("gradeSource"),
            "rob": f("rob"), "decision": f("decision"),
        })
    return out


def slug_of(path):
    s = os.path.basename(path)
    s = re.sub(r"^WebDashboard_EBM_(VanDeCuThe_)?", "", s)
    s = re.sub(r"\.html$", "", s)
    return s or "capnhat"


def li(xs):
    return "\n".join("- " + x for x in xs) if xs else "- —"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--outdir", default="derivatives")
    ap.add_argument("--ghi-de", dest="ghi_de", action="store_true",
                    help="cho phép ghi đè bản ĐÃ RÀ TAY (mất công rà lại từ đầu)")
    a = ap.parse_args()

    html = open(a.file, encoding="utf-8").read()
    b = block(html)
    q = meta(b, "question") or "Vấn đề lâm sàng"
    upd = meta(b, "updated") or ""
    conclusion = meta(b, "conclusion")
    doNow, dontDo, redFlags = arr(b, "doNow"), arr(b, "dontDo"), arr(b, "redFlags")
    its = items(b)
    os.makedirs(a.outdir, exist_ok=True)
    slug = slug_of(a.file)

    # 1) Tờ dặn người bệnh (BẢN NHÁP)
    patient = """# TỜ DẶN NGƯỜI BỆNH — {q}
*Ngày: {upd}*

> **BẢN NHÁP TỰ ĐỘNG** — rà lại NGÔN NGỮ PHỔ THÔNG, **BỎ liều & thuật ngữ kỹ thuật**, trước khi in/phát.

**Tóm tắt**
{conclusion}

**Bạn nên làm**
{do}

**Đi khám ngay nếu**
{rf}

**Lưu ý**
{dont}

---
*Thông tin tham khảo — **không thay thế tư vấn của bác sĩ của bạn**.*
""".format(q=q, upd=upd, conclusion=conclusion or "—", do=li(doNow), rf=li(redFlags), dont=li(dontDo))

    # 2) Dàn ý slide (FAITHFUL — giữ kỹ thuật + PMID)
    rows = []
    for i, it in enumerate(its, 1):
        eff = (" — " + it["effectText"]) if it["effectText"] else ""
        # Phân hạng in NGUYÊN VĂN của nguồn. TUYỆT ĐỐI không tự dựng nhãn "GRADE <mức>"
        # từ gradeLevel — gradeLevel chỉ để tô màu/lọc trên dashboard, không phải GRADE.
        gr = it["gradeSource"] or "Nguồn không cung cấp phân hạng"
        dc = DEC.get(it["decision"], it["decision"] or "")
        rb = (" · RoB: " + it["rob"]) if it["rob"] else ""
        pm = (" · PMID " + it["pmid"]) if it["pmid"] else ""
        rows.append("{i}. **{t}**{eff} — *{gr}* · *{dc}*{rb}{pm} ({src})".format(
            i=i + 2, t=it["title"], eff=eff, gr=gr, dc=dc, rb=rb, pm=pm, src=it["source"]))
    slide = """# DÀN Ý SLIDE — {q}
*Nạp vào skill dao-tao-slide-tai-lieu-y-khoa để xuất .pptx. Giữ số liệu + PMID.*\n*Phân hạng dưới đây in NGUYÊN VĂN của nguồn (trường `gradeSource`) — không quy đổi, không tự gán GRADE.*

1. **Tiêu đề:** Cập nhật chứng cứ — {q} ({upd})
2. **Tóm tắt thực hành:** {conclusion}
{rows}
{nslide}. **Cờ đỏ / chuyển tuyến:** {rf}
{nslide2}. **Tài liệu tham khảo (Vancouver) + disclaimer "Cần bác sĩ kiểm chứng"**

*Mọi số liệu trích đúng nguồn từ bản cập nhật đã PASS cổng liêm chính.*
""".format(q=q, upd=upd, conclusion=conclusion or "—", rows="\n".join(rows),
           nslide=len(its) + 3, nslide2=len(its) + 4, rf="; ".join(redFlags) or "—")

    # 3) Kịch bản TikTok (BẢN NHÁP)
    pts = doNow[:3]
    tiktok = """# KỊCH BẢN TIKTOK — {q} (~45s)
*Giọng: HoaiMy · Phụ đề động: bật · Overlay: "Thông tin tham khảo — không thay tư vấn bác sĩ"*

> **BẢN NHÁP TỰ ĐỘNG** — rà ngôn ngữ đời thường, **bỏ liều**. Video thật: skill `tao-video-tiktok`.

**[Hook]** {hook}

**[Nội dung]**
{pts}

**[Cảnh báo + chốt]** Đi khám ngay nếu: {rf} 👉 Hỏi bác sĩ của bạn.

---
*Bác sĩ duyệt trước khi đăng. Không dùng PII/ảnh bệnh nhân thật.*
""".format(q=q, hook=(conclusion[:90] + "…") if conclusion else q,
           pts="\n".join("• " + x for x in pts) or "• —", rf="; ".join(redFlags[:2]) or "—")

    written, giu = [], []
    for suffix, content in [("to-dan-nguoi-benh", patient), ("slide-outline", slide), ("kich-ban-tiktok", tiktok)]:
        path = os.path.join(a.outdir, "%s_%s.md" % (slug, suffix))
        # KHÔNG ghi đè bản đã rà tay. Bản tự sinh luôn mang dấu "BẢN NHÁP TỰ ĐỘNG";
        # tệp đã có mà KHÔNG còn dấu đó nghĩa là người đã sửa — ghi đè là xoá công rà ngôn ngữ.
        if os.path.isfile(path) and not a.ghi_de:
            cu = open(path, encoding="utf-8").read()
            if "BẢN NHÁP TỰ ĐỘNG" not in cu:
                giu.append(path)
                print("  ⊘ GIỮ NGUYÊN (đã rà tay, không ghi đè): " + path)
                continue
        open(path, "w", encoding="utf-8").write(content)
        written.append(path)
        print("  + " + path)
    print("Đã sinh %d sản phẩm phái sinh%s. Slide=faithful; tờ dặn & TikTok = BẢN NHÁP cần rà ngôn ngữ phổ thông."
          % (len(written), (", GIỮ NGUYÊN %d bản đã rà tay" % len(giu)) if giu else ""))
    if giu:
        print("     Muốn dựng lại từ đầu (mất phần đã rà): thêm --ghi-de.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
