# Kiểm tra cấu trúc viết bài báo khoa học — đối chiếu 9 mục IMRAD

Ngày kiểm: 2026-09-06 · Đối tượng kiểm: đường viết bản thảo trong hệ nghiên cứu y khoa
(`scientific-writing`, `nghien-cuu-y-khoa-chuan-quoc-te`, `peer-review`).

Chuẩn đối chiếu: 9 mục cấu trúc bài báo khoa học (Title · Abstract · Keywords ·
Introduction · Methods · Results · Discussion · Conclusion · References).

---

## 1. Kết quả đối chiếu

| # | Mục | Vị trí trong hệ thống | Kết luận |
|---|---|---|---|
| 1 | Tiêu đề | `workflows/06_bao_cao_cong_bo_ung_dung.md` dòng 13 — gộp chung `- Title/Abstract/Keywords.`, không tiêu chí. `scientific-writing/SKILL.md` Bước 2 không nhắc | ❌ Thiếu |
| 2 | Tóm tắt | `templates/01_mau_de_cuong_tong_the.md` mục 1 có đủ 5 phần + 200–300 từ + "viết SAU CÙNG" — nhưng chỉ áp cho **đề cương**; đường viết **bản thảo** không có | ⚠️ Thiếu cho bản thảo |
| 3 | Từ khóa | Chỉ xuất hiện dưới dạng chữ "Keywords". MeSH có trong `paper-lookup` nhưng phục vụ **truy tìm y văn**, không phải chọn từ khóa cho bài của mình | ❌ Thiếu |
| 4 | Giới thiệu | `scientific-writing` Bước 2 + `templates/01` mục 2 (cấu trúc phễu, bắt buộc PMID/DOI cho số liệu gánh nặng bệnh) | ✅ Vượt chuẩn |
| 5 | Phương pháp | `scientific-writing` Bước 2 + `workflows/06` §2 + toàn bộ G0–G9, SAP, data dictionary, bản đồ chuẩn báo cáo | ✅ Vượt xa |
| 6 | Kết quả | `scientific-writing`: "chỉ sự kiện, kèm ước lượng + 95% CI; bảng/hình không lặp văn" | ✅ Vượt chuẩn |
| 7 | Thảo luận | `scientific-writing` (diễn giải trong giới hạn · đối chiếu y văn · mạnh–hạn chế · ý nghĩa lâm sàng) + `workflows/06` (khả năng khái quát) | ✅ Đạt |
| 8 | Kết luận | Có trong `workflows/06`; **không có** trong `scientific-writing` — skill thực sự sinh bản thảo. Ý "câu hỏi/hướng nghiên cứu tiếp" không có ở file nào | ⚠️ Lệch + thiếu 1 ý |
| 9 | Tài liệu tham khảo | Cổng cứng PMID/DOI, `[TRÍCH DẪN CHƯA XÁC MINH]`, dò bài bị rút, Vancouver/NLM đánh số theo thứ tự xuất hiện, khớp 1-1 in-text ↔ danh mục | ✅ Vượt xa |

**Tổng: 5/9 đạt hoặc vượt · 4/9 có lỗ hổng.**

Toàn bộ 4 lỗ hổng nằm ở phần "vỏ" bài báo (tiêu đề · tóm tắt · từ khóa · kết luận) —
đúng phần biên tập viên đọc trước tiên và là nguyên nhân desk-reject phổ biến nhất.
Phần "ruột" (Methods/Results/Discussion/References) mạnh hơn hẳn yêu cầu của một
infographic phổ thông.

### Lỗ hổng thứ 5 — cổng bình duyệt không bắt được 4 lỗ hổng trên

`peer-review/SKILL.md` lăng kính 5 chỉ soát *"IMRAD mạch lạc; bảng/hình rõ; checklist
CONSORT/STROBE/PRISMA/STARD/TRIPOD đủ mục"* — **không soát tiêu đề, tóm tắt, từ khóa**.
Hệ quả: bản thảo có tiêu đề mơ hồ hoặc tóm tắt thiếu phần vẫn qua được bình duyệt nội bộ.

---

---

## 1B. BỔ SUNG 06/09 — có HAI bản `scientific-writing`, và kết quả khác nhau

