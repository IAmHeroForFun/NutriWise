# 10 — Deployment Guide

## When to Deploy

Deploy only **after** local testing is complete and all Phase 9 checklist items pass.

---

## What Changes Between Local and Production

| Setting | Local | Production |
|---|---|---|
| Database | SQLite (`db.sqlite3`) | Supabase PostgreSQL |
| `DEBUG` | `True` | `False` |
| `SECRET_KEY` | Any string | Strong random key |
| `ALLOWED_HOSTS` | `["*"]` | `["yourdomain.com"]` |
| Static files | Served by Django dev server | `collectstatic` → served by host |
| Server | `python manage.py runserver` | `gunicorn dietary_app.wsgi` |

Only the `.env` file changes. The code is identical.

---

## Step 1 — Supabase Database Setup

1. Create account at https://supabase.com (free)
2. Create new project → choose region nearest to India (e.g. Singapore)
3. Go to: **Settings → Database → Connection string**
4. Use the **direct connection** (not the pooler):
   - Port: **5432** (NOT 6543 — the pooler port breaks Django migrations)
5. Note the values:
   ```
   Host:     db.xxxxxxxxxxxx.supabase.co
   Port:     5432
   Database: postgres
   User:     postgres
   Password: [your project password]
   ```
6. Update `.env`:
   ```bash
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your-supabase-password
   DB_HOST=db.xxxxxxxxxxxx.supabase.co
   ```

---

## Step 2 — Install Production Dependencies

```bash
pip install psycopg2-binary gunicorn
pip freeze > requirements.txt
```

---

## Step 3 — Run Migrations Against Supabase

```bash
# Make sure .env has DB_HOST set
python manage.py migrate
python manage.py createsuperuser
```

---

## Step 4 — Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## Step 5 — Production `.env`

```bash
SECRET_KEY=generate-a-strong-random-key-here
DEBUG=False
OPENWEATHER_API_KEY=your-openweather-key

DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-password
DB_HOST=db.xxxxxxxxxxxx.supabase.co

ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Generate a strong secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Hosting Options

### Option A — Railway (Recommended for hackathon)

**Easiest. Git push to deploy.**

1. Push code to GitHub
2. Go to https://railway.app → New project → Deploy from GitHub repo
3. Set environment variables in Railway dashboard (copy from `.env`)
4. Create `Procfile` in project root:
   ```
   web: gunicorn dietary_app.wsgi --log-file -
   ```
5. Railway auto-detects Python → builds → deploys
6. Get URL: `yourapp.railway.app`

### Option B — Render

1. Push code to GitHub
2. Go to https://render.com → New Web Service → Connect repo
3. Set:
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn dietary_app.wsgi`
4. Add all env vars in the dashboard
5. Deploy

### Option C — PythonAnywhere

1. Upload code (git clone or zip upload)
2. Create virtualenv on the server
3. Configure WSGI file to point to `dietary_app/wsgi.py`
4. Set env vars in the dashboard
5. Reload web app

---

## Post-Deployment Checklist

- [ ] App opens at live URL
- [ ] `/admin/` accessible, login works
- [ ] Upload a test PDF book → click ▶ Process → food records created
- [ ] Register a test user → complete 7-step onboarding
- [ ] Dashboard shows food recommendations with source citations
- [ ] Weather shows for user's location
- [ ] "Can't make this?" feature works
- [ ] All hard filters apply correctly

---

## Troubleshooting

### "OperationalError: could not connect to server"
→ Check `DB_HOST` is the **direct** connection (port 5432), not the pooler

### "Static files not loading in production"
→ Run `python manage.py collectstatic` and check `STATIC_ROOT` in settings

### "DisallowedHost" error
→ Add your domain to `ALLOWED_HOSTS` in production `.env`

### "500 error in production"
→ Temporarily set `DEBUG=True` to see the error, then fix and set back to `False`

### PDF processing hangs
→ Normal for large PDFs. For production, consider upgrading to background tasks (Celery + Redis) after MVP.
