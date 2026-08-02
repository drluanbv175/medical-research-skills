"""Sinh .claude-plugin/marketplace.json cho clone aipoch/medical-research-skills.

Kho gốc viết cho OpenClaw nên KHÔNG có manifest marketplace — đó là lý do
`/plugin marketplace add` báo lỗi. Script này dựng manifest còn thiếu.

Gộp TẤT CẢ skill vào MỘT plugin, có chủ đích: mỗi plugin khai `source: "./"`
sẽ được sao nguyên kho vào ~/.claude/plugins/cache/, nên tách 5 plugin đồng
nghĩa với 5 bản sao (~2,7 GB) thay vì 1 (~545 MB).

Đường dẫn được sinh TỪ ĐĨA THẬT, không gõ tay, để không lệch khi tên thư mục đổi.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path.home() / "Documents/GitHub/medical-research-skills"
TREES = ["awesome-med-research-skills", "scientific-skills"]

VALID_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Trùng tên giữa 2 cây -> giữ bản có description nhiều cụm từ kích hoạt hơn,
# vì description là thứ quyết định Claude có chọn đúng skill hay không.
PREFER_TREE = "awesome-med-research-skills"


def frontmatter_name(path: pathlib.Path) -> str:
    """Đọc khoá `name` trong frontmatter của SKILL.md."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    for line in text[3:end].splitlines():
        key, sep, val = line.partition(":")
        if sep and key.strip() == "name":
            return val.strip().strip('"').strip("'")
    return ""


def main() -> int:
    found: dict[str, pathlib.Path] = {}
    dropped: list[tuple[str, str]] = []
    invalid: list[str] = []

    for tree in TREES:
        for skill_md in sorted((REPO / tree).rglob("SKILL.md")):
            skill_dir = skill_md.parent
            rel = skill_dir.relative_to(REPO).as_posix()
            name = frontmatter_name(skill_md)

            if not name or not VALID_NAME.match(name):
                invalid.append(f"{name!r} <- {rel}")
                continue

            if name in found:
                # Đã có: giữ bản thuộc cây ưu tiên, bỏ bản kia.
                keep_is_preferred = found[name].as_posix().startswith(PREFER_TREE)
                if keep_is_preferred:
                    dropped.append((name, rel))
                    continue
                dropped.append((name, found[name].as_posix()))

            found[name] = pathlib.Path(rel)

    if invalid:
        print("Tên không hợp lệ, đã bỏ:", *invalid, sep="\n  ")

    print(f"Skill trùng tên đã bỏ bớt: {len(dropped)}")
    for name, rel in dropped:
        print(f"  - {name}: bỏ {rel}")

    # Kiểm tra lần cuối: mọi đường dẫn phải tồn tại thật và không chứa dấu cách.
    skills = []
    for name in sorted(found):
        rel = found[name].as_posix()
        abs_path = REPO / rel
        if not (abs_path / "SKILL.md").is_file():
            print(f"LỖI: không thấy SKILL.md tại {rel}", file=sys.stderr)
            return 1
        if " " in rel:
            print(f"LỖI: đường dẫn còn dấu cách: {rel}", file=sys.stderr)
            return 1
        skills.append(f"./{rel}")

    manifest = {
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": "aipoch-medical-research",
        "description": (
            "AIPOCH medical & scientific research skills (aipoch/medical-research-skills), "
            "repackaged for Claude Code. Upstream ships an OpenClaw layout with no "
            "marketplace manifest; this manifest adapts it without altering skill content."
        ),
        "owner": {"name": "AIPOCH"},
        "plugins": [
            {
                "name": "aipoch-medical-research",
                "description": (
                    f"{len(skills)} research skills across protocol design, academic writing, "
                    "data analysis and evidence appraisal. Source: "
                    "https://github.com/aipoch/medical-research-skills (MIT)."
                ),
                "source": "./",
                "strict": False,
                "skills": skills,
            }
        ],
    }

    out_dir = REPO / ".claude-plugin"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "marketplace.json"
    out_file.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"\nĐã ghi {out_file}")
    print(f"Tổng số skill đưa vào manifest: {len(skills)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
