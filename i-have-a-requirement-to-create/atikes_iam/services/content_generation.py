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
    about = _section(sentences, 0, "The article discusses an IAM and security development that identity teams should review.")
    subject = _section(sentences, 1, "The subject is connected to identity governance, authentication, access control, and operational risk.")
    happened = _section(sentences, 2, "The article explains a change, concern, or recommendation that may affect enterprise IAM programs.")
    conclusion = _section(sentences, 3, "The conclusion is that IAM teams should evaluate the impact and convert the learning into practical controls.")

    return (
        f"{trend.title}\n\n"
        f"What this article is about\n"
        f"{about}\n\n"
        f"Main subject\n"
        f"{subject}\n\n"
        f"What happened\n"
        f"{happened}\n\n"
        f"Conclusion\n"
        f"{conclusion} For ATIKES readers, the practical takeaway is to review access governance, "
        f"authentication, privileged access, lifecycle automation, and compliance controls against this trend."
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


def _section(sentences, index, fallback):
    if not sentences:
        return fallback
    start = index * 2
    selected = sentences[start : start + 2] or sentences[:2]
    text = " ".join(selected)
    if len(text) > 420:
        text = text[:417].rsplit(" ", 1)[0] + "..."
    return text
