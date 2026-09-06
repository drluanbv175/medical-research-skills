# Đồng bộ ba bên: Cloud · Cục bộ · Repo

Đo ngày 06/09/2026 bằng `tools/doi_chieu_ba_ben.py`. Repo `ebm-drluanbv175` ở
commit `ce0d83c2`. Mọi con số là đo trực tiếp.

---

## 1. Ba bên là gì, và cặp nào đang KHÔNG ai kiểm

| Bên | Là gì | Ai nạp nó |
|---|---|---|
| **Cloud** | Bundle skill của tài khoản (`~/.claude/skills/synced/<uuid>/`) | **Routine + mọi phiên claude.ai/code** |
| **Cục bộ** | `~/.claude/skills` và `~/.codex/skills` trên máy bác sĩ | Claude Code CLI + Codex trên máy |
| **Repo** | `sync/skills/` trong `ebm-drluanbv175` | nguồn git, không tự chạy |

Ba cặp nối, chỉ hai cặp có công cụ:

```
repo ──link-skills.sh──────────► ~/.claude/skills, ~/.codex/skills     ✅ đã có
repo ──dong_bo_skill.py────────► Claude Desktop local-agent-mode       ✅ đã có
repo ◄────────  ???  ─────────► bundle tài khoản (CLOUD)              ❌ TRỐNG
```

`sync/SYNC-README.md` đã ghi rõ tình trạng này ngay ở bảng đầu: Cowork đồng bộ
"**tự động qua tài khoản**", còn Code+Codex đồng bộ "**tự động từ `sync/skills/`**".
Hai nguồn chân lý song song, không có gì đối chiếu chúng. Tám làn của
`tools/dong_bo_tat_ca.py` (an toàn · git · skill · agent · plugin · hook · bộ nhớ ·
kho công cụ) **không có làn nào chạm bundle cloud**.

Hệ quả đã đo được: bundle cloud và repo lệch nhau ở **20/26** skill dùng chung tên.

---

## 2. Số đo

```
python3 tools/doi_chieu_ba_ben.py ~/Documents/GitHub/EBM-drluanbv175
```

| Nhóm | Số lượng | Nghĩa |
|---|---|---|
| ✅ Giống hệt | 6 | `dao-tao-slide-tai-lieu-y-khoa` · `dashboard-master-ebm-ngoai-tru` · `ehospital-mini` · `nghien-cuu-ebm-tong-hop` · `nghien-cuu-y-khoa-chuan-quoc-te` · `tao-video-tiktok` |
| 🟡 Lệch bản | 13 | cùng skill, khác phiên bản (trùng 53–99%) |
| 🔴 **Khác hẳn** | **7** | **trùng tên nhưng là hai skill khác nhau** (trùng 6–19%) |
| ⚪ Chỉ có ở repo | 16 | cloud và Routine **không nạp được** |
| ⚪ Chỉ có ở cloud | 0 | — |

---

## 3. Vấn đề gốc: có HAI HỌ SKILL trùng tên nhau

| | Họ A — trên cloud | Họ B — trong repo |
|---|---|---|
| Nguồn | bác sĩ tự viết, tải lên qua giao diện | nhập từ K-Dense, chạy qua `sync/skills/_vietnamize.py` |
| Ngôn ngữ thân bài | tiếng Việt (VN 10–17%) | tiếng Anh (VN 0,6–2,8%) + khối `<!-- EBM-VN-GUARD -->` tiếng Việt chèn đầu |
| Kích thước | 2,8–4,6 KB | 6,9–33 KB |
| Kiểu | gọn, cổng liêm chính đặt trước, gắn với lệnh Việt (`viet-ban-thao`, `binh-duyet`, `thu-thu-tai-lieu`) | đầy đủ tính năng (venue-templates, LaTeX, quy ước từng tạp chí) |

Bảy tên đang bị hai họ giành nhau:

`citation-management` · `literature-review` · `paper-lookup` · `peer-review` ·
`research-lookup` · `scientific-writing` · `statistical-analysis`

> **Vì thế "đồng bộ" hiểu theo nghĩa chép đè là PHÁ HOẠI.** Chép repo → cloud thì
> mất bảy skill Việt bác sĩ tự viết. Chép cloud → repo thì mất bảy skill K-Dense.
> Không có chiều nào an toàn. Đây là lý do công cụ mới **chỉ đọc**, và trả mã
> thoát `2` để chặn mọi lệnh chép tự động phía sau.

### Rủi ro cao nhất: bảy bản cloud KHÔNG có bản git

Dò toàn repo bằng các cụm chữ đặc trưng của họ A:

| Cụm chữ (chỉ có ở bản cloud) | Số file trong repo |
|---|---|
| `6 lăng kính` (skill `peer-review`) | **0** |
| `Cổng cứng trích dẫn` (skill `scientific-writing`) | **1** — mà là bản agent đã lưu trữ trong `.claude/agents/_archive/`, không phải skill |

Nghĩa là: **bảy skill họ A chỉ tồn tại trên tài khoản.** Chúng không nằm trong git,
không có lịch sử phiên bản, không khôi phục được nếu tài khoản đổi hoặc bị xóa
nhầm. Trong khi đó chúng chính là các skill mà Routine đang chạy hàng tuần dùng.

### 16 skill chỉ có ở repo — cloud và Routine không thấy

`clinical-decision-support` · `clinical-reports` · `database-lookup` ·
`experimental-design` · `exploratory-data-analysis` · `hypothesis-generation` ·
`plugin-router-chatgpt` · `pyhealth` · `scholar-evaluation` ·
`scientific-critical-thinking` · `scikit-survival` · `statistical-power` ·
`statsmodels` · `tong-thuat-chung-cu` · `treatment-plans` · `venue-templates`

