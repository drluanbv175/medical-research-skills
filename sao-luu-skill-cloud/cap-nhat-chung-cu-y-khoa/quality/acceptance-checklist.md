# Acceptance checklist — câu trả lời EBM theo yêu cầu

Trước khi bàn giao, kiểm tra:

## Câu hỏi và phạm vi
- [ ] Xác định đúng vấn đề cụ thể, bối cảnh và quần thể.
- [ ] Không tự mở rộng sang Dashboard/tác vụ định kỳ khi chưa được yêu cầu.

## Nguồn và tính hiện hành
- [ ] Các kết luận có thể đổi thực hành đều có nguồn gốc chính thức hoặc nguồn nghiên cứu phù hợp.
- [ ] Đã xác minh tiêu đề, tổ chức, ngày/phiên bản, quần thể và nội dung liên quan.
- [ ] Đã phân biệt điểm mới với kiến thức nền.
- [ ] Không sử dụng preprint/tin tức/quảng cáo làm căn cứ đổi thực hành.

## Độ tin cậy
- [ ] Không tự gán GRADE hoặc quy đổi grading.
- [ ] Nếu có High/Moderate/Low vận hành, đã ghi rõ không phải phân hạng chính thức.
- [ ] Dùng công cụ thẩm định phù hợp nếu bác sĩ yêu cầu đánh giá nguồn.

## PICO (khi câu hỏi về hiệu quả/an toàn can thiệp)
- [ ] Mỗi can thiệp có khối PICO đủ 5 dòng (P–I–C–O + chứng cứ tốt nhất + grading từ nguồn + kết luận).
- [ ] Hiệu số (point estimate + CI/p) trích đúng như nguồn, không tự tính/làm tròn gây sai lệch.
- [ ] Nêu cả hai chiều khi chứng cứ không đồng nhất; đánh dấu `[CẦN BỔ SUNG]` khi chỉ có đồng thuận/nguyên lý.

## An toàn và áp dụng
- [ ] Có hành động thực hành cụ thể.
- [ ] Có cờ đỏ/chuyển tuyến nếu liên quan.
- [ ] Có nhóm đặc biệt liên quan: tuổi cao, CKD, bệnh gan, đa thuốc, tim mạch, ĐTĐ.
- [ ] Không bịa liều, cut-off, thời gian điều trị, DOI hoặc tương tác.
- [ ] Có ghi `[CẦN XÁC NHẬN TẠI ĐƠN VỊ]` khi phụ thuộc nguồn lực/quy định địa phương.

## Trình bày
- [ ] Tiếng Việt rõ, ưu tiên quyết định thực hành.
- [ ] Bảng chỉ dùng cho dữ liệu ngắn gọn, không nhồi đoạn văn dài.
- [ ] Tài liệu tham khảo chỉ gồm nguồn đã kiểm tra.
- [ ] Nguồn ghi dạng văn bản thường (tác giả/tổ chức + năm + tạp chí) và Vancouver/NLM.
- [ ] Đã rà soát: KHÔNG còn thẻ markup trích dẫn thô hay mã kỹ thuật lẫn trong câu trả lời.

---

## Bổ sung 08/9/2026 — chống lặp lại lỗi đã xảy ra

Mỗi mục dưới đây tương ứng một lỗi ĐÃ XẢY RA THẬT, không phải giả định.

| # | Phải kiểm | Lỗi đã xảy ra nếu bỏ qua |
|---|---|---|
| 1 | Có tệp `CapNhat_EBM_*.md` theo mẫu 11 mục **và** `kiem_mau_cap_nhat.py` báo ĐÚNG MẪU | Lần đầu chỉ giao Web Dashboard, không có bản cập nhật văn bản nào |
| 2 | `verify_dashboard.py --online` ra **PASS thật**; nếu `⊘ KHÔNG KẾT LUẬN` thì phải nêu ghi vết trong bản giao | Cổng từng in PASS với 17 PMID chưa xác minh dòng nào |
| 3 | Hiệu số phi-tỷ-số đặt ở `effectText`, KHÔNG nhét vào `effect` | Forest plot lấy mốc vô hiệu 1,0 — vẽ sai cho chênh lệch trung bình |
| 4 | `rob` để trống nếu chưa đọc đủ phương pháp | Chấm RoB 2 theo cảm tính là bịa phân hạng |
| 5 | Phái sinh in **nguyên văn `gradeSource`**, không có chuỗi "GRADE &lt;mức&gt;" tự dựng | Dàn ý slide từng ghi "GRADE Cao" cho nguồn không hề cung cấp GRADE |
| 6 | Chuỗi trong khối `DATA` dùng dấu nháy cong `“ ”`, không dùng `"` thẳng | Dấu `"` thẳng làm vỡ bộ đọc mảng → tờ dặn có gạch đầu dòng cụt |
| 7 | Đã dựng **trang đọc được** bằng `render_ban_cap_nhat.py` và giao link | Bác sĩ không mở được `.md`/`.html` gửi kèm trong khung chát |
| 8 | Trang đọc: bảng **vừa khung**, không cuộn ngang; chữ không rơi về Times New Roman | `white-space:nowrap` ở `th` và ở nhãn `[CẦN …]` đẩy bảng tràn; Poppins không có bộ ký tự tiếng Việt |
| 9 | **Đã chạy kiểm bài RÚT** và ghi kết quả + ngày vào mục 10 của bản cập nhật | Bài đã bị rút làm nền cho khuyến cáo — kiểu hỏng nặng nhất của cả hệ thống |
| 10 | Dòng trạng thái cổng trong bản cập nhật khớp kết quả cổng thực tế | Tài liệu từng ghi "PASS" trong khi cổng trả PASS CÓ ĐIỀU KIỆN |
