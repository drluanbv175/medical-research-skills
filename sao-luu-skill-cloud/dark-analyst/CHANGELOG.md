# Changelog

## v1.6.0 — 2026-06-07

- **Đổi mẫu Web Dashboard MẶC ĐỊNH sang "Dark Analyst"** (nền tối, dày dữ liệu) theo lựa chọn của bác sĩ; Evidence Workbench (nền sáng) trở thành mẫu THAY THẾ.
- **Sản phẩm hóa Dark Analyst thành template tham số hóa** `templates/web-dashboard-dark-analyst.html`: chrome (tiêu đề, PICO chips, KPI, băng Clinical Quick View, verdict, bộ lọc, ô tìm) **tự sinh từ `DATA`**; bảng có cột Quyết định; click bung 3 cột thẩm định; hỗ trợ mọi loại thiết kế & mức GRADE.
- **Hai mẫu DÙNG CHUNG một schema `DATA`** (meta/summary/items[]) → một khối dữ liệu chạy được cả hai. Dark Analyst thêm field tùy chọn `effectText` (hiệu số phi-tỷ-số) và `rob` (RoB 2, chỉ RCT); giữ `frame`/`frameLabels`.
- Cập nhật SKILL.md (mục 5A, checklist, danh mục tài nguyên), `CLAUDE.md`, `DESIGN-SPEC.md` và đóng gói lại.

## v1.5.0 — 2026-06-07

- **Thêm mục 5C "Tự chọn khung câu hỏi"**: skill tự nhận diện loại câu hỏi lâm sàng và chọn khung phù hợp — ngoài **PICO(T)(S)** còn **PECO** (tác hại), **PIRT/QUADAS-2** (chẩn đoán), **PROGRESS/PICOTS** (tiên lượng), **CoCoPop** (tần suất), **SPIDER** (định tính), **ECLIPSE** (dịch vụ), PICO+chi phí (kinh tế).
- Bổ sung **mô hình tổng hợp bổ trợ**: phân tầng nguồn 6S, cân lợi ích–tác hại NNT/NNH, GRADE Evidence-to-Decision (EtD), bảng Tóm tắt phát hiện (SoF), tam giác liêm chính.
- Thêm tài liệu `references/07-mo-hinh-cau-hoi-va-khung-thay-the.md` (bảng chọn khung + cách ánh xạ vào Evidence Workbench + ví dụ).
- **Nâng template Evidence Workbench** (tương thích ngược): hỗ trợ field tùy chọn `frame` (nhãn khung) và `frameLabels` để đổi tên 4 ô P/I/C/O cho khung không phải PICO; không đặt thì hiển thị như cũ.
- Cập nhật checklist (nhận diện & nêu rõ khung đã dùng) và danh mục tài nguyên.

## v1.4.0 — 2026-06-07

- **Đổi mô hình Web Dashboard mặc định sang "Evidence Workbench"** (bố cục 3 cột: bộ lọc · Quick View + bảng điểm chứng cứ · panel thẩm định) theo lựa chọn của bác sĩ.
- Thêm template mặc định `templates/web-dashboard-evidence-workbench.html` (chỉ cần thay khối `DATA`); giữ template một-cột cũ làm fallback.
- Ba lớp nội dung bắt buộc giữ nguyên, ánh xạ vào bố cục: Clinical Quick View = băng tóm tắt + tab mặc định; Evidence Detail View = cột phải; Safety/Limits/VN = các tab riêng.
- Cập nhật bảng màu mặc định (nền sáng, dày dữ liệu) + màu ngữ nghĩa theo Quyết định/GRADE/Thiết kế; bổ sung forest plot mini và xuất CSV/JSON.
- Cập nhật mục 5A, frontmatter, checklist, danh mục tài nguyên, `references/05-…md` và `quality/web-dashboard-acceptance-checklist.md`.

## v1.3.0 — 2026-06-06

- Bổ sung **chế độ PICO**: chuẩn hóa trình bày chứng cứ theo P–I–C–O cho câu hỏi về hiệu quả/an toàn của can thiệp, kèm khối PICO 5 dòng (PICO + chứng cứ tốt nhất + grading từ nguồn + kết luận).
- Thêm mục 5B trong SKILL.md và tài liệu `references/06-pico-va-trich-dan.md` với mẫu, ví dụ và quy tắc liêm chính (trích hiệu số đúng nguồn, không tự gán GRADE, nêu cả hai chiều khi chứng cứ không đồng nhất).
- Thêm **quy tắc ghi nguồn sạch**: ghi nguồn dạng văn bản (tác giả/tổ chức + năm + tạp chí) và Vancouver/NLM; tuyệt đối không chèn thẻ markup trích dẫn thô/mã kỹ thuật vào câu trả lời; bắt buộc rà soát trước khi gửi.
- Bổ sung mục checklist tương ứng và cập nhật danh mục tài nguyên.

## v1.2.0 — 2026-06-02

- Bắt buộc tạo Web Dashboard HTML độc lập cho mỗi cập nhật EBM theo vấn đề cụ thể khi môi trường hỗ trợ tạo file.
- Áp dụng kiến trúc 3 lớp: Clinical Quick View mặc định, Evidence Detail View, Safety/Limits/Vietnam.
- Thêm schema record `ITEM-xx` cục bộ; không đồng nghĩa với ID Dashboard Master.
- Thêm template HTML tương tác có tìm kiếm, lọc, panel chi tiết, xuất CSV và tab kiểm chứng thao tác.
- Giữ nguyên nguyên tắc: chỉ tích hợp Dashboard Master/CỔNG A-B khi bác sĩ yêu cầu rõ.


## v1.1.0 — 2026-06-02

- Định nghĩa lại phạm vi: cập nhật chứng cứ cho **vấn đề lâm sàng cụ thể khi bác sĩ yêu cầu**.
- Không bắt buộc Dashboard, Web Dashboard, CỔNG A/B hoặc mã quản trị trong câu trả lời EBM thông thường.
- Bổ sung 4 tài liệu reference nội bộ còn thiếu.
- Bổ sung hai template đầu ra: nhanh và chuyên sâu.
- Bổ sung checklist nghiệm thu chất lượng.
- Tách chế độ an toàn thuốc, antibiotic stewardship, thang điểm/công cụ và thẩm định nguồn.
