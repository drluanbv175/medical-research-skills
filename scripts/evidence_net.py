"""
evidence_net.py — Chẩn đoán truy cập nguồn chứng cứ y khoa.
Diagnose access to medical evidence sources.

VÌ SAO CÓ FILE NÀY / WHY THIS EXISTS
------------------------------------
Nhiều môi trường chạy Claude Code (đặc biệt Claude Code on the web) áp dụng
chính sách egress chỉ cho phép một số host. Khi đó mọi lời gọi tới
eutils.ncbi.nlm.nih.gov, api.crossref.org, api.fda.gov... đều thất bại ở bước
CONNECT với mã 403 — request chưa từng rời khỏi hạ tầng.

Nguy hiểm nằm ở chỗ: nếu script bắt `except Exception` rồi trả về danh sách
rỗng, hệ quả KHÔNG phải "không tìm thấy bài nào" mà là "không tra được nhưng
tưởng là không có". Với công cụ y khoa, hai điều đó khác nhau về bản chất:
cái sau dễ dẫn tới việc mô hình tự bịa trích dẫn để lấp chỗ trống.

Module này phân biệt rạch ròi:
    - bị CHẶN bởi chính sách  (egress_blocked / proxy_auth)
    - lỗi hạ tầng             (dns / timeout / tls / offline)
    - nguồn trả lời nhưng lỗi (http_error)
    - thật sự KHÔNG CÓ kết quả

Chỉ dùng thư viện chuẩn. Không phụ thuộc `requests`.
Stdlib only. No third-party dependencies.
"""

from __future__ import annotations

import json
import os
import socket
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional, Tuple

__all__ = [
    "SourceUnavailable", "classify", "is_blocked", "urlopen_json",
    "urlopen_text", "probe", "probe_all", "SOURCES", "ROUTING_DOC",
]

ROUTING_DOC = "references/EVIDENCE-SOURCE-ROUTING.md"

# --- Phân loại sự cố / failure kinds -------------------------------------
EGRESS_BLOCKED = "egress_blocked"   # chính sách mạng chặn host này
PROXY_AUTH     = "proxy_auth"       # proxy đòi xác thực (407)
TLS_UNTRUSTED  = "tls_untrusted"    # không tin CA của proxy
DNS_FAILURE    = "dns_failure"
TIMEOUT        = "timeout"
OFFLINE        = "offline"
HTTP_ERROR     = "http_error"       # nguồn có trả lời, nhưng mã lỗi
UNKNOWN        = "unknown"

_BLOCKED_KINDS = frozenset({EGRESS_BLOCKED, PROXY_AUTH})


