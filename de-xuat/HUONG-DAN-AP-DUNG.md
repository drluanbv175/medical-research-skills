# Thực hiện đề xuất — trạng thái và việc còn lại

Đo và dựng ngày 05/09/2026. Mọi con số dưới đây là **đo trực tiếp**, không ước lượng.

---

## Việc 2 — ĐÃ XONG, đang chạy

Hai Routine chạy trên cloud, **không phụ thuộc máy bác sĩ thức hay có CLI**:

| Routine | Nhịp | Lần chạy kế | ID |
|---|---|---|---|
| Giám sát an toàn thuốc | thứ Hai hàng tuần, 08:02 VN | 07/09/2026 | `trig_018yTTQBgUigYhboVUk2gmXK` |
| Cập nhật guideline | mùng 1 hàng tháng, 08:00 VN | 01/10/2026 | `trig_01YAUrB48io5z6sy25nMPLgB` |

Cả hai chạy **Opus 5**.

Cả hai chỉ sinh **THẺ ỨNG VIÊN (CANDIDATE)**, dừng đúng ở Cổng A/B. Có báo về điện
thoại và email khi chạy xong.

### Đã bắn thử — và đã chốt cửa fail-closed

Bắn thử Routine tuần lúc 11:56 ngày 05/09: **SUCCEEDED**, chạy 3 phút 37, sinh 28.563
token đầu ra — tức có làm việc thật, không thoát sớm. Nhưng tôi **không đọc được nội
dung phiên đó** từ phiên thiết lập; báo cáo nằm trong email và thông báo đẩy của bác sĩ.

Vì chưa xác nhận được phiên do Routine sinh ra có gọi được skill hay không, tôi đã siết
lời nhắc của **cả hai** Routine thay vì để may rủi. Mỗi lượt chạy nay phải mở đầu bằng
ba dòng tự khai năng lực, và có **cửa fail-closed**:

- Không có công cụ tra cứu nào → **DỪNG NGAY**, viết đúng một câu, không dựng báo cáo.
- Thiếu skill nhưng còn tra cứu được → chạy tiếp, nhưng phải ghi rõ là đang chạy
  không có skill.
- Mọi khẳng định phải truy được về nguồn **mở trong chính lượt đó** — không dựng lại
  từ trí nhớ, kể cả khi thấy chắc chắn.

Lý do viết thẳng vào lời nhắc: trong y khoa, một trích dẫn bịa nguy hiểm hơn hẳn một
tuần không có báo cáo. Trước bản vá này, nếu skill vắng mặt thì phiên có thể lặng lẽ
soạn báo cáo từ trí nhớ mà không ai biết.

**Model: đã đổi sang Opus 5** (05/09, theo yêu cầu của bác sĩ). Lượt chạy thử ngày
05/09 chạy Sonnet 5 vì trigger chưa ghim model; từ lượt thứ Hai 07/09 trở đi cả hai
Routine chạy `claude-opus-5`. Lời nhắc và lịch giữ nguyên, lịch sử chạy không mất.

> **Hạn chế phải biết:** Routine tạo qua đường này **không mang theo connector**
> (PubMed, ClinicalTrials, Amass, Consensus…). Phiên sẽ tra bằng tìm kiếm web, kém
> chính xác hơn. Muốn có connector: mở **claude.ai → Routines**, sửa hai Routine
> trên và gắn connector cần dùng. Nội dung lời nhắc giữ nguyên.

---

## Việc 1 — CẦN BÁC SĨ DÁN VÀO REPO

Tôi **không đẩy được** lên `ebm-drluanbv175` và `medical-ebm-automation`: phiên này
chỉ có quyền ĐỌC hai repo đó, và yêu cầu nâng quyền ghi đã bị chặn. Tệp đã dựng và
kiểm cú pháp sẵn:

**`de-xuat/giam-sat-dinh-ky.yml`** → chép vào `ebm-drluanbv175/.github/workflows/`

Chạy 07:00 VN thứ Hai (tuần) và mùng 1 (tháng), trên máy GitHub.

### Đính chính so với đề xuất ban đầu

Tôi đã nói "đưa nhịp tim lên GitHub Actions" cho cả giám sát chứng cứ. **Sai một
nửa** — đo lại thì:

