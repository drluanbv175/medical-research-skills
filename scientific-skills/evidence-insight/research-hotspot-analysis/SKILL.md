---
name: research-hotspot-analysis
description: Analyze research hotspots for a disease or topic and recommend representative literature. Use when users need to identify trending directions, topic clusters, or generate hotspot review reports. Input is a disease name or research topic; output is a structured hotspot analysis report and representative literature list.
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

## Output Format

Output must strictly follow this structured report format to ensure users receive directly readable decision-ready content rather than a simple text description.

### 1. Hotspot Overview Table

Display all identified hotspot topics and their popularity metrics in tabular form.

| Hotspot Topic | Popularity Index | Trend Direction | Representative Papers | Active Years |
|---------|:-------:|:--------:|:-----------:|:--------:|
| [Topic 1] | ★★★★★ | Rising | 45 papers | 2023-2026 |
| [Topic 2] | ★★★★ | Stable | 28 papers | 2022-2026 |
| [Topic 3] | ★★★ | Declining | 12 papers | 2020-2024 |

- Popularity Index: Composite score based on publication volume, citation frequency, and top-tier journal proportion (max ★★★★★).
- Trend Direction: Recent 3-year publication trend (Rising / Stable / Declining).
- Representative Papers: Number of core papers matching the hotspot topic.
- Active Years: Year range with sustained output for the hotspot.

### 2. Hotspot Detail Analysis

Each hotspot is expanded independently, including popularity rating, trend description, sub-direction composition, and key papers.

#### Hotspot 1: [Topic Name]
- **Popularity Index**: ★★★★★ (Very Hot)
- **Trend**: Rising publication volume over the past 3 years
- **Core Research Directions**:
  - Sub-direction A (40%)
  - Sub-direction B (35%)
- **Key Papers**:

| Paper | Journal | Year | Citations | Evidence Level |
|------|:----:|:----:|:----:|:--------:|
| [Title] | Nature | 2025 | 230 | High |
| [Title] | Cell Rep | 2024 | 98 | Medium |
| [Title] | Front Immunol | 2024 | 15 | Low |

- **Evidence Level**: High (top-tier/highly cited), Medium (mainstream/moderate citations), Low (lower-tier/few citations).

#### Hotspot 2: [Topic Name]
...

### 3. Research Gap Identification

Analyze under-explored areas in current literature.

| Research Gap | Potential Value | Feasibility | Reason |
|---------|:--------:|:------:|:--------:|
| [Gap 1 - underexplored direction] | High | Medium | Few than 10 papers, but clear clinical demand |
| [Gap 2] | Medium | High | Mature tools available, but not yet applied in this field |

- Potential Value: High / Medium / Low, based on unmet clinical or basic research needs.
- Feasibility: High / Medium / Low, based on technical maturity, research barriers, and execution difficulty.

### 4. Recommended Entry Directions

Based on the preceding analysis, provide concrete actionable research entry suggestions.

| Priority | Recommended Direction | Reason | Expected Output |
|:------:|:--------|:-----|:---------|
| 1 | [Direction A] | High popularity + existing gap + good feasibility | 1 review / 1 experimental design |
| 2 | [Direction B] | Emerging hotspot + low competition | 1-2 research papers |
| 3 | [Direction C] | Niche but high clinical value | Case series / methodology paper |

---

# Research Hotspot Analysis

## When to Use

- The user provides a disease name, target, technical roadmap, or research topic, and wants to quickly see current research hotspots.
- The user needs to cluster recent literature by keywords and topics to find directions worth deeper exploration.
- The user wants a Markdown hotspot analysis report with representative literature for topic selection or review writing.

## When Not to Use

- Do not use this skill when the user only needs single-paper retrieval or a simple reference list.
- If there is no clear disease, topic, or search scope, do not start clustering immediately — first ask the user to clarify topic boundaries.
- If the environment cannot access the scripts or retrieval data this skill depends on, do not fabricate hotspot results.

## Required Inputs

| Field | Required | Format/Source | Example | If Missing |
|---|---|---|---|---|
| `topic` | Yes | Text | `lung cancer immunotherapy` | Stop and request topic |
| `time_range` | No | Time range | `last 5 years` | Default to recent literature |
| `focus` | No | Text | `mechanism`, `clinical translation` | Default to comprehensive hotspot output |

## Workflow

1. Use `search_pubmed` from `scripts/analysis_ops.py` to search relevant literature and obtain PMIDs and basic metadata.
2. Run `word_frequency` on the returned `medline_texts` to count high-frequency keywords or MeSH terms.
3. Combine with hotspot prompts in `references/prompt_templates.md` to cluster high-frequency keywords into 3-6 hotspot topics.
4. Use `match_keywords` to map representative literature to each topic, avoiding mismatches between topics and evidence.
5. For each topic, call `sort_by_jif_and_select` to choose representative literature, then use `fetchPMCArticleDetails` or `fetchPubmedArticleDetails` to supplement details.
6. Output a Markdown report with at least: research overview, hotspot topics, representative keywords per topic, representative literature, and follow-up suggestions.

## Output Contract

- Primary output: A Markdown hotspot analysis report.
- Required fields: `topic overview`, `hotspot topics`, `supporting papers`, `next-step suggestions`.
- Recommend at least 2-3 representative papers per hotspot, with explanation of why the topic qualifies as a hotspot.
- If retrieval coverage is insufficient, must explicitly mark as `PARTIAL`.

## Failure Handling

- Too few literature search results: First broaden time range or relax keywords, then explain coverage gaps.
- Unstable keyword clustering: Show high-frequency keywords and indicate clustering is candidate-only — do not force conclusions.
- Representative literature lacks usable details: Keep PMID and title, mark as pending.

## User Checkpoints

- Before starting a broad search, confirm topic boundaries and time range.
- Before outputting the final hotspot report, if cluster topics are clearly ambiguous, send candidate topics to user for confirmation.

## Tools
*   `fetchPMCArticleDetails`: Get article details.
*   `fetchPubmedArticleDetails`: Get PubMed details.

## Scripts
*   `scripts/analysis_ops.py`: Contains helper functions for PubMed search, frequency analysis, keyword matching, and result formatting.

## References
*   `references/prompt_templates.md`: Contains the system prompts for LLM analysis.

## Input Validation

This skill accepts requests that match the documented purpose of `research-hotspot-analysis` and include enough context to complete the workflow safely.

## Quick Validation

- Check that `scripts/analysis_ops.py` exists and can perform at least the three core steps: search, word frequency, and matching.
- Check that the final report contains hotspot topics with corresponding representative literature, not just a keyword list.
- Check that each hotspot topic has clear evidence sources to support it.
