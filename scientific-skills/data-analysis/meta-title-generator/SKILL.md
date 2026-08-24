---
name: meta-title-generator
description: Generates Meta-Analysis research titles based on user keywords, utilizing PubMed search results if available, or creative generation otherwise. Use when the user wants to brainstorm or generate titles for a meta-analysis, specifically starting from keywords or a topic.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

<!-- evidence-source-routing -->
## Nguồn dữ liệu: ưu tiên MCP connector

**Thứ tự bắt buộc: MCP trước, REST API sau.**

1. **Đường chính — MCP connector** (chạy server-side, KHÔNG qua egress của container):
   `mcp__PubMed__search_articles`, `get_article_metadata`, `get_full_text_article`, `convert_article_ids`, `find_related_articles`
2. **Dự phòng — REST API trực tiếp**: chỉ dùng khi không có connector phù hợp, hoặc
   cần tham số mà connector không hỗ trợ.

Host REST mà skill này cần: `eutils.ncbi.nlm.nih.gov`

Trong nhiều môi trường (đặc biệt Claude Code on the web) các host trên **bị chính sách
egress chặn** — lời gọi thất bại với `Tunnel connection failed: 403` ngay ở bước CONNECT.
Khi đó MCP connector vẫn hoạt động bình thường.

**Kiểm tra trước khi chạy:**
```bash
python3 ../../../scripts/check_evidence_sources.py
```

### Quy tắc an toàn bắt buộc

> **"Không tra được nguồn" KHÁC "không có bằng chứng".**

- Nguồn không truy cập được thì **báo lỗi rõ ràng**, tuyệt đối không trả kết quả rỗng
  rồi để người đọc hiểu nhầm là đã tra xong.
- Không bao giờ tự sinh PMID, DOI, tiêu đề bài báo hay số liệu để lấp chỗ trống.
- Mọi báo cáo phải phân biệt ba trạng thái:
  `đã xác minh` · `không xác minh được (nêu lý do)` · `xác minh thấy sai`.
- Không tắt xác thực TLS, không bỏ `HTTPS_PROXY`, không đi vòng qua mirror.

Chi tiết định tuyến nguồn: [`../../../references/EVIDENCE-SOURCE-ROUTING.md`](../../../references/EVIDENCE-SOURCE-ROUTING.md)
<!-- evidence-source-routing -->

# Meta-Analysis Title Generator

## When to Use

- Use this skill when you need generates meta-analysis research titles based on user keywords, utilizing pubmed search results if available, or creative generation otherwise. use when the user wants to brainstorm or generate titles for a meta-analysis, specifically starting from keywords or a topic in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/search_pubmed.py` is the most direct path to complete the request.
- Use this skill when you need the `meta-title-generator` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Generates Meta-Analysis research titles based on user keywords, utilizing PubMed search results if available, or creative generation otherwise. Use when the user wants to brainstorm or generate titles for a meta-analysis, specifically starting from keywords or a topic.
- Packaged executable path(s): `scripts/search_pubmed.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Data Analytics/meta-title-generator"
python -m py_compile scripts/search_pubmed.py
python scripts/search_pubmed.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/search_pubmed.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/search_pubmed.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Description
This skill generates research titles for Meta-Analysis studies. It takes user-provided keywords, searches PubMed to find relevant literature, and proposes titles based on the findings. If the search runs successfully but returns no literature, it may generate titles creatively from the keywords (clearly labelled as not grounded in retrieved literature). If the search CANNOT be performed (network blocked), it stops and reports the failure instead of generating anything. It outputs 5 titles in both English and Chinese.

## Usage

### 1. Search and Generate
When the user provides keywords (e.g., "lung cancer", "hypertension"), follow these steps:

1.  **Generate Search Strategy**: Convert the user's keywords into a PubMed search strategy string (English keywords combined with AND/OR).
2.  **Search PubMed**: Run `scripts/search_pubmed.py` with the search strategy.
    *   The script returns JSON with a **`status`** field. Read `status` FIRST — it decides everything that follows.
3.  **Check Results — theo đúng ba nhánh, không gộp:**

    | `status` | Nghĩa | Hành động |
    |---|---|---|
    | `"ok"`, `total > 0` | Tra được, CÓ bài | Phân tích bài tìm được, sinh 5 tiêu đề dựa trên PICO của chúng. |
    | `"ok"`, `total == 0` | Tra được, PubMed KHÔNG có bài | Được phép sinh 5 tiêu đề sáng tạo từ từ khoá gốc. Ghi rõ tiêu đề **không dựa trên y văn đã tra**. |
    | `"unavailable"` | **KHÔNG tra được** (mạng/bị chặn) | **DỪNG LẠI.** Không sinh tiêu đề. |

    > **Cảnh báo an toàn — đây là điểm dễ gây hại nhất của skill này.**
    > `status: "unavailable"` (script thoát với mã 3) nghĩa là PubMed chưa từng được
    > hỏi. Đây **KHÔNG** phải "không có y văn". Tuyệt đối không rơi vào nhánh sinh
    > tiêu đề sáng tạo trong trường hợp này — làm vậy là trình bày nội dung tự nghĩ
    > ra như thể đã qua tra cứu y văn.
    >
    > Thay vào đó: báo cho người dùng biết nguồn không truy cập được, nêu nguyên nhân
    > từ trường `kind`/`reason`, và đề xuất dùng `mcp__PubMed__search_articles`
    > (connector chạy server-side, không qua egress của container) rồi làm lại bước 2.
4.  **Format Output**:
    *   Present the titles in a specific JSON format containing "Title1" to "Title5", each with "English" and "Chinese" fields.
    *   Ensure titles are strictly for Meta-Analysis (not clinical trials).
    *   Ensure interventions specify a drug or treatment method.

## Quality Rules
*   **Meta-Analysis Focus**: Titles must clearly indicate a Systematic Review and Meta-Analysis.
*   **Specific Interventions**: Do not use broad terms; specify the drug or method.
*   **Bilingual Output**: Every title must have an English and Chinese version.

## Reference Material
For detailed prompting strategies used in title generation, see [references/title_generation_prompts.md](references/title_generation_prompts.md).
