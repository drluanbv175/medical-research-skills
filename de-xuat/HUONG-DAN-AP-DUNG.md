# Thực hiện đề xuất — trạng thái và việc còn lại

Đo và dựng ngày 05/09/2026. Mọi con số dưới đây là **đo trực tiếp**, không ước lượng.

---

## Việc 2 — ĐÃ XONG, đang chạy

Hai Routine chạy trên cloud, **không phụ thuộc máy bác sĩ thức hay có CLI**:

| Routine | Nhịp | Lần chạy kế | ID |
|---|---|---|---|
| Giám sát an toàn thuốc | thứ Hai hàng tuần, 08:02 VN | 07/09/2026 | `trig_018yTTQBgUigYhboVUk2gmXK` |
| Cập nhật guideline | mùng 1 hàng tháng, 08:00 VN | 01/10/2026 | `trig_01YAUrB48io5z6sy25nMPLgB` |

Cả hai chỉ sinh **THẺ ỨNG VIÊN (CANDIDATE)**, dừng đúng ở Cổng A/B. Có báo về điện
thoại và email khi chạy xong.

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

## LỖI THẬT ĐANG TỒN TẠI — sửa được trong 1 phút

`.claude/agents` có **88** tệp. `.codex/agents` có **0** — thư mục đích không tồn
tại. Gương Codex chưa từng được sinh, và không lịch nào chạy `check_claude_codex_
sync_health.py` nên nó **hỏng trong im lặng**.

Đã thử trên bản sao: chạy `python3 tools/sync_agents_to_codex.py` sinh **84 tệp**
và `check_claude_codex_sync_health.py` chuyển **XANH** ngay.

```
cd ~/Documents/GitHub/EBM-drluanbv175
python3 tools/sync_agents_to_codex.py
python3 tools/check_claude_codex_sync_health.py
git add .codex && git commit -m "fix: sinh lại gương .codex khớp 88 agent"
```

Workflow ở Việc 1 chốt luôn việc này — lần sau lệch sẽ báo đỏ, không im lặng nữa.

---

## Việc 3 — BẢNG QUYẾT, chờ bác sĩ

`de-xuat/lech-hai-repo.md` liệt kê đủ **68 tệp trùng tên đã lệch** giữa hai repo,
xếp theo mức lệch giảm dần.

Nặng nhất: **`CLAUDE.md`** — 6.456 bytes ở `medical-ebm-automation` so với
**221.847 bytes** ở `ebm-drluanbv175`, khác **2.169 dòng**. Đây là quyển luật Claude
đọc để biết phải làm gì. Còn hai quyển thì "luôn cập nhật" không có nghĩa.

Phân loại theo bằng chứng kích thước:

| Đề xuất chủ | Số tệp |
|---|---|
| `ebm-drluanbv175` giữ | 13 |
| `medical-ebm-automation` giữ | 7 |
| **Cần bác sĩ quyết** | **48** |

48 tệp kia hai bên xấp xỉ nhau — máy không có căn cứ để chọn, và chọn sai thì mất
nội dung thật. Bác quyết xong, chốt CI báo đỏ khi lệch là việc nhỏ.

**Sau khi cắt ranh giới xong** mới nên xoá 15 script trùng trong `sync/`
(`link-skills`, `copy-claude-md`, `fix-medsci-root`, `copy-commands-vi`,
`link-memory` — mỗi cái ba bản `.sh`/`.cmd`/`.ps1`). Xoá trước khi chốt ranh giới
là tự tháo lưới an toàn.

---

## Còn tồn

- **Skill: repo 52 / tài khoản 26.** `tools/tao_marketplace.py` (đã đẩy ở
  `medical-research-skills`) sinh được `.claude-plugin/marketplace.json` để cài một
  lệnh thay vì tải tay. Cần sửa trước: `sync/skills/ebm-master` khai
  `name: EBM-MASTER` viết hoa — đường plugin sẽ **bỏ qua im lặng**.
- **63 tệp `.bak`** đang được track trong `ebm-drluanbv175`.
- **18 tệp `V4_*`** nằm ở thư mục gốc `medical-ebm-automation`.
- 4 commit liên tiếp `chore: cap nhat timestamp hang doi knowledge pack` chỉ đổi
  timestamp của tệp sinh tự động — nên đưa vào `.gitignore`.

Cần bác sĩ kiểm chứng.
