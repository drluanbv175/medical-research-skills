#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chay_giam_sat_dinh_ky.py — Chạy giám sát chứng cứ (Track B) TRÊN MÁY BÁC SĨ theo lịch,
ghi báo cáo vào repo và đẩy lên, để phiên Claude nào cũng đọc được.

VÌ SAO KHÔNG DÙNG ROUTINE CỦA CLAUDE
------------------------------------
Đã đo 2026-09-05: phiên do Routine sinh ra có `"mcp_servers": []` — **không connector nào**,
và đường tạo Routine bị tổ chức từ chối tham số `connectors`. Phiên Routine cũng không có
nguồn repo. Nên Track B **không thể** chạy trong Routine, dù cấu hình thế nào.

Máy của bác sĩ thì có đủ: mạng tới PubMed, repo, và lịch của hệ điều hành.

VIỆC NÀY LÀM GÌ
    1. `surveillance_scan.py` → báo cáo ứng viên trong N ngày gần đây
    2. Ghi vào `EBM-Dashboards/giam-sat/giam-sat-<ngày>.md`
    3. Commit đúng MỘT tệp đó rồi push (bỏ qua bằng `--khong-day`)

NGUYÊN TẮC AN TOÀN
    · Quét không kết luận được (mạng hỏng) thì **vẫn ghi báo cáo** — nhưng báo cáo nói rõ
      là chưa tra được, và công cụ trả mã thoát 2. Một việc chạy tự động mà im lặng báo
      "không có gì mới" trong khi thật ra chưa hỏi được câu nào là kiểu hỏng tệ nhất.
    · Chỉ `git add` đúng tệp báo cáo. Không bao giờ `git add -A` — việc chạy nền không
      được phép cuốn theo thứ bác sĩ đang sửa dở.
    · Không tự thẩm định, không tự đổi thực hành. Đây chỉ là danh sách ỨNG VIÊN.

CÁCH DÙNG
    python3 tools/chay_giam_sat_dinh_ky.py                 # 90 ngày, commit + push
    python3 tools/chay_giam_sat_dinh_ky.py --days 30 --khong-day
    python3 tools/chay_giam_sat_dinh_ky.py --tao-watchlist # dựng watchlist ban đầu

LỊCH — chọn đúng hệ điều hành, xem `de-xuat/GIAM-SAT-TREN-MAY.md`

MÃ THOÁT
    0 = quét xong, mọi chủ đề đã truy vấn
    2 = KHÔNG KẾT LUẬN (có chủ đề chưa tra được) — báo cáo vẫn được ghi
    1 = không chạy được (thiếu watchlist, thiếu công cụ)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EBM = os.path.join(ROOT, "EBM-Dashboards")
WATCHLIST = os.path.join(EBM, "watchlist.json")
THU_MUC_BAO_CAO = os.path.join(EBM, "giam-sat")


