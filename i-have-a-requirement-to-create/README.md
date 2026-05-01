# ATIKES IAM Community Website

Flask website for ATIKES with:

- Live IAM trends collected from public IAM/security RSS feeds
- User sign up, sign in, questions, answers, and voting-ready data model
- Expert directory ranked from real answer activity
- Upcoming events stored in a dedicated publishing table
- ATIKES-branded home page inspired by the provided reference design

## Run Locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.

## Structure

```text
atikes_iam/
  __init__.py           Flask app factory
  config.py             Settings and live feed sources
  extensions.py         Shared Flask extensions
  models.py             Users, questions, answers
  services/
    trends.py           Live RSS trend collector with cache
  routes/
    main.py             Home and static pages
    auth.py             Register/login/logout
    trends.py           Live trends page
    qa.py               Q&A pages and posting
    experts.py          Directory ranked by answer activity
    events.py           Upcoming events page
  templates/            Jinja pages and partials
  static/
    css/styles.css      Main responsive UI
    js/app.js           Small UI helpers
run.py
instance/
  atikes_iam.sqlite     Created automatically at first run
```

## Live Trend Sources

Feeds are configured in `atikes_iam/config.py`. The page fetches public feeds, filters IAM/security topics, caches briefly, and can be forced to refresh with `/trends?refresh=1`.

## Database Tables

The backend SQLite database is created automatically in `instance/atikes_iam.sqlite`.

- `user`: registered community members
- `trend_source`: configured real IAM RSS/source websites
- `trend`: stored trend articles fetched from those sources
- `question`: IAM questions posted by signed-in users
- `answer`: answers posted by signed-in users
- `expert_profile`: expert directory rows generated from user Q&A activity
- `upcoming_event`: future IAM webinars, conferences, and sessions

The trends page reads from `trend`; refresh first updates `trend_source` and stores new articles into `trend`. Experts are not sample cards: `expert_profile` is updated when users ask or answer questions, and listed experts require at least one answer.
