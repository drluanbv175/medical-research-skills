# Định tuyến nguồn chứng cứ y khoa
### Evidence source routing — MCP trước, REST API sau

> Tài liệu chuẩn cho toàn bộ skill trong kho này khi cần lấy dữ liệu y văn.
> Đọc file này TRƯỚC khi viết bất kỳ lời gọi mạng nào.

---

## 1. Nguyên tắc cốt lõi

**Ưu tiên MCP connector. REST API chỉ là phương án dự phòng.**

Lý do không phải sở thích kỹ thuật mà là thực tế vận hành:

| | MCP connector | REST API gọi thẳng |
|---|---|---|
| Đường đi | Server-side, qua `mcp-proxy.anthropic.com` | Qua egress proxy của container |
| Bị chính sách egress chặn? | **Không** | **Có** — mặc định bị chặn trên Claude Code on the web |
| Cần cấu hình mạng? | Không | Có, phải allowlist từng host |
| Khoá API | Do connector quản lý | Người dùng tự lo |

Trong môi trường remote mặc định, **REST API tới NCBI/Crossref/openFDA đều thất bại**
với 403 ở bước CONNECT, trong khi **MCP connector vẫn chạy bình thường**.

---

## 2. Bảng định tuyến

Cột "MCP" là đường đi chính. Cột "REST dự phòng" chỉ dùng khi không có connector,
hoặc khi cần tham số mà connector không hỗ trợ.

### 2.1 Văn liệu (literature)

| Cần gì | MCP (ưu tiên) | REST dự phòng |
|---|---|---|
| Tìm bài theo chủ đề/PICO | `mcp__PubMed__search_articles` | `eutils.../esearch.fcgi` |
| Siêu dữ liệu theo PMID | `mcp__PubMed__get_article_metadata` | `eutils.../esummary.fcgi` |
| Toàn văn (PMC) | `mcp__PubMed__get_full_text_article` | `eutils.../efetch.fcgi` |
| Đổi PMID ↔ PMCID ↔ DOI | `mcp__PubMed__convert_article_ids` | PMC ID Converter |
| Bài liên quan | `mcp__PubMed__find_related_articles` | `elink.fcgi` |
| Tra bài từ chuỗi trích dẫn | `mcp__PubMed__lookup_article_by_citation` | — |
| Tìm ngữ nghĩa, ngoài PubMed | `mcp__Scholar_Gateway__semanticSearch` | `api.semanticscholar.org` |
| Tìm kèm kết luận rút gọn | `mcp__Consensus__search` | — |
| Hỗ trợ tổng quan hệ thống | `mcp__Elicit__search_papers`, `create_systematic_review` | — |
| Đồ thị trích dẫn | `mcp__Scholar_Gateway__semanticSearch` | `api.openalex.org` |
| Toàn văn mở ngoài PMC | — *(không có connector)* | Europe PMC, Unpaywall, CORE |

### 2.2 Thử nghiệm lâm sàng

| Cần gì | MCP (ưu tiên) | REST dự phòng |
|---|---|---|
| Tìm thử nghiệm | `mcp__Clinical_Trials__search_trials` | `clinicaltrials.gov/api/v2` |
| Chi tiết một NCT | `mcp__Clinical_Trials__get_trial_details` | idem |
| So sánh endpoint | `mcp__Clinical_Trials__analyze_endpoints` | idem |
| Theo nhà tài trợ | `mcp__Clinical_Trials__search_by_sponsor` | idem |
| Tìm nghiên cứu viên/điểm nghiên cứu | `mcp__Clinical_Trials__search_investigators` | idem |
| Khớp bệnh nhân với tiêu chí | `mcp__Clinical_Trials__search_by_eligibility` | idem |
| Thử nghiệm ngoài Hoa Kỳ | — *(không có connector)* | WHO ICTRP (chỉ cổng tra + tệp tuần) |

### 2.3 Thuốc và an toàn

> Điểm hay bị bỏ sót: connector **Scite** đã bao gồm mảng an toàn thuốc/thiết bị.