Bản audit ở mục 1 làm trên **bản CLOUD** — thứ chạy trong Routine và mọi phiên web.
Sau đó, đối chiếu ba bên (`tools/doi_chieu_ba_ben.py`) phát hiện repo giữ một skill
**khác hẳn** dưới cùng cái tên `scientific-writing`: bản K-Dense tiếng Anh, 31.898 B
so với 3.790 B, độ trùng chỉ **6,2%**. Đó là bản chạy trên **máy bác sĩ** qua
`link-skills.sh`.

Nên câu trả lời "đã đạt chuẩn chưa" **phụ thuộc bác sĩ đang làm việc ở đâu**:

| # | Mục | CLOUD (Việt, 3,8 KB) | MÁY (K-Dense, 31,9 KB) |
|---|---|---|---|
| 1 | Tiêu đề | ❌ không nhắc | 🟡 có — "Create Title (concise and descriptive)"; **thiếu** yêu cầu nêu thiết kế nghiên cứu trong tiêu đề |
| 2 | Tóm tắt | ❌ không có ở đường bản thảo | 🟡 có, 100–250 từ, "standalone", nhưng **4/5 phần** (thiếu bối cảnh) — và xem lỗi bên dưới |
| 3 | **Từ khóa** | ❌ | ❌ **grep toàn bộ 31.898 B: 0 dòng chứa "keyword"** |
| 4 | Giới thiệu | ✅ | ✅ 5 ý, có "Identify knowledge gaps" |
| 5 | Phương pháp | ✅ vượt | ✅ đủ Sample · Procedure · Statistics + justification · Ethics/consent |
| 6 | Kết quả | ✅ vượt (bắt buộc 95% CI) | ✅ "Objective reporting **without interpretation**" |
| 7 | Thảo luận | ✅ | ✅ có "limitations honestly" + "future research" |
| 8 | Kết luận | ⚠️ vắng ở `scientific-writing` | ⚠️ không có mục riêng, không có bước viết ở quy trình |
| 9 | Tham khảo | ✅ vượt (cổng cứng PMID/DOI) | ✅ AMA/Vancouver/APA + "verify against original sources" |

**Hai kết luận rút ra:**

1. **Mục 3 (Từ khóa) thiếu ở CẢ HAI nơi.** Đây là lỗ hổng toàn hệ thống, không phải
   chuyện chọn bản nào.
2. Mục 1 và 2 **có ở máy nhưng không có ở cloud**. Cùng một yêu cầu "viết bản thảo",
   bác sĩ sẽ nhận kết quả khác nhau tuỳ chỗ ngồi — mà không có gì báo.

### 🔴 Lỗi phải sửa: quy tắc Abstract mặc định của bản K-Dense SAI cho y khoa

Cùng một file, ba chỗ nói ba kiểu về cùng một việc:

| Dòng | Nội dung |
|---|---|
| 76 | "Support **both** structured abstracts (with labeled sections) and unstructured…" |
| **282** | "❌ **NEVER** use labeled sections (Background:, Methods:, Results:, Conclusions:)" |
| 603 | "**Medical journals (NEJM, Lancet): Structured abstracts**, evidence language" |

Dòng 282 nằm trong khối **"Abstract Format Rule"**, viết đậm, có ❌ và chữ NEVER —
đó là dòng một mô hình đọc file này sẽ tuân theo. Và nó **sai với toàn bộ lĩnh vực
của bác sĩ**: hầu hết tạp chí y khoa yêu cầu tóm tắt có cấu trúc, đúng như chính
dòng 603 của file thừa nhận.

Hệ quả cụ thể: nhờ Claude trên máy viết tóm tắt → nhận một đoạn văn xuôi không nhãn
mục → phần lớn tạp chí y khoa trả lại.

**Bản vá cho `sync/skills/scientific-writing/SKILL.md` dòng 281–284 — thay nguyên khối:**

