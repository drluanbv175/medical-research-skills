# Changelog

## 2026-09-08 (d) — GHI VẾT TRA CỨU · COI/tài trợ · ngày rà lại kế tiếp — **MẪU LÊN 1.1**

Mâu thuẫn nội bộ còn lại: skill `literature-review` buộc *"ghi ngày tra + CSDL"*, còn skill
này — skill **trực tiếp đổi thực hành lâm sàng** — thì không. Hậu quả cụ thể ở bản sa sút trí
tuệ 08/9: không ai, kể cả người viết, tái lập được là đã tra gì; và không có mốc nào nói khi nào
phải rà lại. Một bản cập nhật không ghi vết là **ảnh chụp một lần**, không phải tài sản có vòng đời.

### Đổi mẫu CÓ CHỦ Ý — vì sao phải lên phiên bản

`templates/mau-cap-nhat-chuyen-sau.md` thêm khối **GHI VẾT TRA CỨU** (5 dòng, đặt ngay dưới tiêu
đề) và khung bảng **COI/tài trợ** trong mục 10. **Số mục vẫn là 11, thứ tự không đổi** — nên mọi
bản cập nhật cũ vẫn hợp lệ về cấu trúc mục. Mẫu đã khoá lại:
`kiem_mau_cap_nhat.py --khoa-lai --phien-ban 1.1`.

### Cổng nào chặn cái gì

- `tools/kiem_mau_cap_nhat.py` — thêm **phần C**: danh sách trường ghi vết **đọc thẳng từ bảng
  trong mẫu** (mẫu là nguồn chân lý duy nhất; sửa mẫu → danh sách tự đổi sau khi `--khoa-lai`).
  Lỗi cứng khi: thiếu dòng · để trống · **còn nguyên chỗ trống của mẫu** · trường "Ngày …" không
  có ngày thật. Cảnh báo khi còn dấu `[CẦN …]` — chấp nhận được nhưng phải thấy rõ.
- `tools/verify_dashboard.py` — `DATA.meta` thiếu `searchDate` / `searchSources` / `searchStrategy`
  / `nextReview` là **lỗi cứng**. `retractionCheck` thiếu → cảnh báo. Item không có `funding`
  → cảnh báo (thường không lấy được bằng máy).
- Cả hai mẫu dashboard (Evidence Workbench **và** Dark Analyst) hiển thị dải **Ghi vết tra cứu**
  gập/mở ở chân trang; trường bỏ trống in đỏ `CHƯA GHI — bắt buộc`, không im lặng.

### Một phép đo, để lần sau khỏi mất công thử lại

Câu **tài trợ** chỉ lấy được bằng máy khi tạp chí đặt nó **trong tóm tắt** (*Lancet*: đoạn
FUNDING cuối; *NEJM*: "(Funded by …)"). `mcp__PubMed__get_article_metadata` **không có** trường
funding/COI; **Amass BiomedCore cũng không**. Trên 17 nguồn của bản sa sút trí tuệ: lấy được
**3/17** (evoke/evoke+ → "Novo Nordisk."; CLARITY-AD → "Funded by Eisai and Biogen"; ACHIEVE →
"US National Institutes of Health."). 14 nguồn còn lại phải mở toàn văn trên máy có mạng —
đã ghi rõ là **CHƯA LẤY ĐƯỢC**, không để trống và không suy đoán.

### Quy tắc COI được viết thành luật trong SKILL.md (5D-quater)

Ghi nguyên văn hoặc ghi "nguồn không cung cấp" — **suy đoán tài trợ là bịa dữ liệu**. Tài trợ
công nghiệp **không** tự động hạ mức chứng cứ; phải nêu **chiều** thiên lệch có thể có (evoke là
ví dụ ngược chiều: nhà sản xuất tài trợ, kết quả âm tính với chính sản phẩm của họ).

### Lỗi bắt được ngay trong lần chạy này: `make_derivatives.py` xoá công rà tay

