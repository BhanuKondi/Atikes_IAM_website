from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = "change-this-before-production"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{(BASE_DIR / 'instance' / 'atikes_iam.sqlite').as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
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
