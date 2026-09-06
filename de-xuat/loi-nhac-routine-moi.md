# Lời nhắc ba Routine cloud — ĐÃ TẠO 06/09/2026

Bác sĩ đã duyệt cả ba. Đã tạo, đang bật, model `claude-opus-5` khớp hai Routine cũ.

| | Routine | ID | Cron (UTC) | Giờ VN |
|---|---|---|---|---|
| A | Cập nhật chứng cứ tuần — 1 vấn đề lâm sàng | `trig_01CKTjwPjGiFXDgVbNf5Vohd` | `0 1 * * 6` | thứ Bảy 08:00 |
| B | Ứng viên chứng cứ — 8 bệnh mạn | `trig_012iTUkzrXb8Rv7psy7o2767` | `0 13 * * 0` | Chủ nhật 20:00 |
| C | Digest EBM 13 chuyên khoa | `trig_01UUGYwkhcSBvBTYsTtT7XR9` | `0 0 * * 1` | thứ Hai 07:00 |

Văn bản lời nhắc bên dưới là bản đã nạp vào từng Routine — giữ lại để đối chiếu và
sửa về sau.

Khuôn chung, giữ nguyên ở cả ba: dò công cụ theo **chức năng** (không theo tên hãng,
vì connector ở môi trường này mang tên UUID) · ba dòng tự khai năng lực · fail-closed
**cửa hẹp** (chỉ dừng khi mất SẠCH khả năng tra cứu) · đầu ra là **THẺ ỨNG VIÊN**
dừng ở Cổng A/B · mọi khẳng định truy được về nguồn **mở trong chính lượt đó** · kết
bằng "Cần bác sĩ kiểm chứng."

---

## A. `ebm-uptodate-tuan` — cập nhật chứng cứ tuần cho một vấn đề lâm sàng

Nhịp đề nghị: **thứ Bảy 08:00 giờ VN** → cron UTC `0 1 * * 6`

```
CẬP NHẬT CHỨNG CỨ TUẦN — MỘT VẤN ĐỀ LÂM SÀNG. Làn cloud.

═══ BƯỚC 0 — DÒ CÔNG CỤ RỒI TỰ KIỂM NĂNG LỰC. LÀM TRƯỚC MỌI THỨ KHÁC ═══

Connector ở môi trường này KHÔNG mang tên hãng mà mang tên UUID — ví dụ PubMed thật
sự là `mcp__<uuid>__search_articles`. Đừng tìm theo `mcp__PubMed__*`: mẫu đó KHÔNG
TỒN TẠI và tìm theo nó sẽ ra tay trắng dù công cụ vẫn ở đó. Nhiều công cụ ở dạng
hoãn nạp, phải gọi `ToolSearch` mới dùng được.

Dò theo CHỨC NĂNG:
    ToolSearch("select:WebSearch,WebFetch")
    ToolSearch("pubmed search articles")
    ToolSearch("literature search citations")
    ToolSearch("clinical trials search")

Mở đầu báo cáo bằng đúng 3 dòng:
  NĂNG LỰC-1 skill `cap-nhat-chung-cu-y-khoa`: gọi được / KHÔNG có
  NĂNG LỰC-2 tra cứu: tên CHÍNH XÁC các công cụ đã nạp được (kể cả tên UUID),
             hoặc ghi "không nạp được công cụ tra cứu nào"
  NĂNG LỰC-3 kết luận: ĐỦ / THIẾU — thiếu gì

FAIL-CLOSED, cửa HẸP: chỉ DỪNG khi CẢ BA đều đúng — không nạp được WebSearch ·
không nạp được WebFetch · không nạp được connector tra cứu nào. Khi đó viết đúng một
câu: "Không đủ năng lực tra cứu — không chạy cập nhật tuần này." rồi dừng.
Có ÍT NHẤT MỘT thứ tra cứu được thì CHẠY TIẾP. Thiếu skill nhưng còn tra cứu được
thì vẫn chạy, miễn khai rõ ở NĂNG LỰC-3.

═══ BỐI CẢNH ═══
Tác vụ `ebm-uptodate-tuan` trên máy bác sĩ neo đường dẫn `/Users/nguyenluan/...` và
lịch launchd đo được `runs = 0` — chưa từng nổ. Làn cloud này gánh phần KHÔNG cần
dữ liệu cục bộ. Sổ cái EBM_MASTER và EBM-Dashboards nằm NGOÀI git, trên máy —
KHÔNG cố đọc, KHÔNG cố ghi, không báo lỗi vì thiếu chúng.

═══ VIỆC ═══
1. Gọi skill `cap-nhat-chung-cu-y-khoa`.
2. Chọn MỘT vấn đề lâm sàng ngoại trú người lớn để đào sâu tuần này. Luân phiên qua
   các tuần, không lặp lại chủ đề của 4 tuần gần nhất nếu suy ra được từ ngữ cảnh;
   không suy ra được thì nói rõ là chọn mới và nêu lý do chọn.
3. Với vấn đề đó, rà chứng cứ MỚI trong 7 ngày: thử nghiệm ngẫu nhiên, tổng quan hệ
   thống, khuyến cáo sửa đổi. Mỗi phát hiện ghi: PMID/DOI · thiết kế · cỡ mẫu · kết
   cục chính kèm ước lượng và 95% CI · nguy cơ sai lệch nếu đánh giá được.
4. Đối chiếu với thực hành hiện tại: có đổi hành vi kê đơn hay theo dõi không.

═══ RÀNG BUỘC CỨNG ═══
- Đầu ra là THẺ ỨNG VIÊN (CANDIDATE), dừng ở Cổng A/B. KHÔNG kết luận "nên đổi".
- MỌI khẳng định phải truy được về nguồn MỞ TRONG LƯỢT NÀY. Không tra được thì ghi
  "không tra được" — KHÔNG dựng lại từ trí nhớ, kể cả khi thấy chắc chắn.
- KHÔNG tự gán GRADE cho một nghiên cứu đơn lẻ.
- Trước khi trích một bài, kiểm bài đó có bị RÚT không (dùng công cụ có
  `editorialNotices` nếu nạp được). Không kiểm được thì ghi rõ là chưa kiểm.
- Tuần không có gì đáng kể thì trả lời MỘT DÒNG và dừng.
- Kết thúc bằng: "Cần bác sĩ kiểm chứng."
```

