---
name: citation-management
description: Quản lý & kiểm chứng trích dẫn học thuật — phân giải PMID/DOI bắt buộc qua connector (PubMed; DOI qua Scite/Amass vì Crossref bị chặn), đối chiếu metadata, bắt trích dẫn ma & citation washing, cảnh báo retracted/trùng, xuất danh mục Vancouver/ICMJE/AMA/BibTeX. Dùng khi soạn/soát tài liệu tham khảo, trước khi nộp bản thảo. KHÔNG bao giờ "tin" trích dẫn chưa phân giải; không bịa trích dẫn thay thế.
---

# Skill: Quản lý & kiểm chứng trích dẫn (citation-management)

Dùng cho `kiem-chung-trich-dan`, `binh-duyet`, `thu-thu-tai-lieu`, `tong-quan-y-van`. Cổng liêm chính chống trích dẫn ma.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG tin trích dẫn chưa phân giải được.** PMID/DOI không tra ra → 🔴 NGHI NGỜ MA; KHÔNG "sửa cho hợp lý", KHÔNG bịa trích dẫn thay thế.
- Phân giải qua **connector** (xem ĐƯỜNG TRA CỨU bên dưới): PMID qua PubMed; DOI qua Scite
  hoặc Amass — **Crossref bị chặn egress**, không dùng được trong phiên cloud. Connector lỗi →
  PARTIAL, **không** tuyên bố "đã xác minh".

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

## Quy trình (mỗi tài liệu)
**BƯỚC 0 — Tiền đề:** `ToolSearch` xem đường phân giải nào ĐANG chạy (gọi thử một lệnh thật); xác định phạm vi (chỉ định danh hay cả nội dung trích).
1. **Phân giải định danh:** PMID qua connector PubMed; **DOI**: thử `convert_article_ids` (DOI→PMID)
   trước, không ra thì tra Scite/Amass theo DOI. DOI không phân giải được bằng đường nào →
   🔴 NGHI NGỜ MA. Trích DOI từ văn bản phải cắt đúng dấu: bỏ dấu nháy/dấu câu bám đuôi, nhưng
   **đếm cân bằng ngoặc** trước khi cắt `)` — DOI Elsevier có ngoặc hợp lệ
   (`10.1016/S0140-6736(24)01296-0`).
2. **Đối chiếu metadata:** so tác giả·năm·tạp chí·tiêu đề trong bản thảo với gốc → khớp/lệch (nêu trường lệch).
3. **Kiểm nội dung (citation washing):** câu khẳng định trong bài có ĐÚNG điều bài báo nói không; bắt gán kết luận bài không có, trích sai chiều/quá tầm.
4. **Trùng & rút bài:** kiểm qua Scite `editorialNotices` (rút · đính chính · nêu quan ngại)
   hoặc Amass `isRetracted`. **Không tra được ≠ không bị rút** — ghi **CHƯA KIỂM**, kèm ngày.
5. **Xuất danh mục:** **Vancouver/ICMJE** (mặc định y khoa), hoặc AMA/APA/BibTeX; đánh số nhất quán với chỗ trích trong văn bản.

## Định dạng Vancouver/ICMJE (mẫu)
> Tác giả AA, Tác giả BB. Tiêu đề bài. Tên tạp chí viết tắt. Năm;Tập(Số):trang đầu-cuối. doi:....
- ≤6 tác giả: liệt kê hết; >6: 6 tác giả đầu + "et al."

## Mẫu đầu ra
```
| # | Trích dẫn trong bài | Trạng thái ✅/🟡/🔴 | Ghi chú | PMID/DOI đã xác minh |
DANH SÁCH 🔴 BẮT BUỘC xử lý (chặn "sẵn sàng nộp"): ____
Danh mục tham khảo sạch (Vancouver/ICMJE): ____
[⚠ PARTIAL — đường phân giải nào chưa chạy được: ____ · DOI CHƯA KIỂM bài rút: ____]
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG viết lại nội dung khoa học; KHÔNG bịa trích dẫn thay thế khi thiếu — nêu "cần bổ sung nguồn". Tìm bài mới → `paper-lookup`.
