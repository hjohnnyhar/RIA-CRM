# RIA CRM

A web-based CRM for Registered Investment Advisors (RIAs).

## Tech Stack

**Backend**
- Python 3.12
- Flask 3.0
- SQLAlchemy 2.0 (ORM)
- psycopg2-binary (PostgreSQL driver)
- python-dotenv (environment variable management)

**Database**
- Supabase (PostgreSQL) — production
- SQLite — local fallback (no `.env` file present)

**Frontend**
- Jinja2 templating
- Bootstrap 5.3
- Bootstrap Icons 1.11
- FullCalendar 6.1.9 (calendar UI)
- Vanilla JavaScript

**Deployment**
- Vercel (production hosting)
- GitHub (source control) — [hjohnnyhar/RIA-CRM](https://github.com/hjohnnyhar/RIA-CRM)

---

## Features

- **Welcome Dashboard** — personalized view per team member with today's meetings and assigned tasks
- **Households** — manage client households, contacts, and accounts (AUM tracking)
- **Calendar** — meetings and tasks toggle; click/drag to create; day/week/month views
- **Tasks** — assigned to internal team members with priority, status, and due date
- **Meetings** — linked to households with attendees
- **Team Members** — internal users (Advisors, Operations, etc.) separate from household clients

---

## Local Setup

```bash
git clone https://github.com/hjohnnyhar/RIA-CRM.git
cd RIA-CRM
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://your-supabase-connection-string
SECRET_KEY=your-secret-key
```

Run the app:
```bash
python app.py
```

Open http://localhost:5000

To seed sample data:
```bash
python seed.py
```

---

## Deployment (Vercel)

Set the following environment variables in Vercel dashboard (Settings → Environment Variables):

| Variable | Description |
|---|---|
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `SECRET_KEY` | Flask secret key for sessions |

The app auto-deploys from the `master` branch on GitHub.
