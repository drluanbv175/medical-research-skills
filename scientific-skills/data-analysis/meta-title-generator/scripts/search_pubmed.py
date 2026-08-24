"""Tìm PubMed qua E-utilities.

AN TOÀN: script này PHÂN BIỆT rạch ròi hai tình huống rất khác nhau —
  (a) tra được, PubMed không có bài nào  -> status="ok",          total=0
  (b) KHÔNG tra được (mạng/bị chặn)      -> status="unavailable", total=null

Trước đây cả hai đều trả về total=0, khiến skill hiểu nhầm thành "không có
y văn" rồi chuyển sang tự sinh tiêu đề. Với công cụ y khoa, đó là con đường
dẫn thẳng tới bịa trích dẫn. Nay (b) thoát với mã 3 và KHÔNG được coi là
"không có bằng chứng".
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = {"User-Agent": "medical-research-skills/1.0 (search-pubmed)"}


# --- nạp helper dùng chung nếu có, không thì dùng bản rút gọn tại chỗ ---
def _load_evidence_net():
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        cand = os.path.join(d, "scripts", "evidence_net.py")
        if os.path.isfile(cand):
            sys.path.insert(0, os.path.join(d, "scripts"))
            try:
                import evidence_net
                return evidence_net
            except ImportError:
                return None
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


_EN = _load_evidence_net()
MCP_ALT = ("mcp__PubMed__search_articles / get_article_metadata "
           "— connector chạy server-side, không qua egress của container")


def _diagnose(exc, url):
    """Trả (kind, detail). Dùng helper chung nếu có."""
    if _EN is not None:
        d = _EN.classify(exc, url)
        return d.kind, d.detail, d.blocked_by_policy
    text = f"{exc} | {getattr(exc, 'reason', '')}"
    blocked = "tunnel connection failed" in text.lower()
    return ("egress_blocked" if blocked else "network_error"), text, blocked


class SearchUnavailable(RuntimeError):
    def __init__(self, kind, detail, blocked):
        super().__init__(detail)
        self.kind, self.detail, self.blocked = kind, detail, blocked


def _get_json(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as exc:  # noqa: BLE001
        kind, detail, blocked = _diagnose(exc, url)
        raise SearchUnavailable(kind, detail, blocked) from exc


def search_pubmed(query, retmax=5):
    """Trả (count, ids). Ném SearchUnavailable nếu KHÔNG tra được."""
    url = f"{BASE}/esearch.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "term": query, "retmode": "json", "retmax": str(retmax)})
    data = _get_json(url)
    result = data.get("esearchresult")
    if not result:
        # Có phản hồi nhưng sai định dạng -> vẫn là "không tra được", không phải "rỗng".
        raise SearchUnavailable("bad_response", f"Thiếu 'esearchresult': {str(data)[:200]}", False)
    return int(result.get("count", 0)), result.get("idlist", [])


def fetch_summaries(ids):
    """Trả chuỗi tiêu đề. Ném SearchUnavailable nếu không tra được."""
    if not ids:
        return ""
    url = f"{BASE}/esummary.fcgi?" + urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    result = _get_json(url).get("result", {})
    return "\n".join(f"Title: {result[u].get('title', '')}" for u in ids if u in result)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "total": None, "text": "",
                          "reason": "Thiếu tham số truy vấn."}, ensure_ascii=False))
        return 2

    query = sys.argv[1]
    last = None
    for attempt in range(2):
        try:
            count, ids = search_pubmed(query)
            text = fetch_summaries(ids) if ids else ""
            print(json.dumps({"status": "ok", "total": count, "text": text},
                             ensure_ascii=False))
            return 0
        except SearchUnavailable as exc:
            last = exc
            if exc.blocked:
                break          # bị chặn thì thử lại vô nghĩa
            if attempt == 0:
                time.sleep(1)

    # --- Không tra được: báo TO, không giả vờ là "không có kết quả" ---
    payload = {
        "status": "unavailable",
        "total": None,
        "text": "",
        "kind": last.kind,
        "reason": last.detail,
        "mcp_alternative": MCP_ALT,
        "warning": ("KHÔNG tra được PubMed. Đây KHÔNG phải 'không có y văn'. "
                    "Không được tự sinh tiêu đề, trích dẫn hay kết luận thay thế."),
    }
    print(json.dumps(payload, ensure_ascii=False))
    print("\n".join([
        "",
        "!" * 70,
        "  KHÔNG TRA ĐƯỢC PUBMED — KHÔNG PHẢI 'KHÔNG CÓ KẾT QUẢ'",
        "!" * 70,
        f"  Nguyên nhân : {last.kind}",
        f"  Chi tiết    : {last.detail[:300]}",
        "",
        "  Nếu là egress_blocked: host eutils.ncbi.nlm.nih.gov chưa được allowlist.",
        "    → claude.ai › Settings › Claude Code › Environments",
        f"    → Hoặc dùng: {MCP_ALT}",
        "",
        "  TUYỆT ĐỐI KHÔNG tự sinh tiêu đề/trích dẫn để lấp chỗ trống.",
        "!" * 70,
        "",
    ]), file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
