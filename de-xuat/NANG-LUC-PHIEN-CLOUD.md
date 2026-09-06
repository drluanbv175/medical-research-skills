# Năng lực phiên cloud — đo 2026-09-05 12:25 UTC

> Toàn bộ số liệu dưới đây là kết quả chạy lệnh thật trong chính phiên này, không suy đoán.
> Phạm vi hiệu lực: PHIÊN CLOUD CÓ NGUỒN REPO ĐÍNH KÈM. Xem mục "Giới hạn của phép đo".

- **Phiên này**: có nguồn repo đính kèm (`drluanbv175/medical-research-skills`, nhánh `claude/do-nang-luc-phien-cloud`) — khác Routine ở chỗ Routine sinh phiên mới không có nguồn nào.

- **Skill đồng bộ từ tài khoản**: **44 SKILL.md**
  - 43 skill tại `/root/.claude/skills/synced/663e40d7-aa1d-4124-9a79-2c3563badb4c_1f8efc2f-396b-4507-8f3f-05e10bf3c606/`
  - 1 skill hệ thống tại `/root/.claude/skills/session-start-hook/`
  - Skill đồng bộ được nạp thật vào danh sách khả dụng của phiên (không chỉ nằm trên đĩa).

- **`cap-nhat-chung-cu-y-khoa`**: **CÓ**
  - Đường dẫn: `/root/.claude/skills/synced/663e40d7-aa1d-4124-9a79-2c3563badb4c_1f8efc2f-396b-4507-8f3f-05e10bf3c606/cap-nhat-chung-cu-y-khoa/SKILL.md`
  - Có mặt trong danh sách skill gọi được bằng công cụ `Skill`.

- **Skill EBM tiếng Việt thấy được** (trong danh sách khả dụng của phiên, 10 tên):
  1. `cap-nhat-chung-cu-y-khoa`
  2. `quan-ly-cap-nhat-ebm`
  3. `tham-dinh-chung-cu-grade-nnt`
  4. `kham-ngoai-tru-ebm`
  5. `nghien-cuu-ebm-tong-hop`
  6. `dashboard-master-ebm-ngoai-tru`
  7. `antifacts`
  8. `clinical-evidence-rag`
  9. `nghien-cuu-y-khoa-chuan-quoc-te`
  10. `ebm-master`
  (Ngoài ra còn: `literature-review`, `paper-lookup`, `research-lookup`, `citation-management`, `peer-review`, `scientific-writing`, `statistical-analysis`, `ke-don-an-toan-benh-man`, `tiep-can-chan-doan-co-do-chuyen-tuyen`, `nguoi-cao-tuoi-da-benh-da-thuoc`, `tuan-thu-dieu-tri`, `giao-tiep-quyet-dinh-soap`, `dao-tao-slide-tai-lieu-y-khoa`, `ehospital-mini`, `dark-analyst`.)

- **WebSearch: CÓ** · **WebFetch: CÓ**
  - Cả hai là công cụ hoãn nạp (deferred): phải gọi `ToolSearch` với `select:WebSearch,WebFetch` trước khi dùng. Đã nạp schema thành công trong phiên này để xác nhận, chứ không chỉ đọc danh sách tên.
  - WebSearch ghi rõ giới hạn: **chỉ kết quả US**.

