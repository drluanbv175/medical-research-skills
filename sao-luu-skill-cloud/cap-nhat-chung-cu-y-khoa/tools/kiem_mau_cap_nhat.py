#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kiem_mau_cap_nhat.py — Giữ MẪU CẬP NHẬT CHỨNG CỨ không đổi, và bắt bản cập nhật đi lệch mẫu.

Hai việc, hai chiều khác nhau:

  A. MẪU có bị đổi lén không?    (khoá bằng SHA-256 trong data/mau_cap_nhat.lock.json)
     Mẫu chỉ được đổi CÓ CHỦ Ý, bằng `--khoa-lai`, kèm tăng số phiên bản.

  B. BẢN CẬP NHẬT có theo đúng mẫu không?  (đủ mục · đúng thứ tự · đúng nội dung mục)
     Đây là lỗi đã xảy ra thật: lần đầu chỉ giao Web Dashboard, KHÔNG có bản cập nhật
     văn bản nào; lần sau có văn bản nhưng phải đối chiếu tay mới biết đủ 11 mục.

Cách dùng:
    python3 tools/kiem_mau_cap_nhat.py                      # chỉ kiểm MẪU còn nguyên
    python3 tools/kiem_mau_cap_nhat.py CapNhat_EBM_*.md     # kiểm bản cập nhật theo mẫu
    python3 tools/kiem_mau_cap_nhat.py --khoa-lai --phien-ban 1.1
                                                            # đổi mẫu CÓ CHỦ Ý rồi khoá lại

Mã thoát: 0 = đạt · 1 = lệch mẫu hoặc thiếu mục (phải sửa trước khi giao).

PHÂN BIỆT LỖI CỨNG / CẢNH BÁO
  Lỗi cứng : sai số mục · sai thứ tự · thiếu mục · mẫu đổi mà chưa khoá lại.
  Cảnh báo : chữ tiêu đề mục khác chút so với mẫu (vd thêm "(Vancouver/NLM)") —
             chấp nhận được, nhưng in ra để người viết biết mình đã đổi chữ.
