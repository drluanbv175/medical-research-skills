#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh .claude-plugin/marketplace.json cho MỘT repo skill bất kỳ.

Biến một repo chứa các thư mục SKILL.md thành plugin cài được bằng một lệnh
`/plugin marketplace add <owner>/<repo>` — thay cho việc tải tay từng skill lên
tài khoản. Repo trở thành nguồn chân lý; `git pull` là cập nhật.

    python3 tools/tao_marketplace.py <đường-dẫn-repo>            # xem trước
    python3 tools/tao_marketplace.py <đường-dẫn-repo> --ghi      # ghi file

Chỉ đọc SKILL.md; không sửa nội dung skill. Cần bác sĩ kiểm chứng trước khi đẩy.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Claude Code yêu cầu tên skill dạng chữ-thường-gạch-nối; tên hoa/gạch dưới bị loại.
HOP_LE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BO_QUA = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox"}


def doc_frontmatter(duong_dan: str) -> dict[str, str]:
    """Trả về {name, description} từ YAML frontmatter; {} nếu không đọc được."""
    try:
        noi_dung = open(duong_dan, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return {}
    khop = re.match(r"^---\r?\n(.*?)\r?\n---", noi_dung, re.S)
    if not khop:
        return {}
    ket_qua: dict[str, str] = {}
    for khoa in ("name", "description"):
        m = re.search(rf"^{khoa}:\s*(.+?)\s*$", khop.group(1), re.M)
        if m:
            ket_qua[khoa] = m.group(1).strip().strip("\"'")
    return ket_qua


def tim_skill(goc: str) -> list[str]:
    """Đường dẫn tương đối của mọi thư mục chứa SKILL.md, đã sắp xếp."""
    tim_thay = []
    for thu_muc, con, tep in os.walk(goc):
        con[:] = [c for c in con if c not in BO_QUA and not c.startswith(".")]
        if "SKILL.md" in tep:
            tim_thay.append(os.path.relpath(thu_muc, goc))
    return sorted(tim_thay)


def main() -> int:
    bp = argparse.ArgumentParser(description="Sinh marketplace.json cho repo skill")
    bp.add_argument("repo", help="đường dẫn tới repo")
    bp.add_argument("--ten", help="tên plugin (mặc định: tên thư mục repo)")
    bp.add_argument("--mo-ta", default="", help="mô tả plugin")
    bp.add_argument("--ghi", action="store_true", help="ghi file (mặc định chỉ xem trước)")
    tham_so = bp.parse_args()

    goc = os.path.abspath(os.path.expanduser(tham_so.repo))
    if not os.path.isdir(goc):
        print(f"LỖI: không thấy thư mục {goc}", file=sys.stderr)
        return 2

    thu_muc_skill = tim_skill(goc)
    if not thu_muc_skill:
        print(f"LỖI: không tìm thấy SKILL.md nào trong {goc}", file=sys.stderr)
        return 2

    hop_le, van_de = [], []
    for tuong_doi in thu_muc_skill:
        fm = doc_frontmatter(os.path.join(goc, tuong_doi, "SKILL.md"))
        ten = fm.get("name", "")
        if not ten:
            van_de.append((tuong_doi, "thiếu 'name' trong frontmatter"))
        elif not fm.get("description"):
            van_de.append((tuong_doi, "thiếu 'description' trong frontmatter"))
        elif not HOP_LE.match(ten):
            van_de.append((tuong_doi, f"tên '{ten}' không hợp lệ — cần chữ thường, gạch nối"))
        else:
            hop_le.append("./" + tuong_doi.replace(os.sep, "/"))

    ten_plugin = tham_so.ten or os.path.basename(goc).lower()
    ban_ke = {
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": ten_plugin,
        "description": tham_so.mo_ta or f"Skill từ repo {os.path.basename(goc)}.",
        "owner": {"name": os.path.basename(goc)},
        "plugins": [
            {
                "name": ten_plugin,
                "description": tham_so.mo_ta or f"{len(hop_le)} skill.",
                "source": "./",
                "strict": False,
                "skills": hop_le,
            }
        ],
    }

    print(f"Repo      : {goc}")
    print(f"SKILL.md  : {len(thu_muc_skill)}")
    print(f"Đưa vào   : {len(hop_le)}")
    print(f"Bỏ qua    : {len(van_de)}")
    for tuong_doi, ly_do in van_de:
        print(f"   ✗ {tuong_doi} — {ly_do}")

    dich = os.path.join(goc, ".claude-plugin", "marketplace.json")
    if not tham_so.ghi:
        print(f"\n(xem trước — chưa ghi gì; thêm --ghi để tạo {dich})")
        return 0

    os.makedirs(os.path.dirname(dich), exist_ok=True)
    with open(dich, "w", encoding="utf-8") as f:
        json.dump(ban_ke, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"\nĐã ghi: {dich}")
    return 1 if van_de else 0


if __name__ == "__main__":
    sys.exit(main())