Chạy lại dây chuyền sau khi sửa mẫu thì `make_derivatives.py` **ghi đè** tờ dặn người bệnh và
kịch bản TikTok **đã được rà ngôn ngữ phổ thông** bằng bản nháp máy — im lặng, không hỏi.
Đã khôi phục, và bịt: bản tự sinh luôn mang dấu `BẢN NHÁP TỰ ĐỘNG`; tệp đã có mà **không còn
dấu đó** nghĩa là người đã sửa → công cụ **giữ nguyên** và in `⊘ GIỮ NGUYÊN (đã rà tay)`.
Muốn dựng lại từ đầu phải nói rõ bằng `--ghi-de`.

### Ngày rà lại kế tiếp — có bảng chọn mốc, không tuỳ tiện

3 tháng (cảnh báo an toàn đang mở) · theo lịch guideline nếu nguồn đã công bố · 6 tháng (RCT lớn
sắp đọc kết quả, hoặc lĩnh vực vừa có guideline đầu tiên) · 12 tháng (chủ đề ổn định). **Bắt buộc
kèm lý do** và danh sách **sự kiện buộc rà sớm**. Bản sa sút trí tuệ: **2027-03-08**, 6 tháng.

## 2026-09-08 (c) — Kiểm bài RÚT vào dây chuyền bắt buộc

Lỗ hổng nặng nhất còn lại: một bài **đã bị rút** có thể làm nền cho khuyến cáo đổi thực hành
mà không gì chặn. Skill `citation-management` đã bắt buộc kiểm; skill này thì không — nghịch
lý, vì đây mới là skill trực tiếp đổi thực hành lâm sàng.

Hạ tầng đã có sẵn trong repo (`scripts/retraction_check.py`, thiết kế đúng cho môi trường bị
chặn egress: đi qua connector Scite thay vì Crossref). Thiếu là **phần nối vào dây chuyền**.
Nay: dây chuyền 9 bước, kiểm bài rút là bước 5, ngay sau cổng liêm chính. Mục mới 5D-ter.

### Hai lỗi thật của công cụ, phát hiện khi chạy lần đầu

1. **Không đọc được thứ nó thực sự nhận.** `report` mong JSON thô của Scite, nhưng agent gọi
   qua MCP thì kết quả về dạng phong bì `[{"type":"text","text":"..."}]` → vỡ ngay
   (`AttributeError: 'list' object has no attribute 'get'`). Nay `unwrap_scite()` gỡ được cả
   ba dạng: JSON thô, phong bì MCP (bao nhiêu lớp cũng gỡ), và mảng hit trần.

2. **Regex DOI nuốt dấu nháy đóng.** Rút từ dashboard cho ra `10.1002/alz.14333'` vì trong khối
   `DATA` viết là `doi:'…'`. DOI hỏng thì Scite tra không ra ⇒ bị xếp `CHƯA KIỂM`, che mất việc
   thực chất là chưa kiểm được gì.
   Bản vá đầu **hỏng hơn**: loại luôn `)` nên cắt cụt DOI Elsevier hợp lệ
   (`10.1016/S0140-6736(24)01296-0` → `10.1016/s0140-6736(24`). Nay chỉ loại dấu nháy, còn
   ngoặc thì **đếm cân bằng** rồi mới cắt phần thừa.
   Bài học ghi lại: phép đối chiếu HTML ↔ .md vẫn báo "trùng khớp" trong khi **cả hai cùng sai
   giống nhau** — hai sản phẩm dẫn xuất khớp nhau KHÔNG chứng minh cái nào đúng. Phải đối chiếu
   với dữ liệu thật (ở đây là bộ DOI đã gọi Scite và có kết quả trả về).

### Kết quả trên bản cập nhật sa sút trí tuệ
17/17 DOI: không bài nào bị rút, đính chính hay nêu quan ngại. Ghi vào mục 10.4 của bản cập
nhật, kèm giới hạn: chỉ mục Scite không phủ 100%, nên "không thấy thông báo" chưa phải bằng
chứng tuyệt đối.


## 2026-09-08 (b) — Khoá mẫu cập nhật + đưa bản cập nhật văn bản vào dây chuyền bắt buộc