| Cần gì | MCP (ưu tiên) | REST dự phòng |
|---|---|---|
| Biến cố bất lợi (FAERS) | `mcp__Scite__search_faers` | `api.fda.gov/drug/event` |
| Sự cố thiết bị (MAUDE) | `mcp__Scite__search_maude` | `api.fda.gov/device/event` |
| Cảnh báo thuốc (Anh) | `mcp__Scite__search_mhra` | — |
| Thiết bị 510(k) | `mcp__Scite__search_device510k`, `search_510k_summaries` | `api.fda.gov/device/510k` |
| Thông tin thuốc | `mcp__Scite__search_drugs` | `api.fda.gov/drug/label`, DailyMed |

### 2.4 Liêm chính trích dẫn

| Cần gì | MCP (ưu tiên) | REST dự phòng |
|---|---|---|
| Bài đã bị rút / đính chính | `mcp__Scite__search_literature` → trường `editorialNotices` | `api.crossref.org/works/{DOI}` → `update-to` / `relation` |
| Ngữ cảnh trích dẫn (ủng hộ/phản bác) | `mcp__Scite__search_literature` | — |
| Xác minh DOI có thật | `mcp__Scite__search_literature` (theo `dois`) | `api.crossref.org/works/{DOI}` |

**Cảnh báo:** dữ liệu Retraction Watch đầy đủ chỉ có ở Crossref. Khi Crossref bị chặn,
`editorialNotices` của Scite là phương án tạm, **không tương đương**. Nếu cả hai đều
không dùng được, phải **ghi rõ là chưa kiểm tra được tình trạng rút bài**, không được
mặc định coi là sạch.

### 2.5 Tiền ấn phẩm & thuật ngữ

| Cần gì | MCP (ưu tiên) | REST dự phòng |
|---|---|---|
| Preprint sinh học/y học | `mcp__bioRxiv__search_preprints`, `get_preprint` | `api.biorxiv.org` |
| Preprint đã xuất bản chính thức | `mcp__bioRxiv__search_published_preprints` | idem |
| Mã ICD-10-CM / PCS | `mcp__ICD-10_Codes__search_codes`, `lookup_code` | — |

---

## 3. Không có đường MCP — chấp nhận giới hạn

Các nguồn sau **không có** connector, nên khi egress bị khoá thì không có cách nào
hợp lệ để lấy dữ liệu. Không đi vòng, chỉ báo rõ giới hạn:

- **Cochrane Library (CDSR)** — không có API công khai.
  Cách vòng hợp lệ duy nhất: lọc PubMed `"Cochrane Database Syst Rev"[jour]`.
- **Europe PMC**, **Unpaywall**, **CORE** — toàn văn mở.
- **UpToDate / DynaMed / BMJ Best Practice** — thương mại, ToS cấm truy cập tự động.
- **Embase / Scopus / Web of Science** — cần giấy phép cơ quan.
- **WHO ICTRP**, **PROSPERO** — không có REST API tiện dùng.
- **TRIP Database** — API chỉ cho bản trả phí.

---

## 4. Danh sách host cần allowlist

Khi cần chạy REST API trực tiếp, thêm các host sau vào network policy của môi trường
(claude.ai › Settings › Claude Code › Environments):

```
eutils.ncbi.nlm.nih.gov      PubMed E-utilities            ← quan trọng nhất
pubmed.ncbi.nlm.nih.gov      Giao diện web PubMed
www.ncbi.nlm.nih.gov         PMC, Gene, ClinVar, BLAST
clinicaltrials.gov           ClinicalTrials.gov API v2
api.crossref.org             Crossref + Retraction Watch
www.ebi.ac.uk                Europe PMC
api.fda.gov                  openFDA
api.openalex.org             OpenAlex
api.unpaywall.org            Unpaywall
api.biorxiv.org              bioRxiv / medRxiv
dailymed.nlm.nih.gov         DailyMed
api.semanticscholar.org      Semantic Scholar
```

Tài liệu môi trường: <https://code.claude.com/docs/en/claude-code-on-the-web>

---

## 5. Chẩn đoán khi gọi mạng thất bại

```bash
python3 scripts/check_evidence_sources.py          # bảng trạng thái toàn bộ nguồn
python3 scripts/check_evidence_sources.py pubmed   # kiểm một nguồn
python3 scripts/check_evidence_sources.py --json   # cho máy đọc
```

