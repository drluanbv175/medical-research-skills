#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kiem_dong_bo_skill_ebm.py — Kiểm ĐỒNG BỘ hệ thống skill EBM.

Cùng một file (template dashboard, script công cụ) đang tồn tại ở nhiều nơi:
  - bundle chạy thật:  ~/.claude/skills/synced/<bundle>/<skill>/...
  - bản sao lưu git:   sao-luu-skill-cloud/<skill>/...
  - bản chạy tại chỗ:  EBM-Dashboards/tools/...
Sửa một nơi mà quên nơi khác = trôi lệch âm thầm. Công cụ này bắt đúng việc đó.

BỐN PHÉP KIỂM
  1. TRÔI LỆCH BẢN SAO — file cùng đường dẫn tương đối nhưng khác byte giữa các nơi.
  2. TÀI LIỆU ≠ CODE   — SKILL.md hứa field nào thì template phải cài đặt field đó.
  3. MÔ TẢ TRÙNG NHAU  — hai skill cùng mô tả kích hoạt ⇒ hệ thống có thể chọn nhầm.
  4. THIẾU CỔNG        — skill bảo chạy verify_dashboard.py thì phải có file đó.
  5. KHOÁ MẪU          — mẫu cập nhật phải khớp SHA-256 đã khoá trong lock file.

Cách dùng:
    python3 tools/kiem_dong_bo_skill_ebm.py            # kiểm, in báo cáo
    python3 tools/kiem_dong_bo_skill_ebm.py --sua      # đồng bộ bản sao theo NGUỒN CHUẨN

NGUỒN CHUẨN khi --sua: bản trong `sao-luu-skill-cloud/` (bản đã qua review và nằm trong
git). KHÔNG bao giờ tự ghi ngược lên bundle tài khoản — việc đó phải do bác sĩ tự tải lên.

