---
name: scientific-writing
description: Viết bản thảo khoa học y khoa theo cấu trúc IMRAD, văn xuôi liền mạch, khớp CHUẨN BÁO CÁO đúng thiết kế (CONSORT/STROBE/PRISMA/SPIRIT/STARD/TRIPOD+AI; COREQ/SRQR cho định tính; SQUIRE cho QI). Dùng khi cần viết bài báo, protocol, hoặc báo cáo nghiệm thu; soạn Methods/Results/Discussion; đối chiếu checklist chuẩn báo cáo. Mỗi khẳng định có nguồn PMID/DOI; KHÔNG bịa số liệu/trích dẫn; nhắc khai báo AI + tác giả ICMJE + COI.
---

# Skill: Viết bản thảo khoa học (scientific-writing)

Chuyển kết quả nghiên cứu thành bản thảo mạch lạc, trung thực, đạt chuẩn tạp chí. Dùng cho `viet-ban-thao`.

## Nguyên tắc liêm chính (4 trụ cột)
- **KHÔNG bịa** trích dẫn/số liệu — chỉ viết điều dữ liệu/nguồn chống đỡ; mỗi khẳng định có **PMID/DOI**.
- Phân biệt phát hiện vs suy diễn; không overclaim; không suy nhân quả vượt thiết kế.
- Số liệu chưa có → `[CẦN BỔ SUNG]`; KHÔNG PII; nhắc khai báo **dùng AI + đóng góp tác giả (ICMJE) + COI/tài trợ** theo yêu cầu tạp chí.

## Quy trình 2 bước
**BƯỚC 0 — Tiền đề:** xác nhận kết quả từ SAP đã khóa; có mã đăng ký + số phê duyệt đạo đức THẬT (do tác giả cấp; thiếu → `[CẦN BỔ SUNG]`); chọn ĐÚNG chuẩn báo cáo theo thiết kế.
**Bước 1 — Dàn ý:** chốt thông điệp chính (1 câu) → chọn chuẩn báo cáo → lập sườn IMRAD theo checklist chuẩn đó.
**Bước 2 — Văn xuôi (liền mạch, KHÔNG gạch đầu dòng trong thân):**
- **Introduction:** khoảng trống kiến thức → mục tiêu/giả thuyết.
- **Methods:** đủ chi tiết tái lặp; nêu phê duyệt đạo đức + mã đăng ký; tham chiếu SAP.
- **Results:** chỉ sự kiện, kèm ước lượng + 95% CI; bảng/hình không lặp văn.
- **Discussion:** diễn giải trong giới hạn; đối chiếu y văn; điểm mạnh–hạn chế; ý nghĩa lâm sàng (thận trọng).

## Chọn chuẩn báo cáo theo thiết kế
| Thiết kế | Chuẩn | Ghi chú |
|---|---|---|
| RCT/thử nghiệm | **CONSORT** (+**SPIRIT** cho protocol) | sơ đồ CONSORT, ITT |
| Quan sát (cohort/bệnh-chứng/cắt ngang) | **STROBE** | nêu nhiễu, sai lệch |
| Tổng quan hệ thống/Meta | **PRISMA 2020** | +PROSPERO |
| Độ chính xác chẩn đoán | **STARD** | Se/Sp/LR/AUC |
| Mô hình dự đoán/AI | **TRIPOD+AI** | hiệu chuẩn + phân biệt + validation |
| Định tính / hỗn hợp | **COREQ/SRQR** | trustworthiness |
| Cải tiến chất lượng | **SQUIRE 2.0** | PDSA |

## 🔒 Cổng cứng trích dẫn (trước khi coi là "xong")
Mọi tham khảo phải qua kiểm chứng (skill `citation-management`/agent `kiem-chung-trich-dan`): PMID/DOI có thật + nội dung trích đúng. Trích dẫn chưa xác minh → `[TRÍCH DẪN CHƯA XÁC MINH]`, KHÔNG để lọt bản nộp.

## Mẫu đầu ra
```
Thông điệp chính (1 câu): ____ | Chuẩn báo cáo: [CONSORT/STROBE/…]
Bản thảo IMRAD (Markdown; xuất DOCX/PDF/LaTeX khi cần)
| Mục checklist chuẩn | Ở đoạn/mục nào |
Danh mục tham khảo (đã kiểm chứng PMID/DOI)
Khai báo: COI · tài trợ · đóng góp tác giả (ICMJE) · dùng AI  [tác giả xác nhận]
[CẦN BỔ SUNG]: chỗ thiếu dữ liệu
```

## Ranh giới
KHÔNG tạo dữ liệu/kết quả chưa có; KHÔNG tự quyết phân tích (nhận từ `statistical-analysis`). Bản thảo phải qua bình duyệt (`peer-review`) trước khi coi là sẵn sàng nộp. Kết: **"Cần bác sĩ kiểm chứng."**
