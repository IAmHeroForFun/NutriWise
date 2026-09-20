# AWS Lightsail Quick Deployment Guide: NutriWise

> **Customized for:** AWS Lightsail Multi-Service Architecture  
> **Server Directory:** `/opt/services/nutriwise`  
> **Shared Network:** `omvi_blog_default`  
> **Domain:** `nutriwise.omvihub.in`  
> **Container Name:** `nutriwise_web`  
> **Upstream:** `http://nutriwise_web:8000`

---

## Architecture Summary

Your Lightsail server (`ubuntu@ip-172-26-1-124`) already hosts `dns-stack` and `omvi_blog` with a central Nginx reverse proxy running on the `omvi_blog_default` Docker network.

```
                    Internet (HTTPS Port 443)
                                │
                                ▼
                   Central Nginx (Port 80/443)
               (Network: omvi_blog_default bridge)
                                │
            ┌───────────────────┴───────────────────┐
            ▼                                       ▼
     omvihub.in                           nutriwise.omvihub.in
   (omvi_blog web)                          (nutriwise_web:8000)
```

By connecting NutriWise to `omvi_blog_default`, the central Nginx can proxy requests directly to `http://nutriwise_web:8000` without exposing any ports to the host.

---

## Step 1: On Your Local Machine (Push to GitHub)

If you haven't committed and pushed the latest codebase yet, run these commands in your local project folder:

```bash
cd /mnt/Work/projects/hackday1.0

# Check git status
git status

# Stage all files
git add .

# Commit your changes
git commit -m "feat: complete NutriWise production setup, docs, and Lightsail docker deployment configs"

# Push to your GitHub repository
git push origin main
```

*(Alternatively, if transferring directly without git: `rsync -avz --exclude 'venv' --exclude '__pycache__' ./ ubuntu@YOUR_SERVER_IP:/opt/services/nutriwise/`)*

---

## Step 2: On Your Lightsail Server (Pull the Code)

SSH into your Lightsail instance (or open your existing terminal session):

```bash
# Navigate to your services directory
cd /opt/services/nutriwise

# If cloning for the first time:
# git clone <YOUR_GITHUB_REPO_URL> .

# If you already have the repo cloned, pull the latest changes:
git pull origin main
```

Verify the files are present:
```bash
ls -la
# You should see Dockerfile, docker-compose.lightsail.yml, requirements.txt, dietary_app, core, etc.
```

---

## Step 3: Create the Production `.env` File

Inside `/opt/services/nutriwise`, create your `.env` configuration:

```bash
nano .env
```

Paste the following configuration (replace placeholders with your real API keys):

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

# Database (Leave blank to use persistent SQLite inside ./data)
DB_HOST=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

Press `Ctrl+O`, `Enter` to save, and `Ctrl+X` to exit.

---

## Step 4: Build and Launch `nutriwise_web`

Run Docker Compose using the dedicated Lightsail compose file:

```bash
docker compose -f docker-compose.lightsail.yml up -d --build
```

### Verify Container Status:
```bash
docker ps
```
You should see `nutriwise_web` running (Up) and attached to the `omvi_blog_default` network.

To check its logs:
```bash
docker logs -f nutriwise_web
```
*(Press `Ctrl+C` to exit logs)*

---

## Step 5: Run Database Migrations & Initial Setup

Execute Django management commands inside the running container:

```bash
# 1. Run database migrations
docker compose -f docker-compose.lightsail.yml exec web python manage.py migrate

# 2. Collect static files
docker compose -f docker-compose.lightsail.yml exec web python manage.py collectstatic --noinput

# 3. Create your admin superuser
docker compose -f docker-compose.lightsail.yml exec web python manage.py createsuperuser
```

*(Follow the prompt to set your admin username, email, and password).*

---

## Step 6: Configure DNS & Let's Encrypt SSL

### 1. DNS Record
In your domain DNS manager (Route 53, Cloudflare, Namecheap, etc.):
- Add an **A Record**:
  - **Name / Host:** `nutriwise`
  - **Type:** `A`
  - **Value / Target:** Your Lightsail Static Public IP
- Wait 1–2 minutes and verify it resolves:
  ```bash
  ping nutriwise.omvihub.in
  ```

### 2. Obtain SSL Certificate via Certbot
If using Certbot on the host:
```bash
sudo certbot certonly --webroot -w /var/www/certbot -d nutriwise.omvihub.in
# OR standalone (temporarily stops port 80 if not proxied):
# sudo certbot certonly --standalone -d nutriwise.omvihub.in
```

Verify certificate files exist:
```bash
sudo ls -l /etc/letsencrypt/live/nutriwise.omvihub.in/
# Should contain: fullchain.pem and privkey.pem
```

---

## Step 7: Update Your Central Nginx Reverse Proxy

Add the NutriWise virtual host configuration to your central Nginx configuration directory (e.g. `/opt/services/omvi_blog/nginx/conf.d/` or `/etc/nginx/conf.d/`):

Open or create `nutriwise.conf`:
```bash
# Example location (adjust path to where your central nginx conf files live):
sudo nano /opt/services/omvi_blog/nginx/conf.d/nutriwise.conf
```

Paste the server configuration:

```nginx
upstream nutriwise {
    server nutriwise_web:8000;
}

server {
    listen 80;
    server_name nutriwise.omvihub.in;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    http2 on;
    server_name nutriwise.omvihub.in;

    ssl_certificate /etc/letsencrypt/live/nutriwise.omvihub.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nutriwise.omvihub.in/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    # Static assets
    location /static/ {
        alias /opt/services/nutriwise/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        access_log off;
    }

    # Uploaded books/documents
    location /media/ {
        alias /opt/services/nutriwise/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }

    # Proxy to NutriWise web container
    location / {
        proxy_pass http://nutriwise;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
        proxy_send_timeout 60s;
    }
}
```

### Test & Reload Nginx:
Test the Nginx configuration syntax:
```bash
# If nginx is running inside a docker container:
docker exec $(docker ps -q -f name=nginx) nginx -t

# If syntax is ok, reload:
docker exec $(docker ps -q -f name=nginx) nginx -s reload
```

*(If running Nginx directly on the host: `sudo nginx -t && sudo systemctl reload nginx`)*

---

## Step 8: Verify & Test Everything

1. Open your browser and visit:
   ```
   https://nutriwise.omvihub.in
   ```
2. You should see the landing page with valid HTTPS lock.
3. Access the Admin Dashboard:
   ```
   https://nutriwise.omvihub.in/admin/
   ```
   Log in with the superuser credentials created in Step 5.
4. Try registering a user, onboarding, and testing daily plan generation.

---

## Useful Maintenance Commands

```bash
# View live application logs:
docker logs -f nutriwise_web

# Restart application:
docker compose -f docker-compose.lightsail.yml restart web

# Pull updates and rebuild after git push:
git pull origin main
docker compose -f docker-compose.lightsail.yml up -d --build
docker compose -f docker-compose.lightsail.yml exec web python manage.py migrate

# Enter Django interactive shell:
docker compose -f docker-compose.lightsail.yml exec web python manage.py shell

# Backup SQLite database:
cp /opt/services/nutriwise/data/db.sqlite3 /opt/backups/nutriwise_$(date +%F).sqlite3
```
