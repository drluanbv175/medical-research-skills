# Năng lực phiên cloud — đo 2026-09-05, 12:25–12:45 UTC

> Mọi số liệu dưới đây là kết quả **gọi thật** trong chính phiên này. Nơi nào chỉ nạp được
> schema mà chưa gọi, đã ghi rõ. Không suy đoán, không tô hồng.
> Phạm vi hiệu lực: **phiên cloud CÓ nguồn repo đính kèm**. Xem "Giới hạn của phép đo".

- **Phiên này**: có nguồn repo đính kèm (`drluanbv175/medical-research-skills`, nhánh
  `claude/do-nang-luc-phien-cloud`) — khác Routine ở chỗ Routine sinh phiên mới không có nguồn nào.

---

## 1. Skill

- **Skill đồng bộ từ tài khoản: 44 SKILL.md**
  - 43 skill tại `/root/.claude/skills/synced/663e40d7-aa1d-4124-9a79-2c3563badb4c_1f8efc2f-396b-4507-8f3f-05e10bf3c606/`
  - 1 skill hệ thống tại `/root/.claude/skills/session-start-hook/`
  - Skill đồng bộ được nạp thật vào danh sách gọi được bằng công cụ `Skill`.

- **`cap-nhat-chung-cu-y-khoa`: CÓ** (v1.12.0)
  - Đường dẫn: `.../synced/663e40d7…/cap-nhat-chung-cu-y-khoa/SKILL.md`
  - Cấu trúc đầy đủ, không phải vỏ rỗng: `references/` (11 tệp, gồm `10-giam-sat-dinh-ky.md`
    và `11-guideline-bo-y-te-vn.md`), `templates/` (4 mẫu + `web-dashboard-evidence-workbench.html`
    + `web-dashboard-record-schema.csv`), `quality/` (2 checklist nghiệm thu), `tools/`,
    `data/drug_flags.json`.

- **Skill EBM tiếng Việt thấy được** (10 tên đầu): `cap-nhat-chung-cu-y-khoa`,
  `quan-ly-cap-nhat-ebm`, `tham-dinh-chung-cu-grade-nnt`, `kham-ngoai-tru-ebm`,
  `nghien-cuu-ebm-tong-hop`, `dashboard-master-ebm-ngoai-tru`, `antifacts`,
  `clinical-evidence-rag`, `nghien-cuu-y-khoa-chuan-quoc-te`, `ebm-master`.
  (Còn: `literature-review`, `paper-lookup`, `research-lookup`, `citation-management`,
  `peer-review`, `scientific-writing`, `statistical-analysis`, `ke-don-an-toan-benh-man`,
  `tiep-can-chan-doan-co-do-chuyen-tuyen`, `nguoi-cao-tuoi-da-benh-da-thuoc`,
  `tuan-thu-dieu-tri`, `giao-tiep-quyet-dinh-soap`, `dao-tao-slide-tai-lieu-y-khoa`,
  `ehospital-mini`, `dark-analyst`.)

---

## 2. Công cụ web

| Công cụ | Tồn tại | Gọi thật | Kết quả đo |
|---|---|---|---|
| **WebSearch** | CÓ | ✅ Chạy được | Truy vấn "KDIGO 2024 CKD guideline SGLT2i" trả 8 nguồn + tóm tắt. **Chỉ kết quả US.** Nội dung là tóm tắt từ snippet, **không phải trích nguyên văn tài liệu gốc**. |
| **WebFetch** | CÓ | ❌ **BỊ CHẶN** | 3/3 tên miền y khoa thử đều trả `EGRESS_BLOCKED`: `kdigo.org`, `www.ncbi.nlm.nih.gov`, `academic.oup.com`. |

Cả hai là công cụ hoãn nạp — phải `ToolSearch` với `select:WebSearch,WebFetch` trước khi dùng.

---

## 3. Mạng trực tiếp (curl/python) — **CHẶN TOÀN BỘ NGUỒN Y KHOA**

Đo bằng `curl` thật, mỗi tên miền một lần:

| Tên miền | Kết quả |
|---|---|
| `eutils.ncbi.nlm.nih.gov` (PubMed E-utilities) | **CHẶN** |
| `pubmed.ncbi.nlm.nih.gov` | **CHẶN** |
| `clinicaltrials.gov/api/v2` | **CHẶN** |
| `api.crossref.org` | **CHẶN** |
| `www.who.int` | **CHẶN** |
| `kdigo.org` | **CHẶN** |
| `pypi.org` (pip) | ✅ Chạy được (nằm trong `noProxy`) |