@dataclass
class SourceUnavailable(RuntimeError):
    """Nguồn không truy cập được — kèm nguyên nhân và cách xử lý."""

    kind: str
    url: str = ""
    host: str = ""
    detail: str = ""
    status: Optional[int] = None
    mcp_alternative: str = ""
    extra: dict = field(default_factory=dict)

    # -- thuộc tính tiện dụng --------------------------------------------
    @property
    def blocked_by_policy(self) -> bool:
        """True nếu nguyên nhân là chính sách mạng, không phải lỗi kỹ thuật."""
        return self.kind in _BLOCKED_KINDS

    @property
    def remedy(self) -> str:
        if self.kind == EGRESS_BLOCKED:
            return (
                f"Host '{self.host}' không nằm trong allowlist egress của môi trường này.\n"
                f"  → Cách sửa: claude.ai › Settings › Claude Code › Environments,\n"
                f"    mở network policy hoặc thêm '{self.host}' vào allowlist.\n"
                f"  → KHÔNG tắt xác thực TLS, KHÔNG bỏ HTTPS_PROXY, KHÔNG đi vòng qua mirror.\n"
                f"  → Xem {ROUTING_DOC} để biết nguồn thay thế.\n"
                f"  LƯU Ý: proxy tự phân giải DNS, nên tên miền GÕ SAI hoặc không tồn tại\n"
                f"    cũng trả về đúng lỗi 403 này. Hãy kiểm tra lại chính tả host trước\n"
                f"    khi kết luận là bị chặn."
            )
        if self.kind == PROXY_AUTH:
            return ("Proxy yêu cầu xác thực (407). Đây là cấu hình phía tổ chức, "
                    "không xử lý được trong phiên làm việc.")
        if self.kind == TLS_UNTRUSTED:
            return ("Công cụ không đọc CA bundle của proxy. Trỏ nó tới "
                    "/root/.ccr/ca-bundle.crt (SSL_CERT_FILE / REQUESTS_CA_BUNDLE). "
                    "Tuyệt đối không tắt xác thực chứng chỉ.")
        if self.kind == DNS_FAILURE:
            return f"Không phân giải được tên miền '{self.host}'. Kiểm tra DNS/mạng."
        if self.kind == TIMEOUT:
            return "Hết thời gian chờ. Nguồn có thể đang quá tải — thử lại sau."
        if self.kind == OFFLINE:
            return "Không có kết nối mạng ra ngoài."
        if self.kind == HTTP_ERROR:
            return f"Nguồn trả về HTTP {self.status}. Kiểm tra tham số truy vấn hoặc rate limit."
        return "Nguyên nhân chưa xác định — xem chi tiết bên dưới."

    def report(self) -> str:
        """Thông báo đầy đủ, dùng để in ra cho người dùng."""
        lines = [
            "",
            "=" * 72,
            f"  NGUỒN KHÔNG TRUY CẬP ĐƯỢC — {self.kind.upper()}",
            "=" * 72,
            f"  URL   : {self.url or self.host}",
            f"  Chi tiết: {self.detail}",
            "",
            self.remedy,
        ]
        if self.mcp_alternative:
            lines += ["", f"  ĐƯỜNG ĐI THAY THẾ (dùng được ngay, không qua tường lửa này):",
                      f"    {self.mcp_alternative}"]
        lines += [
            "",
            "  QUAN TRỌNG: đây KHÔNG phải 'không tìm thấy kết quả'.",
            "  Không được suy ra kết luận y khoa, và tuyệt đối không bịa trích dẫn,",
            "  khi nguồn chưa tra được.",
            "=" * 72,
            "",
        ]
        return "\n".join(lines)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.kind}] {self.host or self.url}: {self.detail}"


