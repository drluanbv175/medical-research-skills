# Mẫu thử cho `lay_coi_tai_tro.py` — DỮ LIỆU GIẢ, KHÔNG PHẢI BẢN GHI THẬT

Bộ này chỉ để **kiểm bộ bóc tách chạy đúng** khi không có mạng. DOI là `10.9999/...`
(không tồn tại), tên cơ quan và câu COI đều bịa và có ghi thẳng chữ "MẪU THỬ" bên trong.
**Tuyệt đối không** trích bất cứ dòng nào ở đây vào bản cập nhật chứng cứ.

Chạy tự kiểm:

```bash
python3 tools/lay_coi_tai_tro.py --tu-tho tools/mau-thu-lay-coi \
  --doi 10.9999/day-du 10.9999/chi-muc-trong 10.9999/toan-van-mo
```

Phải ra: `day-du` lấy được cả hai từ PubMed XML (ưu tiên hơn Europe PMC core) ·
`chi-muc-trong` chỉ có tài trợ từ Crossref, COI = KHÔNG CÓ TRONG CHỈ MỤC ·
`toan-van-mo` lấy được câu nguyên văn từ fullTextXML. Mã thoát **2** (còn ô trống).

Đây **không** kiểm được hình dạng phản hồi thật của API — chỉ máy có mạng mới kiểm được,
bằng `--luu-tho` rồi mở tệp thô đối chiếu.
