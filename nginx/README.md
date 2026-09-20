# NutriWise Nginx Configuration Samples

This directory contains production-ready Nginx configuration samples for various deployment scenarios:

## Files in this Directory

| File | Purpose | When to Use |
|---|---|---|
| [`default.conf`](./default.conf) | Active Nginx virtual host configuration used by Docker Compose. | Default configuration out of the box. |
| [`http_only.sample.conf`](./http_only.sample.conf) | Plain HTTP configuration with Let's Encrypt challenge path. | Initial server bootstrap, local Docker dev, or behind AWS ALB / Cloudflare SSL. |
| [`https_ssl.sample.conf`](./https_ssl.sample.conf) | Production-hardened HTTPS configuration with HSTS and modern TLS. | Production with direct domain and Let's Encrypt certificates. |
| [`nginx.conf.example`](./nginx.conf.example) | Master Nginx daemon configuration. | Overriding global Nginx settings (worker processes, logging). |

---

## How to Switch to HTTPS in Production

1. Request your certificate using Certbot (see [`docs/LIGHTSAIL_DOCKER_HOSTING_GUIDE.md`](../docs/LIGHTSAIL_DOCKER_HOSTING_GUIDE.md)).
2. Copy the sample file:
   ```bash
   cp nginx/https_ssl.sample.conf nginx/default.conf
   ```
3. Replace `yourdomain.com` with your real domain:
   ```bash
   sed -i 's/yourdomain.com/myactualdomain.com/g' nginx/default.conf
   ```
4. Test configuration syntax:
   ```bash
   docker compose exec nginx nginx -t
   ```
5. Reload Nginx without downtime:
   ```bash
   docker compose exec nginx nginx -s reload
   ```
