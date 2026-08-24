#!/usr/bin/env bash
# setup-local.sh — Cập nhật và kiểm tra bộ skill trên MÁY CÁ NHÂN.
#
# Máy cá nhân không có egress proxy, nên mọi REST API (NCBI, Crossref,
# Europe PMC, openFDA, Unpaywall...) truy cập được đầy đủ — đây là cách
# "mở khoá" không cần đổi cài đặt nào và không đánh đổi bảo mật.
#
#   bash scripts/setup-local.sh
#
# Script CHỈ đọc và cập nhật; không xoá, không ghi đè thay đổi cục bộ.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2
ROOT="$(pwd)"

b() { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok() { printf '  \033[32m✓\033[0m %s\n' "$1"; }
no() { printf '  \033[31m✗\033[0m %s\n' "$1"; }
wa() { printf '  \033[33m!\033[0m %s\n' "$1"; }

b "1. Kho mã"
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  no "Không phải kho git: $ROOT"; exit 2
fi
ok "kho: $ROOT"
ok "nhánh: $(git rev-parse --abbrev-ref HEAD)"

if [ -n "$(git status --porcelain)" ]; then
  wa "Có thay đổi chưa commit — BỎ QUA bước pull để không đè lên chúng."
  wa "Commit hoặc stash rồi chạy lại nếu muốn cập nhật."
else
  if git pull --ff-only origin main 2>&1 | tail -2; then
    ok "đã đồng bộ với origin/main"
  else
    wa "pull không thành công (mạng, hoặc lịch sử đã rẽ nhánh) — vẫn tiếp tục kiểm tra."
  fi
fi

b "2. Python"
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  no "Cần Python >= 3.10. Cài rồi chạy lại."; exit 2
fi
ok "$($PY --version 2>&1)  ($(command -v $PY))"

b "3. Phụ thuộc"
if $PY -c 'import requests' 2>/dev/null; then
  ok "requests đã có"
else
  wa "thiếu requests — đang cài..."
  if $PY -m pip install --quiet --user requests 2>/dev/null || $PY -m pip install --quiet requests 2>/dev/null; then
    ok "đã cài requests"
  else
    wa "cài tự động thất bại. Chạy tay: $PY -m pip install requests"
    wa "(chỉ ảnh hưởng validate_citations / verify_citations)"
  fi
fi

b "4. Kiểm thử hạ tầng"
if $PY tests/test_evidence_stack.py 2>&1 | tail -4; then
  ok "bộ kiểm thử đạt"
else
  no "bộ kiểm thử có ca hỏng — xem chi tiết ở trên"
fi

b "5. Kiểm tra sức khoẻ nguồn"
$PY scripts/doctor.py
RC=$?

b "Kết luận"
case $RC in
  0) ok "TẤT CẢ THÔNG — mọi skill REST dùng được đầy đủ, không cần mở khoá gì thêm." ;;
  1) wa "Nguồn bị chặn. Nếu đang chạy trên MÁY CÁ NHÂN, kiểm tra tường lửa/VPN/proxy công ty."
     wa "Nếu đang chạy trên Claude Code on the web thì đây là điều bình thường — dùng MCP." ;;
  2) no "Có vấn đề cài đặt — xem mục còn thiếu ở trên." ;;
  3) no "Mạng thông nhưng kiểm thử sống thất bại — nguồn có thể đang đổi API hoặc rate-limit." ;;
esac

b "Bước tiếp theo"
cat <<'TXT'
  Cập nhật manifest plugin sau khi pull (nếu dùng Claude Code cục bộ):
      python3 adapt-for-claude-code.py

  Tra cứu nhanh:
      python3 scripts/check_evidence_sources.py
      python3 scripts/retraction_check.py extract ban-thao.md

  Bảng định tuyến nguồn:
      references/EVIDENCE-SOURCE-ROUTING.md
TXT
exit $RC
