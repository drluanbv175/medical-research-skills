# Sao lưu 7 skill EBM bản CLOUD

Bảy skill này do bác sĩ tự viết và tải lên **tài khoản Claude**. Chúng chạy trong
mọi phiên claude.ai/code và trong hai Routine giám sát hàng tuần/hàng tháng.

## Vì sao có thư mục này

Ngày 06/09/2026, đối chiếu ba bên bằng `tools/doi_chieu_ba_ben.py` phát hiện: bảy
skill này **không có bản nào trong git**. Trong repo `ebm-drluanbv175`, bảy cái tên
đó đang bị một họ skill KHÁC chiếm chỗ — bản K-Dense tiếng Anh, được
`sync/skills/_vietnamize.py` Việt hóa phần đầu.

Dò toàn repo bằng cụm chữ đặc trưng của bản cloud:

| Cụm chữ | Số file tìm thấy trong repo |
|---|---|
| "6 lăng kính" (skill `peer-review`) | **0** |
| "Cổng cứng trích dẫn" (skill `scientific-writing`) | **1** — và đó là agent đã lưu trữ trong `.claude/agents/_archive/`, không phải skill |

Nghĩa là trước bản sao lưu này, **mất tài khoản là mất trắng bảy skill**.

## Đây là BẢN SAO LƯU, không phải nguồn chạy

Nơi ở đúng của chúng là `ebm-drluanbv175/sync/skills/<tên>-vn/` — hậu tố `-vn` để
không đè lên họ K-Dense đang giữ tên gốc. Phiên cloud không có quyền ghi vào repo
đó, nên đặt tạm ở đây.

Chép **nguyên văn từng byte** từ bundle tài khoản (`cmp` xác nhận 7/7 khớp), không
sửa một ký tự nào.

| Skill | Cập nhật trên tài khoản | Byte | SHA-256 (16 ký tự đầu) |
|---|---|---:|---|
| `citation-management` | 2026-06-13 | 2,774 | `8ed95b20cba6fb64` |
| `literature-review` | 2026-06-13 | 3,025 | `45352e170d8c4e33` |
| `paper-lookup` | 2026-06-13 | 3,196 | `be5799833789e56d` |
| `peer-review` | 2026-06-13 | 2,850 | `03525dcfae47e6c4` |
| `research-lookup` | 2026-06-13 | 3,019 | `8f7d77001cdc13e0` |
| `scientific-writing` | 2026-06-13 | 3,790 | `034439bfbb7f4ce5` |
| `statistical-analysis` | 2026-06-13 | 4,599 | `e031a583dec56866` |

- Bundle nguồn: `663e40d7-aa1d-4124-9a79-2c3563badb4c_1f8efc2f-396b-4507-8f3f-05e10bf3c606`
- Ngày sao lưu: 2026-09-06

## Kiểm bản sao còn khớp bundle

```bash
for n in citation-management literature-review paper-lookup peer-review research-lookup scientific-writing statistical-analysis; do
  cmp -s ~/.claude/skills/synced/*/"$n"/SKILL.md "sao-luu-skill-cloud/$n/SKILL.md" \
    && echo "OK   $n" || echo "LỆCH $n"
done
```

Nếu báo LỆCH: bản trên tài khoản đã đổi kể từ ngày sao lưu. Xem bản nào mới hơn
rồi cập nhật thư mục này — đừng chép ngược từ đây lên tài khoản mà chưa xem.
