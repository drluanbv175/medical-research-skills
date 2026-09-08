---
name: research-lookup
description: Tra cứu NGHIÊN CỨU & ĐĂNG KÝ THỬ NGHIỆM — ClinicalTrials.gov qua connector (API v2 trực tiếp bị chặn egress); WHO ICTRP và PROSPERO hiện KHÔNG tra được bằng máy, phải nói rõ là chưa tra. Dùng khi cần kiểm một thử nghiệm đã đăng ký chưa, tìm nghiên cứu đang tiến hành/đã hoàn tất, đối chiếu kết cục đăng ký vs công bố (chống outcome switching), hoặc tra đăng ký tổng quan hệ thống. Trả mã đăng ký (NCT/ISRCTN/PROSPERO ID). KHÔNG bịa mã/đăng ký.
---

# Skill: Tra cứu nghiên cứu & đăng ký thử nghiệm (research-lookup)

Dùng cho `thu-thu-tai-lieu`, `tra-cuu-chung-cu`. Bổ trợ `paper-lookup` (bài báo) — skill này lo phần **đăng ký nghiên cứu**.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG bịa mã đăng ký/NCT/PROSPERO ID.** Chỉ nêu sau khi tra ra; không tra được → ghi rõ.
- Đối chiếu **kết cục đăng ký vs kết cục công bố** để cảnh báo outcome switching — chỉ nêu khi có bằng chứng.
- Connector lỗi → PARTIAL.

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

## Ba nguồn đăng ký — trạng thái thật

| Nguồn | Đường chạy được | Ghi chú |
|---|---|---|
| **ClinicalTrials.gov** | **connector** (`ToolSearch: clinical trials search`) — đo 2026-09-05: trả 81 thử nghiệm kèm NCT, pha, trạng thái, cỡ mẫu | `https://clinicaltrials.gov/api/v2/studies?query.term=…` **bị chặn egress** trong phiên cloud; chỉ dùng trên máy có mạng |
| **WHO ICTRP** | **KHÔNG có** | Không có REST API JSON công khai, **và** `trialsearch.who.int` không mở được bằng WebFetch. Ghi rõ **chưa tra ICTRP**; KHÔNG bịa endpoint, KHÔNG bịa ISRCTN/CTRI ID |
| **PROSPERO** | **KHÔNG có** | Không có API công khai; giao diện không mở được. Ghi rõ **chưa tra PROSPERO**; KHÔNG bịa ID. Bác sĩ tra tay rồi dán ID vào là đường duy nhất hiện nay |

`WebSearch` có thể ra manh mối cho ICTRP/PROSPERO nhưng **chỉ là snippet và chỉ kết quả US** —
dùng để định hướng, **không** dùng làm căn cứ ghi mã đăng ký. Mã đăng ký chỉ ghi khi đọc được
từ chính trang đăng ký.

## Quy trình
**BƯỚC 0 — Tiền đề:** `ToolSearch` xem connector thử nghiệm lâm sàng có chạy không (gọi thử một lệnh thật) — thiếu → PARTIAL, KHÔNG kết luận "không có thử nghiệm nào". Xác định cần: thử nghiệm can thiệp (ClinicalTrials/ICTRP) hay SR (PROSPERO).
1. **Dựng truy vấn:** bệnh/can thiệp/dân số + bộ lọc (pha, trạng thái, năm, quốc gia).
2. **Tra:** connector ClinicalTrials.gov trước. ICTRP/PROSPERO: hiện **không tra được bằng máy** → ghi thẳng là chưa tra, đừng lấp bằng suy đoán. Ghi **ngày tra · công cụ thực sự đã dùng · chuỗi truy vấn · số trả về**.
3. **Trích:** mã đăng ký (NCT/ISRCTN/PROSPERO), tiêu đề, trạng thái, pha, kết cục chính đăng ký, ngày, nhà tài trợ.
4. **Đối chiếu (nếu có bài công bố):** kết cục/thời điểm đăng ký vs công bố → cảnh báo lệch nếu có (nêu bằng chứng).

## Mẫu đầu ra
```
Truy vấn + công cụ/nguồn thực sự đã dùng + ngày tra + số trả về: ____
| Mã đăng ký | Tiêu đề | Trạng thái/Pha | Kết cục chính (đăng ký) | Nguồn |
Cảnh báo outcome switching (nếu có + bằng chứng): ____
[⚠ PARTIAL — nguồn chưa tra (mặc định: ICTRP, PROSPERO): ____]
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG soạn hồ sơ đăng ký (việc của agent `dao-duc-dang-ky`); KHÔNG thẩm định chất lượng. Chỉ TRA + XÁC MINH đăng ký. Nguồn không có API → tra web, ghi rõ, KHÔNG bịa endpoint/ID.
