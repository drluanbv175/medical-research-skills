# Bốn việc đóng khoảng trống "phiên cloud không có mạng" — 2026-09-09

Mọi khoản treo của hệ thống đều cùng một gốc: **phiên cloud bị chặn toàn bộ tên miền y khoa
ở tầng chính sách**. Bốn việc dưới đây đánh vào gốc đó từ bốn phía; làm cả bốn thì hết.

| # | Việc | Ai làm | Trạng thái |
|---|---|---|---|
| 1 | Nới network policy cho 3 host | **Bác sĩ** (cài đặt tài khoản) | chờ bác sĩ |
| 2a | Lưu phản hồi API thật làm mẫu đối chứng | **Bác sĩ** (một lệnh, máy có mạng) | chờ bác sĩ |
| 2b | Biên bản xác minh — cầu nối máy có mạng ↔ phiên cloud | đã xong | ✅ |
| 3 | Giám sát định kỳ chạy trên máy, không dùng Routine | đã xong | ✅ |

---

## 1. Nới network policy — chữa gốc

**claude.ai › Settings › Claude Code › Environments** → thêm host vào network policy.
Danh sách đầy đủ ở `references/EVIDENCE-SOURCE-ROUTING.md` §4. **Tối thiểu ba host** là đủ 90%:

| Host | Mở ra được gì |
|---|---|
| `eutils.ncbi.nlm.nih.gov` | `verify_dashboard.py --online` ra **PASS thật** · `<CoiStatement>` · `<GrantList>` |
| `www.ebi.ac.uk` | Europe PMC `fullTextXML` → câu tài trợ + COI **nguyên văn** |
| `api.crossref.org` | Retraction Watch **bộ đầy đủ** (hết lỗ hổng chỉ mục Scite) · `funder[]` |

Thêm `clinicaltrials.gov` nếu muốn `research-lookup` chạy đường gốc.

Đây là **API công khai, chỉ đọc**; không có thông tin của bác sĩ hay người bệnh nào được gửi
đi. Nhưng nới egress vẫn là quyết định an ninh mạng — nêu ra để bác sĩ cân, không tự quyết.

Kiểm sau khi nới:

```bash
python3 scripts/check_evidence_sources.py   # mã thoát 0 = mọi nguồn thông
```

**Không chữa được:** toàn văn guideline của hội chuyên ngành (`alz.org`, `academic.oup.com`…)
— phần lớn có tường phí, allowlist cũng vô ích. Đường duy nhất vẫn là bác sĩ tải PDF vào repo.

---

## 2a. Lưu phản hồi thật làm mẫu đối chứng

`tools/lay_coi_tai_tro.py` được viết trong phiên bị chặn egress, nên bộ bóc tách **chưa từng
thấy dữ liệu thật**. Một lệnh trên máy có mạng biến chuyện đó thành mẫu đối chứng vĩnh viễn:

```bash
python3 tools/lay_coi_tai_tro.py EBM-Dashboards/CapNhat_EBM_SaSutTriTue_20260908.md \
        --luu-tho tools/mau-that-lay-coi/
git add tools/mau-that-lay-coi/ && git commit -m "chore: lưu phản hồi thật để đối chứng"
```

Rồi **mở vài tệp** đối chiếu bằng mắt với bảng công cụ in ra. Lệch chỗ nào thì báo — sửa xong
chạy lại bằng `--tu-tho tools/mau-that-lay-coi`, **không cần gọi mạng lần nữa**. Đây là siêu
dữ liệu thư mục học công khai, không có thông tin người bệnh.

---

## 2b. Biên bản xác minh — đã xong

Cùng một mẫu `extract → gọi → report` mà `retraction_check.py` đã dùng: việc cần mạng chạy ở
nơi **có** mạng, kết quả đóng thành một tệp commit được, nơi **không** có mạng đọc lại tệp đó.

