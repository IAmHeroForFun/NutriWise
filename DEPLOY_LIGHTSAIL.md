# AWS Lightsail Docker Master Deployment Guide: NutriWise

> **Customized for:** AWS Lightsail Multi-Service Architecture  
> **Server Directory:** `/opt/services/nutriwise`  
> **Shared Network:** `omvi_blog_default`  
> **Domain:** `nutriwise.omvihub.in`  
> **Container Name:** `nutriwise_web`  
> **Upstream Proxy:** `http://nutriwise_web:8000`  
> **Central Nginx Config:** `/opt/services/omvi_blog/nginx/default.conf`

---

## 1. Architectural Overview

Your Lightsail server (`ubuntu@ip-172-26-1-124`) co-hosts multiple services (`dns-stack`, `omvi_blog`, and `nutriwise`) using a central Nginx reverse proxy connected to the external bridge network `omvi_blog_default`.

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

- **Zero Port Collisions**: NutriWise runs internally on port `8000` inside `omvi_blog_default`. It does not expose ports 80/443 on the host.
- **Zero-RAM Persistent Database**: Uses SQLite stored on the host at `/opt/services/nutriwise/data/db.sqlite3` across container restarts.
- **Self-Contained Static Assets**: Uses **WhiteNoise** with Gzip compression and caching directly from Gunicorn, eliminating the need to mount static folders into the central Nginx container.

---

## 2. Step-by-Step Deployment Instructions

### Step 1: Push Code from Local Machine

In your local repository (`/mnt/Work/projects/hackday1.0`):

```bash
cd /mnt/Work/projects/hackday1.0

# Stage all files
git add .

# Commit changes
git commit -m "feat: complete production setup with WhiteNoise and Lightsail deployment guide"

# Push to GitHub
git push origin master
```

---

### Step 2: Pull Code on Lightsail Server

SSH into your Lightsail server and navigate to `/opt/services/nutriwise`:

```bash
cd /opt/services/nutriwise

# Discard any local conflicting edits and pull cleanly:
git restore .
git pull origin master
```

---

### Step 3: Create Production `.env` File

Create `/opt/services/nutriwise/.env`:

```bash
nano .env
```

Paste your configuration (no database credentials needed — SQLite runs automatically):

```ini
# Security Settings
DEBUG=False
SECRET_KEY=generate-a-strong-random-50-character-secret-key-here
ALLOWED_HOSTS=nutriwise.omvihub.in,localhost,127.0.0.1,nutriwise_web
CSRF_TRUSTED_ORIGINS=https://nutriwise.omvihub.in

# Production APIs
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OPENWEATHER_API_KEY=your_actual_openweather_api_key_here
```

Press `Ctrl+O`, `Enter` to save, and `Ctrl+X` to exit.

---

### Step 4: Fix Volume Permissions (One-Time Setup)

Ensure the container process has permission to create and write to SQLite and static folders:

```bash
sudo chmod -R 777 ./data ./staticfiles ./media
```

*(Optional: If you want to seed your production server with all 60 pre-extracted foods and books from your local development machine, copy your local `db.sqlite3` into `/opt/services/nutriwise/data/db.sqlite3`).*

---

### Step 5: Generate Free Let's Encrypt SSL Certificate

Since central Nginx binds port 80, use Certbot standalone by briefly pausing Nginx for 5 seconds:

```bash
# 1. Temporarily pause central Nginx
docker stop $(docker ps -q -f name=nginx)

# 2. Run Certbot to generate the certificate
sudo certbot certonly --standalone -d nutriwise.omvihub.in

# 3. Start central Nginx back up
docker start $(docker ps -aq -f name=nginx)
```

Certificates will be saved to:
- `/etc/letsencrypt/live/nutriwise.omvihub.in/fullchain.pem`
- `/etc/letsencrypt/live/nutriwise.omvihub.in/privkey.pem`

---

### Step 6: Build and Launch `nutriwise_web`

Build the Docker image and start the container in the background:

```bash
docker compose -f docker-compose.lightsail.yml up -d --build
```

### Verify Container Status:
```bash
docker ps -f name=nutriwise_web
```
Verify logs show Gunicorn listening at `http://0.0.0.0:8000`:
```bash
docker logs --tail 20 nutriwise_web
```

---

### Step 7: Create Administrator Account

Create your Django admin superuser:

```bash
docker compose -f docker-compose.lightsail.yml exec web python manage.py createsuperuser
```
*(Enter your chosen admin username, email, and password).*

---

### Step 8: Connect Central Nginx to NutriWise

Your central Nginx configuration file is `/opt/services/omvi_blog/nginx/default.conf`. Update it with the NutriWise server block:

```bash
# 1. Cleanly strip any previous partial nutriwise blocks
sudo sed -i '/upstream nutriwise/,$d' /opt/services/omvi_blog/nginx/default.conf

# 2. Append the clean nutriwise configuration
sudo cat /opt/services/nutriwise/nginx/nutriwise.omvihub.in.conf | sudo tee -a /opt/services/omvi_blog/nginx/default.conf

# 3. Restart Nginx to load the new file
docker restart $(docker ps -q -f name=nginx)

# 4. Verify syntax
docker exec $(docker ps -q -f name=nginx) nginx -t
```

You should see:
`nginx: the configuration file /etc/nginx/nginx.conf syntax is ok`  
`nginx: configuration file /etc/nginx/nginx.conf test is successful`

---

### Step 9: Verify Your Live Site

Open your browser and visit:
👉 **`https://nutriwise.omvihub.in`**

- **Landing Page**: Full green theme, hero section, features, and buttons.
- **Admin Dashboard**: Accessible at **`https://nutriwise.omvihub.in/admin/`**.
- **Static Assets**: CSS, JavaScript, and icons served with gzip compression and instant caching via WhiteNoise.

---

## 3. Routine Operations & Maintenance Cheat Sheet

### View Application Logs:
```bash
docker logs -f nutriwise_web
```

### Applying Future Code Updates:
```bash
cd /opt/services/nutriwise
git pull origin master
docker compose -f docker-compose.lightsail.yml up -d --build
```

### Restart Web Service:
```bash
docker compose -f docker-compose.lightsail.yml restart web
```

### Backup Database:
```bash
cp /opt/services/nutriwise/data/db.sqlite3 /opt/backups/nutriwise_$(date +%F_%H%M%S).sqlite3
```

### Certbot SSL Auto-Renewal:
Certbot installs an automatic systemd timer / cron job. To test renewal dry-run:
```bash
sudo certbot renew --dry-run
```