Hai vấn đề hệ thống, không phải lỗi lẻ.

### Bản cập nhật văn bản trước đây KHÔNG nằm trong dây chuyền
Dây chuyền tự động ở mục 5D chỉ có: dựng Dashboard → cổng → thư viện → phái sinh.
Không bước nào sinh ra `CapNhat_EBM_*.md`. Hậu quả thật: lần chạy đầu cho ca sa sút trí
tuệ chỉ giao Web Dashboard, bác sĩ phải hỏi mới có bản cập nhật văn bản.
Nay dây chuyền có 8 bước, **bước 1 là viết bản cập nhật theo mẫu 11 mục**, và bước 8 là
dựng trang đọc được — vì `.md`/`.html` gửi kèm thường không mở được trong khung chát.

### Mẫu cập nhật nay được KHOÁ
`templates/mau-cap-nhat-chuyen-sau.md` khoá bằng SHA-256 trong
`data/mau_cap_nhat.lock.json` (phiên bản 1.0, 11 mục, khoá 2026-09-08).
Công cụ mới `tools/kiem_mau_cap_nhat.py`:
- kiểm **mẫu** có bị đổi lén không (so SHA-256);
- kiểm **bản cập nhật** có đủ 11 mục, đúng thứ tự không;
- đổi mẫu phải CÓ CHỦ Ý: `--khoa-lai --phien-ban <mới>` kèm ghi CHANGELOG.
Đổi chữ tiêu đề mục = cảnh báo (chấp nhận). Đổi số mục hoặc thứ tự = lỗi cứng, chặn giao.
Quy tắc kèm theo: chủ đề không có nội dung cho một mục thì ghi "không áp dụng" hoặc
`[CẦN BỔ SUNG]` — **không xoá mục**.

### Kèm theo
- `tools/render_ban_cap_nhat.py` + `templates/trang-doc-ban-cap-nhat.css`: dựng bản cập
  nhật thành trang đọc/in được. Bảng xuống dòng cho vừa khung (đo được 9/9 bảng vừa,
  kể cả bảng 7 cột); chuỗi font tránh Times New Roman và thêm Be Vietnam Pro vì
  **Poppins không có bộ ký tự tiếng Việt**.
- `quality/acceptance-checklist.md`: thêm 9 mục kiểm, mỗi mục tương ứng một lỗi ĐÃ XẢY RA.
- Công cụ đồng bộ ở repo có thêm phép kiểm [5]: mẫu còn khớp khoá không.


## 2026-09-08 — Sửa 3 lỗi liêm chính + đồng bộ tài liệu với code

Phát hiện khi dùng skill cho ca sa sút trí tuệ. Cả ba đều ảnh hưởng đến độ tin cậy
của đầu ra, không phải lỗi hình thức.

### 1. Cổng liêm chính nay FAIL CLOSED (`tools/verify_dashboard.py`)
Trước: `--online` mà mạng chặn PubMed → chỉ ghi cảnh báo, vẫn in **PASS**. Một PMID
bịa sẽ lọt cổng ở mọi môi trường không có mạng.
Nay: trả `⊘ KHÔNG KẾT LUẬN` (mã thoát 2). Muốn giao phải nêu rõ bằng `--offline-ok`,
khi đó in `PASS CÓ ĐIỀU KIỆN` kèm dòng GHI VẾT. Lỗi cứng thật vẫn được ưu tiên báo
trước (FAIL, mã 1). Chạy không `--online` nay có cảnh báo "mới kiểm cấu trúc".

### 2. Mẫu MẶC ĐỊNH đã cài đặt `effectText` và `rob`
Trước: SKILL.md ghi "cả hai mẫu hỗ trợ", nhưng `web-dashboard-evidence-workbench.html`
KHÔNG cài đặt field nào trong hai field đó — chỉ `dark-analyst` có. Hậu quả: hiệu số
phi-tỷ-số (chênh lệch trung bình, %, SMD) không có chỗ chứa có cấu trúc, phải viết
lẫn vào văn xuôi.
Nay: mẫu mặc định hiển thị `effectText` ở bảng và ở panel thẩm định (kèm ghi chú vì
sao không vẽ forest cho hiệu số phi-tỷ-số), và có khối RoB 2 cho `rob`.
Khối RoB 2 được gắn nhãn **"đánh giá vận hành"** — đây là chấm của người tổng hợp,
KHÔNG phải phân hạng của nguồn; để trống vẫn tốt hơn là đoán.

