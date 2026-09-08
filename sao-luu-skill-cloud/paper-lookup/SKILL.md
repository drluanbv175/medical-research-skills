---
name: paper-lookup
description: Tra cứu bài báo y khoa — connector MCP trước (PubMed/Scite/Amass/Consensus), API miễn phí trực tiếp (E-utilities/Crossref/Europe PMC) chỉ khi tên miền mở — tìm theo PICO/từ khóa/MeSH, phân giải và xác minh PMID/DOI, lấy metadata gốc. Dùng khi cần tìm bài cho một câu hỏi, kiểm một PMID/DOI có thật, hoặc lấy thông tin trích dẫn. LUÔN trả PMID/DOI; KHÔNG bịa bài; không tra ra → nói rõ, không "đoán".
---

# Skill: Tra cứu bài báo qua API miễn phí (paper-lookup)

Dùng cho `tra-cuu-chung-cu`, `thu-thu-tai-lieu`, `tong-quan-y-van`, `kiem-chung-trich-dan`.

## Nguyên tắc liêm chính (4 trụ cột)
- **CHỈ nguồn/API miễn phí và connector đã có sẵn**, không backend trả phí.
- **KHÔNG bịa bài/PMID/DOI.** Một bài chỉ được nêu sau khi phân giải được định danh thật + metadata khớp. Không tra ra → ghi rõ, KHÔNG ghép tên/tiêu đề cho "nghe hợp lý".
- Connector lỗi → đánh dấu **PARTIAL**, không kết luận "không có bài".

## ĐƯỜNG TRA CỨU — connector TRƯỚC, API trực tiếp SAU

**Đo 2026-09-05 (gọi thật):** trong phiên cloud, **mọi tên miền y khoa đều bị chặn ở tầng chính
sách** — `eutils.ncbi.nlm.nih.gov`, `api.crossref.org`, `clinicaltrials.gov`, Europe PMC đều trả
`403 to CONNECT`; `WebFetch` cũng bị chặn. Vậy nên **đường curl/python tới API miễn phí KHÔNG
chạy được ở đây**, và nguy hiểm nhất là nó trả lỗi mạng → rất dễ bị báo cáo nhầm thành
*"không tìm thấy bài nào"*.

**Thứ tự bắt buộc:**

1. **Connector MCP trước.** Tìm bằng `ToolSearch` theo **chức năng**, KHÔNG ghi cứng tên công cụ
   — tên connector **đã đổi ngay trong một phiên** (`mcp__290a5fde-…__search_articles` →
   `mcp__PubMed__search_articles`).
2. **API trực tiếp sau**, và chỉ khi kiểm thấy tên miền mở (trên máy bác sĩ thì thường mở):
   `curl -sS -o /dev/null -w '%{http_code}' https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi`
   → không ra `200` thì quay lại bước 1.
3. **Không tra được ≠ không có.** Lỗi mạng · thiếu connector · hết hạn ngạch → `⚠ PARTIAL`,
   ghi rõ nguồn nào chưa tra. **Tuyệt đối không** kết luận "không có bài nào".

| Cần gì | `ToolSearch` gợi ý | Giới hạn phải biết |
|---|---|---|
| Tìm bài · metadata · PMID↔PMCID↔DOI | `pubmed search articles` | trả `query_translation` MeSH; **không có trường funding/COI** |
| Kiểm **bài rút / đính chính** theo DOI | `scite search literature` | trường `editorialNotices`; chỉ mục **không phủ 100%** |
| Bản ghi bài + `isRetracted` + số trích dẫn | `amass biomedcore records` | có abstract đầy đủ; không có funding/COI |
| Đăng ký thử nghiệm (NCT, pha, kết cục) | `clinical trials search` | ClinicalTrials.gov; **không** gộp WHO ICTRP |
| Tìm theo câu hỏi, kèm abstract | `consensus search` | gói miễn phí **tối đa 10 kết quả, chỉ trang 0** |
| Tiền ấn phẩm bioRxiv/medRxiv | `biorxiv search preprints` | **KHÔNG tìm được theo từ khoá** — chỉ lọc ngày + chuyên mục |
| Tổng quan tự động | `elicit` | ❌ **HỎNG**: `api_access_denied` — đừng đưa vào chu trình |
| Tìm web | `WebSearch` | ✅ nhưng **chỉ kết quả US**, là snippet — **không phải văn bản gốc** |

