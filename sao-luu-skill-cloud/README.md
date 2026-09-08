# Sao lưu 7 skill EBM bản CLOUD

Bảy skill này do bác sĩ tự viết và tải lên **tài khoản Claude**. Chúng chạy trong
mọi phiên claude.ai/code và trong hai Routine giám sát hàng tuần/hàng tháng.

## Vì sao có thư mục này

Ngày 06/09/2026, đối chiếu ba bên bằng `tools/doi_chieu_ba_ben.py` phát hiện: bảy
skill này **không có bản nào trong git**. Trong repo `ebm-drluanbv175`, bảy cái tên
đó đang bị một họ skill KHÁC chiếm chỗ — bản K-Dense tiếng Anh, được
`sync/skills/_vietnamize.py` Việt hóa phần đầu.

Dò toàn repo bằng cụm chữ đặc trưng của bản cloud:

| Cụm chữ | Số file tìm thấy trong repo |
|---|---|
| "6 lăng kính" (skill `peer-review`) | **0** |
| "Cổng cứng trích dẫn" (skill `scientific-writing`) | **1** — và đó là agent đã lưu trữ trong `.claude/agents/_archive/`, không phải skill |

Nghĩa là trước bản sao lưu này, **mất tài khoản là mất trắng bảy skill**.

## Đây là BẢN SAO LƯU, không phải nguồn chạy

Nơi ở đúng của chúng là `ebm-drluanbv175/sync/skills/<tên>-vn/` — hậu tố `-vn` để
không đè lên họ K-Dense đang giữ tên gốc. Phiên cloud không có quyền ghi vào repo
đó, nên đặt tạm ở đây.

Chép **nguyên văn từng byte** từ bundle tài khoản (`cmp` xác nhận 7/7 khớp), không
sửa một ký tự nào.

| Skill | Cập nhật trên tài khoản | Byte | SHA-256 (16 ký tự đầu) |
|---|---|---:|---|
| `citation-management` | 2026-06-13 | 2,774 | `8ed95b20cba6fb64` |
| `literature-review` | 2026-06-13 | 3,025 | `45352e170d8c4e33` |
| `paper-lookup` | 2026-06-13 | 3,196 | `be5799833789e56d` |
| `peer-review` | 2026-06-13 | 2,850 | `03525dcfae47e6c4` |
| `research-lookup` | 2026-06-13 | 3,019 | `8f7d77001cdc13e0` |
| `scientific-writing` | 2026-06-13 | 3,790 | `034439bfbb7f4ce5` |
| `statistical-analysis` | 2026-06-13 | 4,599 | `e031a583dec56866` |

- Bundle nguồn: `663e40d7-aa1d-4124-9a79-2c3563badb4c_1f8efc2f-396b-4507-8f3f-05e10bf3c606`
- Ngày sao lưu: 2026-09-06

## Kiểm bản sao còn khớp bundle

```bash
for n in citation-management literature-review paper-lookup peer-review research-lookup scientific-writing statistical-analysis; do
  cmp -s ~/.claude/skills/synced/*/"$n"/SKILL.md "sao-luu-skill-cloud/$n/SKILL.md" \
    && echo "OK   $n" || echo "LỆCH $n"
done
```

Nếu báo LỆCH: bản trên tài khoản đã đổi kể từ ngày sao lưu. Xem bản nào mới hơn
rồi cập nhật thư mục này — đừng chép ngược từ đây lên tài khoản mà chưa xem.

---

## Bổ sung 08/9/2026 — skill NHIỀU FILE đầu tiên

Bảy skill ở trên là skill **một file** (`SKILL.md`). Bản bổ sung này là skill **nhiều
file** đầu tiên trong thư mục, nên chép **toàn bộ cây thư mục**, không chỉ `SKILL.md`.

| Skill | Số file | Dung lượng | `SKILL.md` (byte) | SHA-256 `SKILL.md` (16 ký tự đầu) |
|---|---:|---:|---:|---|
| `cap-nhat-chung-cu-y-khoa` | 30 | 316 KB | 36.358 | `9819e01310f8f500` |

Gồm: `SKILL.md`, `README.md`, `CHANGELOG.md`, `references/` (11 file), `templates/`
(8 file — trong đó có **`mau-cap-nhat-nhanh.md`** và **`mau-cap-nhat-chuyen-sau.md`**,
tức "mẫu cập nhật chứng cứ", cùng 3 template Web Dashboard), `tools/` (5 script),
`data/drug_flags.json`, `quality/` (2 checklist).

`diff -rq` với bundle tài khoản: **khớp toàn bộ**, không sửa một ký tự nào.

### Vì sao phải có `.gitignore` riêng trong thư mục này

`.gitignore` ở gốc repo loại trừ `*.html`. Ba template Web Dashboard của skill này là
file `.html`; nếu không ghi đè, bản sao lưu sẽ **thiếu đúng phần quan trọng nhất**.
Vì vậy thư mục này có `.gitignore` với dòng `!*.html`.

### Kiểm bản sao nhiều file còn khớp bundle

```bash
diff -rq ~/.claude/skills/synced/*/cap-nhat-chung-cu-y-khoa \
         sao-luu-skill-cloud/cap-nhat-chung-cu-y-khoa && echo "OK"
```

## CÒN THIẾU — 18 skill tiếng Việt chưa có bản nào trong git

Rà ngày 08/9/2026: bundle tài khoản có **26 skill tiếng Việt do bác sĩ tự viết**;
thư mục này mới giữ **8**. Mười tám skill dưới đây **không tồn tại ở bất kỳ đâu trong
repo** (đã kiểm bằng `find -type d -name <tên>`), nghĩa là vẫn đúng tình trạng mà
README này cảnh báo ở trên: **mất tài khoản là mất trắng**.

| Skill | Số file | Dung lượng |
|---|---:|---:|
| `antifacts` | 1 | 8 KB |
| `clinical-evidence-rag` | 5 | 36 KB |
| `dao-tao-slide-tai-lieu-y-khoa` | 4 | 36 KB |
| `dark-analyst` | 18 | 232 KB |
| `dashboard-master-ebm-ngoai-tru` | 12 | 152 KB |
| `ebm-master` | 1 | 292 KB |
| `ehospital-mini` | 1 | 8 KB |
| `giao-tiep-quyet-dinh-soap` | 1 | 12 KB |
| `ke-don-an-toan-benh-man` | 1 | 12 KB |
| `kham-ngoai-tru-ebm` | 1 | 20 KB |
| `nghien-cuu-ebm-tong-hop` | 8 | 56 KB |
| `nghien-cuu-y-khoa-chuan-quoc-te` | 38 | 220 KB |
| `nguoi-cao-tuoi-da-benh-da-thuoc` | 2 | 28 KB |
| `quan-ly-cap-nhat-ebm` | 1 | 8 KB |
| `tao-video-tiktok` | 8 | 80 KB |
| `tham-dinh-chung-cu-grade-nnt` | 1 | 12 KB |
| `tiep-can-chan-doan-co-do-chuyen-tuyen` | 1 | 12 KB |
| `tuan-thu-dieu-tri` | 1 | 20 KB |
| **Tổng** | **105** | **~1,2 MB** |

Chưa sao lưu 18 skill này trong lần commit ngày 08/9/2026 vì nhánh đang dùng là nhánh
nội dung lâm sàng (sa sút trí tuệ); việc sao lưu cả bộ nên đi bằng một nhánh riêng để
lịch sử git đọc được. **Cần bác sĩ quyết định** trước khi thực hiện.