### 3. Phái sinh không còn tự gán nhãn GRADE (`tools/make_derivatives.py`)
Trước: dàn ý slide in `gradeLevel` thành "*GRADE Cao*" kể cả với RCT và guideline mà
nguồn KHÔNG hề cung cấp GRADE — trái đúng quy tắc liêm chính của chính skill, và sai
lệch đi thẳng vào bài giảng.
Nay: in nguyên văn `gradeSource`; thêm `rob` khi có.
Sửa kèm: bộ đọc chuỗi JS trước đây dùng `['\"]` ở cả hai đầu nên một dấu `"` bên
trong chuỗi nháy đơn làm cắt nhầm mảng (đã gây một gạch đầu dòng cụt trong tờ dặn
người bệnh). Nay tôn trọng dấu mở và bỏ qua ngoặc nằm trong chuỗi.

### Đồng bộ tài liệu
`SKILL.md` cập nhật ở mục 5D và ô checklist để mô tả đúng hành vi mới của cổng và
của phái sinh. Kèm công cụ mới ở repo: `tools/kiem_dong_bo_skill_ebm.py` — bắt trôi
lệch giữa bundle tài khoản, bản sao lưu git và bản chạy tại chỗ; bắt "tài liệu hứa
mà code không có"; bắt hai skill trùng mô tả kích hoạt.


## v1.12.0 — 2026-06-10

- **Sửa mất cân đối bố cục dọc** (bác sĩ báo: dashboard hiện tại vẫn chưa cân đối). Nguyên nhân thật: khối **GRADE Evidence-to-Decision là băng LUÔN hiển thị, rất cao ở đầu trang** → ép bảng chứng cứ (nội dung chính) thành dải mỏng ở đáy. (grep markers PASS nhưng mắt thấy lệch → đã kiểm chứng bằng ảnh chụp thực tế.)
  - *Evidence Workbench:* chuyển GRADE EtD từ băng đầu trang → **một TAB "⚖ GRADE EtD"** ở khu giữa (chỉ hiện khi có `etd`). Bảng giờ chiếm phần lớn màn hình. Thêm trần chiều cao thẻ tóm tắt (`max-height:188px;overflow:auto`) chống dữ liệu dài làm phình băng Quick View.
  - *Dark Analyst:* bọc GRADE EtD trong `<details>` **thu gọn mặc định** (bấm để mở) → còn 1 dòng thay vì băng to.
- Đồng bộ 2 template (EW+DA) qua 4 bản skill; **ghép lại 11 dashboard đã xuất** trong `EBM-Dashboards/` (giữ nguyên `DATA`); dựng lại 2 zip.
- Verify trực quan (1440×900): bảng chứng cứ là khu vực chính, EtD truy cập qua tab/details. Mặc định vẫn **Evidence Workbench**.

## v1.11.0 — 2026-06-09

- **Bố cục Dashboard responsive (cân đối mọi bề ngang)** — khắc phục "phần dưới hẹp, khó xem" trên màn ~1000px.
  - *Evidence Workbench:* lưới `clamp()`+`minmax(0,1fr)` (cột giữa `min-width:0`); ≤1199px panel thẩm định thành **ngăn kéo (drawer)** trượt từ phải (nền mờ + nút ✕) → bảng dùng trọn bề ngang; ≤820px bộ lọc thành dải ngang + ẩn cột Forest; ≤540px dồn 1–2 cột. Thêm `select`→`openDrawer`/`closeDetail`.
  - *Dark Analyst:* KPI/EtD/Quick-View tự giãn cột theo breakpoint; ≤860px chi tiết bung DỌC (`exp-in` 1 cột).