- `scripts/weekly_safety.sh`, `monthly_update.sh`, `quarterly_superseded.sh`:
  **0 tệp tracked** trong git.
- `EBM_MASTER`, `EBM-Dashboards`: bị `.gitignore` **cố ý**.

Nên Actions **không thể** chạy giám sát chứng cứ thật. Nó chạy được phần **tất
định**: 14 verifier trên tệp có trong git + gương `.codex`. Phần giám sát chứng cứ
do hai Routine ở Việc 2 gánh. Workflow ghi rõ ranh giới này trong phần đầu tệp.

### Đo được gì

| Nhóm | Số verifier |
|---|---|
| Chạy xanh trên bản sao git trần | **11** |
| Xanh thêm khi có repo anh em | **+3** (tổng 14) |
| Cần dữ liệu cục bộ — không chạy được trên CI | 7 |
| Cần tham số / chỉ nhắc | 5 |

3 verifier cần repo anh em chỉ chạy khi có secret `SIBLING_REPO_TOKEN`
(Settings → Secrets → Actions). **Không có secret vẫn chạy được 11 cái** — dùng
ngay ngày đầu, không cần cấu hình gì.

---

## ĐÍNH CHÍNH: "lỗi `.codex`" tôi báo trước đó KHÔNG phải lỗi

Tôi đã viết: *".claude/agents có 88 tệp, .codex/agents có 0 — gương chưa từng được
sinh, hỏng trong im lặng"*, kèm lệnh `git add .codex && git commit`. **Cả hai đều sai.**

Đo lại:

```
$ git check-ignore -v .codex/agents/binh-duyet.md
.gitignore:13:/*    .codex/agents/binh-duyet.md
```

`.codex/` **bị .gitignore cố ý** — nó là **sản phẩm sinh**, không phải nội dung. Và nó
được tái tạo tự động ở hai nơi:

- `.claude/hooks/session-start.sh:114` → chạy `sync_agents_to_codex.py` **mỗi phiên**
- `.github/workflows/kiem-tinh-da-nen.yml:76` → chạy lại **mỗi lần CI**

Nên **bản sao git trần có 0 tệp là ĐÚNG TRẠNG THÁI**, không phải hỏng. Trên máy bác sĩ
gương vẫn được sinh đều. Lệnh `git add .codex` tôi đưa sẽ ép thêm tệp đang bị ignore
vào git — **đừng chạy nó**.

Đây là cùng một lớp sai lầm mà chính `tools/kiem_cay_lam_viec.py` của bác sĩ sinh ra để
cảnh báo: đo trên bản sao trần rồi đọc "thiếu sản phẩm sinh" thành "cơ chế đã hỏng".
Docstring của nó ghi rõ một cuộc kiểm toán 11 agent từng báo động NGHIÊM TRỌNG vì đúng
lỗi này. Tôi đã mắc lại.

### Hệ quả: một lỗi thật trong workflow tôi giao

Bản đầu của `giam-sat-dinh-ky.yml` kiểm gương bằng `git diff --quiet -- .codex`. Trên
đường dẫn bị ignore, lệnh đó **luôn** báo "không lệch" — cổng sẽ xanh giả vĩnh viễn.
Đã thay bằng thứ kiểm được thật: bộ sinh có chạy nổi không, gương có qua cổng sức khoẻ
không, và có sinh ra tệp nào không.

**Đã chạy thử toàn bộ workflow trên bản sao thật:** 11/11 verifier xanh, gương sinh 84
tệp và qua cổng. Workflow không đỏ ngày đầu.

## Việc 3 — ĐÃ THU HẸP: không phải 48 quyết định, mà là MỘT

> **Đính chính.** Bảng đầu tiên tôi gửi ghép tệp theo **tên**, nên 12/68 dòng so hai
> tệp chẳng liên quan (`app/chatgpt_app/knowledge.py` bị đem so với
> `tools/orchestrator/knowledge.py`). Ghép lại theo **đường dẫn**: 92 tệp cùng đường
> dẫn, **59 lệch** — không phải 68.

**86% lệch nằm ở đúng một chỗ:** `.claude/agents/` — 51 trong 59 tệp.

