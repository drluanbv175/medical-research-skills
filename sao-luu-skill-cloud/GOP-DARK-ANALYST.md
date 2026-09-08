# Gộp `dark-analyst` vào `cap-nhat-chung-cu-y-khoa` — 08/9/2026

## Vì sao phải gộp

Hai skill có **mô tả kích hoạt giống hệt nhau**. Khi bác sĩ yêu cầu cập nhật chứng cứ,
hệ thống có thể chọn `dark-analyst` — và bản `dark-analyst` **thiếu toàn bộ `tools/`**:

| Thiếu ở `dark-analyst` | Hậu quả nếu bị kích hoạt nhầm |
|---|---|
| `tools/verify_dashboard.py` | **Không cổng liêm chính nào chạy** — PMID không được xác minh |
| `tools/kiem_mau_cap_nhat.py` | Không kiểm bản cập nhật có đúng mẫu 11 mục |
| `tools/make_derivatives.py` | Không có tờ dặn người bệnh / dàn ý slide / kịch bản TikTok |
| `tools/build_library.py` | Không vào thư viện chỉ mục |
| `tools/drug_safety_scan.py` + `data/drug_flags.json` | Không có lớp phủ Beers / STOPP-START |
| `tools/render_ban_cap_nhat.py` | Không dựng được trang đọc/in |
| `references/08`–`11` | Mất playbook phái sinh, an toàn thuốc, giám sát định kỳ, bản địa hoá BYT |

Nói cách khác: mọi việc siết liêm chính làm trong skill chính đều **vô hiệu** nếu hệ
thống lỡ chọn skill kia.

## Đối chiếu trước khi gộp — có mất gì không

Kiểm ngày 08/9/2026 bằng `cmp` từng byte:

| Kiểm | Kết quả |
|---|---|
| `templates/web-dashboard-dark-analyst.html` | **trùng byte** với bản trong skill chính |
| `templates/web-dashboard-evidence-workbench.html` | trùng byte |
| `templates/web-dashboard-van-de-cu-the-clinical-quick-view.html` | trùng byte |
| `templates/mau-cap-nhat-chuyen-sau.md` · `mau-cap-nhat-nhanh.md` | trùng byte |
| File chỉ có ở `dark-analyst` | **không có file nào** |
| Dòng khác nhau trong `SKILL.md` | **8 dòng**, tất cả chỉ đảo vai trò: mẫu nào MẶC ĐỊNH, mẫu nào THAY THẾ |

**Kết luận: không có nội dung riêng nào để port.** `dark-analyst` chỉ là một *tuỳ chọn
hiển thị* (nền tối) bị tách thành cả một skill trùng tên gọi.

## Cách gộp

Không phải trộn file — mà là **bỏ skill trùng, giữ chế độ**:

1. `SKILL.md` của `cap-nhat-chung-cu-y-khoa` nay ghi rõ: *“Dark Analyst” là một **CHẾ ĐỘ
   HIỂN THỊ**, không phải skill riêng*, kèm cách gọi (“dùng mẫu Dark Analyst” / “bản nền tối”),
   và nhấn mạnh chế độ đó dùng **cùng schema `DATA`, cùng dây chuyền, cùng cổng liêm chính**.
2. Mẫu nền tối vẫn ở nguyên `templates/web-dashboard-dark-analyst.html` — **không mất gì**.
3. Trên tài khoản: **xoá skill `dark-analyst`** (việc này bác sĩ tự làm, xem bên dưới).

## Việc bác sĩ phải tự làm

Phiên Claude **không ghi được** vào bundle skill trên tài khoản. Hai việc:

```bash
# 1. Đóng gói bản đã sửa của skill chính
python3 tools/dong_goi_skill_de_tai_len.py cap-nhat-chung-cu-y-khoa
#    → dist/cap-nhat-chung-cu-y-khoa.zip
```

- **Tải lên** gói trên, **thay thế** skill cùng tên đang có (đừng tạo bản trùng tên).
- **Xoá** skill `dark-analyst` khỏi tài khoản.
- Mở **phiên mới** để bundle đồng bộ lại, rồi kiểm:

```bash
python3 tools/kiem_dong_bo_skill_ebm.py
```

Đạt khi báo cáo **hết dòng `MÔ TẢ TRÙNG`** và **hết dòng `LỆCH bundle↔sao-lưu`**
cho `cap-nhat-chung-cu-y-khoa`.

## Bản sao lưu `dark-analyst` giữ lại hay xoá?

**Giữ lại** trong `sao-luu-skill-cloud/dark-analyst/` như **bản ghi lịch sử**: nó chứng
minh skill từng tồn tại và từng có nội dung gì, phòng khi cần đối chiếu về sau. Xoá khỏi
**tài khoản** là đủ để hết nguy cơ kích hoạt nhầm; xoá khỏi **git** thì mất dấu vết.

> Sau khi đã xoá trên tài khoản, `kiem_dong_bo_skill_ebm.py` sẽ báo
> *“skill `dark-analyst` có bản sao lưu nhưng KHÔNG có trong bundle đang chạy”* —
> đó là **ghi chú bình thường** (dòng `·`), không phải lỗi, và đúng là trạng thái mong muốn.
