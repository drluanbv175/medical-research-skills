---
name: literature-review
description: Quy trình TỔNG QUAN Y VĂN HỆ THỐNG theo PRISMA 2020 — câu hỏi PICO → đăng ký PROSPERO → chiến lược tìm tái lặp → sàng lọc (sơ đồ dòng chảy) → trích xuất → đánh giá nguy cơ sai lệch → tổng hợp định tính/meta + GRADE. Dùng khi cần làm tổng quan hệ thống đầy đủ, tái lặp, cho công bố/đề tài. Chỉ nguồn miễn phí; mỗi bài kèm PMID/DOI; ghi ngày tra + công cụ/CSDL THỰC SỰ đã chạy (connector hay API trực tiếp) + số trả về → số chọn.
---

# Skill: Tổng quan y văn hệ thống (literature-review)

Dùng cho `tong-quan-y-van`, `thu-thu-tai-lieu`. Khung chuẩn **PRISMA 2020**.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG bịa trích dẫn**; mỗi bài kèm **PMID/DOI** đã kiểm; ghi **ngày tra + CSDL** để tái lặp.
- CHỈ nguồn miễn phí. **Nhưng phải biết nguồn nào THỰC SỰ tra được** (xem ĐƯỜNG TRA CỨU):
  PubMed qua connector ✅ · bioRxiv/medRxiv ✅ nhưng **không tìm được theo từ khoá** ·
  Europe PMC · OpenAlex · Crossref · Cochrane CENTRAL/CDSR **KHÔNG có đường nào trong phiên
  cloud**. Liệt kê một CSDL trong chiến lược tìm mà không chạy được nó là **báo cáo sai
  phương pháp** — phải xếp vào phần "CSDL chưa tra".
- Đăng ký PROSPERO **TRƯỚC sàng lọc** để chống thay đổi hồi tố; đăng ký muộn → ghi rõ. Connector lỗi → PARTIAL.

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

## Quy trình PRISMA 2020
**BƯỚC 0 — Tiền đề:** `ToolSearch` + gọi thử một lệnh thật để biết CSDL nào chạy được (nạp được schema ≠ gọi được); xác định đây là SR chính thức → đăng ký PROSPERO; đối chiếu xem đã có SR tương tự chưa.
1. **Câu hỏi & tiêu chí:** PICO/PECO; tiêu chí nhận/loại; loại thiết kế.
2. **Đăng ký PROSPERO:** câu hỏi, tiêu chí, chiến lược tìm, phương pháp tổng hợp, kết cục.
3. **Chiến lược tìm — ghi CẢ HAI, không được ghi một:**
   (a) **chuỗi chuẩn** cho từng CSDL, đúng cú pháp CSDL đó (`[tiab]`, `[mh]`, ngoặc lồng) — để
   người khác tái lặp trên giao diện gốc; (b) **lệnh thực tế đã chạy**: công cụ/connector nào,
   tham số gì, ngày nào, trả về bao nhiêu. Connector **không nhận nguyên cú pháp PubMed** nên
   (a) và (b) thường KHÁC nhau — chỉ ghi (a) là mô tả một việc mình chưa làm.
   (dùng skill `paper-lookup`/`research-lookup`).
4. **Sàng lọc:** lưu số lượng từng bước → **sơ đồ dòng chảy PRISMA** (nhận diện → sàng lọc → đủ điều kiện → đưa vào); 2 người sàng độc lập nếu có (ghi κ đồng thuận).
5. **Trích xuất dữ liệu:** bảng đặc điểm (thiết kế, n, dân số, can thiệp, kết cục, hiệu ứng) — dùng skill trích xuất nếu có.
6. **Nguy cơ sai lệch:** RoB 2 (RCT)/ROBINS-I (quan sát)/QUADAS-2 (chẩn đoán)/AMSTAR-2 (SR).
7. **Tổng hợp:** định tính; nếu đồng nhất đủ → meta (skill `statistical-analysis`: pooled + I²/forest/funnel); **GRADE** Summary of Findings.

## Mẫu đầu ra
```
PICO + tiêu chí | PROSPERO: [ID / [CẦN BỔ SUNG] / đăng ký muộn]
Chiến lược tìm — chuỗi CHUẨN (mỗi CSDL + cú pháp gốc): ____
Lệnh THỰC TẾ đã chạy (công cụ + tham số + ngày + số trả về): ____
Sơ đồ PRISMA: nhận diện __ → sàng lọc __ → đủ điều kiện __ → đưa vào __
| Bài (PMID/DOI) | Thiết kế | n | Kết cục | Hiệu ứng (CI) | RoB |
GRADE SoF + khoảng trống/giới hạn (heterogeneity, publication bias)
[⚠ PARTIAL — CSDL chưa tra (mặc định trong phiên cloud: Europe PMC, Cochrane, OpenAlex, Crossref, PROSPERO): ____]
```
Kết: **"Cần bác sĩ kiểm chứng."**

## Ranh giới
KHÔNG tự gộp số phức tạp (→ `statistical-analysis`); KHÔNG viết bản thảo (→ `scientific-writing`). Connector thiếu → PARTIAL, ghi rõ CSDL nào chưa tra.
