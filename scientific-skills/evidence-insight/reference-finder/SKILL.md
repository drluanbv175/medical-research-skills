---
name: reference-finder
description: Automatically finds and ranks PubMed references for each sentence in scientific text; use when you need titles, DOIs, and brief recommendation reasons from the PubMed E-utilities API.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

<!-- evidence-source-routing -->
## Nguồn dữ liệu: ưu tiên MCP connector

**Thứ tự bắt buộc: MCP trước, REST API sau.**

1. **Đường chính — MCP connector** (chạy server-side, KHÔNG qua egress của container):
   `mcp__PubMed__search_articles`, `get_article_metadata`, `get_full_text_article`, `convert_article_ids`, `find_related_articles`; `mcp__Scholar_Gateway__semanticSearch`, `mcp__Consensus__search`, `mcp__Elicit__search_papers`
2. **Dự phòng — REST API trực tiếp**: chỉ dùng khi không có connector phù hợp, hoặc
   cần tham số mà connector không hỗ trợ.

Host REST mà skill này cần: `eutils.ncbi.nlm.nih.gov, api.crossref.org`

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

## When to Use

- You have a scientific paragraph and want suggested PubMed papers for **each sentence**.
- You need **top-ranked references** with **title, DOI, PMID, year**, and a short **why recommended** explanation.
- You are drafting or reviewing a manuscript and want quick **literature grounding** for key claims.
- You want a lightweight reference matcher that uses **only the official PubMed E-utilities API** (no third-party services).
- You need a scriptable tool for batch or CLI workflows to generate candidate citations.

## Key Features

- Sentence-level reference matching for scientific text.
- Returns the **top N (default: 3)** most relevant PubMed records per sentence.
- Outputs structured fields: **title, DOI, PMID, year, recommendation reason**.
- Relevance ranking based on:
  - keyword overlap / match strength,
  - publication year preference,
  - citation-count signal (when available/derivable).
- Safety constraints:
  - Network access restricted to `eutils.ncbi.nlm.nih.gov`.
  - No local filesystem writes except to `outputs/` during execution.
  - Request timeout set to **30 seconds** with clear error messages.
- Supports Python API usage and CLI usage (including interactive mode).

## Dependencies

- Python **3.x** (standard library only; no third-party packages required)

## Example Usage

### Python (direct call)

```python
from reference_finder import find_references

text = "CRISPR-Cas9 gene editing has revolutionized biomedical research."

results = find_references(text)

for ref in results[:3]:
    print(f"- {ref['title']} ({ref['year']})")
    print(f"  DOI: {ref['doi']}")
    print(f"  PMID: {ref['pmid']}")
    print(f"  Reason: {ref['reason']}")
```

### CLI (single input)

```bash
python scripts/find_refs.py "CRISPR-Cas9 gene editing has revolutionized biomedical research."
```

### CLI (interactive mode)

```bash
python scripts/find_refs.py
```

### Example output (JSON)

```json
[
  {
    "pmid": "PMID:",
    "title": "A Programmable Dual-RNA-Guided DNA Endonuclease in Vitro",
    "doi": "10.1126/science.1225829",
    "year": 2012,
    "reason": "Highest keyword match for 'CRISPR-Cas9', foundational paper"
  }
]
```

## Implementation Details

### Data flow

1. **Sentence splitting**: The input text is split into sentences (implementation-defined; typically punctuation-based).
2. **PubMed search (ESearch)**: For each sentence, a query is sent to:
   - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
3. **Record retrieval (EFetch)**: The top candidate PMIDs are fetched via:
   - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`
4. **Field extraction**: Title, year, PMID, and DOI (when present) are extracted from the returned metadata.
5. **Ranking and selection**: Candidates are scored and the top **N** are returned with a short recommendation reason.

### Ranking signals

- **Keyword match**: Measures overlap between sentence terms and retrieved record metadata (e.g., title/abstract terms when available).
- **Publication year**: Used as a preference signal (e.g., favoring more recent work unless a classic/foundational match is strong).
- **Citation count**: Incorporated when available/derivable; otherwise treated as missing without failing the run.

### Operational constraints and safety

- **Allowed network host**: `eutils.ncbi.nlm.nih.gov` only.
- **Prohibited**: Any third-party URLs.
- **Filesystem**: Do not write outside `outputs/` during execution.
- **Rate limiting**: Use a reasonable request cadence (e.g., **~0.5s** between requests) to respect API limits.
- **Timeout**: **30 seconds** per request.
- **Error handling**: Return semantic, user-readable error messages for network/API/parse failures.

### Defaults

- **Top references per sentence**: 3
- **Endpoints**:
  - ESearch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
  - EFetch: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`

### Related project files

- Main script: `scripts/find_refs.py`
- Tests: `tests/test_finder.py`
- Evaluation checklist: `references/evaluation-checklist.md`
- PubMed E-utilities documentation: https://www.ncbi.nlm.nih.gov/books/NBK25504/