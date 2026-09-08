#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dong_goi_skill_de_tai_len.py — Đóng gói skill trong repo thành .zip SẴN SÀNG TẢI LÊN tài khoản.

Vì sao cần: phiên làm việc của Claude KHÔNG ghi được vào bundle skill trên tài khoản.
Bản sửa nằm trong git phải do bác sĩ tự tải lên. Script này lo phần chuẩn bị để việc
đó chỉ còn là kéo–thả, và kiểm trước để không tải lên một bản đang lỗi.

    python3 tools/dong_goi_skill_de_tai_len.py cap-nhat-chung-cu-y-khoa
    python3 tools/dong_goi_skill_de_tai_len.py cap-nhat-chung-cu-y-khoa --bo-qua-kiem

KIỂM TRƯỚC KHI ĐÓNG GÓI (mặc định, có thể bỏ qua bằng --bo-qua-kiem):
  · có SKILL.md ở gốc thư mục skill;
  · frontmatter có `name` và `description`;
  · nếu skill có khoá mẫu → mẫu phải còn khớp SHA-256;
  · mọi script .py biên dịch được (không lỗi cú pháp).

Zip đặt ở `dist/` (đã bị .gitignore bỏ qua nhờ quy tắc *.zip) — KHÔNG commit bản đóng gói.
"""
import sys, os, re, json, zipfile, hashlib, argparse, py_compile, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP = os.path.join(REPO, "sao-luu-skill-cloud")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill", help="tên thư mục skill trong sao-luu-skill-cloud/")
    ap.add_argument("--bo-qua-kiem", action="store_true", help="đóng gói dù kiểm không đạt")
    a = ap.parse_args()

    src = os.path.join(BACKUP, a.skill)
    if not os.path.isdir(src):
        print("✗ Không thấy %s" % src)
        print("  Các skill có sẵn: %s" % ", ".join(sorted(os.listdir(BACKUP))[:8]) + " …")
        return 1

    loi = []
    smd = os.path.join(src, "SKILL.md")
    if not os.path.isfile(smd):
        loi.append("Thiếu SKILL.md ở gốc thư mục skill.")
    else:
        head = open(smd, encoding="utf-8").read()[:4000]
        for k in ("name:", "description:"):
            if k not in head:
                loi.append("Frontmatter thiếu `%s`." % k.rstrip(":"))

    lk = os.path.join(src, "data", "mau_cap_nhat.lock.json")
    if os.path.isfile(lk):
        lock = json.load(open(lk, encoding="utf-8"))
        tpl = os.path.join(src, lock["tep_mau"])
        if not os.path.isfile(tpl):
            loi.append("Lock trỏ tới %s nhưng không có tệp." % lock["tep_mau"])
        elif hashlib.sha256(open(tpl, "rb").read()).hexdigest() != lock["sha256_mau"]:
            loi.append("MẪU đã đổi mà chưa khoá lại — chạy tools/kiem_mau_cap_nhat.py trước.")

    for dp, _, fns in os.walk(src):
        for fn in fns:
            if fn.endswith(".py"):
                f = os.path.join(dp, fn)
                try:
                    py_compile.compile(f, cfile=os.path.join(tempfile.gettempdir(), "x.pyc"),
                                       doraise=True)
                except py_compile.PyCompileError as e:
                    loi.append("Lỗi cú pháp: %s (%s)" % (os.path.relpath(f, src), e.msg.splitlines()[0]))

    print("=" * 66)
    print("ĐÓNG GÓI SKILL ĐỂ TẢI LÊN — %s" % a.skill)
    print("=" * 66)
    for e in loi:
        print("  ✗ " + e)
    if loi and not a.bo_qua_kiem:
        print("-" * 66)
        print("DỪNG: sửa các lỗi trên rồi đóng gói lại (hoặc --bo-qua-kiem nếu cố ý).")
        return 1
    if not loi:
        print("  ✓ Kiểm trước khi đóng gói: đạt.")

    out_dir = os.path.join(REPO, "dist")
    os.makedirs(out_dir, exist_ok=True)
    zpath = os.path.join(out_dir, "%s.zip" % a.skill)
    n = 0
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dns, fns in os.walk(src):
            dns[:] = [d for d in dns if d != "__pycache__"]
            for fn in sorted(fns):
                if fn.endswith(".pyc"):
                    continue
                f = os.path.join(dp, fn)
                # SKILL.md phải nằm ở GỐC zip, trong thư mục mang tên skill
                z.write(f, os.path.join(a.skill, os.path.relpath(f, src)))
                n += 1

    sha_skill = hashlib.sha256(open(smd, "rb").read()).hexdigest()[:16] if os.path.isfile(smd) else "?"
    print("  ✓ Đã đóng gói %d tệp → %s (%.0f KB)" % (n, zpath, os.path.getsize(zpath) / 1024))
    print("  · SHA-256 của SKILL.md (16 ký tự đầu): %s" % sha_skill)
    print("-" * 66)
    print("VIỆC CÒN LẠI — bác sĩ tự làm, phiên Claude KHÔNG ghi được vào tài khoản:")
    print("  1. Tải %s lên phần quản lý Skills của tài khoản Claude" % os.path.basename(zpath))
    print("     (thay thế skill cùng tên đang có, đừng tạo bản trùng tên).")
    print("  2. Mở một phiên MỚI để bundle được đồng bộ lại.")
    print("  3. Chạy: python3 tools/kiem_dong_bo_skill_ebm.py")
    print("     → phải hết dòng 'LỆCH bundle↔sao-lưu' cho skill này.")
    print("  4. Đối chiếu nhanh: SHA-256 SKILL.md trên bundle phải bắt đầu bằng %s" % sha_skill)
    return 0


if __name__ == "__main__":
    sys.exit(main())