```markdown
**Abstract Format Rule:**
- **Y khoa là mặc định CÓ CẤU TRÚC.** Dùng nhãn mục (Background/Objective ·
  Methods · Results · Conclusions) trừ khi hướng dẫn tác giả của tạp chí đích nói
  ngược lại. Kiểm hướng dẫn tác giả TRƯỚC khi viết, đừng đoán.
- Chỉ viết văn xuôi liền mạch không nhãn khi tạp chí yêu cầu như vậy (một số tạp chí
  khoa học cơ bản), hoặc khi đó là abstract hội nghị có quy định riêng.
- Đủ 5 phần dù có nhãn hay không: bối cảnh · mục tiêu · phương pháp · kết quả (kèm
  ước lượng và 95% CI) · kết luận.
- Mọi con số trong tóm tắt phải có mặt y hệt trong Results.
```

**Và thêm mục Từ khóa vào §2 `Section-Specific Writing Guidance` (thiếu ở CẢ HAI bản):**

```markdown
**Keywords Selection**: Choose 3–6 terms. Prioritise terms that do **not** already
appear in the title — repeating title words adds no discoverability. Check each
against the MeSH Browser for medical papers; mark unverified terms rather than
guessing.
```

## 2. Bản vá — dán nguyên khối vào repo `EBM-drluanbv175`

Ba file cần sửa. Nội dung dưới đây đã viết sẵn, chỉ việc thay/chèn.

### 2.1. `sync/skills/scientific-writing/SKILL.md`

**Chèn khối sau ngay trước dòng `**Bước 2 — Văn xuôi`:**

```markdown
**Bước 1b — Vỏ bài báo (làm SAU khi thân bài đã xong, KHÔNG làm trước):**
- **Tiêu đề:** nêu được quần thể + can thiệp/phơi nhiễm + kết cục chính, và **gọi tên
  thiết kế** (RCT / đoàn hệ / cắt ngang / tổng quan hệ thống) theo yêu cầu của chuẩn
  báo cáo tương ứng. Không dùng câu hỏi tu từ, không viết tắt chưa định nghĩa, không
  khẳng định kết quả vượt dữ liệu ("chứng minh…", "hiệu quả vượt trội…").
- **Tóm tắt có cấu trúc:** đủ **5 phần** — bối cảnh · mục tiêu · phương pháp (thiết kế,
  đối tượng, cỡ mẫu, kết cục chính) · kết quả (số hiệu + 95% CI, không chỉ p) · kết luận.
  Giới hạn từ theo tạp chí (thường 250–300). **Độc lập**: người chỉ đọc tóm tắt phải
  nắm được toàn bộ nghiên cứu. Mọi con số trong tóm tắt phải **có mặt y hệt** trong
  Results — lệch số giữa tóm tắt và thân bài là lỗi bị bắt nhiều nhất.
- **Từ khóa:** 3–6 từ, **ưu tiên từ chưa xuất hiện trong tiêu đề** (từ khóa lặp lại
  tiêu đề không làm tăng khả năng được tìm thấy). Đối chiếu MeSH Browser; đánh dấu
  `[CẦN KIỂM CHỨNG NGUỒN CHÍNH THỨC]` nếu chưa tra được MeSH.
```

**Thay khối `**Bước 2 — Văn xuôi …` bằng bản có đủ Conclusion + References:**

```markdown
**Bước 2 — Văn xuôi (liền mạch, KHÔNG gạch đầu dòng trong thân):**
- **Introduction:** khoảng trống kiến thức → mục tiêu/giả thuyết.
- **Methods:** đủ chi tiết tái lặp; nêu phê duyệt đạo đức + mã đăng ký; tham chiếu SAP.
- **Results:** chỉ sự kiện, kèm ước lượng + 95% CI; bảng/hình không lặp văn.
  **KHÔNG diễn giải, KHÔNG so sánh y văn ở mục này** — để dành cho Discussion.
- **Discussion:** diễn giải trong giới hạn; đối chiếu y văn; điểm mạnh–hạn chế; ý nghĩa
  lâm sàng (thận trọng).
- **Conclusion:** đóng góp cốt lõi trong đúng phạm vi dữ liệu; **không lặp lại Results**;
  không phóng đại, không suy nhân quả vượt thiết kế; nêu **câu hỏi/hướng nghiên cứu tiếp**.
- **References:** chỉ liệt kê tài liệu **đã thực sự trích trong bài** (không "đọc thêm");
  Vancouver/NLM, đánh số theo thứ tự xuất hiện; kiểm khớp 1-1 giữa số trong văn bản và
  danh mục cuối bài trước khi nộp.
```