```bash
# trên máy có mạng
python3 tools/lap_bien_ban_xac_minh.py \
        EBM-Dashboards/WebDashboard_EBM_VanDeCuThe_SaSutTriTue_20260908.html \
        --ban-cap-nhat EBM-Dashboards/CapNhat_EBM_SaSutTriTue_20260908.md
git add EBM-Dashboards/bien-ban/ && git commit && git push

# ở phiên cloud
python3 EBM-Dashboards/tools/verify_dashboard.py <dashboard>.html \
        --bien-ban EBM-Dashboards/bien-ban/<tệp>.bien-ban.json
```

Gom ba việc cần mạng vào một lần chạy: **phân giải PMID** · **kiểm bài rút bằng bộ Retraction
Watch đầy đủ** · **lấy nguyên văn tài trợ + COI**. Bước nào không chạy được thì ghi thẳng
`CHƯA LÀM` vào biên bản, không bỏ trống.

**Ràng buộc theo tập định danh, không theo byte tệp.** Sửa lỗi chính tả trong dashboard mà mất
hiệu lực cả biên bản thì không ai dùng nổi; ngược lại **thêm item mới thì PMID của nó không có
trong biên bản → cổng báo chưa xác minh**, đúng như phải thế. sha256 lúc lập vẫn được ghi, cổng
in cảnh báo nếu tệp đã đổi.

### Lỗi fail-open đã bắt được khi tự kiểm

Bản đầu: biên bản mà **không xác minh được PMID nào** vẫn cho ra `✓ PASS` kèm dòng *"đã xác
minh theo biên bản"* — đúng loại lỗi cả hệ thống này sinh ra để chặn. Nguyên nhân: mục có
`phan_giai: null` bị bỏ qua thay vì tính là **chưa xác minh**. Nay mọi PMID đều phải có phán
định khi đã đưa biên bản vào, và dòng ghi vết chỉ được nói "theo biên bản" kèm **số thật**
(`17/17 PMID theo biên bản lập …`).

Sáu ca đã thử: biên bản đủ → PASS + ghi vết đúng số · biên bản rỗng → ⊘ KHÔNG KẾT LUẬN ·
biên bản thiếu 1 mã → ⊘, chỉ đúng mã thiếu · sha lệch → cảnh báo, vẫn dùng được ·
không biên bản không `--online` → như cũ · `--online --offline-ok` → như cũ.

---

## 3. Giám sát định kỳ chạy trên máy — đã xong

Chi tiết + đoạn cấu hình launchd/cron/Task Scheduler: **`de-xuat/GIAM-SAT-TREN-MAY.md`**.

```bash
python3 tools/chay_giam_sat_dinh_ky.py --tao-watchlist   # dựng từ library.json, mọi chủ đề TẮT
# điền `query` cho từng chủ đề rồi bật active=true
python3 tools/chay_giam_sat_dinh_ky.py --days 30 --khong-day   # chạy thử
```

Kèm một bản vá quan trọng cho `surveillance_scan.py`: trước đây lỗi truy vấn bị nuốt thành
dòng `- (lỗi truy vấn: …)` rồi chân trang vẫn ghi *"Tổng 0 ứng viên"* — đọc lướt thành **"không
có gì mới"**. Với việc chạy tự động không người trông, đó là kiểu hỏng nguy hiểm nhất. Nay báo
cáo mở đầu bằng `⊘ KHÔNG KẾT LUẬN cho n/N chủ đề` và mã thoát là **2**.

---

## Sau khi làm xong cả bốn

| Khoản đang treo | Đóng bằng |
|---|---|
| 17 PMID chưa xác minh → `PASS CÓ ĐIỀU KIỆN` | 1 hoặc 2b |
| 14/17 ô COI `[CẦN KIỂM CHỨNG]` | 1 hoặc 2b (bước 3 của biên bản) |
| Bộ bóc tách COI chưa đối chứng | 2a |
| Chỉ mục Scite không phủ 100% khi kiểm bài rút | 1 (Crossref) hoặc 2b |
| Không giám sát định kỳ được | 3 |
| Không đọc được toàn văn guideline hội chuyên ngành | **không việc nào** — bác sĩ tải PDF vào repo |
