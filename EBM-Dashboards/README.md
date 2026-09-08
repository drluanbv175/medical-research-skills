# EBM-Dashboards — Thư mục tích luỹ bản cập nhật chứng cứ theo vấn đề lâm sàng

Thư mục này chứa các **Web Dashboard EBM độc lập** sinh ra bởi skill `cap-nhat-chung-cu-y-khoa`,
cùng thư viện chỉ mục và các sản phẩm phái sinh.

> ⚠ **Các dashboard ở đây KHÔNG phải Dashboard Master và KHÔNG phải nội dung đã được duyệt vào Master.**
> Đây là công cụ tra cứu nhanh tại điểm chăm sóc cho một vấn đề lâm sàng cụ thể.
> Mọi nội dung **cần bác sĩ kiểm chứng** trước khi áp dụng cho người bệnh cụ thể.

---

## Cấu trúc

```
EBM-Dashboards/
├── CapNhat_EBM_<ChuDe>_YYYYMMDD.md                      # bản cập nhật viết theo mẫu chuyên sâu
├── WebDashboard_EBM_VanDeCuThe_<ChuDe>_YYYYMMDD.html   # dashboard theo vấn đề
├── evidence-library.html                                # chỉ mục mọi bản cập nhật (tự sinh)
├── library.json                                         # dữ liệu chỉ mục
├── derivatives/                                         # tờ dặn người bệnh · dàn ý slide · kịch bản TikTok
├── tools/                                               # bộ công cụ của skill (bản sao để chạy tại chỗ)
└── data/drug_flags.json                                 # bảng cờ Beers 2023 / STOPP-START v3 (cô đọng)
```

## Dây chuyền chuẩn cho mỗi bản cập nhật

Chạy trong thư mục `EBM-Dashboards/`:

```bash
python3 tools/verify_dashboard.py <dashboard>.html --online   # 1. cổng liêm chính (phải PASS)
python3 tools/drug_safety_scan.py <dashboard>.html            # 2. lớp phủ an toàn thuốc (nếu có thuốc)
python3 tools/build_library.py add <dashboard>.html           # 3. cập nhật thư viện chỉ mục
python3 tools/make_derivatives.py <dashboard>.html            # 4. sinh 3 sản phẩm phái sinh
```

**Cổng FAIL CLOSED (từ 08/9/2026).** Bước xác minh PMID gọi trực tiếp NCBI E-utilities
(`eutils.ncbi.nlm.nih.gov`). Ở môi trường chặn egress, cổng **không in PASS** mà trả:

| Kết quả | Mã thoát | Nghĩa là |
|---|:--:|---|
| `✓ PASS` | 0 | Không lỗi cứng; nếu chạy `--online` thì **mọi PMID đã phân giải** |
| `✗ FAIL` | 1 | Có lỗi cứng (thiếu định danh, PMID không phân giải, thiếu disclaimer…) |
| `⊘ KHÔNG KẾT LUẬN` | 2 | Không lỗi cứng nhưng **chưa xác minh được PMID** (mạng chặn) |
| `✓ PASS CÓ ĐIỀU KIỆN` | 0 | Đã dùng `--offline-ok`; báo cáo kèm dòng **GHI VẾT** số PMID chưa xác minh |

Lý do: *chưa xác minh* khác *đã xác minh*. Trước bản sửa này, mạng chặn vẫn ra PASS —
nghĩa là một PMID bịa sẽ lọt cổng ở mọi môi trường không có mạng.

Khi buộc phải giao trong hoàn cảnh mạng chặn: dùng `--offline-ok`, xác minh PMID bằng
đường khác (kết nối PubMed, trình duyệt) và **nói rõ cách đã xác minh trong bản giao**.

**Lưu ý về nhãn `gradeLevel`:** trường này chỉ dùng để tô màu/lọc trên dashboard.
Phân hạng NGUYÊN BẢN của nguồn nằm ở trường `gradeSource`. Khi nguồn không cung cấp phân hạng,
`gradeSource` phải ghi rõ điều đó và nói rõ mức hiển thị là **đánh giá vận hành**.
Từ 08/9/2026, dàn ý slide in **nguyên văn `gradeSource`** — không còn tự dựng chuỗi
"GRADE <mức>" từ `gradeLevel`, nên không cần đính chính thủ công nữa.

**Hiệu số phi-tỷ-số:** dùng `effectText` (chênh lệch trung bình, %, SMD…), KHÔNG nhét vào
`effect` — forest plot lấy mốc vô hiệu là 1,0 nên sẽ vẽ sai cho hiệu số hiệu. `rob` (RoB 2)
chỉ dành cho RCT và được gắn nhãn **đánh giá vận hành**; để trống tốt hơn là đoán.

**Kiểm đồng bộ toàn hệ thống:** `python3 ../tools/kiem_dong_bo_skill_ebm.py` — bắt trôi lệch
giữa bundle tài khoản, bản sao lưu git và bản chạy tại chỗ trong `tools/` này.

## Danh mục hiện có

| Ngày | Vấn đề lâm sàng | Bản cập nhật (mẫu chuyên sâu) | Dashboard | Số item |
|---|---|---|---|---|
| 2026-09-08 | Sa sút trí tuệ — chẩn đoán và điều trị theo chứng cứ (ngoại trú Việt Nam) | `CapNhat_EBM_SaSutTriTue_20260908.md` | `WebDashboard_EBM_VanDeCuThe_SaSutTriTue_20260908.html` | 17 |

**Mỗi bản cập nhật gồm HAI phần, không thay thế nhau:**
- **Văn bản** `CapNhat_EBM_*.md` — viết theo mẫu `templates/mau-cap-nhat-chuyen-sau.md`
  của skill `cap-nhat-chung-cu-y-khoa` (11 mục, có thẩm định nguồn và tài liệu tham khảo
  Vancouver). Đây là bản để đọc, in, đưa vào hồ sơ chuyên môn hoặc dùng làm nền soạn bài giảng.
- **Dashboard** `WebDashboard_EBM_*.html` — bản tra cứu nhanh tại điểm chăm sóc.

Mở `evidence-library.html` để tra cứu và lọc toàn bộ thư viện.

## Quy tắc dữ liệu

- Không lưu thông tin định danh người bệnh (PII) trong bất kỳ file nào.
- Mọi điểm chứng cứ phải có ít nhất một định danh truy nguyên (PMID hoặc DOI).
- Tờ dặn người bệnh và kịch bản TikTok **không nêu liều thuốc** và phải được bác sĩ duyệt trước khi phát hành.
- Không tự tạo mã quản trị (`EBM-W-…`, `MED-W-…`, `SCORE-Q-…`) khi bác sĩ chưa yêu cầu đưa vào Dashboard Master.