Trên máy bác sĩ có (qua `link-skills.sh`). Trong phiên cloud và trong Routine thì
**không tồn tại**. Nếu một Routine trông chờ `statistical-power` hay
`tong-thuat-chung-cu`, nó sẽ không tìm thấy — và trước bản vá fail-closed đã làm
tuần trước, nó sẽ im lặng chạy tiếp mà không báo.

---

## 4. Đề xuất — làm theo thứ tự này

**Bước 1 — ĐÃ LÀM XONG trong phiên này.**
Bảy skill họ A đã được sao lưu vào git, chép nguyên văn từng byte từ bundle tài
khoản (`cmp` xác nhận 7/7 khớp): xem `sao-luu-skill-cloud/` trong repo
`medical-research-skills`, kèm bảng SHA-256 để đối chiếu về sau.

Mất tài khoản không còn đồng nghĩa mất skill. Việc còn lại là dời chúng về **nhà
đúng** — repo `ebm-drluanbv175`, dưới tên có hậu tố `-vn` để không đè lên họ
K-Dense đang giữ tên gốc (phiên cloud không có quyền ghi vào repo đó):

```bash
cd ~/Documents/GitHub/EBM-drluanbv175
SAO=~/Documents/GitHub/medical-research-skills/sao-luu-skill-cloud
for s in citation-management literature-review paper-lookup peer-review \
         research-lookup scientific-writing statistical-analysis; do
  cp -R "$SAO/$s" "sync/skills/$s-vn"
done
git add sync/skills/*-vn
git commit -m "chore: đưa 7 skill EBM bản cloud vào git"
```

**Bước 2 — chọn một họ cho mỗi tên, đổi tên họ còn lại.**
Khuyến nghị: **giữ họ A ở tên gốc**, đổi họ B thành `<tên>-kdense`. Lý do: các lệnh
Việt và bảng định tuyến trong `CLAUDE.md` (dòng 226, 229) cùng
`plugin-router-chatgpt` đang trỏ vào tên gốc; đổi tên họ A sẽ phải sửa
83 file có chuỗi `viet-ban-thao` và 45 file có `thu-thu-tai-lieu`, còn đổi tên họ B
thì không file nào đang trỏ tới. Đổi cái ít ràng buộc hơn.

Sau khi đổi tên, cả hai họ cùng sống được, và cloud có thể nhận đủ cả hai.

**Bước 3 — nạp lên cloud những gì cloud đang thiếu.**
16 skill chỉ-có-ở-repo cộng họ B đã đổi tên, tải lên tài khoản. Sau đó cloud, cục bộ
và repo mới thật sự cùng một tập.

**Bước 4 — chốt cửa để không trôi lại.**
Thêm **làn ⑨** vào `tools/dong_bo_tat_ca.py`:

```python
# ⑨ Cloud ↔ repo — làn duy nhất chạm bundle tài khoản.
#    Mã thoát 2 = có skill trùng tên khác nội dung -> CHẶN, không chép gì.
("Cloud ↔ repo", ["python3", "tools/doi_chieu_ba_ben.py", "."]),
```

Làn này chỉ đọc, nên đặt ở đâu trong thứ tự cũng an toàn; nhưng để **trước** làn ③
thì tốt hơn: biết có xung đột tên trước khi ③ chép skill sang hai runtime.

---

## 5. Dùng công cụ ở cả ba nơi

```bash
# Trên máy bác sĩ (có đủ ba bên):
python3 tools/doi_chieu_ba_ben.py ~/Documents/GitHub/EBM-drluanbv175

# Trong phiên cloud (không có ~/.codex, phần "cục bộ" sẽ báo trống — đúng):
python3 tools/doi_chieu_ba_ben.py /đường/dẫn/tới/ebm-drluanbv175

# Cho CI / script:
python3 tools/doi_chieu_ba_ben.py <repo> --json
```

Mã thoát: `0` khớp · `1` lệch bản hoặc thiếu/thừa · `2` **có trùng tên khác nội
dung, đừng chép gì** · `3` **không đo được — đây KHÔNG phải "đã khớp"**.

Mặc định chỉ so skill `custom` của bác sĩ, bỏ qua skill do Anthropic phát hành
(`docx`, `pptx`, `pdf`, `xlsx`, `skill-creator`...). Thêm `--tat-ca` nếu muốn so hết.

---

## 6. Một lỗi của chính công cụ này, đã sửa

Bản đầu dùng Jaccard theo **dòng**. Nó báo `antifacts` là "KHÁC HẲN" với độ trùng
0,0% — sai. Đọc file thì thấy bản cloud của `antifacts` là **cùng một skill nhưng
đã bị dàn phẳng**: bỏ đề mục, gộp các gạch đầu dòng thành câu dài. Nội dung gần như
y nguyên, nhưng không một *dòng* nào trùng.

Đã đổi sang Jaccard theo **từ** (miễn nhiễm với việc xuống dòng). Đo lại trên bộ
EBM thật, hai nhóm tách sạch và không chồng lấn:

| | theo dòng | theo từ |
|---|---|---|
| khác skill thật (7 ca) | 0,1–0,9% | **6,2–18,8%** |
| cùng skill (13 ca) | 0,0–99,8% | **53,6–98,6%** |

Ngưỡng 0,35 nằm giữa khoảng trống 18,8% → 53,6%. Chỉ số theo dòng vẫn được tính
nhưng chỉ dùng làm bằng chứng phụ: từ giống nhiều mà dòng giống rất ít thì gắn nhãn
`[cloud bị dàn phẳng]`. Trên dữ liệu thật đúng một skill dính nhãn này: `antifacts`.

Ca hồi quy đã đưa vào `tests/test_doi_chieu_ba_ben.py`.
