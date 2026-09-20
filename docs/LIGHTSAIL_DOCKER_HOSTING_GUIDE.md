# AWS Lightsail Docker Hosting & Deployment Guide

This guide provides an end-to-end DevOps walkthrough for deploying **NutriWise** on an **Amazon Web Services (AWS) Lightsail** virtual private server using **Docker**, **Docker Compose**, **Gunicorn**, **Nginx**, and free automated **Let's Encrypt SSL**.

---

## 1. Architectural Overview

```
Internet (HTTPS / Port 443)
           ↓
AWS Lightsail Firewall (Ports 80, 443, 22)
           ↓
[ Host OS: Ubuntu 22.04 LTS (Static IP) ]
           ↓
┌─────────────────────────────────────────────────────────────┐
│                      DOCKER ENGINE                          │
│                                                             │
│  ┌───────────────────────────┐                              │
│  │   nutriwise_nginx         │  (Port 80, 443)              │
│  │   • SSL Termination       │                              │
│  │   • Direct Static Serving │ ──► static_volume            │
│  │   • Direct Media Serving  │ ──► media_volume             │
│  └─────────────┬─────────────┘                              │
│                │ (Reverse Proxy: http://web:8000)           │
│                ▼                                            │
│  ┌───────────────────────────┐                              │
│  │   nutriwise_web (Gunicorn)│                              │
│  │   • Django 5.1 App        │                              │
│  │   • Ingestion Pipeline    │ ──► db_data (SQLite/Data)    │
│  │   • Gemini AI / Weather   │                              │
│  └───────────────────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Recommended Instance Sizing & Cost

In the AWS Lightsail console:
- **Platform**: Linux/Unix
- **Blueprint**: **OS Only** ➔ **Ubuntu 22.04 LTS** (or Ubuntu 24.04 LTS)
- **Recommended Plan**: **2 GB RAM, 1 vCPU, 60 GB SSD, 3 TB Transfer ($10/month)**
  - *Why 2 GB?* Provides sufficient RAM for Python PDF OCR parsing (`PyMuPDF`, `tesseract`) and multiple Gunicorn worker processes.

---

## 3. Step-by-Step Deployment Instructions

### Step 1: Create the Lightsail Instance
1. Log in to your [AWS Lightsail Console](https://lightsail.aws.amazon.com/).
2. Click **Create instance**.
3. Select your closest AWS Region (e.g., `ap-south-1` Mumbai).
4. Select **OS Only** ➔ **Ubuntu 22.04 LTS**.
5. Select the **$10/month (2 GB RAM)** plan.
6. Name your instance (e.g., `nutriwise-prod`) and click **Create instance**.

---

### Step 2: Attach a Static IP Address
By default, Lightsail changes public IPs on reboot. Attach a permanent Static IP:
1. In the Lightsail dashboard, go to the **Networking** tab.
2. Click **Create static IP**.
3. Attach it to your `nutriwise-prod` instance.
4. Note your public **Static IP** (e.g., `13.235.xx.xx`).

---

### Step 3: Configure Firewall Rules
In the Lightsail console, click on your instance ➔ **Networking** tab ➔ **IPv4 Firewall**:
Ensure the following ports are open:
- **SSH**: Port 22 (TCP)
- **HTTP**: Port 80 (TCP)
- **HTTPS**: Port 443 (TCP)

---

### Step 4: Point Your Domain (DNS Configuration)
Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, Route 53):
1. Create an **A Record**:
   - **Host / Name**: `@` (or `app` / `nutriwise`)
   - **Type**: `A`
   - **Value / Target**: Your Lightsail **Static IP**
2. Create a `www` CNAME or A-record pointing to the same IP.
3. Wait 2–5 minutes for DNS propagation.

---

### Step 5: Connect to the Server & Install Docker
Connect to your instance via the browser-based SSH terminal in Lightsail, or from your local machine:
```bash
ssh -i /path/to/your-lightsail-key.pem ubuntu@YOUR_STATIC_IP
```

Update packages and install Docker Engine and the Docker Compose plugin:
```bash
# Update system repositories
sudo apt-get update && sudo apt-get upgrade -y

# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker and Docker Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Allow ubuntu user to run docker without sudo
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

---

### Step 6: Deploy the Project Codebase
Clone your repository (or copy your files using `scp` / `rsync`):
```bash
cd /home/ubuntu
git clone https://github.com/your-username/hackday1.0.git nutriwise
cd nutriwise
```

---

### Step 7: Configure Production Environment Variables
Create the production `.env` file:
```bash
nano .env
```
Paste and fill in your production values:
```bash
# Security
DEBUG=False
SECRET_KEY=generate-a-strong-random-50-character-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_STATIC_IP

# APIs
OPENWEATHER_API_KEY=your-openweather-api-key
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-3.6-flash

# Database (Leave blank to use local persistent SQLite in Docker volume)
DB_HOST=
DB_NAME=
DB_USER=
DB_PASSWORD=
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

### Step 8: Build and Launch Containers
Run Docker Compose to build the application image, apply migrations, collect static assets, and start Nginx:
```bash
docker compose up -d --build
```

Check the status of running containers:
```bash
docker compose ps
```
You should see:
- `nutriwise_web` (State: Up)
- `nutriwise_nginx` (State: Up, Ports: 0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp)

Create your initial admin superuser:
```bash
docker compose exec web python manage.py createsuperuser
```

At this stage, you can visit `http://YOUR_STATIC_IP` or `http://yourdomain.com` in your browser.