"""
import sys, os, re, json, difflib, hashlib, argparse, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(HERE, "..", "data", "mau_cap_nhat.lock.json")
GIONG_NHAU = 0.72   # ngưỡng coi là "cùng một mục, chỉ khác chữ"


def chuan_hoa(s):
    """Bỏ số thứ tự, dấu câu, dấu tiếng Việt → so sánh theo nghĩa, không theo hình thức."""
    s = re.sub(r"^\s*\d+\.\s*", "", s.strip()).lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s]", " ", s).split()


def giong(a, b):
    return difflib.SequenceMatcher(None, " ".join(chuan_hoa(a)), " ".join(chuan_hoa(b))).ratio()


def doc_muc(path):
    return [h.strip() for h in re.findall(r"^##\s+(.+)$", open(path, encoding="utf-8").read(), re.M)]


def sha_tep(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="bản cập nhật .md cần kiểm")
    ap.add_argument("--khoa-lai", action="store_true", help="khoá lại sau khi ĐỔI MẪU có chủ ý")
    ap.add_argument("--phien-ban", help="số phiên bản mới, bắt buộc khi --khoa-lai")
    a = ap.parse_args()

    if not os.path.isfile(LOCK):
        print("✗ Không thấy %s — mẫu chưa được khoá." % LOCK); return 1
    lock = json.load(open(LOCK, encoding="utf-8"))
    tpl = os.path.join(HERE, "..", lock["tep_mau"])
    loi, canh_bao, dat = [], [], []

    # ---------- A. MẪU còn nguyên không ----------
    if not os.path.isfile(tpl):
        loi.append("Không thấy tệp mẫu %s." % lock["tep_mau"])
    else:
        sha_now = sha_tep(tpl)
        if a.khoa_lai:
            if not a.phien_ban:
                print("✗ --khoa-lai phải kèm --phien-ban (vd 1.1). Đổi mẫu là việc CÓ CHỦ Ý.")
                return 1
            lock.update({"phien_ban": a.phien_ban, "sha256_mau": sha_now,
                         "muc": doc_muc(tpl), "so_muc": len(doc_muc(tpl))})
            from datetime import date
            lock["ngay_khoa"] = date.today().isoformat()
            json.dump(lock, open(LOCK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("✓ Đã khoá lại mẫu: phiên bản %s · %d mục · sha256 %s"
                  % (a.phien_ban, lock["so_muc"], sha_now[:16]))
            print("  Nhớ ghi lý do đổi mẫu vào CHANGELOG.md của skill.")
            return 0
        if sha_now != lock["sha256_mau"]:
            loi.append("MẪU ĐÃ BỊ ĐỔI mà chưa khoá lại (sha256 %s ≠ %s đã khoá).\n"
                       "      Nếu đổi có chủ ý: chạy --khoa-lai --phien-ban <mới> và ghi CHANGELOG.\n"
                       "      Nếu KHÔNG chủ ý: khôi phục mẫu trước khi làm bản cập nhật nào."
                       % (sha_now[:16], lock["sha256_mau"][:16]))
        else:
            dat.append("Mẫu nguyên vẹn — phiên bản %s, khoá ngày %s, %d mục."
                       % (lock["phien_ban"], lock["ngay_khoa"], lock["so_muc"]))

    # ---------- B. BẢN CẬP NHẬT có theo mẫu không ----------
    if a.file:
        if not os.path.isfile(a.file):
            print("✗ Không thấy %s" % a.file); return 1
        thuc = doc_muc(a.file)
        chuan = lock["muc"]
        if len(thuc) != len(chuan):
            loi.append("Bản cập nhật có %d mục, mẫu quy định %d mục." % (len(thuc), len(chuan)))
        for i, mc in enumerate(chuan):
            if i >= len(thuc):
                loi.append("THIẾU mục %d: «%s»" % (i + 1, mc)); continue
            r = giong(mc, thuc[i])
            if r >= 0.985:
                dat.append("mục %2d khớp mẫu" % (i + 1))
            elif r >= GIONG_NHAU:
                canh_bao.append("mục %d đổi chữ: mẫu «%s» → bản «%s»" % (i + 1, mc, thuc[i]))
            else:
                # đúng mục nhưng sai vị trí, hay lạc hẳn?
                o = [j + 1 for j, t in enumerate(thuc) if giong(mc, t) >= GIONG_NHAU]
                loi.append("mục %d SAI: cần «%s», đang là «%s»%s"
                           % (i + 1, mc, thuc[i],
                              (" — nội dung đó đang nằm ở mục %s (SAI THỨ TỰ)" % o) if o else ""))
        for j in range(len(chuan), len(thuc)):
            canh_bao.append("mục thừa %d: «%s» — mẫu không có" % (j + 1, thuc[j]))

    # ---------- Báo cáo ----------
    print("=" * 68)
    print("KIỂM MẪU CẬP NHẬT CHỨNG CỨ")
    print("=" * 68)
    if dat:
        print("  ✓ %s" % dat[0])
        khop = len([d for d in dat if "khớp mẫu" in d])
        if khop:
            print("  ✓ %d/%d mục khớp nguyên văn mẫu." % (khop, lock["so_muc"]))
    for c in canh_bao:
        print("  ⚠ " + c)
    for e in loi:
        print("  ✗ " + e)
    print("-" * 68)
    if loi:
        print("KẾT QUẢ: ✗ LỆCH MẪU — %d lỗi. KHÔNG giao bản cập nhật này." % len(loi))
        return 1
    print("KẾT QUẢ: ✓ ĐÚNG MẪU%s." % (" (%d chỗ đổi chữ, chấp nhận được)" % len(canh_bao) if canh_bao else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