# --- Đăng ký nguồn + tương đương MCP -------------------------------------
# mcp_alternative: công cụ MCP chạy server-side, KHÔNG đi qua egress của
# container, nên vẫn hoạt động khi host bị chặn.
SOURCES: dict[str, dict[str, str]] = {
    "pubmed": {
        "host": "eutils.ncbi.nlm.nih.gov",
        "probe": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json",
        "purpose": "PubMed E-utilities (esearch/efetch/esummary)",
        "mcp": "mcp__PubMed__search_articles, get_article_metadata, get_full_text_article, "
               "convert_article_ids, find_related_articles, lookup_article_by_citation",
    },
    "pubmed_web": {
        "host": "pubmed.ncbi.nlm.nih.gov",
        "probe": "https://pubmed.ncbi.nlm.nih.gov/",
        "purpose": "Giao diện web PubMed",
        "mcp": "mcp__PubMed__search_articles",
    },
    "ncbi": {
        "host": "www.ncbi.nlm.nih.gov",
        "probe": "https://www.ncbi.nlm.nih.gov/",
        "purpose": "NCBI (PMC, Gene, ClinVar, BLAST...)",
        "mcp": "mcp__PubMed__* (chỉ phần văn liệu; Gene/ClinVar/BLAST không có tương đương MCP)",
    },
    "clinicaltrials": {
        "host": "clinicaltrials.gov",
        "probe": "https://clinicaltrials.gov/api/v2/version",
        "purpose": "ClinicalTrials.gov API v2",
        "mcp": "mcp__Clinical_Trials__search_trials, get_trial_details, analyze_endpoints, "
               "search_by_sponsor, search_investigators, search_by_eligibility",
    },
    "crossref": {
        "host": "api.crossref.org",
        "probe": "https://api.crossref.org/works/10.1136/bmj.n71",
        "purpose": "Crossref REST + dữ liệu Retraction Watch (kiểm bài bị rút)",
        "mcp": "mcp__Scite__search_literature -> editorialNotices (retracted/concern/"
               "correction/erratum) + bộ lọc has_retraction. ĐÃ ĐỐI CHỨNG trên Mehra 2020 "
               "và Wakefield 1998. Quy trình: scripts/retraction_check.py",
    },
    "europepmc": {
        "host": "www.ebi.ac.uk",
        "probe": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=cancer&format=json&pageSize=1",
        "purpose": "Europe PMC (abstract + full text mở)",
        "mcp": "mcp__PubMed__get_full_text_article (chỉ phần PMC), mcp__Elicit__search_papers",
    },
    "openfda": {
        "host": "api.fda.gov",
        "probe": "https://api.fda.gov/drug/label.json?limit=1",
        "purpose": "openFDA — nhãn thuốc, thu hồi, FAERS, thiết bị",
        "mcp": "mcp__Scite__search_faers, search_maude, search_device510k, search_drugs, "
               "search_510k_summaries, search_mhra",
    },
    "openalex": {
        "host": "api.openalex.org",
        "probe": "https://api.openalex.org/works?per-page=1",
        "purpose": "OpenAlex — đồ thị trích dẫn, siêu dữ liệu",
        "mcp": "mcp__Scholar_Gateway__semanticSearch, mcp__Consensus__search",
    },
    "unpaywall": {
        "host": "api.unpaywall.org",
        "probe": "https://api.unpaywall.org/v2/10.1136/bmj.n71?email=test@example.com",
        "purpose": "Unpaywall — tìm bản toàn văn hợp pháp",
        "mcp": "KHÔNG có tương đương MCP.",
    },
    "biorxiv": {
        "host": "api.biorxiv.org",
        "probe": "https://api.biorxiv.org/details/biorxiv/10.1101/2020.01.30.927871",
        "purpose": "bioRxiv / medRxiv preprint",
        "mcp": "mcp__bioRxiv__search_preprints, get_preprint, search_published_preprints",
    },
    "dailymed": {
        "host": "dailymed.nlm.nih.gov",
        "probe": "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?pagesize=1",
        "purpose": "DailyMed — nhãn thuốc FDA nguyên văn",
        "mcp": "mcp__Scite__search_drugs (một phần).",
    },
    "semanticscholar": {
        "host": "api.semanticscholar.org",
        "probe": "https://api.semanticscholar.org/graph/v1/paper/search?query=covid&limit=1",
        "purpose": "Semantic Scholar",
        "mcp": "mcp__Scholar_Gateway__semanticSearch",
    },
}


