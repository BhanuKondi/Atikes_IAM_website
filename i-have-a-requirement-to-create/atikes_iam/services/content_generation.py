from html import unescape
from re import sub
from urllib.request import Request, urlopen


def generate_trend_content(trend):
    source_text = _fetch_source_text(trend.url)
    base = source_text or trend.summary or trend.title
    cleaned = " ".join(base.split())
    excerpt = cleaned[:900]
    return (
        f"{trend.title}\n\n"
        f"ATIKES perspective:\n"
        f"This trend is relevant for IAM teams because it connects to access governance, "
        f"identity lifecycle operations, authentication controls, and compliance readiness. "
        f"Organizations should review how this topic affects provisioning, access reviews, "
        f"privileged access, and user experience across enterprise applications.\n\n"
        f"Key points for readers:\n"
        f"- Understand the identity and security risk behind the update.\n"
        f"- Check whether current IAM processes already cover this scenario.\n"
        f"- Identify affected platforms such as SailPoint, Okta, Saviynt, Ping Identity, cloud IAM, or PAM tools.\n"
        f"- Convert the learning into a practical control, review, or automation improvement.\n\n"
        f"Source context:\n{excerpt}"
    )


def _fetch_source_text(url):
    if not url:
        return ""
    request = Request(url, headers={"User-Agent": "ATIKES-IAM-Content/1.0"})
    with urlopen(request, timeout=10) as response:
        html = response.read(800000).decode("utf-8", errors="ignore")
    text = sub(r"(?is)<(script|style).*?>.*?</\\1>", " ", html)
    text = sub(r"(?is)<[^>]+>", " ", text)
    return " ".join(unescape(text).split())