| | A (`medical-ebm-automation`) | E (`ebm-drluanbv175`) |
|---|---|---|
| Số agent | 84 | **179** (chứa đủ 84 của A) |
| Tệp lớn hơn, trên 51 tệp lệch | **0** | **51** |
| Dòng chỉ có ở bên này | 23 | 870 |

23 dòng "chỉ có ở A" đã soi từng dòng: 5 dòng `description:` **cùng chữ**, chỉ khác
kiểu nháy; phần còn lại ở `_VONG-LAP-KHEP-KIN.md` — bản A (75 dòng) chỉ có tuyến
nghiên cứu, bản E (177 dòng) viết lại cho **cả hai tuyến**, đủ 5 bất biến, chỉ đổi
tên mục. **Không nội dung nào của A vắng mặt ở E.**

→ **E là nguồn chân lý; bản agent trong A là gương cũ.** Đúng với chính khai báo của
`check_claude_codex_sync_health.py`: *"Source of truth is `.claude/agents`"* — vấn đề
là đang tồn tại HAI bản. Cách xử lý: A sinh agent từ E, hoặc bỏ hẳn bản sao trong A.
Không phải ngồi quyết từng tệp.

**Còn 8 tệp cần bác sĩ nhìn** — chi tiết trong `lech-hai-repo.md`. Trong đó 5 tệp
nghiêng về E (`AGENTS.md`, `.gitignore`, `.gitattributes`, `.githooks/pre-commit`,
`tools/generate_agent.py`), 1 nghiêng về A (`tools/scaffold_research_project.py`), và
2 tệp **không phải lệch**: `CLAUDE.md` và `README.md` là hai tài liệu **khác phạm vi**.

### Đính chính về `CLAUDE.md`

Tôi đã nói đây là "hai quyển luật lệch 2.169 dòng". **Sai.** `A/CLAUDE.md` mở đầu bằng
`_harness_template: "CLAUDE.md.template"`, `_harness_version: "4.3.3"` — bản **sinh từ
khuôn**, phạm vi dự án con. `E/CLAUDE.md` là học thuyết "EBM Copilot" viết tay cho toàn
hệ. Và vì A nằm **lồng trong** E trên máy thật, dự án con có `CLAUDE.md` riêng là
**đúng cách** — Claude Code đọc bản gần nhất cộng bản cha. **Không phải việc cần sửa.**

Vậy nên: **đừng gộp hai repo.** Việc 3 rút lại còn một câu hỏi — A có cần bản sao agent
riêng không, và nếu có thì sinh từ E chứ đừng sửa tay hai nơi.

## Ba khoản "còn tồn" — tôi đã nêu sai cả ba, theo ba kiểu

Rà từng khoản thì chỉ **một** là việc thật, và nó nhỏ.

| Khoản | Tôi đã nói | Đo thật |
|---|---|---|
| Tệp `.bak` tracked | 63 | **21** |
| `V4_*` ở gốc | "rác cần dọn" | **hồ sơ kiểm toán — không được xoá** |
| Tệp sinh tự động bị commit lặp | có | **đúng** — và sửa được trong 2 dòng |

### `.bak`: 21 chứ không phải 63 — và không phải việc cần làm

Con số 63 của tôi đến từ một lệnh `grep` đếm **dòng khớp chuỗi**, không đếm **tệp**;
đường dẫn chứa thư mục `_bak_20260613/` bị đếm nhiều lần. Đếm đúng theo đuôi tệp:

- **21** tệp, trong đó **20 nằm trong `.claude/agents/_archive/_bak_20260613/` và
  `_bak2_20260613/`** — kho lưu có chủ ý, đặt tên theo ngày. Không phải rác.
- **1** tệp lẻ: `.claude/agents/_SO-TRANG-THAI-CHECKPOINT.md.bak` — bản mẫu cũ
  (43 dòng) đã bị bản sống (59 dòng) thay thế; 10 dòng riêng của nó là phiên bản cũ
  của chính các dòng đó, không có nội dung độc lập.
- **0** tệp `.bak` nào được mã nguồn tham chiếu.

**Không có việc phải làm.** Cùng lắm xoá 1 tệp lẻ, và cũng không cấp thiết.

