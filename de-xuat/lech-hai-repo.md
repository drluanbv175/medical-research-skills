# Lệch giữa hai repo — bản ĐO LẠI 05/09/2026

> **Bản trước của tệp này SAI.** Nó ghép tệp theo **tên**, nên 12 trong 68 dòng đã so
> hai tệp chẳng liên quan gì nhau — ví dụ `knowledge.py` ở `app/chatgpt_app/` bị đem so
> với `tools/orchestrator/knowledge.py`. Bảng dưới ghép theo **đường dẫn tương đối**.

`medical-ebm-automation` = **A** (1,556 tệp) · `ebm-drluanbv175` = **E** (1,152 tệp)

## Số đúng

| Đo | Kết quả |
|---|---|
| Tệp ở CÙNG đường dẫn trong cả hai repo | 92 |
| Trong đó đã lệch | **59** |
| — thuộc `.claude/agents/` | **51** (86%) |
| — còn lại | 8 |

## Phát hiện chính: đây KHÔNG phải 48 quyết định, mà là MỘT

`.claude/agents/`: A có **84** agent, E có **179**. Cả 84 agent của A
đều có trong E; E có thêm **95** agent mà A không có.

Trên 51 tệp lệch:

| | A | E |
|---|---|---|
| Số tệp lớn hơn | **0** | **51** |
| Dòng chỉ có ở bên này | 23 | 870 |

23 dòng "chỉ có ở A" đã soi từng dòng: 5 dòng là `description:` **cùng nội dung**, chỉ
khác kiểu nháy kép; phần còn lại thuộc `_VONG-LAP-KHEP-KIN.md` — bản A (75 dòng) chỉ có
tuyến nghiên cứu, bản E (177 dòng) viết lại tổng quát cho **cả hai tuyến**, đủ cả 5 bất
biến, chỉ đổi tên mục. **Không nội dung nào của A vắng mặt ở E.**

→ **`ebm-drluanbv175/.claude/agents/` là nguồn chân lý; bản trong A là gương cũ.**
Đúng với chính khai báo của `check_claude_codex_sync_health.py`:
*"Source of truth is `.claude/agents`"* — vấn đề là đang có HAI bản.

Cách xử lý: A **sinh** agent từ E (hoặc bỏ hẳn bản sao trong A), thay vì hai bên tự sửa tay.

## 8 tệp lệch còn lại — cần bác sĩ nhìn

| Tệp | A | E | Khác | Nhận định |
|---|---|---|---|---|
| `.gitattributes` | 458b | 1,073b | 37 | E giàu hơn. Nghiêng về **E**. |
| `.githooks/pre-commit` | 2,631b | 5,661b | 136 | E giàu hơn (có chốt kiem_o_nhiem_artifact). Nghiêng về **E**. |
| `.gitignore` | 4,449b | 6,756b | 275 | E giàu hơn. Nghiêng về **E**. |
| `AGENTS.md` | 2,562b | 19,902b | 224 | E giàu hơn nhiều. Nghiêng về **E**. |
| `CLAUDE.md` | 6,456b | 221,847b | 2169 | **KHÔNG phải lệch** — hai tài liệu khác phạm vi (xem ghi chú dưới). Giữ cả hai. |
| `README.md` | 16,423b | 1,801b | 331 | A là bản thật (gấp 9 lần). Khác phạm vi — giữ cả hai. |
| `tools/generate_agent.py` | 9,443b | 15,170b | 489 | E giàu hơn. Nghiêng về **E**. |
| `tools/scaffold_research_project.py` | 31,067b | 22,915b | 1156 | **A giàu hơn** — A đi trước ở tệp này. Nghiêng về **A**. |

## Đính chính về `CLAUDE.md`

Lần trước tôi nói đây là "hai quyển luật lệch 2.169 dòng". **Sai.** Đọc nội dung:

- `A/CLAUDE.md` (6.456b) mở đầu bằng `_harness_template: "CLAUDE.md.template"`,
  `_harness_version: "4.3.3"` — **bản sinh từ khuôn**, phạm vi dự án `medical-ebm-automation`.
- `E/CLAUDE.md` (221.847b) là học thuyết "EBM Copilot" viết tay cho toàn hệ.

Hai tài liệu **khác phạm vi**, không phải hai bản sao đã trôi. Và vì A nằm LỒNG trong E
trên máy thật (`verify_research_gate_contracts.py:32` → `ROOT / "medical-ebm-automation"`),
dự án con có `CLAUDE.md` riêng là **đúng cách** — Claude Code đọc bản gần nhất cộng bản cha.

**Không phải việc cần sửa.**

Cần bác sĩ kiểm chứng.
