# Phản hồi THẬT của API — mẫu đối chứng cho `lay_coi_tai_tro.py`

Khác hẳn `tools/mau-thu-lay-coi/` (dữ liệu **giả**, DOI `10.9999/…`). Thư mục này chứa
**phản hồi thật** do máy có mạng lưu lại bằng `--luu-tho`, để:

1. **Đối chứng bộ bóc tách** — phiên viết ra công cụ bị chặn egress nên chỉ viết theo tài
   liệu API, chưa từng thấy dữ liệu thật. Có thư mục này thì sửa được chỗ lệch.
2. **Kiểm hồi quy mãi về sau** — `--tu-tho tools/mau-that-lay-coi` chạy lại được ở bất kỳ
   đâu, kể cả nơi không có mạng.

Đây là **siêu dữ liệu thư mục học công khai** (tên bài, tạp chí, cơ quan tài trợ, câu COI đã
công bố). **Không** chứa thông tin người bệnh.

## Cách tạo (chạy trên máy có mạng)

```bash
python3 tools/lay_coi_tai_tro.py EBM-Dashboards/CapNhat_EBM_SaSutTriTue_20260908.md \
        --luu-tho tools/mau-that-lay-coi/
git add tools/mau-that-lay-coi/ && git commit -m "chore: lưu phản hồi thật để đối chứng bộ bóc tách"
```

Rồi **mở vài tệp** đối chiếu bằng mắt với bảng công cụ in ra. Lệch chỗ nào thì báo, sửa
bộ bóc tách rồi chạy lại bằng `--tu-tho` — **không cần gọi mạng lần nữa**.