def _host_of(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def _mcp_for_host(host: str) -> str:
    for meta in SOURCES.values():
        if meta["host"] == host:
            return meta["mcp"]
    return ""


def classify(exc: BaseException, url: str = "") -> SourceUnavailable:
    """Quy một exception mạng về nguyên nhân cụ thể + cách xử lý.

    Nhận diện được lỗi từ cả `urllib` lẫn `requests` (nếu có), vì cả hai đều
    giữ nguyên chuỗi 'Tunnel connection failed: <mã>' do proxy trả về.
    """
    if isinstance(exc, SourceUnavailable):
        return exc

    host = _host_of(url)
    text = f"{exc}".strip()
    # requests bọc nhiều lớp; gom cả chuỗi nguyên nhân lồng nhau.
    cause = getattr(exc, "reason", None) or getattr(exc, "__cause__", None)
    if cause is not None:
        text = f"{text} | {cause}"
    low = text.lower()

    kind = UNKNOWN
    status: Optional[int] = None

    if isinstance(exc, urllib.error.HTTPError):
        kind, status = HTTP_ERROR, exc.code
        if exc.code == 407:
            kind = PROXY_AUTH
        elif exc.code == 403 and "tunnel" in low:
            kind = EGRESS_BLOCKED
    elif "tunnel connection failed" in low:
        # Dấu hiệu chắc chắn nhất: proxy từ chối mở tunnel.
        kind = PROXY_AUTH if "407" in low else EGRESS_BLOCKED
        if "403" in low:
            kind = EGRESS_BLOCKED
        status = 403 if kind == EGRESS_BLOCKED else 407
    elif isinstance(exc, (ssl.SSLError, ssl.SSLCertVerificationError)) or \
            "certificate verify failed" in low or "self-signed certificate" in low:
        kind = TLS_UNTRUSTED
    elif isinstance(exc, socket.timeout) or "timed out" in low or "timeout" in low:
        kind = TIMEOUT
    elif isinstance(exc, socket.gaierror) or "name or service not known" in low \
            or "nodename nor servname" in low or "temporary failure in name resolution" in low:
        kind = DNS_FAILURE
    elif "network is unreachable" in low or "connection refused" in low:
        kind = OFFLINE

    return SourceUnavailable(
        kind=kind, url=url, host=host, detail=text, status=status,
        mcp_alternative=_mcp_for_host(host),
    )


def is_blocked(exc: BaseException) -> bool:
    """True nếu lỗi là do chính sách mạng chặn, không phải nguồn hết dữ liệu."""
    return classify(exc).blocked_by_policy


def _open(url: str, timeout: float = 20.0, headers: Optional[dict] = None):
    req = urllib.request.Request(
        url, headers=headers or {"User-Agent": "medical-research-skills/1.0 (evidence_net)"}
    )
    return urllib.request.urlopen(req, timeout=timeout)


def urlopen_text(url: str, timeout: float = 20.0, headers: Optional[dict] = None) -> str:
    """Như urlopen nhưng ném SourceUnavailable có chẩn đoán rõ ràng."""
    try:
        with _open(url, timeout, headers) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001 - phân loại lại ngay bên dưới
        raise classify(exc, url) from exc


def urlopen_json(url: str, timeout: float = 20.0, headers: Optional[dict] = None) -> Any:
    """Tải và parse JSON, ném SourceUnavailable khi không truy cập được."""
    raw = urlopen_text(url, timeout, headers)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SourceUnavailable(
            kind=HTTP_ERROR, url=url, host=_host_of(url),
            detail=f"Nguồn trả về nội dung không phải JSON: {raw[:200]}",
            mcp_alternative=_mcp_for_host(_host_of(url)),
        ) from exc


def probe(name_or_url: str, timeout: float = 15.0) -> Tuple[bool, Optional[SourceUnavailable]]:
    """Thử một nguồn. Trả (True, None) nếu vào được, (False, chẩn đoán) nếu không."""
    meta = SOURCES.get(name_or_url)
    url = meta["probe"] if meta else name_or_url
    try:
        with _open(url, timeout) as resp:
            resp.read(256)
        return True, None
    except urllib.error.HTTPError:
        # Có phản hồi HTTP nghĩa là tunnel đã mở và tới được máy chủ nguồn.
        # Mã lỗi (401/403/404/429...) là chuyện của truy vấn hoặc khoá API,
        # không phải chuyện chính sách mạng. Coi như đường mạng THÔNG.
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, classify(exc, url)


def probe_all(timeout: float = 15.0) -> dict[str, Tuple[bool, Optional[SourceUnavailable]]]:
    """Dò toàn bộ nguồn đã đăng ký."""
    return {name: probe(name, timeout) for name in SOURCES}


def require(name: str, timeout: float = 15.0) -> None:
    """Bảo đảm nguồn dùng được, nếu không thì dừng với thông báo rõ ràng.

    Dùng ở đầu script để thất bại SỚM và TO, thay vì trả kết quả rỗng
    khiến người đọc tưởng là 'không có bằng chứng nào'.
    """
    ok, diag = probe(name, timeout)
    if not ok and diag is not None:
        raise diag