- Đồng bộ CẢ HAI template (EW + DA) qua 4 bản: `sync/skills/{cap-nhat,dark-analyst}` + bản live; dựng lại zip.
- Đã ghép layout mới cho các dashboard EW đã xuất trong `EBM-Dashboards/` (giữ nguyên khối `DATA`).
- Mặc định vẫn là **Evidence Workbench**. Verify trực quan ở 1000/1280/1440px PASS.

## v1.10.0 — 2026-06-07

- **Đổi mẫu MẶC ĐỊNH về "Evidence Workbench"** (nền sáng) theo lựa chọn của bác sĩ; **Dark Analyst** (nền tối) chỉ dùng KHI bác sĩ yêu cầu.
- **Thêm khối GRADE Evidence-to-Decision (EtD) vào template Evidence Workbench** (light theme) — nay CẢ HAI mẫu đều có EtD (field `etd`); tách rõ hàng chứng cứ-từ-nguồn vs đánh giá-vận-hành. JS cân bằng, gate PASS.
- **TỰ ĐỘNG khi gọi skill:** mỗi lần skill được gọi → tự chạy trọn dây chuyền (dựng Dashboard EW → cổng liêm chính `--online` → an toàn thuốc nếu liên quan → thư viện → 3 phái sinh), không cần yêu cầu từng bước. Ghi trong SKILL.md 5A + CLAUDE.md.
- Cập nhật checklist, danh mục tài nguyên, DESIGN-SPEC; đồng bộ template (mockup + skill).

## v1.9.0 — 2026-06-07

- **Sản phẩm phái sinh TỰ ĐỘNG mỗi lần chạy:** `tools/make_derivatives.py` sinh tờ dặn người bệnh + dàn ý slide (faithful, giữ PMID/GRADE) + kịch bản TikTok vào `EBM-Dashboards/derivatives/`. Video TikTok thật để bác sĩ gọi skill `tao-video-tiktok` khi cần. (Đã test trên ca thần kinh ĐTĐ.)
- **GRADE Evidence-to-Decision (EtD) trong Dashboard Dark Analyst:** thêm field tùy chọn `etd` (vấn đề · lợi ích · tác hại · độ chắc chắn · giá trị · cân bằng · nguồn lực · công bằng · chấp nhận · khả thi → khuyến cáo + độ mạnh). Tách rõ **hàng chứng cứ (từ nguồn) vs hàng đánh giá vận hành**; tương thích ngược (không có `etd` thì không hiển thị). Đã thêm CSS + render + ví dụ thật; JS cân bằng; gate vẫn PASS.
- Cập nhật SKILL.md (5D), checklist, tài nguyên; đồng bộ template (mockup + skill + standalone).

## v1.8.0 — 2026-06-07

- **Mục 5E + 3 nâng cấp** (theo yêu cầu bác sĩ):
  - **#5 Lớp phủ an toàn thuốc:** `tools/drug_safety_scan.py` + `data/drug_flags.json` (cờ Beers 2023/STOPP-START v3 cô đọng, có nguồn, KHÔNG đầy đủ) → quét thuốc trong dashboard, sinh prompt rà soát đầy đủ bằng skill `nguoi-cao-tuoi-da-benh-da-thuoc`. Ref 09. (Đã test: bắt amitriptyline/gabapentin/opioid.)
  - **#6 Giám sát định kỳ (Track B):** `tools/surveillance_scan.py` + `EBM-Dashboards/watchlist.json` → quét PubMed tìm guideline/SR/meta/RCT mới theo chủ đề lõi, báo cáo ứng viên để thẩm định. Ref 10. (Đã test: trả về chứng cứ 2026 thật.)
  - **#7 Bản địa hóa BYT:** `EBM-Dashboards/vn-guidelines/registry.json` + README → đối chiếu quốc tế ↔ hướng dẫn Bộ Y tế (do bác sĩ cung cấp, không bịa số QĐ), nối `clinical-evidence-rag`. Ref 11.
