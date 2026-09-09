# Chạy giám sát chứng cứ trên máy bác sĩ — 2026-09-09

## Vì sao không dùng Routine của Claude

Đã đo 2026-09-05 (`de-xuat/NANG-LUC-PHIEN-CLOUD.md`, gọi thật):

| Hạng mục | Phiên Routine |
|---|---|
| Connector MCP | `"mcp_servers": []` — **không có cái nào** |
| Nguồn repo | `"sources": []` |
| Tạo Routine kèm connector | hệ thống từ chối: *"the connectors parameter is not available for this organization"* |

Nghĩa là Track B **không thể** chạy trong Routine, dù cấu hình thế nào. Máy của bác sĩ thì
có đủ ba thứ cần: mạng tới PubMed, repo, và lịch của hệ điều hành.

## Ba bước

### 1. Dựng watchlist

```bash
python3 tools/chay_giam_sat_dinh_ky.py --tao-watchlist
```

Lấy chủ đề từ chính `EBM-Dashboards/library.json` — các bản cập nhật bác sĩ đã làm. Mọi chủ đề
sinh ra đều **đang TẮT** và `query` để trống: **chuỗi tìm là quyết định chuyên môn, công cụ
không đặt thay bác sĩ**. Mở `EBM-Dashboards/watchlist.json`, điền `query` theo cú pháp PubMed
rồi đổi `active` thành `true`. Nên giữ **10–20 chủ đề lõi**, đừng nhiều hơn.

### 2. Chạy thử một lần

```bash
python3 tools/chay_giam_sat_dinh_ky.py --days 30 --khong-day
```

Đọc `EBM-Dashboards/giam-sat/giam-sat-<ngày>.md`. Mã thoát: `0` quét xong · `2` **KHÔNG KẾT
LUẬN** (có chủ đề chưa tra được) · `1` chưa chạy được.

### 3. Đặt lịch

Khuyến nghị **hằng tuần**, sáng thứ Hai. Quét 90 ngày thì trùng lặp giữa các lần là bình thường
và có lợi: bài mới lập chỉ mục muộn vẫn được bắt.

**macOS — launchd.** Ghi `~/Library/LaunchAgents/vn.ebm.giamsat.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>vn.ebm.giamsat</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/ĐƯỜNG/DẪN/medical-research-skills/tools/chay_giam_sat_dinh_ky.py</string>
    <string>--days</string><string>90</string>
  </array>
  <key>WorkingDirectory</key><string>/ĐƯỜNG/DẪN/medical-research-skills</string>
  <key>StartCalendarInterval</key>
  <dict><key>Weekday</key><integer>1</integer>
        <key>Hour</key><integer>7</integer>
        <key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/tmp/giamsat.log</string>
  <key>StandardErrorPath</key><string>/tmp/giamsat.err</string>
</dict></plist>
```

```bash
launchctl load ~/Library/LaunchAgents/vn.ebm.giamsat.plist
launchctl start vn.ebm.giamsat          # chạy thử ngay
```

**Linux — cron.** `crontab -e`:

```
0 7 * * 1 cd /ĐƯỜNG/DẪN/medical-research-skills && /usr/bin/python3 tools/chay_giam_sat_dinh_ky.py --days 90 >> /tmp/giamsat.log 2>&1
```

**Windows — Task Scheduler.** PowerShell (chạy một lần, quyền thường):

```powershell
$dir = "C:\ĐƯỜNG\DẪN\medical-research-skills"
$act = New-ScheduledTaskAction -Execute "python" `
        -Argument "tools\chay_giam_sat_dinh_ky.py --days 90" -WorkingDirectory $dir
$trg = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7am
Register-ScheduledTask -TaskName "EBM giam sat" -Action $act -Trigger $trg
```

## Việc chạy nền được phép làm gì

- **Chỉ `git add` đúng tệp báo cáo.** Không bao giờ `git add -A` — việc nền không được cuốn
  theo thứ bác sĩ đang sửa dở.
- **Không tự thẩm định, không tự đổi thực hành.** Đầu ra là danh sách **ứng viên** để bác sĩ
  chọn, rồi mới chạy skill `cap-nhat-chung-cu-y-khoa` thẩm định đầy đủ.
- **Quét hỏng thì nói là hỏng.** Mạng chặn giữa chừng thì báo cáo mở đầu bằng
  `⊘ KHÔNG KẾT LUẬN cho n/N chủ đề` và mã thoát là 2. Một việc chạy tự động, không người
  trông, mà im lặng báo *"không có gì mới"* trong khi thật ra **chưa hỏi được câu nào** —
  đó là kiểu hỏng nguy hiểm nhất của cả cơ chế này.

## Nếu push hỏng

Báo cáo vẫn được commit tại chỗ; công cụ in cảnh báo và không coi đó là quét thất bại.
Đẩy tay sau bằng `git push`. Máy dùng SSH key có passphrase thì nên thêm key vào agent,
hoặc chạy với `--khong-day` rồi commit tay.
