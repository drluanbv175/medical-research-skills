# Việc định kỳ: cái nào đang thực sự có người chạy

Đo 06/09/2026. Nguồn: `ebm-drluanbv175/sync/scheduled-tasks/` (10 tác vụ) đối chiếu
với danh sách Routine cloud đang bật (2 Routine, lấy qua `list_triggers`).

---

## 1. Kết luận trước

**9 việc định kỳ · 3 được gánh MỘT PHẦN · 6 KHÔNG AI CHẠY.**

Và chỗ không ai chạy thì **im lặng** — không có gì báo, vì tác vụ chưa từng nổ nên
cũng chưa từng báo lỗi.

Lý do gốc đã đo từ trước: `launchd` trên máy bác sĩ có `runs = 0` — lịch cục bộ chưa
bao giờ nổ. Còn phiên cloud thì không gánh thay được, vì **cả 10 tác vụ đều neo
đường dẫn tuyệt đối của máy** (`/Users/nguyenluan/...`, `CloudStorage`, `OneDrive`) —
container cloud không có những đường dẫn đó.

Việc neo máy tự nó **không phải lỗi**: các tác vụ này thao tác trên sổ cái EBM_MASTER
và thư mục EBM-Dashboards nằm ngoài git, trên máy. Vấn đề là hệ quả: máy không chạy
thì không ai chạy.

---

## 2. Bảng đối chiếu từng việc

| # | Tác vụ | Nhịp | Chạy được ở cloud? | Làn đang sống |
|---|---|---|---|---|
| 1 | `cap-nhat-thang-ebm` | tháng | ❌ cần `monthly_update.sh` cục bộ | 🟡 Routine "Cập nhật guideline — tháng" gánh phần rà guideline |
| 2 | `ebm-antifacts-weekly` | T2 07:00 | 🟡 digest PubMed được; dựng `Antifacts.html` thì không | ❌ **không** |
| 3 | `ebm-drug-safety` | T2 & T5 | ✅ nguồn công khai | 🟡 Routine tuần gánh FDA/EMA, **không** gánh Beers-STOPP/tương tác |
| 4 | `ebm-giam-sat-chung-cu` | T4 19:20 | ❌ ủy thác đội Agent nằm ở máy | ❌ **không** |
| 5 | `ebm-nckh-qy175` | chạy tay | ❌ hồ sơ đề tài ở máy | — không tính (ad-hoc) |
| 6 | `ebm-tong-hop-chung-cu-tuan` | CN 20:00 | ✅ | ❌ **không** |
| 7 | `ebm-tu-kiem-dong-bo` | CN | 🟡 phần đối chiếu skill nay làm được bằng `doi_chieu_ba_ben.py`; phần agent cần máy | ❌ **không** |
| 8 | `ebm-uptodate-tuan` | T7 | ✅ | ❌ **không** |
| 9 | `goi-duyet-tuan-ebm` | T2 18:30 | ❌ ghi `queue/tuan-<W>.md` trên máy | ❌ **không** |
| 10 | `thu-thap-tuan-an-toan-thuoc` | T2 18:00 | ❌ chạy `weekly_safety.sh` cục bộ | 🟡 trùng việc với #3 |

Hai Routine cloud đang bật:

| Routine | Cron (UTC) | Giờ VN | Lần chạy kế | Lần chạy gần nhất |
|---|---|---|---|---|
| Giám sát an toàn thuốc — tuần | `0 1 * * 1` | 08:00 thứ Hai | 07/10/2026 | 05/09 — SUCCEEDED, 3 phút 37 |
| Cập nhật guideline — tháng | `0 1 1 * *` | 08:00 mùng 1 | 01/10/2026 | chưa chạy lần nào |

---

## 3. Ba việc chạy được ngay trên cloud mà chưa có làn

Ba việc dưới đây **không cần một file nào trên máy** — chỉ cần tra nguồn công khai.
Chúng đang trống, và trống một cách im lặng.

### 3.1. `ebm-uptodate-tuan` — cập nhật chứng cứ tuần cho một vấn đề lâm sàng (T7)

### 3.2. `ebm-tong-hop-chung-cu-tuan` — ứng viên chứng cứ 8 bệnh mạn (CN)

### 3.3. `ebm-antifacts-weekly` — digest 13 chuyên khoa, PubMed 7 ngày (T2)
Chỉ phần **digest**. Phần dựng lại `Antifacts.html` vẫn phải chạy trên máy.

Lời nhắc cho cả ba, viết theo đúng khuôn hai Routine đang chạy (dò công cụ theo
chức năng · ba dòng tự khai năng lực · fail-closed cửa hẹp · đầu ra là THẺ ỨNG VIÊN
dừng ở Cổng A/B · kết bằng "Cần bác sĩ kiểm chứng"): xem `loi-nhac-routine-moi.md`.

> **Chưa tạo Routine nào cho ba việc này.** Mỗi Routine là một cam kết định kỳ: tốn
> hạn mức và gửi email/thông báo mỗi kỳ. Việc đó là quyết định của bác sĩ, không
> phải thứ nên tự bật thay bác sĩ. Nói một câu là tôi tạo.

---

## 4. Ba việc KHÔNG cloud nào gánh được

`ebm-giam-sat-chung-cu` (ủy thác đội Agent) · `goi-duyet-tuan-ebm` (ghi hàng đợi
duyệt) · `cap-nhat-thang-ebm` + `thu-thap-tuan-an-toan-thuoc` (chạy shell script).

Với nhóm này chỉ có hai lối:

1. **Sửa lịch trên máy cho nó thật sự nổ.** Gốc rễ là `launchd` không chạy khi máy
   ngủ. Cách chắc ăn hơn: đổi sang chạy lúc bác sĩ chắc chắn mở máy, hoặc dùng
   `launchd` với `StartCalendarInterval` + `RunAtLoad` để bù kỳ đã lỡ.
2. **Chấp nhận chúng chạy tay**, và ghi rõ điều đó vào `ops/schedule.md` để không ai
   tưởng nhầm là có tự động.

Điều KHÔNG nên làm: tải mấy tác vụ này lên cloud. Chúng sẽ chạy, không tìm thấy
`/Users/nguyenluan/...`, rồi tùy ứng biến — đó là kiểu hỏng tệ nhất, vì nó vẫn sinh
ra báo cáo trông như thật.

---

## 5. `ebm-tu-kiem-dong-bo` — nay đã có một nửa

Tác vụ này tự kiểm đồng bộ đội agent, chạy Chủ nhật, và cũng chưa từng nổ. Phần
**đối chiếu skill** của nó nay chạy được ở bất kỳ đâu, kể cả cloud:

```bash
python3 tools/doi_chieu_ba_ben.py <đường-dẫn-repo>
```

Phần còn lại (đọc `_TU-SUA-CHUA-PROTOCOL.md`, tự sửa số đếm agent, ghi
`nhat-ky.md`) vẫn cần file trên máy.
