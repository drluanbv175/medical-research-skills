---
name: nsfc-grant-writer
description: Generate a complete NSFC (National Natural Science Foundation of China) General Program grant application in Chinese, following the 2026 official template. Use when the user provides a scientific hypothesis and wants to generate a full grant application document, including abs...
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

# NSFC Grant Writer

Generate a complete NSFC General Program grant application from a scientific hypothesis and export it as a Word document.

## Workflow

```
Step 1: Parse hypothesis → extract key terms
Step 2: PubMed search → retrieve real references
Step 3: Generate full Markdown document (all sections)
Step 4: Save Markdown → call generate_docx.py → output .docx
```

## Step 1: Parse the Hypothesis

Extract from the hypothesis:
- Disease/condition
- Key molecules (proteins, genes, miRNAs, etc.)
- Biological process or pathway
- Proposed mechanism (e.g., promotes, inhibits, regulates via)

Also generate the **project title** (≤30 Chinese characters):
- Format: `Mechanism of {key molecules}/{axis}/{pathway} regulating {biological process}` or similar
- Must reflect the core molecules, mechanism, and disease from the hypothesis
- Example: `Mechanism of KDM5D/NEDD4/Cx43/ATP axis in astrocytes regulating microglial activation and inflammatory response in NP`
- This title is used as the `# [Title]` heading at the top of the document

Do NOT ask the user for additional information unless they have provided it. Proceed with only the hypothesis.

## Step 2: PubMed Literature Search

**MANDATORY**: All references must be retrieved via real PubMed API calls. Never fabricate references.

Read `references/pubmed-guide.md` for the full search protocol.

Quick reference:
- Search: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={QUERY}&retmax=10&sort=relevance&retmode=json`
- Fetch summaries: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={PMIDs}&retmode=json`
- Run 3-5 queries covering: disease epidemiology, key molecule expression, pathway/mechanism, therapeutic relevance
- Select 15-25 total references; format in APA

## Step 3: Generate the Full Document

Read `references/writing-guide.md` for detailed section-by-section requirements.

Generate the complete document as a single Markdown string following the structure in `references/template.md`.

**Section generation rules**:

| Section | Action |
|---------|--------|
| Abstract | Generate Chinese + English abstract + keywords |
| Section I: Research Rationale | Generate full content: 5 numbered subsections with `####` subheadings + hypothesis statement + research directions + reference list |
| Section II: Research Content | Generate: 3-4 research modules + innovation points + 4-year plan |
| Section III-1.1: Preliminary Research Foundation | Generate: expand on preliminary data from Section I |
| Section III-1.2: Feasibility Analysis | Generate: 4-dimension feasibility analysis |
| Section III (2-4) and Section IV (all subsections) | Leave as headings only — do NOT generate content |

**Citation rules**:
- Inline: `[N]` or `[N][M]` (max 2 per location), placed before punctuation
- Reference list at end of Section I only, APA format
- Sections II and III reuse the same reference numbers if needed

**Consistency rule**: Every preliminary data item mentioned in Section I (Figure 1, Figure 2, Table 1, etc.) MUST appear again in Section III 1.1, expanded with methods and results detail.

## Step 4: Create Output Folder and Export

### Output folder naming
Extract 2-3 core keywords from the hypothesis (Chinese preferred, use underscores).
Format: `{keyword1}_{keyword2}_{YYYYMMDD_HHMMSS}`
Example: `EGFR_LungCancer_20260527_143022`

Create this folder in the current working directory (or user's specified path).

### Save Markdown
Save the full generated document as `{folder_name}.md` inside the output folder (same stem as the folder name).

### Generate Word document
Run the script:
```bash
python scripts/generate_docx.py {output_folder}/{folder_name}.md {output_folder}
```

This produces `{output_folder}/{folder_name}.docx`.

### Dependency check
If `python-docx` is not installed, inform the user:
```
pip install python-docx
```
Then re-run the script.

### Final output to user
After successful generation, report:
- Output folder path
- Files created: `{folder_name}.md` and `{folder_name}.docx`
- Note: Sections requiring personal information (working conditions, ongoing projects, completed projects, Part IV) are left as headings for the applicant to complete
- Note: The mechanism diagram placeholder in Section I requires replacement with an actual figure

## Resources

- `references/template.md` — 2026 official template structure
- `references/writing-guide.md` — detailed writing requirements per section
- `references/pubmed-guide.md` — PubMed API search protocol and reference formatting
- `scripts/generate_docx.py` — Markdown to Word converter (requires `python-docx`)

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If execution fails, report the failure point, summarize what can still be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `nsfc-grant-writer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `nsfc-grant-writer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.
