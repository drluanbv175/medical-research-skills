# Đường tra cứu y văn — bản chuẩn dùng chung cho 5 skill

> Bản gốc của đoạn "ĐƯỜNG TRA CỨU" được chép vào `SKILL.md` của `paper-lookup`,
> `citation-management`, `research-lookup`, `literature-review`, `nghien-cuu-ebm-tong-hop`.
> Skill là các gói RIÊNG, không đọc được tệp của nhau — nên phải chép, và khi sửa thì
> **sửa ở đây trước**, rồi đồng bộ sang cả 5.
>
> Căn cứ: `de-xuat/NANG-LUC-PHIEN-CLOUD.md` (đo 2026-09-05, gọi thật).

## 1. Vấn đề đang sửa

Năm skill trên **mô tả cách làm việc là gọi API miễn phí bằng curl/python**: PubMed E-utilities,
Crossref, Europe PMC, ClinicalTrials.gov API v2, OpenAlex, Unpaywall.

Phép đo ngày 2026-09-05 cho thấy trong phiên cloud, **mọi tên miền y khoa đều bị chặn ở tầng
chính sách** (proxy trả `403 to CONNECT`), gồm `eutils.ncbi.nlm.nih.gov`, `api.crossref.org`,
`clinicaltrials.gov`, `www.who.int`. `WebFetch` cũng bị chặn (3/3 tên miền thử). Nghĩa là
**phương pháp đã ghi trong 5 skill không chạy được** — và tệ hơn: một tác tử làm theo đúng
tài liệu sẽ nhận lỗi mạng, rồi rất dễ báo cáo nhầm thành *"không tìm thấy bài nào"*.

Sửa: **connector trước, API trực tiếp sau**, và **không tra được thì phải nói là không tra được**.

## 2. Quy tắc bất biến

1. **Không tra được ≠ không có.** Lỗi mạng, connector thiếu, hạn ngạch hết → `⚠ PARTIAL`,
   ghi rõ nguồn nào chưa tra. **Tuyệt đối không** kết luận "không có bài nào".
2. **Không ghi cứng tên công cụ.** Tên connector **đã đổi ngay trong một phiên**
   (`mcp__290a5fde-…__search_articles` → `mcp__PubMed__search_articles`). Luôn tìm bằng
   `ToolSearch` theo **chức năng**, rồi dùng tên vừa tìm được.
3. **Ghi vết**: mỗi lần tra ghi lại **ngày · công cụ/CSDL thực sự đã dùng · chuỗi truy vấn ·
   số trả về → số chọn**. Ghi ngay lúc tra, không tái dựng về sau.
4. **Chuỗi tìm PRISMA ≠ lệnh đã chạy.** Connector không nhận nguyên cú pháp PubMed
   (`[tiab]`, `[mh]`, ngoặc lồng). Phải ghi **cả hai**: chuỗi chuẩn định chạy, và **lệnh
   thực tế đã chạy qua công cụ nào**. Chỉ ghi chuỗi chuẩn là báo cáo sai việc mình đã làm.

## 3. Bảng năng lực — tìm bằng `ToolSearch`, đừng ghi cứng tên

| Cần gì | `ToolSearch` gợi ý | Trạng thái đo 2026-09-05 | Giới hạn phải biết |
|---|---|---|---|
| Tìm bài · metadata · PMID↔PMCID↔DOI | `pubmed search articles` | ✅ chạy | Trả `query_translation` MeSH. **Không có trường funding/COI.** |
| Kiểm **bài rút / đính chính** theo DOI | `scite search literature` | ✅ chạy | Trường `editorialNotices`. Chỉ mục **không phủ 100%** |
| Bản ghi bài báo + `isRetracted` + `citationCount` | `amass biomedcore records` | ✅ chạy | 40M bản ghi, có abstract đầy đủ; **không có funding/COI** |
| Đăng ký thử nghiệm (NCT, pha, kết cục) | `clinical trials search` | ✅ chạy | ClinicalTrials.gov; **không** gộp ICTRP |
| Nhãn thuốc FDA/EMA nguyên văn | `amass regulatorycore` | ✅ chạy | Có `sourceUrl` truy nguyên |
| Tìm theo câu hỏi, kèm abstract | `consensus search` | ✅ chạy | **Gói miễn phí: tối đa 10 kết quả, chỉ trang 0** |
| Tiền ấn phẩm bioRxiv/medRxiv | `biorxiv search preprints` | ✅ chạy | **KHÔNG tìm được theo từ khoá** — chỉ lọc theo ngày + chuyên mục |
| Tổng quan hệ thống tự động | `elicit` | ❌ **HỎNG** | `api_access_denied` — tài khoản không có API. Đừng đưa vào chu trình |
| Đọc tài liệu guideline gốc trên web | `WebFetch` | ❌ **BỊ CHẶN** | 3/3 tên miền y khoa thử đều `EGRESS_BLOCKED` |
| Tìm web | `WebSearch` | ✅ chạy | **Chỉ kết quả US**; là snippet, **không phải văn bản gốc** |

**Không có connector cho:** Crossref, Europe PMC, OpenAlex, Unpaywall, WHO ICTRP, PROSPERO,
Cochrane Library. Cần các nguồn này thì phải chạy trên máy có mạng, hoặc bác sĩ tải tài liệu
vào repo để phiên đọc tại chỗ.

## 4. Hệ quả phải viết ra trong đầu ra

- **Mức khuyến cáo (GRADE / 1A / 2B) không được lấy từ WebSearch.** Không mở được văn bản gốc
  thì đánh dấu `[CẦN KIỂM CHỨNG]` và để bác sĩ mở tài liệu.
- **PROSPERO và WHO ICTRP hiện không tra được bằng máy.** Nêu rõ là chưa tra, không suy đoán ID.
- **Crossref không dùng được để phân giải DOI.** Đường thay thế: PubMed (`convert_article_ids`)
  cho bài có PMID; Scite hoặc Amass cho bài chỉ có DOI. DOI không phân giải được bằng đường
  nào → 🔴 NGHI NGỜ MA, **không** "sửa cho hợp lý".

## 5. Khi nào đường API trực tiếp vẫn đúng

Trên **máy của bác sĩ** hoặc môi trường có egress mở, `curl`/`urllib` tới E-utilities,
Crossref, Europe PMC vẫn là đường tốt và miễn phí. Giữ nguyên đoạn đó trong tài liệu, nhưng
đặt **sau** đường connector và **kèm điều kiện**: chỉ dùng khi kiểm tra thấy tên miền mở.
Kiểm nhanh: `curl -sS -o /dev/null -w '%{http_code}' https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi`
— không ra `200` thì chuyển sang connector, **không** kết luận "không có bài".
