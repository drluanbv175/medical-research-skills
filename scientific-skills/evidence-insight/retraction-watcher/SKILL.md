---
name: retraction-watcher
description: Automatically scan reference lists and check whether cited papers have been retracted, corrected, or flagged; use before submission, review, or evidence synthesis to reduce citation risk.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

<!-- evidence-source-routing -->
## Nguồn dữ liệu: ưu tiên MCP connector

**Thứ tự bắt buộc: MCP trước, REST API sau.**

1. **Đường chính — MCP connector** (chạy server-side, KHÔNG qua egress của container):
   `mcp__Scite__search_literature` (kèm `editorialNotices` để phát hiện bài bị rút)
2. **Dự phòng — REST API trực tiếp**: chỉ dùng khi không có connector phù hợp, hoặc
   cần tham số mà connector không hỗ trợ.

Host REST mà skill này cần: `api.crossref.org`

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

# Retraction Watcher

A specialized skill for identifying retracted, corrected, or questionable papers in academic reference lists before they compromise research integrity.

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


## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## When to Use

- Use this skill when the task needs Automatically scan document reference lists and check against Retraction.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Purpose

Academic misconduct and errors can lead to paper retractions. Citing retracted work undermines research credibility. This skill:
- Scans reference lists from manuscripts, papers, or bibliographies
- Cross-checks citations against Retraction Watch and other retraction databases
- Identifies papers with retraction notices, expressions of concern, or corrections
- Provides detailed reports with retraction reasons and dates

## Trigger Conditions

Activate this skill when:
1. User provides a document with references and asks to check for retractions
2. User explicitly requests "check my references" or "scan for retracted papers"
3. User submits a bibliography or reference list for verification
4. Pre-submission manuscript review is requested
5. User wants to verify citation integrity

## Input Format

Accepted inputs:
- PDF files (manuscripts, papers, theses)
- Plain text files (.txt, .bib, .ris)
- Raw text containing reference lists
- URLs to papers or reference lists
- Clipboard content with citations

## Output Format

### Report Header
```
🔍 RETRACTION WATCH REPORT
Documents Scanned: [N]
References Found: [N]
Check Date: [YYYY-MM-DD]
```

### Status Categories

**🔴 RETRACTED** - Paper has been officially retracted
- Reason for retraction
- Retraction date
- Original DOI/PMID
- Recommended action: Remove citation

**🟡 EXPRESSION OF CONCERN** - Journal has raised concerns
- Nature of concern
- Date issued
- Recommended action: Verify current status, consider alternative sources

**🟠 CORRECTED** - Paper has published corrections/errata
- Correction details
- Date of correction
- Recommended action: Check if correction affects cited claims

**🟢 CLEAR** - No retraction issues found

## Technical Approach

### Citation Parsing Strategy
1. **Format Detection**: Identify citation style (APA, MLA, Vancouver, Chicago, etc.)
2. **Field Extraction**: Parse DOI, PMID, title, authors, journal, year
3. **Identifier Resolution**: Normalize DOIs (remove prefixes, validate format)
4. **Title Matching**: Extract article titles for fuzzy matching

### Database Checking
1. **Retraction Watch Database** - Primary source for retraction data
2. **Crossref API** - Retraction metadata via "update-type: retraction"
3. **PubMed API** - Retraction notices via publication type filters
4. **Open Retractions** - Aggregated retraction data

### Matching Algorithm
- **Exact Match**: DOI/PMID exact match (highest confidence)
- **Title Match**: Normalized title comparison (90%+ similarity threshold)
- **Author + Year**: Secondary verification for ambiguous matches
- **Fuzzy Matching**: Handle minor title variations and typos

## Difficulty Level

**Medium-High** - Requires:
- Robust citation parsing across multiple formats
- API integration with retraction databases
- Handling of partial/incomplete citation data
- Fuzzy matching for title-based lookups
- Rate limiting and caching for API calls

## Quality Criteria

A successful scan must:
- [ ] Parse >90% of citations correctly from standard formats
- [ ] Achieve <1% false positive rate on retraction detection
- [ ] Provide actionable recommendations for each flagged citation
- [ ] Handle missing DOIs/PMIDs via title matching fallback
- [ ] Complete checks within reasonable time (<30s for 50 references)
- [ ] Preserve reference numbering for easy identification

## Limitations

- Requires internet connection for database lookups
- Rate limits may apply to free API tiers
- Very recent retractions (<48 hours) may not be indexed
- Title-only matching may produce false positives with similar titles
- Non-English papers may have limited coverage
- Preprint citations (arXiv, bioRxiv) typically not tracked for retractions

## Example Usage

```python
# Check a PDF manuscript
python scripts/main.py --input manuscript.pdf --format detailed

# Check a BibTeX file
python scripts/main.py --input references.bib --output report.txt

# Check raw text
python scripts/main.py --text "[paste references here]"

# Quick check with summary only
python scripts/main.py --input paper.pdf --format summary
```

## Data Sources

- **Retraction Watch Database**: https://retractionwatch.com/
- **Crossref API**: https://api.crossref.org/
- **PubMed E-utilities**: https://www.ncbi.nlm.nih.gov/home/develop/api/
- **Open Retractions**: https://openretractions.com/

## References

See `references/` for:
- `citation-formats.md`: Supported citation format specifications
- `api-documentation.md`: Database API reference and rate limits
- `example-reports/`: Sample output reports for testing

---

**Author**: AI Assistant  
**Version**: 1.0  
**Last Updated**: 2026-02-06  
**Status**: Ready for use  
**Requires**: Internet connection for database lookups

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture

## Prerequisites

```text
# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `retraction-watcher` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `retraction-watcher` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.


## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.

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

## Quick Validation

- Check that key scripts, templates, or reference file paths this skill depends on exist.
- Check that the final output contains the core fields, sections, or files specified for this task.
- Check that results clearly mark assumptions, limitations, and incomplete items.