---

### Step 9: Install Free SSL Certificate (Let's Encrypt HTTPS)

To secure your site with HTTPS, install Certbot on the host machine:
```bash
sudo apt-get install -y certbot

# Temporarily stop Nginx container to free port 80 for verification
docker compose stop nginx

# Request certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Start Nginx back up
docker compose start nginx
```

Now, update `nginx/default.conf` to enable SSL. Open `nginx/default.conf`:
```bash
nano nginx/default.conf
```
Replace its contents with the SSL configuration:
```nginx
upstream django_app {
    server web:8000;
}

# Redirect all HTTP traffic to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 50M;

    # SSL Certificates from Let's Encrypt volume
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Static files with 30-day client caching
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Uploaded media documents
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }

    # Reverse proxy to Gunicorn
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
    }
}
```

Reload Nginx to activate SSL:
```bash
docker compose restart nginx
```
Your application is now live at `https://yourdomain.com` with a secure green padlock!

---

### Step 10: Auto-Renew SSL Certificates
Set up an automatic cron job to renew the certificate before expiration:
```bash
sudo crontab -e
```
Add the following line at the bottom:
```cron
0 3 1 * * certbot renew --pre-hook "docker compose -f /home/ubuntu/nutriwise/docker-compose.yml stop nginx" --post-hook "docker compose -f /home/ubuntu/nutriwise/docker-compose.yml start nginx" >> /var/log/certbot_renew.log 2>&1
```

---

## 4. Useful Production Operations & Commands

### Monitoring Logs in Real-Time
```bash
# View all container logs
docker compose logs -f

# View only web application errors
docker compose logs -f web

# View Nginx access logs
docker compose logs -f nginx
```

### Applying Code Updates (Zero-Downtime Deploy)
Whenever you push new code to your repository:
```bash
cd /home/ubuntu/nutriwise
git pull origin main
docker compose up -d --build
```

### Backing Up Data
To back up your SQLite database and uploaded book files:
```bash
# Create a timestamped backup archive
mkdir -p /home/ubuntu/backups
docker compose exec web python -c "
import shutil, datetime
now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.copyfile('db.sqlite3', f'/app/data/backup_db_{now}.sqlite3')
"
```

---

## 5. Multi-Service Co-Hosting Architecture (Shared Nginx & Networks)

If your AWS Lightsail instance already hosts other web projects (e.g. under `/opt/services/` such as `omvi_blog` and `dns-stack`) with an existing central Nginx reverse proxy running on Docker, you should **not** bind ports `80` and `443` in NutriWise. Instead, run NutriWise as a backend web container attached to the shared Docker network.

### Architecture Diagram

```
                       Internet (HTTPS Port 443 / HTTP Port 80)
                                        │
                                        ▼
                  [ Central Nginx Container (Ports 80 & 443) ]
                       (Network: omvi_blog_default)
                                        │
            ┌───────────────────────────┴───────────────────────────┐
            ▼                                                       ▼
    omvihub.in                                            nutriwise.omvihub.in
  (omvi_blog:8000)                                        (nutriwise_web:8000)
```

### 1. Identifying the Shared Network
On your Lightsail host, inspect the existing Nginx container:
```bash
docker inspect $(docker ps -q -f name=nginx) --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Output: omvi_blog_default
```

### 2. The Multi-Service Compose File (`docker-compose.lightsail.yml`)
NutriWise includes a dedicated compose file for this architecture:
```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nutriwise_web
    restart: always
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
      - ./data:/app/data
    expose:
      - "8000"
    networks:
      - omvi_blog_default

networks:
  omvi_blog_default:
    external: true
```

### 3. Deployment Workflow at `/opt/services/nutriwise`
```bash
cd /opt/services/nutriwise

# Build & launch container
docker compose -f docker-compose.lightsail.yml up -d --build

# Run database migrations
docker compose -f docker-compose.lightsail.yml exec web python manage.py migrate

# Collect static files
docker compose -f docker-compose.lightsail.yml exec web python manage.py collectstatic --noinput

# Create admin user
docker compose -f docker-compose.lightsail.yml exec web python manage.py createsuperuser
```

### 4. Central Nginx Upstream Configuration
Append the NutriWise server block to your central Nginx configuration file (`/opt/services/omvi_blog/nginx/default.conf`):
```nginx
upstream nutriwise {
    server nutriwise_web:8000;
}

server {
    listen 80;
    server_name nutriwise.omvihub.in;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name nutriwise.omvihub.in;

    ssl_certificate /etc/letsencrypt/live/nutriwise.omvihub.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nutriwise.omvihub.in/privkey.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://nutriwise;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 60s;
        proxy_read_timeout 120s;
    }
}
```

Restart Nginx:
```bash
docker restart $(docker ps -q -f name=nginx)
docker exec $(docker ps -q -f name=nginx) nginx -t
```