def chay(lenh, cwd=None):
    r = subprocess.run(lenh, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def tao_watchlist() -> int:
    """Dựng watchlist ban đầu TỪ CHÍNH các bản cập nhật đã làm, không bịa chủ đề."""
    if os.path.isfile(WATCHLIST):
        print("· Đã có %s — không ghi đè." % os.path.relpath(WATCHLIST, ROOT))
        return 0
    thu_vien = os.path.join(EBM, "library.json")
    topics = []
    if os.path.isfile(thu_vien):
        for m in json.load(open(thu_vien, encoding="utf-8")):
            topics.append({
                "topic": m.get("question", "")[:90],
                "query": "",           # để trống: chuỗi tìm là việc chuyên môn của bác sĩ
                "active": False,       # tắt cho tới khi bác sĩ điền query và bật lên
                "_ghi_chu": "[DỰ THẢO] Điền `query` theo cú pháp PubMed rồi đổi active=true. "
                            "Công cụ KHÔNG tự đặt chuỗi tìm thay bác sĩ.",
            })
    wl = {
        "_muc_dich": "Danh sách chủ đề lõi cần theo dõi chứng cứ mới (Track B). "
                     "Mỗi mục cần `query` theo cú pháp PubMed và `active: true` mới được quét.",
        "_huong_dan": "Thêm chủ đề: {\"topic\": \"tên ngắn\", \"query\": \"chuỗi PubMed\", "
                      "\"active\": true}. Nên giới hạn 10–20 chủ đề lõi.",
        "topics": topics,
    }
    os.makedirs(EBM, exist_ok=True)
    json.dump(wl, open(WATCHLIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("✓ Đã tạo %s với %d chủ đề lấy từ library.json — tất cả đang TẮT."
          % (os.path.relpath(WATCHLIST, ROOT), len(topics)))
    print("  Mở tệp, điền `query` cho từng chủ đề rồi đổi `active` thành true.")
    print("  Chuỗi tìm là quyết định chuyên môn — công cụ không đặt thay bác sĩ.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Chạy giám sát chứng cứ định kỳ trên máy.")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--max", type=int, default=6)
    ap.add_argument("--tao-watchlist", dest="tao_wl", action="store_true",
                    help="dựng watchlist ban đầu từ library.json rồi thoát")
    ap.add_argument("--khong-day", dest="khong_day", action="store_true",
                    help="chỉ ghi báo cáo, không commit/push")
    a = ap.parse_args()

    if a.tao_wl:
        return tao_watchlist()

    if not os.path.isfile(WATCHLIST):
        print("✗ Chưa có %s. Chạy `--tao-watchlist` trước."
              % os.path.relpath(WATCHLIST, ROOT), file=sys.stderr)
        return 1
    wl = json.load(open(WATCHLIST, encoding="utf-8"))
    bat = [t for t in wl.get("topics", []) if t.get("active") and (t.get("query") or "").strip()]
    if not bat:
        print("✗ Watchlist chưa có chủ đề nào BẬT kèm `query`. Mở %s và điền."
              % os.path.relpath(WATCHLIST, ROOT), file=sys.stderr)
        return 1

    cong_cu = os.path.join(EBM, "tools", "surveillance_scan.py")
    if not os.path.isfile(cong_cu):
        print("✗ Không thấy %s" % cong_cu, file=sys.stderr)
        return 1

    ngay = datetime.date.today().isoformat()
    os.makedirs(THU_MUC_BAO_CAO, exist_ok=True)
    bao_cao = os.path.join(THU_MUC_BAO_CAO, "giam-sat-%s.md" % ngay)

    ma, ra, loi = chay([sys.executable, cong_cu, "--watchlist", WATCHLIST,
                        "--days", str(a.days), "--max", str(a.max),
                        "--report", bao_cao], cwd=EBM)
    sys.stderr.write(loi)
    print("· Quét %d chủ đề, %d ngày → %s (mã thoát %d)"
          % (len(bat), a.days, os.path.relpath(bao_cao, ROOT), ma))

    if not os.path.isfile(bao_cao):
        print("✗ Không sinh được báo cáo.", file=sys.stderr)
        return 1

    if a.khong_day:
        print("· Bỏ qua commit/push theo --khong-day.")
        return ma

    # Chỉ đụng đúng MỘT tệp. Việc chạy nền không được cuốn theo thứ đang sửa dở.
    tuong_doi = os.path.relpath(bao_cao, ROOT)
    for lenh in (["git", "add", "--", tuong_doi],
                 ["git", "commit", "-m",
                  "chore(giam-sat): ứng viên chứng cứ mới %s%s"
                  % (ngay, " [KHÔNG KẾT LUẬN — có chủ đề chưa tra được]" if ma == 2 else ""),
                  "--", tuong_doi]):
        mg, so, se = chay(lenh, cwd=ROOT)
        if mg != 0 and "nothing to commit" not in (so + se):
            print("⚠ Dừng ở bước git: %s\n  %s" % (" ".join(lenh), (se or so).strip()[:300]),
                  file=sys.stderr)
            return ma or 1
    mg, so, se = chay(["git", "push"], cwd=ROOT)
    if mg != 0:
        print("⚠ Push không được (%s). Báo cáo đã commit tại chỗ, đẩy tay sau."
              % (se or so).strip()[:200], file=sys.stderr)
    else:
        print("✓ Đã commit và push %s" % tuong_doi)
    return ma


if __name__ == "__main__":
    sys.exit(main())
