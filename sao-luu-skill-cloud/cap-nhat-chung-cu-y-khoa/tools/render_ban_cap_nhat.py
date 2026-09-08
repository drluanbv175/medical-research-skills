#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_ban_cap_nhat.py — Dựng bản cập nhật (.md, mẫu chuyên sâu 11 mục) thành TRANG ĐỌC ĐƯỢC.

Vì sao cần: file .md và .html trong repo không mở được trực tiếp trong khung chát của
bác sĩ. Trang này để đọc trên trình duyệt, in ra A4, hoặc đăng thành Artifact.

Cách dùng:
    python3 tools/render_ban_cap_nhat.py CapNhat_EBM_<ChuDe>_YYYYMMDD.md
    python3 tools/render_ban_cap_nhat.py <file>.md -o trang.html

Cần: pip install markdown

THIẾT KẾ theo quy ước của bác sĩ:
  - Tiêu đề Poppins (kèm Be Vietnam Pro làm dự phòng vì POPPINS KHÔNG CÓ BỘ KÝ TỰ
    TIẾNG VIỆT — thiếu nó thì chữ có dấu rơi về Arial/Times New Roman).
  - Nội dung Lora; dự phòng Georgia → Noto Serif → DejaVu Serif, CHẶN trước Times New Roman
    (Georgia không có sẵn trên nhiều máy Linux/Android).
  - Cam #d97757 cảnh báo/điểm mới · Xanh dương #6a9bcc chẩn đoán/quy trình ·
    Xanh lá #788c5d điều trị/theo dõi. Màu gắn theo VAI TRÒ của mục, không trang trí.
  - Bảng xuống dòng để VỪA TRANG thay vì cuộn ngang; các nhãn [CẦN …] được tô nổi.
"""
import sys, os, re, argparse, html as H

FONTS = ("https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;600;700"
         "&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Poppins:wght@500;600;700&display=swap")
# vai trò màu theo thứ tự 11 mục của mẫu chuyên sâu
ROLE = {1: "sum", 2: "new", 3: "dx", 4: "warn", 5: "rx", 6: "rx",
        7: "rx", 8: "warn", 9: "dx", 10: "dx", 11: "ref"}
FLAGS = "CẦN BỔ SUNG|CẦN KIỂM CHỨNG|CẦN XÁC NHẬN TẠI ĐƠN VỊ|DỰ THẢO"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="bản cập nhật .md")
    ap.add_argument("-o", "--out", help="file .html xuất ra (mặc định: cùng tên, đuôi .html)")
    a = ap.parse_args()
    try:
        import markdown
    except ImportError:
        print("Thiếu thư viện: pip install markdown"); return 1

    here = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(here, "..", "templates", "trang-doc-ban-cap-nhat.css")
    if not os.path.isfile(css_path):
        print("Không thấy %s" % css_path); return 1
    css = open(css_path, encoding="utf-8").read()

    md = open(a.file, encoding="utf-8").read()
    body = markdown.markdown(md, extensions=["tables", "sane_lists"])

    toc, state = [], {"n": 0}

    def h2(m):
        state["n"] += 1
        n = state["n"]
        label = re.sub(r"^\d+\.\s*", "", m.group(1))
        r = ROLE.get(n, "sum")
        toc.append((n, label, r))
        return ('<h2 id="m%d" class="s-%s"><span class="num">%02d</span>%s</h2>'
                % (n, r, n, H.escape(label)))

    body = re.sub(r"<h2>(.*?)</h2>", h2, body)
    body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    body = re.sub(r"\[(%s)\]" % FLAGS, r'<span class="flag">[\1]</span>', body)
    body = re.sub(r"(PMID:?\s?\d{7,8})", r'<span class="pmid">\1</span>', body)

    title = (re.search(r"^#\s+(.+)$", md, re.M) or [None, "Bản cập nhật chứng cứ"])[1]
    title = re.sub(r"^Cập nhật thực hành:\s*", "", title).strip()
    nav = "\n".join('<a href="#m%d" class="t-%s"><i>%02d</i>%s</a>' % (i, r, i, H.escape(l))
                    for i, l, r in toc)

    out = a.out or os.path.splitext(a.file)[0] + ".html"
    open(out, "w", encoding="utf-8").write(
        '<title>%s</title>\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="%s">\n'
        '<style>\n@import url("%s");\n%s</style>\n\n'
        '<div class="wrap">\n<nav aria-label="Mục lục">'
        '<div class="lbl">%d mục · mẫu chuyên sâu</div>\n%s\n</nav>\n<main>\n%s\n</main>\n</div>\n'
        % (H.escape(title), FONTS, FONTS, css, len(toc), nav, body))

    print("  + %s  (%d mục)" % (out, len(toc)))
    if len(toc) != 11:
        print("  ⚠ Đếm được %d mục H2, mẫu chuyên sâu có 11 — kiểm lại bản cập nhật." % len(toc))
    print("Trang KHÔNG nhúng font: cần mạng để tải Google Fonts; thiếu mạng vẫn đọc được "
          "bằng font dự phòng đã chọn sẵn (không rơi về Times New Roman).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
