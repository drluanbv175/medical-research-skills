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

**Lưu ý khi chạy `--online`:** bước xác minh PMID gọi trực tiếp NCBI E-utilities
(`eutils.ncbi.nlm.nih.gov`). Ở môi trường có chặn egress, bước này trả về cảnh báo
"chưa xác minh được (lỗi mạng)" — **không phải lỗi cứng**. Khi đó phải xác minh PMID bằng
đường khác (ví dụ trình duyệt, hoặc kết nối PubMed sẵn có) và **ghi lại cách đã xác minh**.

**Lưu ý về nhãn `gradeLevel`:** trường này chỉ dùng để tô màu/lọc trên dashboard.
Phân hạng NGUYÊN BẢN của nguồn nằm ở trường `gradeSource`. Khi nguồn không cung cấp phân hạng,
`gradeSource` phải ghi rõ điều đó và nói rõ mức hiển thị là **đánh giá vận hành**.
Các sản phẩm phái sinh sinh tự động có thể rút gọn thành "GRADE …" — cần đính chính khi dùng để giảng dạy.

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
