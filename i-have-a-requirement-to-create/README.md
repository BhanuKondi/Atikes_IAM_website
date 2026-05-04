# ATIKES IAM Community Website

Flask website for ATIKES with:

- Live IAM trends collected from public IAM/security RSS feeds
- User sign up, sign in, questions, answers, and voting-ready data model
- Expert directory ranked from real answer activity
- Upcoming events stored in a dedicated publishing table
- Admin/user modes with approval workflow for trends, questions, and answers
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
    admin.py            Admin review, edit, and approve workflow
  templates/            Jinja pages and partials
  static/
    css/styles.css      Main responsive UI
    js/app.js           Small UI helpers
run.py
atikes_mysql_schema_seed.sql  MySQL schema and seed data
```

## Use Local MySQL

The app now defaults to MySQL on your local machine:

```text
mysql+pymysql://root:<password>@127.0.0.1:3306/atikes_iam
```

Set your password before running Flask:

```powershell
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your_mysql_password"
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_DATABASE="atikes_iam"
python run.py
```

If you want to use SQLite temporarily:

```powershell
$env:DB_ENGINE="sqlite"
python run.py
```

## Live Trend Sources

Feeds are configured in `atikes_iam/config.py`. The page fetches public feeds, filters IAM/security topics, caches briefly, and can be forced to refresh with `/trends?refresh=1`.

## Database Tables

The backend MySQL database is `atikes_iam`. Import `atikes_mysql_schema_seed.sql` first if the tables do not exist.

- `user`: registered community members
- `trend_source`: configured real IAM RSS/source websites
- `trend`: stored trend articles fetched from those sources
- `question`: IAM questions posted by signed-in users
- `answer`: answers posted by signed-in users
- `expert_profile`: expert directory rows generated from user Q&A activity
- `upcoming_event`: future IAM webinars, conferences, and sessions

Trends, questions, and answers use `status` moderation. Newly fetched trends and newly posted Q&A content are `pending`. Admin users review, edit, and approve them from `/admin/`; approved records become visible to signed-in users. Experts are not sample cards: `expert_profile` is updated from approved Q&A activity, and listed experts require at least one approved answer.

Seed admin account from `atikes_mysql_schema_seed.sql`:

```text
admin@atikes.com
Atikes@123
```
