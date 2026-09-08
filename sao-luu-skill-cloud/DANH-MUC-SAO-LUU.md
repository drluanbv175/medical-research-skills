# Danh mục sao lưu skill cloud — đợt 08/9/2026 (18 skill)

Thư mục `sao-luu-skill-cloud/` trước đợt này giữ **7 skill một file**. Đợt này bổ sung
**18 skill tiếng Việt** còn lại của bác sĩ mà **không tồn tại ở bất kỳ đâu trong repo**
(đã kiểm bằng `find -type d -name <tên>` trước khi chép).

Chép **nguyên cây thư mục, từng byte**, không sửa một ký tự. `diff -rq` với bundle tài
khoản: **18/18 khớp**.

- Bundle nguồn: `663e40d7-aa1d-4124-9a79-2c3563badb4c_1f8efc2f-396b-4507-8f3f-05e10bf3c606`
- Ngày sao lưu: 2026-09-08
- Nhánh: `claude/sao-luu-18-skill-cloud` (tách khỏi `main`)

> Skill `cap-nhat-chung-cu-y-khoa` (30 file) được sao lưu ở nhánh
> `claude/dementia-diagnosis-treatment-m0slk2` trong cùng ngày, nên **không** lặp lại ở đây.
> Sau khi cả hai nhánh vào `main`, thư mục sẽ có đủ **26 skill**.

## Bảng đối chiếu

| Skill | Số file | KB | `SKILL.md` (byte) | SHA-256 `SKILL.md` (16 ký tự đầu) |
|---|---:|---:|---:|---|
| `antifacts` | 1 | 8 | 2839 | `0301da0eac0a9cba` |
| `clinical-evidence-rag` | 5 | 36 | 3008 | `f9d082083d166a24` |
| `dao-tao-slide-tai-lieu-y-khoa` | 4 | 36 | 6628 | `4890fcb8a343f998` |
| `dark-analyst` | 18 | 232 | 30605 | `50ed2aff43313314` |
| `dashboard-master-ebm-ngoai-tru` | 12 | 152 | 8576 | `4e8d3dde45afa091` |
| `ebm-master` | 1 | 292 | 291682 | `7e87c1b8ae1c9e68` |
| `ehospital-mini` | 1 | 8 | 3176 | `4e4da21cbddda276` |
| `giao-tiep-quyet-dinh-soap` | 1 | 12 | 4580 | `c731dc516fce0631` |
| `ke-don-an-toan-benh-man` | 1 | 12 | 5347 | `5a569b288e389054` |
| `kham-ngoai-tru-ebm` | 1 | 20 | 14172 | `e147ba81528fd920` |
| `nghien-cuu-ebm-tong-hop` | 8 | 56 | 4626 | `3c8c3bf92724a971` |
| `nghien-cuu-y-khoa-chuan-quoc-te` | 38 | 220 | 11329 | `e8cbb7ad05888ae7` |
| `nguoi-cao-tuoi-da-benh-da-thuoc` | 2 | 28 | 8581 | `871b77a81e49473e` |
| `quan-ly-cap-nhat-ebm` | 1 | 8 | 3148 | `a599c7e6f2fdb758` |
| `tao-video-tiktok` | 8 | 80 | 4580 | `42f3fbec5f5ffe24` |
| `tham-dinh-chung-cu-grade-nnt` | 1 | 12 | 5146 | `6dd16cf11b05146b` |
| `tiep-can-chan-doan-co-do-chuyen-tuyen` | 1 | 12 | 5830 | `9ea80bdeb7331063` |
| `tuan-thu-dieu-tri` | 1 | 20 | 13108 | `6d6b7389a7cedae1` |
| **Tổng** | **105** | **1244** | | |

## Vì sao thư mục này có `.gitignore` riêng

`.gitignore` ở gốc repo có hai quy tắc sẽ **âm thầm nuốt mất** file của skill:

| Quy tắc gốc | File bị mất nếu không ghi đè |
|---|---|
| `*.html` | `dark-analyst/templates/web-dashboard-{dark-analyst,evidence-workbench,van-de-cu-the-clinical-quick-view}.html` |
| `test_*` | `clinical-evidence-rag/scripts/test_clinical_calculator.py` |

Vì vậy `sao-luu-skill-cloud/.gitignore` có `!*.html` và `!test_*`. **Đừng xoá file này** —
xoá đi thì lần sao lưu sau sẽ thiếu 4 file mà `git status` không báo gì.

## Kiểm bản sao còn khớp bundle

```bash
for n in $(ls -d sao-luu-skill-cloud/*/ | xargs -n1 basename); do
  diff -rq ~/.claude/skills/synced/*/"$n" "sao-luu-skill-cloud/$n" >/dev/null 2>&1 \
    && echo "OK   $n" || echo "LỆCH $n"
done
```

Báo `LỆCH` nghĩa là bản trên tài khoản đã đổi kể từ ngày sao lưu. **Xem bản nào mới hơn
rồi mới cập nhật** — đừng chép ngược từ đây lên tài khoản khi chưa đối chiếu.

## Đây là BẢN SAO LƯU, không phải nguồn chạy

Nguồn chạy vẫn là bundle trên tài khoản Claude. Thư mục này tồn tại để trả lời đúng một
câu hỏi: *nếu mất tài khoản, có lấy lại được skill không?*
