---
name: antifacts
description: "Dùng khi bác sĩ muốn MỞ hoặc CẬP NHẬT \"Antifacts\" — Trung tâm EBM theo chuyên khoa (gom cập nhật chứng cứ + 45 thang điểm lâm sàng + công cụ nghiên cứu theo chuyên khoa). Kích hoạt khi nghe \"Antifacts\", \"mở Antifacts\", \"cập nhật Antifacts\", \"trung tâm/hub EBM theo chuyên khoa\". KHÔNG dùng để tạo dashboard chứng cứ MỚI (dùng cap-nhat-chung-cu-y-khoa); KHÔNG phải Dashboard Master."
---

Antifacts là MẶT TIỀN (HTML tĩnh) gom mọi sản phẩm EBM trong thư mục "Claude AI" theo CHUYÊN KHOA (Tim mạch · Hô hấp · Tiêu hóa-Gan mật · Nội tiết · Thận · Thần kinh-Đột quỵ · Cơ xương khớp · Nhiễm · Tâm thần · Lão khoa · Cấp cứu · Thuốc · Tổng hợp). 4 tab: Theo chuyên khoa (mặc định) · Cập nhật · Thang điểm · Nghiên cứu. File kết quả: Antifacts.html ở gốc "Claude AI", sinh bằng tools/build_antifacts.py (chỉ dùng stdlib).

QUY TẮC EBM BẮT BUỘC: đầu ra tiếng Việt; KHÔNG bịa dữ liệu (chỉ GOM + trình bày lại nguồn đã có, giữ nguyên PMID/DOI + GRADE gốc); kèm "⚠️ Cần bác sĩ kiểm chứng"; KHÔNG PII.

QUY TRÌNH (chạy ở thư mục gốc "Claude AI"; trên Windows BẮT BUỘC đặt PYTHONUTF8=1 trước python, nếu không script crash khi in tiếng Việt). KHÔNG sửa tay Antifacts.html — đổi bố cục thì sửa tools/build_antifacts.py rồi chạy lại.

A. Mở nhanh (chỉ xem): mở Antifacts.html ở gốc trong trình duyệt.

B. Cập nhật ĐẦY ĐỦ rồi mở (mặc định khi nói "cập nhật"):
1. Trong EBM-Dashboards/: PYTHONUTF8=1 python tools/build_library.py add WebDashboard_*.html (làm giàu badge Áp dụng/Cân nhắc/PMID).
2. Ở gốc "Claude AI": PYTHONUTF8=1 python tools/build_antifacts.py
3. Mở Antifacts.html; báo số liệu (X cập nhật · 45 thang điểm · công cụ NC).

NGUỒN (chỉ đọc): EBM-Dashboards/WebDashboard_*.html (+ library.json) · medical-ebm-automation/data/reference/clinical_scores_45.json · danh mục công cụ NC trong generator.

LIÊN KẾT HUB: Antifacts nối 2 chiều với EBM_MASTER (nút "Antifacts" trên EBM_WEBAPP/DANH_MUC/EBM_LIENKET ⇄ "Hub EBM" trên Antifacts). sync_all.py (EBM_MASTER/tools) ở bước cuối tự build_library add → build_antifacts → tự cập nhật TÍCH LŨY.

GIỚI HẠN: KHÔNG tạo chứng cứ/khuyến cáo mới ở đây — thêm chủ đề mới thì dùng skill cap-nhat-chung-cu-y-khoa rồi chạy lại skill này. Cần môi trường thấy thư mục "Claude AI"; trong Cowork sandbox không thấy OneDrive thì chỉ giải thích/điều hướng, không bịa kết quả.

Kết: "Cần bác sĩ kiểm chứng."