---

## B. `ebm-tong-hop-chung-cu-tuan` — ứng viên chứng cứ 8 bệnh mạn

Nhịp đề nghị: **Chủ nhật 20:00 giờ VN** → cron UTC `0 13 * * 0`

```
GIÁM SÁT ỨNG VIÊN CHỨNG CỨ — 8 BỆNH MẠN. Nhịp TUẦN, làn cloud. Track B (CHƯA thẩm định).

═══ BƯỚC 0 — DÒ CÔNG CỤ RỒI TỰ KIỂM NĂNG LỰC. LÀM TRƯỚC MỌI THỨ KHÁC ═══
[giữ NGUYÊN khối BƯỚC 0 của mục A, chỉ đổi câu dừng thành:
 "Không đủ năng lực tra cứu — không chạy giám sát tuần này."]

═══ BỐI CẢNH ═══
Tác vụ `ebm-tong-hop-chung-cu-tuan` trên máy neo `/Users/nguyenluan/...`, lịch chưa
từng nổ. Đây là Track B: thu ỨNG VIÊN, KHÔNG thẩm định. Việc thẩm định là của bác sĩ
ở Cổng A/B. Sổ cái EBM_MASTER nằm ngoài git — KHÔNG cố đọc, KHÔNG cố ghi.

═══ VIỆC ═══
1. Gọi skill `cap-nhat-chung-cu-y-khoa`.
2. Quét 7 ngày qua cho 8 nhóm bệnh mạn ngoại trú người lớn: tăng huyết áp · đái tháo
   đường típ 2 · rối loạn lipid máu · bệnh thận mạn · COPD · hen · suy tim · rung nhĩ.
   (Nếu bối cảnh nêu danh sách 8 bệnh khác của bác sĩ thì theo danh sách đó và nói rõ.)
3. Mỗi nhóm: tối đa 3 ứng viên đáng chú ý nhất. Không đủ 3 thì ghi ít hơn, KHÔNG
   độn cho đủ. Nhóm không có gì thì ghi "không có ứng viên mới".
4. Mỗi ứng viên: PMID/DOI · thiết kế · cỡ mẫu · kết cục chính + 95% CI · vì sao đáng
   chú ý (1 câu).

═══ RÀNG BUỘC CỨNG ═══
- TỔNG cộng không quá 24 thẻ. Nhiều hơn thì cắt theo mức đáng chú ý và nói rõ đã cắt.
- Đầu ra là THẺ ỨNG VIÊN, dừng ở Cổng A/B. KHÔNG xếp hạng khuyến cáo, KHÔNG gán GRADE.
- MỌI khẳng định truy được về nguồn MỞ TRONG LƯỢT NÀY.
- Kiểm bài bị rút trước khi đưa vào danh sách; không kiểm được thì ghi rõ.
- Kết thúc bằng: "Cần bác sĩ kiểm chứng."
```

---

## C. `ebm-antifacts-weekly` — digest 13 chuyên khoa (CHỈ phần digest)

Nhịp đề nghị: **thứ Hai 07:00 giờ VN** → cron UTC `0 0 * * 1`

> ⚠️ Chỉ gánh phần **digest**. Phần dựng lại `Antifacts.html` bằng
> `tools/build_antifacts.py` **phải chạy trên máy** — lời nhắc dưới đây nói rõ điều
> đó để không ai tưởng Antifacts đã được cập nhật.
>
> Nhịp này trùng ngày với Routine an toàn thuốc (thứ Hai 08:00). Đặt lệch 1 giờ để
> hai lượt không chồng nhau.