**Cập nhật khối `## Mẫu đầu ra` — thêm dòng vỏ bài báo:**

```
Tiêu đề: ____ | Từ khóa (3–6, ưu tiên từ ngoài tiêu đề): ____
Tóm tắt có cấu trúc (5 phần, ≤ giới hạn tạp chí) — mọi số khớp Results
```

### 2.2. `sync/skills/nghien-cuu-y-khoa-chuan-quoc-te/workflows/06_bao_cao_cong_bo_ung_dung.md`

**Thay dòng 13 (`- Title/Abstract/Keywords.`) bằng 3 dòng:**

```markdown
- **Title:** quần thể + can thiệp/phơi nhiễm + kết cục chính + tên thiết kế; không viết
  tắt chưa định nghĩa; không khẳng định vượt dữ liệu.
- **Abstract:** có cấu trúc, đủ 5 phần (bối cảnh · mục tiêu · phương pháp · kết quả có
  95% CI · kết luận); độc lập; mọi số khớp y hệt mục Results.
- **Keywords:** 3–6 từ, ưu tiên từ chưa có trong tiêu đề; đối chiếu MeSH.
```

**Bổ sung vào §2 sau dòng `- Conclusions:`:**

```markdown
- Conclusions: đúng phạm vi dữ liệu, không phóng đại; không lặp lại Results; nêu hướng
  nghiên cứu tiếp theo.
- References: chỉ tài liệu đã trích trong bài; Vancouver/NLM đánh số theo thứ tự xuất
  hiện; khớp 1-1 in-text ↔ danh mục.
```

**Bổ sung vào bảng §3 "Bộ hồ sơ công bố" một dòng:**

```markdown
| Title/Abstract/Keywords đã soát theo mục Title-and-abstract của chuẩn báo cáo | [CẦN BỔ SUNG] |
```

### 2.3. `sync/skills/peer-review/SKILL.md`

**Thay lăng kính 5:**

```markdown
5. **Trình bày & chuẩn báo cáo:** **tiêu đề** có nêu thiết kế + quần thể + kết cục?
   **tóm tắt** đủ 5 phần, độc lập, mọi số khớp Results? **từ khóa** có bổ sung từ ngoài
   tiêu đề? IMRAD mạch lạc; Results không lẫn diễn giải; Conclusion không vượt dữ liệu;
   bảng/hình rõ; checklist CONSORT/STROBE/PRISMA/STARD/TRIPOD đủ mục — kể cả mục
   Title-and-abstract của chuẩn đó.
```

---

## 3. Điểm hệ thống VƯỢT infographic (giữ nguyên, không hạ chuẩn)

Infographic là chuẩn viết bài phổ thông. Bản thảo y khoa nộp tạp chí cần thêm những
thứ infographic không nhắc, và hệ thống đã có:

- **Chuẩn báo cáo theo thiết kế** — CONSORT · STROBE · PRISMA 2020 · SPIRIT · STARD ·
  TRIPOD+AI · COREQ/SRQR · SQUIRE 2.0 · CARE · CHEERS · ARRIVE · RIGHT
  (`references/02_ban_do_chuan_bao_cao.md` — 20 loại nghiên cứu).
- **Cổng chất lượng G0–G9** — không cho viết Results khi chưa khóa dữ liệu.
- **Cổng cứng trích dẫn** — PMID/DOI phải thật + trích đúng nội dung + dò bài bị rút.
- **Khai báo bắt buộc** — ICMJE authorship · COI · tài trợ · dùng AI · data availability ·
  mã đăng ký · số phê duyệt đạo đức.
- **Flow diagram** theo chuẩn (CONSORT flow, PRISMA flow).