Mã thoát: 0 = đồng bộ · 1 = phát hiện lệch.
"""
import sys, os, re, glob, hashlib, argparse, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP = os.path.join(REPO, "sao-luu-skill-cloud")
WORKDIR = os.path.join(REPO, "EBM-Dashboards")
BUNDLE_GLOB = os.path.expanduser("~/.claude/skills/synced/*/")

# Field mà SKILL.md tuyên bố là template hỗ trợ → phải tìm thấy trong template đó.
DOC_CLAIMS = [
    ("effectText", ["web-dashboard-evidence-workbench.html", "web-dashboard-dark-analyst.html"]),
    ("rob",        ["web-dashboard-evidence-workbench.html", "web-dashboard-dark-analyst.html"]),
]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def skills_in(root):
    if not os.path.isdir(root):
        return {}
    return {n: os.path.join(root, n) for n in sorted(os.listdir(root))
            if os.path.isdir(os.path.join(root, n))}


def rel_files(root):
    out = {}
    for dp, _, fns in os.walk(root):
        for fn in fns:
            f = os.path.join(dp, fn)
            out[os.path.relpath(f, root)] = f
    return out


def bundle_root():
    for d in glob.glob(BUNDLE_GLOB):
        if os.path.isdir(d):
            return d
    return None


def desc_of(skill_md):
    """Lấy description trong frontmatter YAML (một dòng hoặc nhiều dòng thụt lề)."""
    try:
        txt = open(skill_md, encoding="utf-8").read()
    except OSError:
        return ""
    m = re.search(r"^---\s*$(.*?)^---\s*$", txt, re.S | re.M)
    fm = m.group(1) if m else txt[:4000]
    m = re.search(r"^description:\s*(.*(?:\n[ \t]+.*)*)", fm, re.M)
    return re.sub(r"\s+", " ", m.group(1)).strip().strip('"\'') if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sua", action="store_true",
                    help="đồng bộ bản chạy tại chỗ theo bản trong sao-luu-skill-cloud")
    a = ap.parse_args()
    problems, notes, fixed = [], [], []

    backup = skills_in(BACKUP)
    broot = bundle_root()
    bundle = skills_in(broot) if broot else {}

    # ---------- 1. TRÔI LỆCH BẢN SAO ----------
    print("=" * 72)
    print("KIỂM ĐỒNG BỘ HỆ THỐNG SKILL EBM")
    print("=" * 72)
    print("\n[1] TRÔI LỆCH GIỮA CÁC BẢN SAO")

    for name, bpath in sorted(backup.items()):
        if name not in bundle:
            notes.append("skill `%s` có bản sao lưu nhưng KHÔNG có trong bundle đang chạy." % name)
            continue
        bk, bd = rel_files(bpath), rel_files(bundle[name])
        for rel in sorted(set(bk) & set(bd)):
            if sha(bk[rel]) != sha(bd[rel]):
                problems.append("LỆCH bundle↔sao-lưu : %s/%s" % (name, rel))
        for rel in sorted(set(bd) - set(bk)):
            problems.append("THIẾU trong sao lưu   : %s/%s" % (name, rel))

    # bản chạy tại chỗ EBM-Dashboards/tools
    src_tools = os.path.join(BACKUP, "cap-nhat-chung-cu-y-khoa", "tools")
    dst_tools = os.path.join(WORKDIR, "tools")
    if os.path.isdir(src_tools) and os.path.isdir(dst_tools):
        for fn in sorted(os.listdir(src_tools)):
            s_, d_ = os.path.join(src_tools, fn), os.path.join(dst_tools, fn)
            if not os.path.exists(d_):
                problems.append("THIẾU bản chạy tại chỗ: EBM-Dashboards/tools/%s" % fn)
            elif sha(s_) != sha(d_):
                if a.sua:
                    shutil.copy2(s_, d_); fixed.append("EBM-Dashboards/tools/%s" % fn)
                else:
                    problems.append("LỆCH sao-lưu↔EBM-Dashboards: tools/%s" % fn)

    # ---------- 2. TÀI LIỆU ≠ CODE ----------
    print("[2] TÀI LIỆU CÓ KHỚP CODE KHÔNG")
    for name, bpath in sorted(backup.items()):
        smd = os.path.join(bpath, "SKILL.md")
        if not os.path.isfile(smd):
            continue
        txt = open(smd, encoding="utf-8").read()
        for field, tpls in DOC_CLAIMS:
            if field not in txt:
                continue
            for t in tpls:
                tp = os.path.join(bpath, "templates", t)
                if os.path.isfile(tp) and field not in open(tp, encoding="utf-8").read():
                    problems.append("SKILL.md của `%s` hứa field `%s` nhưng %s KHÔNG cài đặt."
                                    % (name, field, t))

    # ---------- 3. MÔ TẢ TRÙNG NHAU ----------
    print("[3] MÔ TẢ KÍCH HOẠT CÓ TRÙNG NHAU KHÔNG")
    seen = {}
    for name, bpath in sorted({**bundle, **backup}.items()):
        d = desc_of(os.path.join(bpath, "SKILL.md"))
        if len(d) < 40:
            continue
        seen.setdefault(d[:200], []).append(name)
    for d, names in seen.items():
        if len(set(names)) > 1:
            problems.append("MÔ TẢ TRÙNG: %s → hệ thống có thể kích hoạt nhầm skill."
                            % " / ".join(sorted(set(names))))

    # ---------- 4. THIẾU CỔNG LIÊM CHÍNH ----------
    print("[4] SKILL BẢO CHẠY CỔNG THÌ CÓ CỔNG KHÔNG")
    for name, bpath in sorted({**bundle, **backup}.items()):
        smd = os.path.join(bpath, "SKILL.md")
        if not os.path.isfile(smd):
            continue
        if "verify_dashboard.py" in open(smd, encoding="utf-8").read():
            if not os.path.isfile(os.path.join(bpath, "tools", "verify_dashboard.py")):
                problems.append("`%s` yêu cầu chạy verify_dashboard.py nhưng KHÔNG ship file đó "
                                "⇒ mọi đầu ra của skill này chưa qua cổng liêm chính." % name)

    # ---------- 5. KHOÁ MẪU CẬP NHẬT ----------
    print("[5] MẪU CẬP NHẬT CÒN KHỚP KHOÁ KHÔNG")
    import json as _json
    for name, bpath in sorted({**bundle, **backup}.items()):
        lk = os.path.join(bpath, "data", "mau_cap_nhat.lock.json")
        if not os.path.isfile(lk):
            continue
        try:
            lock = _json.load(open(lk, encoding="utf-8"))
            tpl = os.path.join(bpath, lock["tep_mau"])
            if not os.path.isfile(tpl):
                problems.append("`%s`: lock trỏ tới %s nhưng không có tệp đó." % (name, lock["tep_mau"]))
            elif sha(tpl) != lock["sha256_mau"]:
                problems.append("`%s`: MẪU CẬP NHẬT đã đổi mà chưa khoá lại "
                                "⇒ bản cập nhật sau sẽ theo mẫu khác bản trước." % name)
            else:
                notes.append("`%s`: mẫu cập nhật khoá ở phiên bản %s (%d mục) — còn nguyên."
                             % (name, lock.get("phien_ban", "?"), lock.get("so_muc", 0)))
        except Exception as e:
            problems.append("`%s`: không đọc được lock mẫu (%s)." % (name, e))

    # ---------- BÁO CÁO ----------
    print("-" * 72)
    for f in fixed:
        print("  ✎ ĐÃ ĐỒNG BỘ : " + f)
    for n in notes:
        print("  · " + n)
    for p in sorted(set(problems)):
        print("  ✗ " + p)
    print("-" * 72)
    if problems:
        print("KẾT QUẢ: ✗ LỆCH — %d vấn đề. Sửa trước khi tin vào bất kỳ đầu ra nào." % len(set(problems)))
        if any(x.startswith("LỆCH bundle↔sao-lưu") for x in problems):
            print()
            print("  Dòng \"LỆCH bundle↔sao-lưu\" có HAI nguyên nhân — phải phân biệt:")
            print("   (a) Vừa sửa bản trong git, CHƯA tải lên tài khoản")
            print("       → tải thư mục skill đã sửa lên tài khoản Claude, rồi chạy lại lệnh này.")
            print("   (b) Đã sửa trên tài khoản, CHƯA cập nhật bản sao lưu trong git")
            print("       → xem `diff` để biết bản nào mới hơn RỒI mới chép; đừng chép mù.")
            print("  Công cụ KHÔNG tự đoán chiều nào đúng và KHÔNG bao giờ tự ghi lên bundle.")
        return 1
    print("KẾT QUẢ: ✓ ĐỒNG BỘ%s." % (" (đã sửa %d file)" % len(fixed) if fixed else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
