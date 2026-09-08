# Tải lên 5 skill đã sửa đường tra cứu — 2026-09-08

Phiên Claude **không ghi được** vào bundle skill trên tài khoản. Bản sửa nằm trong git;
bác sĩ phải tự tải lên thì skill đang chạy mới đổi theo.

## Việc phải làm

```bash
# đã đóng gói sẵn, chỉ cần chạy lại nếu muốn dựng mới
python3 tools/dong_goi_skill_de_tai_len.py <tên-skill>
```

Tải 5 gói trong `dist/` lên phần quản lý Skills, **thay thế** skill cùng tên (đừng tạo bản trùng tên):

| Skill | Gói | SHA-256 của `SKILL.md` (16 ký tự đầu) |
|---|---|---|
| `paper-lookup` | `dist/paper-lookup.zip` | `121743ca14fe0327` |
| `citation-management` | `dist/citation-management.zip` | `18f871a7426638e1` |
| `research-lookup` | `dist/research-lookup.zip` | `434696688f034581` |
| `literature-review` | `dist/literature-review.zip` | `d66dd9c2f74d025e` |
| `nghien-cuu-ebm-tong-hop` | `dist/nghien-cuu-ebm-tong-hop.zip` | `8b0fc65fa30575bf` |

Sau khi tải lên, mở **phiên mới** rồi chạy:

```bash
python3 tools/kiem_dong_bo_skill_ebm.py
```

Đạt khi **hết dòng `LỆCH bundle↔sao-lưu`** cho 5 skill này.

## Sửa cái gì, vì sao

Cả 5 skill mô tả cách làm việc là **gọi API miễn phí bằng curl/python** (PubMed E-utilities,
Crossref, Europe PMC, ClinicalTrials.gov API v2, OpenAlex, Unpaywall). Phép đo ngày 2026-09-05
(`de-xuat/NANG-LUC-PHIEN-CLOUD.md`, gọi thật) cho thấy **mọi tên miền y khoa đều bị chặn ở tầng
chính sách** trong phiên cloud. Nghĩa là phương pháp đã ghi **không chạy được** — và nguy hiểm
nhất là nó trả lỗi mạng, rất dễ bị báo cáo nhầm thành *"không tìm thấy bài nào"*.

Nay: **connector trước, API trực tiếp sau** (kèm lệnh `curl` kiểm nhanh tên miền có mở không),
bảng năng lực ghi rõ đường nào chạy · đường nào chặn · giới hạn từng công cụ, và quy tắc
**không tra được ≠ không có**. Bản chuẩn dùng chung: `de-xuat/DUONG-TRA-CUU-Y-VAN.md`.

Không ghi cứng tên connector ở bất cứ đâu — tên đã đổi **ngay trong một phiên**
(`mcp__290a5fde-…__search_articles` → `mcp__PubMed__search_articles`); mọi chỗ đều dùng
`ToolSearch` theo chức năng.

## Đường tra cứu cũ có bị xoá không

**Không.** Đoạn API miễn phí trực tiếp vẫn còn nguyên trong `paper-lookup`, chỉ bị **đặt sau**
và **kèm điều kiện**: trên máy của bác sĩ, nơi egress mở, đó vẫn là đường tốt và miễn phí.
