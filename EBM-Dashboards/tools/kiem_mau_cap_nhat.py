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

  C. BẢN CẬP NHẬT có GHI VẾT TRA CỨU không?  (ngày tra · CSDL · chiến lược · kiểm bài rút ·
     ngày rà lại kế tiếp)
     Danh sách trường lấy TRỰC TIẾP từ bảng "GHI VẾT TRA CỨU" trong mẫu — mẫu là nguồn
     chân lý duy nhất, sửa mẫu là danh sách tự đổi theo (sau khi `--khoa-lai`).
     Thiếu trường, hoặc để nguyên chỗ trống của mẫu, là LỖI CỨNG: một bản cập nhật không
     nói mình tra ngày nào, ở đâu, thì không ai rà lại hay tái lập được.

Cách dùng:
    python3 tools/kiem_mau_cap_nhat.py                      # chỉ kiểm MẪU còn nguyên
    python3 tools/kiem_mau_cap_nhat.py CapNhat_EBM_*.md     # kiểm bản cập nhật theo mẫu
    python3 tools/kiem_mau_cap_nhat.py --khoa-lai --phien-ban 1.1
                                                            # đổi mẫu CÓ CHỦ Ý rồi khoá lại

Mã thoát: 0 = đạt · 1 = lệch mẫu hoặc thiếu mục (phải sửa trước khi giao).

PHÂN BIỆT LỖI CỨNG / CẢNH BÁO
  Lỗi cứng : sai số mục · sai thứ tự · thiếu mục · mẫu đổi mà chưa khoá lại ·
             thiếu trường ghi vết tra cứu · trường ghi vết còn nguyên chỗ trống của mẫu ·
             trường "Ngày ..." không có ngày thật.
  Cảnh báo : chữ tiêu đề mục khác chút so với mẫu (vd thêm "(Vancouver/NLM)") —
             chấp nhận được, nhưng in ra để người viết biết mình đã đổi chữ;
             trường ghi vết còn dấu [CẦN ...] — chấp nhận được nhưng phải thấy rõ.
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


TIEU_DE_GHI_VET = "GHI VẾT TRA CỨU"
CHO_TRONG = re.compile(r"\[[^\]]*(?:\.\.\.|…|YYYY-MM-DD|n/n|liệt kê|từ khoá)[^\]]*\]", re.I)
CO_NGAY = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}")
CAN_LAM = re.compile(r"\[CẦN [^\]]*\]", re.I)


def doc_bang_ghi_vet(path):
    """Đọc bảng GHI VẾT TRA CỨU → [(nhãn, giá trị), ...] theo đúng thứ tự trong tệp.

    Bảng nhận diện bằng dòng tiêu đề `**GHI VẾT TRA CỨU**`; lấy các dòng `| a | b |`
    ngay sau đó cho tới khi hết bảng. Không phụ thuộc vị trí tuyệt đối trong tệp.
    """
    txt = open(path, encoding="utf-8").read()
    i = txt.find(TIEU_DE_GHI_VET)
    if i < 0:
        return []
    ra, trong_bang = [], False
    for dong in txt[i:].splitlines()[1:]:
        d = dong.strip()
        if not d.startswith("|"):
            if trong_bang:
                break
            continue
        o = [c.strip() for c in d.strip("|").split("|")]
        if len(o) < 2:
            continue
        if set("".join(o)) <= set("-: "):          # dòng gạch ngăn
            trong_bang = True
            continue
        if not trong_bang:                          # dòng tiêu đề cột
            continue
        ra.append((o[0], o[1]))
    return ra


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
            gv = doc_bang_ghi_vet(tpl)
            lock.update({"phien_ban": a.phien_ban, "sha256_mau": sha_now,
                         "muc": doc_muc(tpl), "so_muc": len(doc_muc(tpl)),
                         "truong_ghi_vet": [n for n, _ in gv],
                         "cho_trong_ghi_vet": {n: v for n, v in gv}})
            from datetime import date
            lock["ngay_khoa"] = date.today().isoformat()
            json.dump(lock, open(LOCK, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("✓ Đã khoá lại mẫu: phiên bản %s · %d mục · %d trường ghi vết · sha256 %s"
                  % (a.phien_ban, lock["so_muc"], len(lock["truong_ghi_vet"]), sha_now[:16]))
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

        # ---------- C. GHI VẾT TRA CỨU ----------
        can = lock.get("truong_ghi_vet") or []
        if not can:
            canh_bao.append("Bản khoá %s chưa có danh sách trường ghi vết tra cứu — "
                            "chạy --khoa-lai để nạp từ mẫu." % lock["phien_ban"])
        else:
            co = dict(doc_bang_ghi_vet(a.file))
            mau_trong = lock.get("cho_trong_ghi_vet") or {}
            for nhan in can:
                if nhan not in co:
                    loi.append("GHI VẾT: thiếu dòng «%s» — bản cập nhật không nói "
                               "mình tra ngày nào / ở đâu / bằng gì." % nhan)
                    continue
                gt = co[nhan].strip()
                if not gt or gt in ("—", "-", "…"):
                    loi.append("GHI VẾT: «%s» để trống." % nhan)
                elif gt == mau_trong.get(nhan, "").strip():
                    loi.append("GHI VẾT: «%s» còn NGUYÊN chỗ trống của mẫu — chưa điền." % nhan)
                elif CHO_TRONG.search(gt):
                    loi.append("GHI VẾT: «%s» còn chỗ trống chưa điền: %s"
                               % (nhan, CHO_TRONG.search(gt).group(0)))
                elif nhan.lower().startswith("ngày") and not CO_NGAY.search(gt):
                    loi.append("GHI VẾT: «%s» không có ngày thật (cần YYYY-MM-DD hoặc "
                               "dd/mm/yyyy), đang là: %s" % (nhan, gt[:60]))
                else:
                    if CAN_LAM.search(gt):
                        canh_bao.append("GHI VẾT: «%s» còn dấu %s — chấp nhận được, "
                                        "nhưng phải nêu rõ khi giao."
                                        % (nhan, CAN_LAM.search(gt).group(0)))
                    dat.append("ghi vết «%s» đã điền" % nhan)

    # ---------- Báo cáo ----------
    print("=" * 68)
    print("KIỂM MẪU CẬP NHẬT CHỨNG CỨ")
    print("=" * 68)
    if dat:
        print("  ✓ %s" % dat[0])
        khop = len([d for d in dat if "khớp mẫu" in d])
        if khop:
            print("  ✓ %d/%d mục khớp nguyên văn mẫu." % (khop, lock["so_muc"]))
        gv = len([d for d in dat if d.startswith("ghi vết")])
        if gv:
            print("  ✓ %d/%d trường ghi vết tra cứu đã điền."
                  % (gv, len(lock.get("truong_ghi_vet") or [])))
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
