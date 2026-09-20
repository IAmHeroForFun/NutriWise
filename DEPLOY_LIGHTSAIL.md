# AWS Lightsail Quick Deployment Guide: NutriWise

> **Customized for:** AWS Lightsail Multi-Service Architecture  
> **Server Directory:** `/opt/services/nutriwise`  
> **Shared Network:** `omvi_blog_default`  
> **Domain:** `nutriwise.omvihub.in`  
> **Container Name:** `nutriwise_web`  
> **Upstream:** `http://nutriwise_web:8000`

---

## Architecture Summary

Your Lightsail server (`ubuntu@ip-172-26-1-124`) hosts `dns-stack` and `omvi_blog` with a central Nginx reverse proxy running on the `omvi_blog_default` Docker network.

```
                    Internet (HTTPS Port 443 / HTTP Port 80)
                                       │
                                       ▼
                   Central Nginx (Port 80/443)
               (Network: omvi_blog_default bridge)
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
     omvihub.in                                         nutriwise.omvihub.in
   (omvi_blog web)                                      (nutriwise_web:8000)
```

By connecting NutriWise to `omvi_blog_default`, the central Nginx can proxy requests directly to `http://nutriwise_web:8000` without exposing any ports on the host.

---

## Step 1: On Your Local Machine (Push to GitHub)

In your local repository (`/mnt/Work/projects/hackday1.0`):

```bash
cd /mnt/Work/projects/hackday1.0

# Stage all files
git add .

# Commit your changes
git commit -m "feat: complete Lightsail docker deployment with PostgreSQL support and 2-stage SSL"

# Push to your repository
git push origin master
```

---

## Step 2: On Your Lightsail Server (Pull the Code)

SSH into your Lightsail instance:

```bash
# Navigate to your services directory
cd /opt/services/nutriwise

# Pull the latest changes
git pull origin master
```

Verify that the files exist:
```bash
ls -la
# You should see Dockerfile, docker-compose.lightsail.yml, requirements.txt, dietary_app, core, nginx/, etc.
```

---

## Step 3: Choose Your Database & Create `.env`

NutriWise supports both **SQLite** and **PostgreSQL**.

### Database Options:

#### Option A: Persistent SQLite (Recommended for 2 GB Lightsail — Zero Extra RAM)
SQLite runs embedded within Python and requires **0 extra RAM or services**. The database file is stored safely on the host at `/opt/services/nutriwise/data/db.sqlite3` across container restarts.

#### Option B: PostgreSQL (External RDS, Supabase, or Existing Postgres Container)
If you already have a PostgreSQL container (e.g. on `omvi_blog_default`) or an external managed PostgreSQL (like Supabase or AWS RDS), NutriWise connects to it seamlessly via `psycopg2-binary`.

---

### Create the `.env` file:

```bash
nano .env
```

Paste your `.env` configuration (no database settings needed!):
```ini
# Security
DEBUG=False
SECRET_KEY=nutriwise-prod-sec-key-replace-with-a-random-string-98342718
ALLOWED_HOSTS=nutriwise.omvihub.in,localhost,127.0.0.1,nutriwise_web
CSRF_TRUSTED_ORIGINS=https://nutriwise.omvihub.in

# AI & Weather APIs
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OPENWEATHER_API_KEY=your_actual_openweather_api_key_here
```

Press `Ctrl+O`, `Enter` to save, and `Ctrl+X` to exit.

> **Optional (Instant 60 Foods & Books in Production):**  
> If you'd like your production server to immediately have all 60 foods, meal pairings, and book extractions from your local machine, you can copy your local `db.sqlite3` to `/opt/services/nutriwise/data/db.sqlite3`:
> ```bash
> mkdir -p /opt/services/nutriwise/data
> # From your local machine:
> # scp /mnt/Work/projects/hackday1.0/db.sqlite3 ubuntu@YOUR_SERVER_IP:/opt/services/nutriwise/data/db.sqlite3
> ```
> If you don't copy it, running `python manage.py migrate` in Step 5 will simply initialize a fresh database.


#### If Using Option B (PostgreSQL):
```ini
# Security
DEBUG=False
SECRET_KEY=nutriwise-prod-sec-key-replace-with-a-random-string-98342718
ALLOWED_HOSTS=nutriwise.omvihub.in,localhost,127.0.0.1,nutriwise_web
CSRF_TRUSTED_ORIGINS=https://nutriwise.omvihub.in

# AI & Weather APIs
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OPENWEATHER_API_KEY=your_actual_openweather_api_key_here

# PostgreSQL Settings (Container name, localhost, or external endpoint)
DB_HOST=postgres_container_name_or_endpoint
DB_NAME=nutriwise_db
DB_USER=nutriwise_user
DB_PASSWORD=your_db_password
DB_PORT=5432
```

Press `Ctrl+O`, `Enter` to save, and `Ctrl+X` to exit.

---

## Step 4: Build and Launch `nutriwise_web`