- Cập nhật checklist (lớp phủ an toàn thuốc) và danh mục tài nguyên.

## v1.7.1 — 2026-06-07

- **Thư mục chung tích lũy `EBM-Dashboards/`** (mục 5D-d + CLAUDE.md): mọi dashboard xuất vào một thư mục duy nhất trong OneDrive (tự đồng bộ Mac↔Windows), kèm `evidence-library.html` + `library.json` + bản sao `tools/` + `README.md`. Quy trình mỗi cập nhật: lưu vào thư mục → `verify_dashboard.py --online` PASS → `build_library.py add` để tích lũy vào chỉ mục.

## v1.7.0 — 2026-06-07

- **Thêm mục 5D + bộ công cụ `tools/`** (3 nâng cấp workflow theo yêu cầu bác sĩ):
  - **Cổng kiểm liêm chính** `tools/verify_dashboard.py`: kiểm mọi item có PMID/DOI, `gradeLevel`/`decision` hợp lệ, có disclaimer, quét PII; `--online` **tự xác minh mỗi PMID phân giải đúng trên PubMed** (chống trích dẫn ảo). Đã test: PASS/FAIL/âm tính + online xác minh thật.
  - **Thư viện cập nhật** `tools/build_library.py`: gom mọi dashboard vào `library.json` + sinh `evidence-library.html` (chỉ mục có tìm/lọc, mở thẳng từng bản).
  - **Sản phẩm phái sinh**: `references/08-xuat-san-pham-phai-sinh.md` + mẫu `templates/phai-sinh-to-dan-nguoi-benh.md`, `templates/phai-sinh-kich-ban-tiktok.md` (tờ dặn người bệnh / slide / TikTok — giữ liêm chính, không liều cho người bệnh/TikTok, có disclaimer, không PII).
- Cập nhật checklist (chạy cổng liêm chính trước khi giao) và danh mục tài nguyên.

## v1.6.0 — 2026-06-07

- **Đổi mẫu Web Dashboard MẶC ĐỊNH sang "Dark Analyst"** (nền tối, dày dữ liệu) theo lựa chọn của bác sĩ; Evidence Workbench (nền sáng) trở thành mẫu THAY THẾ.
- **Sản phẩm hóa Dark Analyst thành template tham số hóa** `templates/web-dashboard-dark-analyst.html`: chrome (tiêu đề, PICO chips, KPI, băng Clinical Quick View, verdict, bộ lọc, ô tìm) **tự sinh từ `DATA`**; bảng có cột Quyết định; click bung 3 cột thẩm định; hỗ trợ mọi loại thiết kế & mức GRADE.
- **Hai mẫu DÙNG CHUNG một schema `DATA`** (meta/summary/items[]) → một khối dữ liệu chạy được cả hai. Dark Analyst thêm field tùy chọn `effectText` (hiệu số phi-tỷ-số) và `rob` (RoB 2, chỉ RCT); giữ `frame`/`frameLabels`.
- Cập nhật SKILL.md (mục 5A, checklist, danh mục tài nguyên), `CLAUDE.md`, `DESIGN-SPEC.md` và đóng gói lại.

## v1.5.0 — 2026-06-07

- **Thêm mục 5C "Tự chọn khung câu hỏi"**: skill tự nhận diện loại câu hỏi lâm sàng và chọn khung phù hợp — ngoài **PICO(T)(S)** còn **PECO** (tác hại), **PIRT/QUADAS-2** (chẩn đoán), **PROGRESS/PICOTS** (tiên lượng), **CoCoPop** (tần suất), **SPIDER** (định tính), **ECLIPSE** (dịch vụ), PICO+chi phí (kinh tế).
- Bổ sung **mô hình tổng hợp bổ trợ**: phân tầng nguồn 6S, cân lợi ích–tác hại NNT/NNH, GRADE Evidence-to-Decision (EtD), bảng Tóm tắt phát hiện (SoF), tam giác liêm chính.
- Thêm tài liệu `references/07-mo-hinh-cau-hoi-va-khung-thay-the.md` (bảng chọn khung + cách ánh xạ vào Evidence Workbench + ví dụ).
- **Nâng template Evidence Workbench** (tương thích ngược): hỗ trợ field tùy chọn `frame` (nhãn khung) và `frameLabels` để đổi tên 4 ô P/I/C/O cho khung không phải PICO; không đặt thì hiển thị như cũ.
- Cập nhật checklist (nhận diện & nêu rõ khung đã dùng) và danh mục tài nguyên.

