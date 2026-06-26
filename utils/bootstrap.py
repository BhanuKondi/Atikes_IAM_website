from models.db import db
from models import TrendSource


def sync_trend_sources(app):
    for feed in app.config["TRENDS_FEEDS"]:
        source = TrendSource.query.filter_by(feed_url=feed["url"]).first()
        if source is None:
            source = TrendSource(feed_url=feed["url"])
            db.session.add(source)
        source.name = feed["name"]
        source.website_url = feed.get("website_url", "")
        source.category = feed["category"]
        source.is_active = True
    db.session.commit()