Mã thoát: `0` tất cả thông · `1` có nguồn bị chính sách chặn · `2` lỗi khác.

### Đọc lỗi

| Dấu hiệu | Nghĩa là | Xử lý |
|---|---|---|
| `Tunnel connection failed: 403` | Host không nằm trong allowlist | Nới network policy, hoặc chuyển sang MCP |
| `Tunnel connection failed: 407` | Proxy đòi xác thực | Cấu hình phía tổ chức |
| `certificate verify failed` | Công cụ không đọc CA bundle | Trỏ tới `/root/.ccr/ca-bundle.crt` |
| HTTP 429 | Bị giới hạn tần suất | Chờ, thêm khoá API NCBI |

> Proxy tự phân giải DNS, nên **tên miền gõ sai cũng trả về đúng lỗi 403**.
> Kiểm tra chính tả host trước khi kết luận là bị chặn.

### Ba điều tuyệt đối không làm

1. Không tắt xác thực TLS (`verify=False`, `-k`, `NODE_TLS_REJECT_UNAUTHORIZED=0`).
2. Không bỏ hoặc ghi đè `HTTPS_PROXY`.
3. Không đi vòng qua mirror/proxy trung gian để lách chính sách.

Đây là lớp bảo vệ do quản trị viên bật có chủ đích. Bị chặn thì **báo cáo**, không lách.

---

## 6. Nguyên tắc an toàn — phần quan trọng nhất

**"Không tra được nguồn" KHÁC "không có bằng chứng".**

Đây là chỗ dễ gây hại nhất trong một công cụ y khoa. Khi một script bắt
`except Exception` rồi trả về danh sách rỗng, mô hình đọc kết quả sẽ hiểu thành
"tìm rồi, không có gì" — và xu hướng tự nhiên là lấp chỗ trống bằng nội dung tự sinh.
Với y văn, việc lấp chỗ trống đó chính là **bịa trích dẫn**.

Quy tắc bắt buộc cho mọi skill trong kho này:

1. **Thất bại phải ồn ào.** Nguồn không truy cập được thì báo lỗi rõ ràng,
   không trả kết quả rỗng giả vờ như đã tra xong.
2. **Phân biệt ba trạng thái** trong mọi báo cáo:
   `đã xác minh` · `không xác minh được (nêu lý do)` · `xác minh thấy sai`.
3. **Không suy luận lâm sàng** từ dữ liệu chưa tra được.
4. **Không bịa PMID/DOI/số liệu** trong bất kỳ hoàn cảnh nào. Không tra ra thì nói
   thẳng là không tra ra.
5. Khi kiểm tra bài bị rút mà nguồn bị chặn, phải ghi
   **"chưa kiểm tra được tình trạng rút bài"**, không được ngầm hiểu là sạch.

### Dùng helper trong script

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts"))
import evidence_net as en

try:
    data = en.urlopen_json("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?...")
except en.SourceUnavailable as e:
    print(e.report(), file=sys.stderr)   # nêu rõ nguyên nhân + đường MCP thay thế
    if e.blocked_by_policy:
        sys.exit(3)                       # KHÔNG trả kết quả rỗng
    raise
```

---

## 7. Danh mục connector y khoa đang có

Đã kiểm tra hoạt động (2026-08-24):

| Connector | Vai trò |
|---|---|
| PubMed | Nền tảng văn liệu y sinh |
| Clinical Trials | ClinicalTrials.gov API v2 |
| Scite | Trích dẫn + FAERS/MAUDE/MHRA/510(k)/thuốc |
| Consensus | Tìm bài kèm kết luận |
| Elicit | Hỗ trợ tổng quan hệ thống |
| Scholar Gateway | Tìm ngữ nghĩa học thuật |
| bioRxiv | Preprint sinh/y học |
| ICD-10 Codes | Mã chẩn đoán & thủ thuật |
| BioRender | Hình khoa học |

**Nên bổ sung:** SNOMED CT Terminology (có trong thư mục connector, authless) —
ghép với ICD-10 thành bộ thuật ngữ lâm sàng đầy đủ.
