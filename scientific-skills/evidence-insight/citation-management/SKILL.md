---
name: citation-management
description: Comprehensive citation management for academic research; use when you need to discover papers (Google Scholar/PubMed), extract/verify metadata (DOI/PMID/arXiv/URL), and produce validated, clean BibTeX for manuscripts.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)


<!-- evidence-source-routing -->
## Nguồn dữ liệu: ưu tiên MCP connector

**Thứ tự bắt buộc: MCP trước, REST API sau.**

1. **Đường chính — MCP connector** (chạy server-side, KHÔNG qua egress của container):
   `mcp__Scite__search_literature` (kèm `editorialNotices` để phát hiện bài bị rút); `mcp__PubMed__search_articles`, `get_article_metadata`, `get_full_text_article`, `convert_article_ids`, `find_related_articles`
2. **Dự phòng — REST API trực tiếp**: chỉ dùng khi không có connector phù hợp, hoặc
   cần tham số mà connector không hỗ trợ.

Host REST mà skill này cần: `api.crossref.org, doi.org, eutils.ncbi.nlm.nih.gov`

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

### Quy trình KHÔNG CẦN MẠNG (dùng khi Crossref bị chặn)

Dữ liệu Retraction Watch đầy đủ nằm ở `api.crossref.org` — host này thường bị
chính sách egress chặn. Connector **Scite** chạy server-side và trả cùng thông tin
đó trong trường `editorialNotices`. Đã đối chứng: Mehra 2020 (Surgisphere/HCQ) và
Wakefield 1998 (MMR) đều được nhận diện `retracted` kèm DOI thông báo và ngày rút;
PRISMA 2020 sạch.

Ba bước — script lo hai đầu, bạn gọi Scite ở giữa:

```bash
# 1) Rút DOI từ bản thảo / .bib
python3 ../../../scripts/retraction_check.py extract manuscript.md
```

```
# 2) Gọi connector với danh sách DOI vừa nhận:
     mcp__Scite__search_literature(dois=[...], limit=<số DOI>)
     Lưu nguyên JSON trả về vào scite.json
```

```bash
# 3) Dựng bảng phán định
python3 ../../../scripts/retraction_check.py report scite.json --dois-from manuscript.md
```

Mã thoát: `0` sạch · `1` **có bài bị rút** · `2` có quan ngại/đính chính · `3` có DOI chưa kiểm được.

**Quy tắc bắt buộc:** DOI mà Scite không trả về được xếp `CHƯA KIỂM`, **không**
được coi là sạch. Báo cáo phải ghi rõ "chưa xác minh được tình trạng rút bài".

Mẹo: có thể lọc thẳng bằng `mcp__Scite__search_literature(has_retraction=true, ...)`
khi muốn quét một chủ đề thay vì một danh sách DOI cụ thể.

### Bản đầy đủ — tra offline bằng Retraction Watch

Chỉ mục Scite không phủ 100%. Muốn kết luận chắc chắn, tải bộ dữ liệu
Retraction Watch về máy (chỉ làm được nơi có mạng tới Crossref):

```bash
python3 ../../../tools/tai_retraction_watch.py tai --email ban@vidu.com
python3 ../../../scripts/retraction_check.py local ban-thao.md
```

Ở chế độ này, DOI không có trong bộ dữ liệu được kết luận **SẠCH** (vì đây là sổ
đăng ký đầy đủ), khác với chế độ Scite phải xếp `CHƯA KIỂM`. Tuổi dữ liệu luôn
được in ra; quá 30 ngày sẽ bị cảnh báo là CŨ.



## When to Use

- You need to **find relevant or highly cited papers** on a topic using Google Scholar or PubMed.
- You have identifiers (e.g., **DOI, PMID, arXiv ID, URL**) and must **convert them into correct BibTeX**.
- You want to **verify citation accuracy** (DOI resolution, required fields, consistency with CrossRef/PubMed).
- You need to **clean, deduplicate, sort, and standardize** an existing `.bib` file before submission.
- You are preparing a thesis/manuscript and need a **reproducible workflow** from search → extraction → formatting → validation.

## Key Features

- **Paper discovery**
  - Google Scholar search with year filtering, pagination, and citation-count sorting.
  - PubMed search with MeSH terms, field tags, publication-type filters, and date ranges.
- **Metadata extraction**
  - Resolve DOI/PMID/arXiv/URL to structured metadata via CrossRef, PubMed E-utilities, and arXiv APIs.
  - Batch processing from files containing mixed identifiers.
- **BibTeX generation & cleanup**
  - Generate BibTeX entries with appropriate entry types and required fields.
  - Format, sort (key/year/author), and deduplicate BibTeX libraries.
- **Citation validation**
  - DOI resolution checks and metadata cross-checking.
  - Required-field checks by entry type, syntax validation, duplicate detection, and optional auto-fix.
- **Workflow integration**
  - Produces submission-ready `.bib` files for LaTeX/Overleaf workflows and complements literature review pipelines.

## Dependencies

- Python: 3.10+ (recommended)
- Python packages:
  - `requests>=2.31.0`
  - `scholarly>=1.7.11` (optional; required only for Google Scholar automation)

## Example Usage

A complete, end-to-end workflow that searches, extracts metadata, formats, deduplicates, and validates a bibliography:

