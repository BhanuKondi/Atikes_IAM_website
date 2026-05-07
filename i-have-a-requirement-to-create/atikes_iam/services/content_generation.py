from html import unescape
from html.parser import HTMLParser
from re import split, sub
from urllib.request import Request, urlopen


class ArticleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip_depth = 0
        self.capture_depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header", "form"}:
            self.skip_depth += 1
        if tag in {"article", "main", "p", "h1", "h2", "h3", "li"}:
            self.capture_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header", "form"} and self.skip_depth:
            self.skip_depth -= 1
        if tag in {"article", "main", "p", "h1", "h2", "h3", "li"} and self.capture_depth:
            self.capture_depth -= 1
            self.parts.append(" ")

    def handle_data(self, data):
        if self.skip_depth:
            return
        text = " ".join(unescape(data).split())
        if self.capture_depth and len(text) > 25:
            self.parts.append(text)

    def text(self):
        return " ".join(self.parts)


def generate_trend_content(trend):
    article_text = _fetch_source_text(trend.url)
    base = _clean_text(article_text or trend.summary or trend.title)
    sentences = _sentences(base)
    summary = _build_summary(sentences)
    takeaways = _build_takeaways(sentences)

    return (
        f"{trend.title}\n\n"
        f"Summary\n"
        f"{summary}\n\n"
        f"Why this matters for IAM teams\n"
        f"This update is relevant to identity teams because it may affect governance, access reviews, "
        f"authentication policy, privileged access, lifecycle automation, and compliance evidence. "
        f"IAM leaders should review whether current controls across SailPoint, Okta, Saviynt, Ping Identity, "
        f"cloud IAM, and PAM platforms already address the risks described here.\n\n"
        f"Recommended actions\n"
        f"{takeaways}"
    )


def _fetch_source_text(url):
    if not url:
        return ""
    request = Request(url, headers={"User-Agent": "ATIKES-IAM-Content/1.0"})
    with urlopen(request, timeout=12) as response:
        html = response.read(1500000).decode("utf-8", errors="ignore")
    parser = ArticleTextParser()
    parser.feed(html)
    return parser.text()


def _clean_text(text):
    text = sub(r"https?://\\S+", " ", text)
    text = sub(r"\\{[^{}]{80,}\\}", " ", text)
    text = sub(r"\[[^\[\]]{80,}\]", " ", text)
    text = sub(r"\\b(@type|@id|context|schema.org|wp-json|CDATA)\\b", " ", text, flags=2)
    text = sub(r"\\s+", " ", text)
    return text.strip()


def _sentences(text):
    rows = [row.strip() for row in split(r"(?<=[.!?])\\s+", text) if len(row.strip()) > 55]
    blocked = ("cookie", "subscribe", "newsletter", "privacy policy", "terms of use", "all rights reserved")
    clean = []
    for row in rows:
        low = row.lower()
        if any(term in low for term in blocked):
            continue
        if row.count("{") or row.count("[") or row.count("\\"):
            continue
        clean.append(row)
    return clean[:24]


def _build_summary(sentences):
    if not sentences:
        return "This IAM trend is under review. The article highlights a change that identity teams should evaluate for access governance, authentication, and operational risk."
    selected = sentences[:5]
    return " ".join(selected)


def _build_takeaways(sentences):
    candidates = sentences[5:12] or sentences[:4]
    if not candidates:
        return (
            "- Review the impact on identity governance and access controls.\n"
            "- Check whether existing IAM policies already cover this scenario.\n"
            "- Convert the learning into a practical control or automation improvement."
        )
    bullets = []
    for sentence in candidates[:4]:
        trimmed = sentence.strip()
        if len(trimmed) > 180:
            trimmed = trimmed[:177].rsplit(" ", 1)[0] + "..."
        bullets.append(f"- {trimmed}")
    return "\n".join(bullets)