Build the application image (installs Python packages, `psycopg2-binary`, OCR libraries) and start the container:

```bash
docker compose -f docker-compose.lightsail.yml up -d --build
```

### Verify Container Status:
```bash
docker ps -f name=nutriwise_web
```
You should see `nutriwise_web` with Status `Up` (attached to `omvi_blog_default`).

Check logs to verify clean boot:
```bash
docker logs --tail 20 nutriwise_web
```

---

## Step 5: Run Database Migrations & Initial Setup

Execute Django setup commands inside the container:

```bash
# 1. Run database migrations (creates all 10 schema tables)
docker compose -f docker-compose.lightsail.yml exec web python manage.py migrate

# 2. Collect static files into /app/staticfiles
docker compose -f docker-compose.lightsail.yml exec web python manage.py collectstatic --noinput

# 3. Create your administrator superuser account
docker compose -f docker-compose.lightsail.yml exec web python manage.py createsuperuser
```
*(Enter your chosen admin username, email, and password).*

---

## Step 6: Two-Stage SSL Certificate Generation (Foolproof)

> **Why 2 Stages?**  
> If Nginx attempts to load an SSL configuration before the certificate files exist at `/etc/letsencrypt/live/nutriwise.omvihub.in/`, Nginx **fails syntax testing and crashes**.  
> We solve this cleanly: **Stage 1 (HTTP)** lets Nginx serve the ACME challenge, Certbot issues the certificate, and **Stage 2 (HTTPS)** locks in SSL.

### 1. DNS Pre-check
Make sure your domain DNS has an **A Record** for `nutriwise.omvihub.in` pointing to your Lightsail public IP.
Verify with:
```bash
ping -c 2 nutriwise.omvihub.in
```

---

### 2. Stage 1: Load HTTP-Only Pre-SSL Config

Copy NutriWise's Stage 1 configuration into your central Nginx `conf.d/` directory:

```bash
# Copy Stage 1 config (adjust destination path to your central nginx conf folder)
# E.g., if central nginx reads from /opt/services/omvi_blog/nginx/conf.d/:
sudo cp /opt/services/nutriwise/nginx/nutriwise_stage1_http.conf /opt/services/omvi_blog/nginx/conf.d/nutriwise.conf
```

Test and reload Nginx:
```bash
# If central Nginx is running in Docker:
docker exec $(docker ps -q -f name=nginx) nginx -t
docker exec $(docker ps -q -f name=nginx) nginx -s reload
```
*(Now `http://nutriwise.omvihub.in` is active and ready to handle the Let's Encrypt challenge).*

---

### 3. Issue the SSL Certificate via Certbot

Run Certbot to request the certificate:

**Method A: Using Host Certbot (if installed on Ubuntu host):**
```bash
sudo certbot certonly --webroot -w /var/www/certbot -d nutriwise.omvihub.in
```

**Method B: Using Dockerized Certbot:**
```bash
docker run --rm \
  -v /var/www/certbot:/var/www/certbot \
  -v /etc/letsencrypt:/etc/letsencrypt \
  certbot/certbot certonly --webroot -w /var/www/certbot -d nutriwise.omvihub.in
```

Verify the certificate files were created:
```bash
sudo ls -la /etc/letsencrypt/live/nutriwise.omvihub.in/
# You should see: cert.pem, chain.pem, fullchain.pem, privkey.pem
```

---

### 4. Stage 2: Activate Full HTTPS SSL Config

Now that the certificates exist, replace the Nginx configuration with the production HTTPS config:

```bash
sudo cp /opt/services/nutriwise/nginx/nutriwise.omvihub.in.conf /opt/services/omvi_blog/nginx/conf.d/nutriwise.conf
```

Test syntax and reload Nginx:
```bash
docker exec $(docker ps -q -f name=nginx) nginx -t
docker exec $(docker ps -q -f name=nginx) nginx -s reload
```

---

## Step 7: Verify Everything Is Live

1. **Visit the Web App**:  
   Open `https://nutriwise.omvihub.in` in your browser.  
   You should see the landing page with an active HTTPS padlock.
2. **Access Admin**:  
   Open `https://nutriwise.omvihub.in/admin/` and log in with your superuser.
3. **Upload Books**:  
   Under **Documents > Sources**, click **Add Source**, upload a nutrition PDF or EPUB, and click **Process Document** to extract foods automatically.

---

## Routine Maintenance & Operations

```bash
# View live application logs:
docker logs -f nutriwise_web

# Restart web container:
docker compose -f docker-compose.lightsail.yml restart web

# Pull updates and rebuild:
git pull origin master
docker compose -f docker-compose.lightsail.yml up -d --build
docker compose -f docker-compose.lightsail.yml exec web python manage.py migrate

# Database backup (SQLite):
cp /opt/services/nutriwise/data/db.sqlite3 /opt/backups/nutriwise_$(date +%F).sqlite3
```