- **Công cụ connector**:
  - **KHÔNG có tên nào đúng dạng `mcp__PubMed__*`, `mcp__Amass_Connector__*`, `mcp__Consensus__*`, `mcp__Clinical_Trials__*`.** Trong môi trường này mọi MCP server được đặt tên bằng **UUID**, không phải tên hãng.
  - Các server tra cứu y văn/thử nghiệm **thật sự có** (tên chính xác như trong danh sách công cụ):

    | Prefix công cụ (chính xác) | Nội dung — căn cứ | Trạng thái |
    |---|---|---|
    | `mcp__290a5fde-2a63-41d1-b1d0-733b6cd943be__*` | **PubMed** (`search_articles`, `get_full_text_article`, `find_related_articles`, `convert_article_ids`, `lookup_article_by_citation`, `get_article_metadata`, `get_copyright_status`) — mô tả công cụ ghi rõ "Search PubMed" | Đã nạp schema, sẵn dùng |
    | `mcp__22dee40c-8c1f-43b6-8258-fc81d367cf2d__*` | **ClinicalTrials.gov API v2** (`search_trials`, `get_trial_details`, `analyze_endpoints`, `search_by_eligibility`, `search_by_sponsor`, `search_investigators`) — hướng dẫn server ghi rõ | Sẵn dùng |
    | `mcp__7ab88be3-4cca-4ee9-a484-d48b8a924bb3__*` | **Amass** (BiomedCore 40M+ bài, TrialCore 1.2M+ thử nghiệm, DrugCore, GeneCore, RegulatoryCore FDA+EMA, PatentCore) — tên công cụ chứa `amass` | Sẵn dùng |
    | `mcp__5346c7ae-d7d4-4878-946f-5ebe7aea0bfd__*` | **Elicit** (`search_papers`, `search_trials`, `create_systematic_review`, `create_report`) — mô tả ghi "Elicit's academic paper corpus" | Đã nạp schema, sẵn dùng |
    | `mcp__7e5ade36-f545-464d-bf7a-bfd8ebcbacc0__*` | **scite** (`search_literature`, `read_fulltext`, `citation_graph`, `bibliography`, cảnh báo retraction qua `editorialNotices`) — hướng dẫn server ghi rõ | Sẵn dùng |
    | `mcp__20bc00dd-8dac-4995-a37a-7b0b5fcb3897__search` | Tìm 220 triệu bài (Semantic Scholar + PubMed + Scopus + arXiv), có `medical_mode`, lọc `study_types` RCT/SR/MA, quartile SJR | Đã nạp schema, sẵn dùng. Tên hãng không được server công bố — **[CẦN KIỂM CHỨNG]** nếu muốn gọi đích danh "Consensus" |
    | `mcp__eb6674e9-2c4e-454f-a7ff-554b1da37f32__*` | **bioRxiv / medRxiv** preprint | Sẵn dùng |
    | `mcp__185aad4c-f557-46bc-8e66-7d5656dbd885__semanticSearch` | Tìm ngữ nghĩa (không rõ nguồn) | **[CẦN KIỂM CHỨNG]** |
    | `mcp__bb740761-1dc3-44f5-a43c-4e9429d9ddc0__*` | ICD-10-CM/PCS FY2026 | Sẵn dùng |
    | `mcp__3ad0de59-bdd9-473c-8da5-2f9cbcf20de2__*` | ChEMBL v34 (dược chất, cơ chế, ADMET) | Sẵn dùng |

  - **3 MCP server đang CHỜ XÁC THỰC**, chưa dùng được và **không thể** xác thực trong phiên không tương tác:
    `2e366b39-cf09-4ff5-917a-659de628ef5f`, `a55ba7b7-4ecb-4a17-801c-e4889bf98d51`, `c9f0f68f-fd28-41db-ad40-0b6ea93da618`.
    Muốn dùng phải cấp quyền ở cài đặt connector claude.ai hoặc `/mcp` trong phiên tương tác. **[CẦN XÁC NHẬN TẠI ĐƠN VỊ]** — chưa xác định được đây có phải connector y khoa hay không.

## KẾT LUẬN cho Routine giám sát chứng cứ

**ĐỦ về năng lực kỹ thuật, nhưng THIẾU về tính ổn định định danh công cụ và chưa chứng minh cho phiên Routine.**

Cụ thể:

1. **Đủ**: có `cap-nhat-chung-cu-y-khoa` + 9 skill EBM tiếng Việt khác; có WebSearch + WebFetch; có PubMed, ClinicalTrials.gov, Amass, Elicit, scite, bioRxiv/medRxiv. Đây là đủ hạ tầng để chạy một chu trình giám sát chứng cứ có trích dẫn kiểm chứng được.

2. **Thiếu — định danh công cụ không ổn định**: mọi connector mang tên UUID, **không** phải `mcp__PubMed__*`. Bất kỳ prompt Routine nào ghi cứng tên dạng `mcp__PubMed__*` sẽ **gọi hụt công cụ**. Routine phải mô tả công cụ theo *chức năng* và dùng `ToolSearch` (ví dụ `ToolSearch("pubmed search articles")`) thay vì ghi cứng tên. **[CẦN KIỂM CHỨNG]**: UUID có giữ nguyên giữa các phiên hay không — chưa đo được trong một phiên đơn lẻ.

3. **Thiếu — chưa đo được phiên Routine thật**: phép đo này thực hiện trong phiên **có nguồn repo**. Phiên do Routine sinh ra không có nguồn nào. Chưa có bằng chứng phiên Routine cũng nạp đủ 44 skill đồng bộ và cùng bộ connector. **[CẦN KIỂM CHỨNG]** — cách kiểm: cho Routine chạy đúng kịch bản đo này một lần và ghi kết quả ra tệp riêng để đối chiếu.

4. **Thiếu — WebSearch chỉ trả kết quả US**: guideline của hội chuyên ngành châu Âu/khu vực và tài liệu Bộ Y tế Việt Nam có thể không xuất hiện. Bù bằng WebFetch trực tiếp vào URL nguồn chính thức đã biết.

5. **Thiếu — 3 connector chưa xác thực**: không thể mở khoá tự động; phiên Routine sẽ gặp đúng rào cản này.

### Giới hạn của phép đo
- Đo tại **một thời điểm**, trong **một loại phiên** (cloud + repo). Không suy rộng cho phiên Routine, phiên tương tác trên máy, hay thời điểm khác.
- Chỉ xác nhận công cụ **tồn tại và nạp được schema**; **chưa** chạy truy vấn thật để đo hạn ngạch, độ trễ hay quyền truy cập nội dung toàn văn.
