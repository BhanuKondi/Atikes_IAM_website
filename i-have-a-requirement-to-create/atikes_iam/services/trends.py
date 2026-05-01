from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from re import sub
from time import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from flask import current_app


_cache = {"expires_at": 0, "items": [], "errors": []}


def _entry_date(entry):
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if not value:
            continue
        try:
            parsed = parsedate_to_datetime(value)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
    return datetime.now(timezone.utc)


def _summary(entry):
    text = entry.get("summary") or entry.get("description") or ""
    return " ".join(unescape(sub(r"<[^>]+>", " ", text)).split())[:280]


def _text(node, names):
    for name in names:
        found = node.find(name)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def _link(node):
    rss_link = _text(node, ["link"])
    if rss_link:
        return rss_link
    for link_node in node.findall("{http://www.w3.org/2005/Atom}link"):
        href = link_node.attrib.get("href")
        if href:
            return href
    return ""


def _parse_feed(xml_bytes):
    root = ET.fromstring(xml_bytes)
    entries = []
    rss_items = root.findall(".//item")
    atom_entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    for node in rss_items:
        entries.append(
            {
                "title": _text(node, ["title"]),
                "summary": _text(node, ["description", "summary"]),
                "link": _link(node),
                "published": _text(node, ["pubDate", "published", "updated"]),
            }
        )

    for node in atom_entries:
        entries.append(
            {
                "title": _text(node, ["{http://www.w3.org/2005/Atom}title"]),
                "summary": _text(
                    node,
                    [
                        "{http://www.w3.org/2005/Atom}summary",
                        "{http://www.w3.org/2005/Atom}content",
                    ],
                ),
                "link": _link(node),
                "published": _text(
                    node,
                    [
                        "{http://www.w3.org/2005/Atom}published",
                        "{http://www.w3.org/2005/Atom}updated",
                    ],
                ),
            }
        )
    return entries


def _score(item, keywords):
    haystack = f"{item['title']} {item['summary']}".lower()
    return sum(1 for keyword in keywords if keyword in haystack)


def _source_domain(url):
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


def fetch_live_trends(force=False):
    now = time()
    if not force and _cache["expires_at"] > now:
        return _cache["items"], _cache["errors"], False

    feeds = current_app.config["TRENDS_FEEDS"]
    keywords = current_app.config["IAM_KEYWORDS"]
    items = []
    errors = []

    for feed in feeds:
        try:
            request = Request(
                feed["url"],
                headers={"User-Agent": "ATIKES-IAM-Trends/1.0"},
            )
            with urlopen(request, timeout=8) as response:
                entries = _parse_feed(response.read())
            if not entries:
                raise ValueError("Feed returned no readable entries")

            for entry in entries[:12]:
                link = entry.get("link", "")
                item = {
                    "title": entry.get("title", "Untitled IAM update").strip(),
                    "summary": _summary(entry),
                    "url": link,
                    "source": feed["name"],
                    "source_domain": _source_domain(link or feed["url"]),
                    "category": feed["category"],
                    "published_at": _entry_date(entry),
                }
                item["score"] = _score(item, keywords)
                if item["score"] > 0:
                    items.append(item)
        except Exception as exc:
            errors.append(f"{feed['name']}: {exc}")

    items.sort(key=lambda row: (row["published_at"], row["score"]), reverse=True)
    items = items[:36]
    _cache.update(
        {
            "expires_at": now + current_app.config["TRENDS_CACHE_SECONDS"],
            "items": items,
            "errors": errors,
        }
    )
    return items, errors, True