**KHÔNG có connector cho:** Crossref · Europe PMC · OpenAlex · Unpaywall · WHO ICTRP · PROSPERO ·
Cochrane Library. Cần các nguồn này → chạy trên máy có mạng, hoặc bác sĩ tải tài liệu vào chỗ
làm việc để đọc tại chỗ. **Không mở được văn bản gốc thì không được kết luận mức khuyến cáo
(GRADE/1A/2B)** — đánh dấu `[CẦN KIỂM CHỨNG]`.

**Ghi vết mỗi lần tra:** ngày · công cụ/CSDL **thực sự** đã dùng · chuỗi truy vấn · số trả về →
số chọn. Ghi ngay lúc tra, không tái dựng về sau.

## API miễn phí trực tiếp — dùng KHI tên miền mở (máy bác sĩ), không dùng được trong phiên cloud
- **PubMed E-utilities** — `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
  - `esearch.fcgi?db=pubmed&term=...&retmax=...` → danh sách PMID
  - `esummary.fcgi?db=pubmed&id=PMID` → metadata tóm tắt
  - `efetch.fcgi?db=pubmed&id=PMID&rettype=abstract` → abstract
  - (Khuyến nghị ≤3 req/giây nếu không có API key; có key thì cao hơn.)
- **Crossref** — `https://api.crossref.org/works?query=...` hoặc `/works/{DOI}` (thêm `mailto=` polite pool).
- **Europe PMC** — `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=...&format=json` → có PMC toàn văn mở; trường `pmid`,`doi`,`isOpenAccess`.

## Quy trình
**BƯỚC 0 — Tiền đề:** `ToolSearch` xem connector tra cứu nào ĐANG có; thử một lệnh thật để biết nó chạy (nạp được schema ≠ gọi được). Không có đường nào → PARTIAL, KHÔNG kết luận "không có bài". Xác định chế độ: TÌM (từ câu hỏi) hay PHÂN GIẢI (từ PMID/DOI sẵn).
1. **Dựng truy vấn:** từ khóa tự do + đồng nghĩa + MeSH (đánh dấu nếu MeSH chưa kiểm trong MeSH Browser); ghép AND/OR; nêu bộ lọc (năm/loại bài/ngôn ngữ).
2. **Tra:** connector PubMed (chính) → bổ sung Consensus (≤10 kết quả) / Amass BiomedCore. Chỉ khi tên miền mở mới dùng E-utilities/Europe PMC/Crossref trực tiếp. Ghi **ngày tra · công cụ thực sự đã dùng · chuỗi truy vấn · số trả về → số chọn**.
3. **Xác minh:** với mỗi bài lấy metadata gốc (tác giả, tiêu đề, tạp chí, năm, tập/số/trang, PMID, DOI); loại bài không phân giải được; cảnh báo **retracted** — đường chạy được hiện nay là Scite `editorialNotices` hoặc Amass `isRetracted` (Crossref/RetractionWatch bị chặn). Không kiểm được thì ghi **CHƯA KIỂM**, không ghi "sạch".
4. **Xếp hạng:** theo thứ bậc chứng cứ (guideline→SR/MA→RCT→cohort→khác) + độ mới.

## Mẫu đầu ra
```
Truy vấn + công cụ/CSDL thực sự đã dùng + ngày tra + số trả về → số chọn: ____
| # | Tác giả (năm) | Tiêu đề | Loại NC | PMID | DOI | Toàn văn mở? |
[⚠ PARTIAL — connector lỗi / CSDL chưa tra: ____]
```
Mỗi bài kèm PMID/DOI đã xác minh. Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG thẩm định GRADE/chất lượng (→ thẩm định/critical appraisal); KHÔNG soát nội dung trích đúng/sai (→ `citation-management`). Chỉ TÌM + PHÂN GIẢI + XÁC MINH định danh.