Lưu ý phiên bản: các chuẩn đều có mục riêng cho tiêu đề và tóm tắt (ví dụ STROBE mục 1a
"nêu thiết kế trong tiêu đề hoặc tóm tắt" và 1b "tóm tắt cân bằng"; CONSORT và PRISMA có
extension riêng cho abstract). **Số hiệu mục thay đổi theo phiên bản** — trước khi nộp
phải đối chiếu bản hiện hành trên EQUATOR, theo đúng quy tắc 7 của
`nghien-cuu-y-khoa-chuan-quoc-te`: chưa kiểm chứng thì ghi
`[CẦN KIỂM CHỨNG NGUỒN CHÍNH THỨC]`.

---

## 4. Checklist tự soát 9 mục (dùng cho mọi bản thảo trước khi nộp)

```
[ ] 1. Tiêu đề    — có quần thể + can thiệp/phơi nhiễm + kết cục + tên thiết kế?
                    không viết tắt lạ? không khẳng định vượt dữ liệu?
[ ] 2. Tóm tắt    — đủ 5 phần? độc lập? ≤ giới hạn tạp chí?
                    MỌI con số khớp y hệt Results (kiểm từng số)?
[ ] 3. Từ khóa    — 3–6 từ? có ít nhất 2 từ KHÔNG xuất hiện trong tiêu đề? đã tra MeSH?
[ ] 4. Giới thiệu — nêu được vì sao cần nghiên cứu? khoảng trống cụ thể (không "còn ít
                    nghiên cứu")? mọi số dịch tễ có PMID/DOI? kết bằng mục tiêu/giả thuyết?
[ ] 5. Phương pháp— người khác đọc có lặp lại được không? đủ Thiết kế · Đối tượng/cỡ mẫu ·
                    Quy trình · Thống kê? có phê duyệt đạo đức + mã đăng ký + tham chiếu SAP?
[ ] 6. Kết quả    — CHỈ sự kiện? không một câu diễn giải, không so sánh y văn?
                    có ước lượng + 95% CI (không chỉ p)? bảng/hình không lặp lại văn?
[ ] 7. Thảo luận  — diễn giải trong giới hạn thiết kế? đối chiếu y văn? nêu điểm mạnh VÀ
                    hạn chế? ý nghĩa lâm sàng thận trọng? khả năng khái quát?
[ ] 8. Kết luận   — đúng phạm vi dữ liệu? KHÔNG lặp lại Results? không suy nhân quả vượt
                    thiết kế? có nêu hướng nghiên cứu tiếp?
[ ] 9. Tham khảo  — chỉ tài liệu ĐÃ trích? Vancouver/NLM? đánh số theo thứ tự xuất hiện?
                    khớp 1-1 in-text ↔ danh mục? mọi mục có PMID/DOI đã xác minh?
                    đã dò bài bị rút (retraction)?

Cổng cuối: [ ] checklist chuẩn báo cáo đúng thiết kế đã điền, ghi số trang từng mục
           [ ] khai báo COI · tài trợ · ICMJE authorship · dùng AI · data availability
           [ ] "Cần bác sĩ kiểm chứng."
```

---

## 5. Vì sao bản vá nằm ở repo này

Các skill cần sửa thuộc repo `EBM-drluanbv175`. Phiên cloud này **không có quyền push**
vào repo đó (yêu cầu `add_repo access: push` đã bị chính sách từ chối), nên bản vá được
đặt sẵn ở đây để dán tay — cùng cách làm với `de-xuat/giam-sat-dinh-ky.yml`.

Sau khi dán, chạy trình kiểm tính toàn vẹn có sẵn:

```bash
python3 sync/skills/nghien-cuu-y-khoa-chuan-quoc-te/scripts/validate_skill.py
```

Lưu ý: script này **chỉ kiểm được skill `nghien-cuu-y-khoa-chuan-quoc-te`** (nó tự chốt
tên thư mục gốc ở dòng `if root.name != "nghien-cuu-y-khoa-chuan-quoc-te"`), tức chỉ phủ
bản vá 2.2. Hai bản vá 2.1 và 2.3 (`scientific-writing`, `peer-review`) **chưa có trình
kiểm tự động** — soát tay: frontmatter `name`/`description` còn nguyên, mọi khối mã
đóng đủ cặp ba dấu huyền, và `SKILL.md` sau khi sửa vẫn dưới ~5.000 token.