```bash
# 1) Search PubMed (biomedical focus)
python scripts/search_pubmed.py \
  --query '"CRISPR-Cas Systems"[MeSH] AND "Gene Editing"[MeSH]' \
  --date-start 2020-01-01 \
  --date-end 2024-12-31 \
  --limit 200 \
  --output crispr_pubmed.json

# 2) Search Google Scholar (broad coverage)
python scripts/search_google_scholar.py "CRISPR gene editing therapeutics" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100 \
  --output crispr_scholar.json

# 3) Extract metadata from search outputs (or mixed identifiers)
cat crispr_pubmed.json crispr_scholar.json > combined_results.json
python scripts/extract_metadata.py \
  --input combined_results.json \
  --output combined.bib

# 4) Add known papers by DOI (append)
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2 >> combined.bib
python scripts/doi_to_bibtex.py 10.1126/science.aam9317 >> combined.bib

# 5) Format + deduplicate + sort (newest first)
python scripts/format_bibtex.py combined.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output formatted.bib

# 6) Validate + auto-fix common issues + emit report
python scripts/validate_citations.py formatted.bib \
  --auto-fix \
  --report validation.json \
  --output final_references.bib

# 7) Inspect validation results
cat validation.json
```

## Implementation Details

### 1) Search (Discovery)

- **Google Scholar** (`scripts/search_google_scholar.py`)
  - Supports query operators such as exact phrases (`"deep learning"`), author filters (`author:LeCun`), title-only (`intitle:"neural networks"`), exclusions (`-survey`), and year ranges.
  - Typical parameters:
    - `--year-start`, `--year-end`: constrain publication years
    - `--limit`: cap results
    - `--sort-by citations`: prioritize highly cited papers (when supported by the script)

- **PubMed** (`scripts/search_pubmed.py`)
  - Uses NCBI E-utilities (e.g., ESearch/EFetch/ESummary) to retrieve PMIDs and metadata.
  - Typical parameters:
    - `--query`: supports MeSH terms, field tags, and Boolean logic
    - `--date-start`, `--date-end`: publication date filtering
    - `--publication-types`: e.g., `Clinical Trial,Review`
    - `--format`: JSON or BibTeX output (if supported)

(See: `references/google_scholar_search.md`, `references/pubmed_search.md`)

### 2) Metadata Extraction (Normalization)

- **Identifier inputs**: DOI, PMID, arXiv ID, URL, or mixed lists/files.
- **Primary sources**:
  - CrossRef API for DOI-centric journal metadata
  - PubMed E-utilities for biomedical records (PMID/PMCID, MeSH, abstracts)
  - arXiv API for preprints and versioned records
  - DataCite API for datasets/software DOIs (if implemented/used)
- **Field mapping goals**:
  - Required: `author`, `title`, `year`
  - Articles: `journal`, `volume`, `number`, `pages`, `doi`
  - Conferences: `booktitle`, `pages`
  - Preprints: repository + identifier (e.g., `eprint`, `archivePrefix`)

(See: `references/metadata_extraction.md`)

### 3) BibTeX Formatting (Quality & Consistency)

- Entry types commonly produced: `@article`, `@inproceedings`, `@book`, `@misc`.
- Formatting rules enforced/encouraged:
  - Page ranges use `--` (e.g., `123--145`)
  - Protect capitalization in titles with braces (e.g., `{CRISPR}`)
  - Consistent author formatting (`Last, First and Last, First`)
  - Stable citation keys (project convention; often `FirstAuthorYearKeyword`)

(See: `references/bibtex_formatting.md`)

### 4) Validation (Correctness)

Validation typically checks:

- **DOI validity**: resolves via `doi.org` and matches CrossRef metadata.
- **Required fields**: present per entry type; no empty critical fields.
- **Consistency**: year format, numeric volume/issue, page-range syntax, URL accessibility.
- **Duplicates**: same DOI, near-identical titles, or same author/year/title combinations.
- **BibTeX syntax**: braces/quotes, commas, unique keys, special character handling.

Outputs may include a machine-readable report (e.g., JSON) with `errors` and `warnings`.
(See: `references/citation_validation.md`)

## When Not to Use

- Do not proceed when required input files, identifiers, parameters, or context are missing — ask the user to provide them first.
- Do not assume capabilities beyond this skill's declared scope when the user requests external operations or inferences.
- Do not proceed without user confirmation when overwriting existing results, executing high-cost batch operations, or expanding task scope.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| User task description | Yes | Text | Research question, writing goal, analysis objective | Stop and ask user to provide |
| Primary input material | Depends on task | Text, file path, ID, table, or literature | PMID, PDF, CSV, DOCX, keywords, etc. | Specify which material type is missing |
| Output preference | No | Text | Language, format, target journal, template | Use skill default format |

## Output Contract

- Primary output: Structured result or target file aligned with this skill's objective.
- Optional output: Intermediate check notes, issue list, supplementary suggestions, or generated file paths.
- Format requirement: Unless the user specifies otherwise, prefer stable, reviewable Markdown or JSON; if the skill's bundled script requires a fixed format, use that format.
- If partially complete: Must explicitly mark as PARTIAL and state which steps are completed and which remain.

## Failure Handling

- Missing critical input: Explicitly state which fields, files, or identifiers are missing and pause.
- Script, template, or resource execution failure: Report the failing step, likely cause, and recovery suggestions — do not silently degrade.
- Partial completion only: Return the verified portion first, then list remaining blockers and suggested next steps.

## User Checkpoints

- Before executing batch processing, overwriting files, long-running searches, or multi-stage generation, confirm scope and output format with the user.
- Before proceeding when a key judgment is ambiguous, evidence is insufficient, or the workflow is entering the next stage, confirm with the user.


## Input Validation

This skill accepts requests that match the documented purpose of `citation-management` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `citation-management` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