```
DIGEST EBM 13 CHUYÊN KHOA — nhịp TUẦN, làn cloud. CHỈ phần digest.

═══ BƯỚC 0 — DÒ CÔNG CỤ RỒI TỰ KIỂM NĂNG LỰC. LÀM TRƯỚC MỌI THỨ KHÁC ═══
[giữ NGUYÊN khối BƯỚC 0 của mục A, câu dừng: "Không đủ năng lực tra cứu — không
 chạy digest tuần này."]

═══ BỐI CẢNH VÀ GIỚI HẠN — ĐỌC KỸ ═══
Tác vụ gốc `ebm-antifacts-weekly` làm HAI việc: (a) digest PubMed 7 ngày, (b) dựng
lại `Antifacts.html` bằng `tools/build_antifacts.py` ở thư mục "Claude AI" trên máy.
Làn cloud CHỈ làm được (a). Phần (b) cần file cục bộ mà container không có.

BẮT BUỘC: kết thúc báo cáo phải ghi đúng câu này —
  "Antifacts.html CHƯA được cập nhật. Phải chạy trên máy: PYTHONUTF8=1 python
   tools/build_antifacts.py"
KHÔNG được viết bất cứ câu nào ngụ ý Antifacts đã được dựng lại.

═══ VIỆC ═══
1. Gọi skill `cap-nhat-chung-cu-y-khoa`.
2. Digest PubMed 7 ngày qua cho 13 chuyên khoa: Tim mạch · Hô hấp · Tiêu hóa–Gan mật
   · Nội tiết · Thận · Thần kinh–Đột quỵ · Cơ xương khớp · Nhiễm · Tâm thần · Lão
   khoa · Cấp cứu · Thuốc · Tổng hợp.
3. Mỗi chuyên khoa tối đa 2 mục. Không có thì ghi "không có mục mới" — KHÔNG độn.
4. Mỗi mục: PMID/DOI · thiết kế · một câu vì sao đáng chú ý với ngoại trú người lớn.
5. Rà phiên bản thang điểm/guideline: có bản mới của thang điểm hay khuyến cáo đang
   dùng không. Có thì ghi tên · phiên bản cũ → mới · ngày · URL chính thức.

═══ RÀNG BUỘC CỨNG ═══
- Đầu ra là THẺ ỨNG VIÊN, dừng ở Cổng A/B.
- MỌI khẳng định truy được về nguồn MỞ TRONG LƯỢT NÀY. KHÔNG dựng từ trí nhớ.
- Kiểm bài bị rút; không kiểm được thì ghi rõ.
- Kết thúc bằng câu về Antifacts.html ở trên, rồi: "Cần bác sĩ kiểm chứng."
```

---

## Lịch sau khi thêm — 5 Routine, không lượt nào chồng nhau

| Thứ | Giờ VN | Routine | Trạng thái |
|---|---|---|---|
| Hai | 07:00 | Digest 13 chuyên khoa | mới |
| Hai | 08:00 | Giám sát an toàn thuốc | đang chạy |
| Bảy | 08:00 | Cập nhật chứng cứ 1 vấn đề | mới |
| Chủ nhật | 20:00 | Ứng viên chứng cứ 8 bệnh mạn | mới |
| Mùng 1 | 08:00 | Cập nhật guideline tháng | đang chạy |

Khoảng 4 lượt/tuần. Mỗi lượt gửi một thông báo đẩy và một email.

---

## ⚠️ Hạn chế phải biết: các Routine chạy KHÔNG có connector

Đo trên cả **năm** Routine: trường `mcp_connections` đều **rỗng**. Nghĩa là phiên do
Routine sinh ra **không có công cụ connector** — không có PubMed connector, không có
Scite, không có ClinicalTrials.

Đây **không phải lỗi mới**: hai Routine cũ cũng vậy, và lượt chạy thử 05/09 vẫn
SUCCEEDED trong điều kiện đó. Nhưng nó có hệ quả thật:

- Báo cáo sẽ dựa vào **WebSearch/WebFetch**, không phải PubMed connector. Lấy PMID
  khó hơn và có thể sót nguồn ngoài Mỹ.
- Dòng **NĂNG LỰC-2** trong mỗi báo cáo sẽ phơi ra đúng điều này — bác sĩ đọc dòng
  đó là biết lượt chạy có gì trong tay.
- Cửa fail-closed đã tính sẵn tình huống này: chỉ WebSearch cũng đủ để chạy tiếp,
  nên không có lượt nào bị dừng oan.

**Muốn Routine có connector** thì phải tạo từ giao diện Routines trên claude.ai —
Routine tạo qua công cụ chỉ mang được connector mà chính phiên gọi đang giữ, và
phiên này không giữ cái nào để truyền sang.
