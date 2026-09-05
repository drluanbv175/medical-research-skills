#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử bộ sinh marketplace.json.

Dựng repo skill giả trong thư mục tạm (gồm cả các ca hỏng: thiếu name,
thiếu description, tên viết hoa, không có frontmatter) rồi xác minh bộ sinh
nhận đúng skill hợp lệ và loại đúng skill hỏng — không đụng repo thật.

    python3 tests/test_tao_marketplace.py
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import tao_marketplace as tm

P = F = 0


def t(name, cond):
    global P, F
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    P, F = (P + 1, F) if cond else (P, F + 1)


def dung_skill(goc, tuong_doi, noi_dung):
    thu_muc = os.path.join(goc, tuong_doi)
    os.makedirs(thu_muc, exist_ok=True)
    with open(os.path.join(thu_muc, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(noi_dung)


def dung_repo_gia(goc):
    dung_skill(goc, "sync/skills/tra-cuu-bai-bao",
               '---\nname: tra-cuu-bai-bao\ndescription: "Tra cứu PMID/DOI."\n---\n\n# Nội dung\n')
    dung_skill(goc, "sync/skills/tham-dinh-grade",
               "---\nname: tham-dinh-grade\ndescription: Thẩm định GRADE.\n---\n")
    # Ca hỏng — phải bị loại, kèm lý do:
    dung_skill(goc, "sync/skills/ten-viet-hoa",
               "---\nname: TEN-VIET-HOA\ndescription: Tên sai quy ước.\n---\n")
    dung_skill(goc, "sync/skills/thieu-mo-ta", "---\nname: thieu-mo-ta\n---\n")
    dung_skill(goc, "sync/skills/thieu-ten", "---\ndescription: Không có name.\n---\n")
    dung_skill(goc, "sync/skills/khong-frontmatter", "# Chỉ có tiêu đề, không frontmatter\n")
    # Thư mục phải bị bỏ qua:
    dung_skill(goc, ".git/skills/an", "---\nname: an\ndescription: Trong .git.\n---\n")
    dung_skill(goc, "node_modules/x", "---\nname: x\ndescription: Trong node_modules.\n---\n")


def test_doc_frontmatter():
    print("\n### Đọc frontmatter ###")
    goc = tempfile.mkdtemp()
    try:
        dung_skill(goc, "a", '---\nname: a-b\ndescription: "Có nháy kép."\n---\n')
        fm = tm.doc_frontmatter(os.path.join(goc, "a", "SKILL.md"))
        t("lấy đúng name", fm.get("name") == "a-b")
        t("bóc nháy kép khỏi description", fm.get("description") == "Có nháy kép.")

        dung_skill(goc, "b", "# không frontmatter\n")
        t("không frontmatter -> rỗng", tm.doc_frontmatter(os.path.join(goc, "b", "SKILL.md")) == {})
        t("tệp không tồn tại -> rỗng", tm.doc_frontmatter(os.path.join(goc, "khong-co", "SKILL.md")) == {})
    finally:
        shutil.rmtree(goc, ignore_errors=True)


def test_ten_hop_le():
    print("\n### Quy ước tên skill (chỉ để CẢNH BÁO, không để loại) ###")
    for ten in ("ebm-master", "paper-lookup", "a", "x1-y2"):
        t(f"nhận '{ten}'", bool(tm.HOP_LE.match(ten)))
    for ten in ("EBM-MASTER", "Ebm-Master", "ebm_master", "-ebm", "ebm-", "ebm--master", "ebm master"):
        t(f"nhận diện '{ten}' lệch quy ước", not tm.HOP_LE.match(ten))


def test_tim_skill():
    print("\n### Quét thư mục skill ###")
    goc = tempfile.mkdtemp()
    try:
        dung_repo_gia(goc)
        tim_thay = tm.tim_skill(goc)
        t("tìm đủ 6 skill ngoài thư mục ẩn", len(tim_thay) == 6)
        t("bỏ qua .git", not any(".git" in d for d in tim_thay))
        t("bỏ qua node_modules", not any("node_modules" in d for d in tim_thay))
        t("kết quả đã sắp xếp", tim_thay == sorted(tim_thay))
    finally:
        shutil.rmtree(goc, ignore_errors=True)


def test_sinh_ban_ke():
    print("\n### Sinh bản kê ###")
    goc = tempfile.mkdtemp()
    try:
        dung_repo_gia(goc)
        argv = sys.argv[:]
        sys.argv = ["tao_marketplace.py", goc, "--ten", "thu-nghiem", "--ghi"]
        try:
            ma = tm.main()
        finally:
            sys.argv = argv

        t("có skill hỏng -> mã thoát 1", ma == 1)
        dich = os.path.join(goc, ".claude-plugin", "marketplace.json")
        t("đã ghi marketplace.json", os.path.isfile(dich))

        d = json.load(open(dich, encoding="utf-8"))
        ky_nang = d["plugins"][0]["skills"]
        t("nhận 3 skill có đủ name+description", len(ky_nang) == 3)
        t("giữ tra-cuu-bai-bao", "./sync/skills/tra-cuu-bai-bao" in ky_nang)
        t("giữ tham-dinh-grade", "./sync/skills/tham-dinh-grade" in ky_nang)
        # Đo thật 05/09/2026: skill khai `name: EBM-MASTER` vẫn nạp và chạy trên máy
        # này — Claude Code định danh theo tên thư mục. Loại nó khỏi bản kê là làm
        # người dùng mất một skill đang hoạt động mà không hay biết.
        t("GIỮ tên viết hoa (chỉ cảnh báo)", any("ten-viet-hoa" in s for s in ky_nang))
        t("loại thiếu mô tả", not any("thieu-mo-ta" in s for s in ky_nang))
        t("loại thiếu tên", not any("thieu-ten" in s for s in ky_nang))
        t("loại không frontmatter", not any("khong-frontmatter" in s for s in ky_nang))

        t("tên plugin theo --ten", d["name"] == "thu-nghiem")
        t("source trỏ gốc repo", d["plugins"][0]["source"] == "./")
        t("mọi đường dẫn bắt đầu bằng ./", all(s.startswith("./") for s in ky_nang))
        t("mọi đường dẫn có SKILL.md thật",
          all(os.path.isfile(os.path.join(goc, s[2:], "SKILL.md")) for s in ky_nang))
        t("ghi UTF-8 không escape", "\\u" not in open(dich, encoding="utf-8").read())
    finally:
        shutil.rmtree(goc, ignore_errors=True)


def test_ca_bien():
    print("\n### Ca biên ###")
    goc = tempfile.mkdtemp()
    try:
        argv = sys.argv[:]
        sys.argv = ["tao_marketplace.py", goc]
        try:
            t("repo không có skill -> mã thoát 2", tm.main() == 2)
        finally:
            sys.argv = argv

        sys.argv = ["tao_marketplace.py", os.path.join(goc, "khong-ton-tai")]
        try:
            t("thư mục không tồn tại -> mã thoát 2", tm.main() == 2)
        finally:
            sys.argv = argv

        dung_skill(goc, "s", "---\nname: s\ndescription: Hợp lệ.\n---\n")
        sys.argv = ["tao_marketplace.py", goc]
        try:
            t("xem trước -> mã thoát 0", tm.main() == 0)
        finally:
            sys.argv = argv
        t("xem trước KHÔNG ghi file",
          not os.path.exists(os.path.join(goc, ".claude-plugin", "marketplace.json")))
    finally:
        shutil.rmtree(goc, ignore_errors=True)


for fn in (test_doc_frontmatter, test_ten_hop_le, test_tim_skill,
           test_sinh_ban_ke, test_ca_bien):
    fn()

print(f"\n{'=' * 50}\n  PASS={P}  FAIL={F}\n{'=' * 50}")
sys.exit(1 if F else 0)