Trạng thái proxy xác nhận đây là **chặn theo chính sách**, không phải lỗi cấu hình:
`{"kind":"connect_rejected","detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)","host":"eutils.ncbi.nlm.nih.gov:443"}`

**Hệ quả trực tiếp:** mọi skill mô tả cách làm việc là "dùng API MIỄN PHÍ PubMed E-utilities /
Crossref / Europe PMC" qua curl hoặc python — gồm `paper-lookup`, `nghien-cuu-ebm-tong-hop`,
`citation-management`, `research-lookup`, `literature-review` — **KHÔNG chạy được theo đường đó**
trong môi trường này. Chúng chỉ chạy được nếu chuyển sang gọi connector MCP.

---

## 4. Connector — tên chính xác và kết quả GỌI THẬT

**Cảnh báo về định danh:** lúc 12:25 UTC mọi server mang tên **UUID**
(`mcp__290a5fde-…__search_articles`). Lúc ~12:44 UTC các server kết nối lại và đổi sang **tên thật**
(`mcp__PubMed__search_articles`). **Tên công cụ thay đổi ngay trong cùng một phiên.**

| Connector | Prefix hiện tại | Gọi thật | Kết quả |
|---|---|---|---|
| **PubMed** | `mcp__PubMed__*` | ✅ | `search_articles("SGLT2 inhibitors chronic kidney disease", ≥2025)` → **2 870 kết quả**, có `query_translation` MeSH. `convert_article_ids(PMID 39453837)` → `PMC7616743` + DOI → **đường lấy toàn văn PMC thông suốt**. |
| **Clinical Trials** | `mcp__Clinical_Trials__*` | ✅ | `search_trials(CKD + dapagliflozin)` → **81 thử nghiệm**, trả NCT ID, phase, status, enrollment. |
| **Amass Connector** | `mcp__Amass_Connector__*` | ✅ | BiomedCore → 10 bản ghi kèm **abstract đầy đủ**, `journalQualityJufo`, `isRetracted`, `citationCount`. RegulatoryCore (FDA) → **nguyên văn nhãn thuốc FDA** kèm `sourceUrl` accessdata.fda.gov. |
| **Consensus** | `mcp__Consensus__*` | ✅ | 10 bài kèm abstract + URL. **Gói miễn phí: tối đa 10 kết quả, chỉ trang 0.** |
| **Scite** | `mcp__Scite__*` | ✅ | Tra theo DOI → metadata + `tally` (41 citation) + Smart Citations nguyên văn + trường `editorialNotices` (**kiểm retraction**) + `isOa`/`license`. |
| **bioRxiv / medRxiv** | `mcp__bioRxiv__*` | ✅ | `search_preprints(medrxiv, 14 ngày)` → trả kết quả. **Hạn chế của chính công cụ: KHÔNG tìm được theo từ khoá**, chỉ lọc theo ngày + chuyên mục. |
| **Elicit** | `mcp__Elicit__*` | ❌ **HỎNG** | `api_access_denied` — "This Elicit account's plan doesn't include API access". **Nạp được schema nhưng không chạy được.** Cần nâng gói Pro. |
| Scholar Gateway | `mcp__Scholar_Gateway__semanticSearch` | ⬜ Chưa gọi | Tồn tại, chưa đo chức năng. |
| ICD-10 / ChEMBL | `mcp__ICD-10_Codes__*`, `mcp__ChEMBL__*` | ⬜ Chưa gọi | Tồn tại, chưa đo chức năng. |

**Connector cần kết nối lại** (`ListConnectors`, `installState: needs_reconnect`): **Canva**,
**HyperFrames by HeyGen**, **Synapse.org**. Không có cái nào là connector EBM cốt lõi → không
ảnh hưởng Routine giám sát chứng cứ. Phiên không tương tác **không** tự xác thực được; phải cấp
quyền ở cài đặt connector claude.ai.

---

## 5. Môi trường thực thi

- Python **3.11.15**; `pip install` chạy được (pypi nằm trong `noProxy`) — đã cài thử `beautifulsoup4` thành công.
- Ghi tệp vào repo: OK.
- `bs4` **không** có sẵn, phải cài.