## v1.4.0 — 2026-06-07

- **Đổi mô hình Web Dashboard mặc định sang "Evidence Workbench"** (bố cục 3 cột: bộ lọc · Quick View + bảng điểm chứng cứ · panel thẩm định) theo lựa chọn của bác sĩ.
- Thêm template mặc định `templates/web-dashboard-evidence-workbench.html` (chỉ cần thay khối `DATA`); giữ template một-cột cũ làm fallback.
- Ba lớp nội dung bắt buộc giữ nguyên, ánh xạ vào bố cục: Clinical Quick View = băng tóm tắt + tab mặc định; Evidence Detail View = cột phải; Safety/Limits/VN = các tab riêng.
- Cập nhật bảng màu mặc định (nền sáng, dày dữ liệu) + màu ngữ nghĩa theo Quyết định/GRADE/Thiết kế; bổ sung forest plot mini và xuất CSV/JSON.
- Cập nhật mục 5A, frontmatter, checklist, danh mục tài nguyên, `references/05-…md` và `quality/web-dashboard-acceptance-checklist.md`.

## v1.3.0 — 2026-06-06

- Bổ sung **chế độ PICO**: chuẩn hóa trình bày chứng cứ theo P–I–C–O cho câu hỏi về hiệu quả/an toàn của can thiệp, kèm khối PICO 5 dòng (PICO + chứng cứ tốt nhất + grading từ nguồn + kết luận).
- Thêm mục 5B trong SKILL.md và tài liệu `references/06-pico-va-trich-dan.md` với mẫu, ví dụ và quy tắc liêm chính (trích hiệu số đúng nguồn, không tự gán GRADE, nêu cả hai chiều khi chứng cứ không đồng nhất).
- Thêm **quy tắc ghi nguồn sạch**: ghi nguồn dạng văn bản (tác giả/tổ chức + năm + tạp chí) và Vancouver/NLM; tuyệt đối không chèn thẻ markup trích dẫn thô/mã kỹ thuật vào câu trả lời; bắt buộc rà soát trước khi gửi.
- Bổ sung mục checklist tương ứng và cập nhật danh mục tài nguyên.

## v1.2.0 — 2026-06-02

- Bắt buộc tạo Web Dashboard HTML độc lập cho mỗi cập nhật EBM theo vấn đề cụ thể khi môi trường hỗ trợ tạo file.
- Áp dụng kiến trúc 3 lớp: Clinical Quick View mặc định, Evidence Detail View, Safety/Limits/Vietnam.
- Thêm schema record `ITEM-xx` cục bộ; không đồng nghĩa với ID Dashboard Master.
- Thêm template HTML tương tác có tìm kiếm, lọc, panel chi tiết, xuất CSV và tab kiểm chứng thao tác.
- Giữ nguyên nguyên tắc: chỉ tích hợp Dashboard Master/CỔNG A-B khi bác sĩ yêu cầu rõ.


## v1.1.0 — 2026-06-02

- Định nghĩa lại phạm vi: cập nhật chứng cứ cho **vấn đề lâm sàng cụ thể khi bác sĩ yêu cầu**.
- Không bắt buộc Dashboard, Web Dashboard, CỔNG A/B hoặc mã quản trị trong câu trả lời EBM thông thường.
- Bổ sung 4 tài liệu reference nội bộ còn thiếu.
- Bổ sung hai template đầu ra: nhanh và chuyên sâu.
- Bổ sung checklist nghiệm thu chất lượng.
- Tách chế độ an toàn thuốc, antibiotic stewardship, thang điểm/công cụ và thẩm định nguồn.
