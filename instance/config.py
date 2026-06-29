import os
from pathlib import Path
from urllib.parse import quote_plus


BASE_DIR = Path(__file__).resolve().parent.parent


def build_database_uri():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_engine = os.getenv("DB_ENGINE", "mysql").lower()
    if db_engine == "sqlite":
        return f"sqlite:///{(BASE_DIR / 'instance' / 'atikes_iam.sqlite').as_posix()}"

    user = os.getenv("MYSQL_USER", "hruser")
    password = quote_plus(os.getenv("MYSQL_PASSWORD", "Hr@1234"))
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "atikes_iam")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-before-production")
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    TRENDS_CACHE_SECONDS = 600
    TRENDS_FEEDS = [
        {
            "name": "Okta Blog",
            "url": "https://www.okta.com/blog/feed/",
            "website_url": "https://www.okta.com/blog/",
            "category": "Identity Platform",
        },
        {
            "name": "Curity Blog",
            "url": "https://curity.io/news-feed.xml",
            "website_url": "https://curity.io/blog/",
            "category": "API Security",
        },
        {
            "name": "IDSA Blog",
            "url": "https://www.idsalliance.org/blog/feed/",
            "website_url": "https://www.idsalliance.org/blog/",
            "category": "Identity Security",
        },
        {
            "name": "SecurityWeek Identity & Access",
            "url": "https://www.securityweek.com/category/identity-access/feed/",
            "website_url": "https://www.securityweek.com/category/identity-access/",
            "category": "Cybersecurity",
        },
        {
            "name": "SailPoint Blog",
            "url": "https://www.sailpoint.com/blog/feed/",
            "website_url": "https://www.sailpoint.com/blog/",
            "category": "Identity Governance",
        },
        {
            "name": "Identity Management Institute",
            "url": "https://identitymanagementinstitute.org/feed/",
            "website_url": "https://identitymanagementinstitute.org/",
            "category": "IAM Careers",
        },
    ]

    IAM_KEYWORDS = [
        "identity",
        "access",
        "iam",
        "iga",
        "governance",
        "sailpoint",
        "okta",
        "entra",
        "azure ad",
        "rbac",
        "pam",
        "privileged",
        "zero trust",
        "passwordless",
        "mfa",
        "provisioning",
        "certification",
        "authentication",
        "authorization",
        "lifecycle",
        "compliance",
    ]