---

## 6. KẾT LUẬN cho Routine giám sát chứng cứ

**THIẾU — và thiếu đúng một thứ then chốt: không đọc được văn bản guideline gốc.**

### Đủ để làm
Phát hiện bài mới (PubMed 2 870 hit, Amass 40M bản ghi), lọc theo ngày/chất lượng tạp chí,
đọc abstract đầy đủ, **kiểm retraction** (Scite `editorialNotices`, Amass `isRetracted`),
tra đăng ký thử nghiệm (ClinicalTrials 81 hit, có NCT), lấy **nguyên văn nhãn FDA/EMA**
(Amass RegulatoryCore), lần được PMID → PMCID để lấy toàn văn OA.

### Thiếu chính xác cái gì

1. **Không mở được tài liệu guideline gốc.** `kdigo.org`, `academic.oup.com`, `ncbi.nlm.nih.gov`
   đều bị chặn với cả WebFetch lẫn curl. Routine **không thể trích nguyên văn** khuyến cáo,
   số hiệu recommendation, hay mức 1A/2B từ tài liệu của hội chuyên ngành.
   WebSearch có trả về chuỗi "1A"/"2B", nhưng đó là **snippet tìm kiếm, không phải văn bản gốc**.
   Chiếu theo nguyên tắc làm việc đã đặt ra — *nêu nguồn chính và năm/phiên bản*, *không tự gán
   mức chứng cứ khi nguồn không cung cấp hoặc chưa kiểm chứng* — **Routine không được phép kết luận
   mức khuyến cáo dựa trên WebSearch**. Phải đánh dấu `[CẦN KIỂM CHỨNG]` và để bác sĩ mở tài liệu gốc.
   Guideline Bộ Y tế Việt Nam cũng nằm ngoài tầm với vì lý do này *và* vì WebSearch chỉ trả kết quả US.

2. **Elicit hỏng ở tầng tài khoản**, không phải tầng kỹ thuật. Routine nào gọi Elicit sẽ lỗi.

3. **Định danh công cụ không ổn định** — đã đổi tên **ngay trong phiên này** (UUID → tên thật).
   Prompt Routine **tuyệt đối không được ghi cứng** tên công cụ; phải mô tả theo chức năng và
   dùng `ToolSearch` (ví dụ `ToolSearch("pubmed search articles")`).

4. **Chưa đo được phiên Routine thật.** Phép đo này chạy trong phiên **có repo**. Phiên Routine
   không có nguồn nào. Chưa có bằng chứng nó nạp đủ 44 skill và cùng bộ connector.
   **[CẦN KIỂM CHỨNG]** — cách kiểm: cho Routine chạy đúng kịch bản này một lần, ghi ra tệp riêng
   để đối chiếu.

### Việc phải làm trước khi bật Routine
1. Viết prompt Routine **không ghi cứng tên connector**.
2. Buộc Routine **đánh dấu `[CẦN KIỂM CHỨNG]` cho mọi mức khuyến cáo (GRADE/1A/2B)** không lấy
   được từ tài liệu gốc — chỉ ghi mức khi trích được từ nguồn chính.
3. Không đưa Elicit vào chu trình cho tới khi nâng gói.
4. Chạy chính kịch bản đo này **từ trong một Routine** để xác nhận điểm 4 ở trên.
5. [CẦN XÁC NHẬN TẠI ĐƠN VỊ] Nếu cần đọc guideline gốc (KDIGO/ESC/ADA/Bộ Y tế), phải xin mở
   allowlist tên miền cho môi trường, hoặc bác sĩ tải tài liệu về repo để phiên đọc tại chỗ.

---

## Giới hạn của phép đo
- Đo trong **một loại phiên** (cloud + repo), trong **một cửa sổ 20 phút**. Không suy rộng cho
  phiên Routine, phiên tương tác trên máy, hay thời điểm khác — tên công cụ đã chứng minh là
  có thể đổi trong vòng vài phút.
- Chặn mạng đo trên **6 tên miền**; không phải toàn bộ danh sách chặn. Có thể còn tên miền khác mở.
- Chưa đo: hạn ngạch (rate limit) của từng connector, độ trễ, kích thước toàn văn PMC trả về,
  và chức năng của Scholar Gateway / ICD-10 / ChEMBL.