### `V4_*`: hồ sơ phát hành, xoá là mất chứng cứ

18 tệp ở gốc `medical-ebm-automation` mang tên `ARCHIVE_RECEIPT`, `FREEZE_SUMMARY`,
`CLEANUP_EXECUTION_LOG`, `RETENTION_POLICY`, `GIT_BASELINE_VERIFICATION`,
`TEST_REPORT`… Đây là **bằng chứng đóng băng phiên bản** V4_3_3 và V4_3_3_2.

Repo đã có chỗ đúng cho chúng: `release_evidence/` với 192 tệp tracked, chia theo
`PROGRAM`, `R0`…`R6_0`, `R_GOV_1/2`, `V4_3_3_2`, `V4_3_4`, `V4_3_5`. Nhưng:

- **17/18 tệp ở gốc KHÔNG có bản nào trong `release_evidence/`** — chúng là bản duy nhất.
- 1 tệp (`V4_3_3_2_FREEZE_SUMMARY.md`) có ở cả hai nơi và **khác nhau 133 dòng**.

Nên việc đúng là **`git mv` vào `release_evidence/`** (giữ lịch sử), tạo thêm thư mục
`V4_3_3/` cho nhóm V4_3_3, và đối chiếu tệp khác 133 dòng kia trước — **không phải xoá**.
Với một hệ y khoa có cổng ký duyệt, xoá hồ sơ phát hành là mất dấu vết kiểm toán.

Vì đây là quyết định về hồ sơ kiểm toán, tôi để bác quyết, không tự làm.

### Tệp sinh tự động: việc thật, sửa 2 dòng

`results/knowledge_pack_update_queue.json` đang được track, và `.gitignore` đã loại
`results/daily_*`, `results/weekly_*` nhưng **sót đúng tệp này** — nên nó sinh ra chuỗi
commit `chore: cap nhat timestamp hang doi knowledge pack` chỉ đổi timestamp.

```
cd ~/Documents/GitHub/medical-ebm-automation
echo 'results/knowledge_pack_update_queue.json' >> .gitignore
git rm --cached results/knowledge_pack_update_queue.json
git commit -m "chore: ngừng track hàng đợi knowledge pack (tệp sinh tự động)"
```

Cần bác sĩ kiểm chứng.

---

## Skill: repo 52 / tài khoản 26 — công cụ đã sẵn

`tools/tao_marketplace.py` (trong `medical-research-skills`, đã đẩy) sinh
`.claude-plugin/marketplace.json` cho một repo skill bất kỳ, để cài bằng một lệnh
thay vì tải tay từng skill lên tài khoản. Repo thành nguồn chân lý, `git pull` là
cập nhật.

```
python3 tools/tao_marketplace.py ~/Documents/GitHub/EBM-drluanbv175          # xem trước
python3 tools/tao_marketplace.py ~/Documents/GitHub/EBM-drluanbv175 --ghi    # ghi file
```

Đã chạy trên cả hai repo: `EBM-drluanbv175` **52/52 skill**, `medical-research-skills`
**605/605**. Không mất skill nào.

> **Đính chính.** Tôi từng nói phải sửa `sync/skills/ebm-master` trước, vì nó khai
> `name: EBM-MASTER` chữ hoa và "đường plugin sẽ bỏ qua im lặng". **Sai — suy đoán,
> không có phép đo nào chống lưng.** Bằng chứng ngược lại: skill đó **đang nạp và
> chạy** ngay trong phiên này với đúng cái tên chữ hoa ấy; Claude Code định danh
> skill theo **tên thư mục**, không theo trường `name`.
>
> Công cụ của tôi lúc đầu **loại** nó khỏi bản kê. Nghĩa là nếu bác chạy `--ghi`
> sớm hơn, bác đã nhận bản kê 51/52 — thiếu đúng skill cửa chính của hệ — mà không
> hay biết. Nay nó chỉ **cảnh báo** và vẫn đưa vào. **Không cần sửa gì trong repo.**

Sau khi `--ghi`, cài bằng `/plugin marketplace add drluanbv175/EBM-drluanbv175`
trong Claude Code, thay cho việc tải tay lên tài khoản.

Cần bác sĩ kiểm chứng.
