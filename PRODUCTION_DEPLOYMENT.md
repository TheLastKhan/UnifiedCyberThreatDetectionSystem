# 🚀 Production Deployment Guide

## Unified Cyber Threat Detection System - Production Setup

---

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: 8GB minimum (16GB recommended)
- **CPU**: 4 cores minimum (8 cores recommended)
- **Disk**: 50GB minimum (SSD recommended)
- **Docker**: 20.10+ & Docker Compose 2.0+

### Domain & SSL
- Domain name configured (e.g., `threat-detection.yourdomain.com`)
- DNS A record pointing to server IP
- Port 80, 443 open for HTTPS

---

## 🔧 Installation Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 2. Clone Repository

```bash
# Clone project
git clone https://github.com/YourOrg/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# Checkout production branch
git checkout main
```

### 3. Configuration

```bash
# Copy production environment template
cp .env.production .env

# Edit environment variables
nano .env
```

**Important variables to change:**
```bash
SECRET_KEY=<generate-with: openssl rand -hex 32>
POSTGRES_PASSWORD=<strong-database-password>
ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-domain.com
VT_API_KEY=<your-virustotal-api-key>
SMTP_PASSWORD=<your-email-app-password>
```

### 4. SSL Certificates (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (cron job)
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet --post-hook "docker compose restart nginx"
```

### 5. Build & Deploy

```bash
# Build Docker images
docker compose build

# Start services
docker compose up -d

# Check logs
docker compose logs -f api

# Verify health
curl http://localhost:5000/api/health
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Nginx (443)   │  ← SSL/TLS, Rate Limiting, Static Files
└────────┬────────┘
         │
┌────────▼────────────────────────────────────┐
│  Gunicorn (5000)                           │
│  ├─ Worker 1 (Flask App + ML Models)      │
│  ├─ Worker 2 (Flask App + ML Models)      │
│  ├─ Worker 3 (Flask App + ML Models)      │
│  └─ Worker 4 (Flask App + ML Models)      │
└────────┬────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ PG   │  │ Redis │
│ SQL  │  │ Cache │
└──────┘  └───────┘
```

---

## 🐳 Docker Services

### API Service
```yaml
Container: threat-detection-api
Port: 5000
Workers: 4 Gunicorn processes
Health: /api/health endpoint
Restart: unless-stopped
```

### Database Service
```yaml
Container: threat-detection-db
Image: postgres:15-alpine
Port: 5432 (internal)
Volume: postgres_data
Health: pg_isready check
```

### Cache Service
```yaml
Container: threat-detection-cache
Image: redis:7-alpine
Port: 6379 (internal)
Volume: redis_data
Health: redis-cli ping
```

### Nginx Service (optional)
```yaml
Container: threat-detection-nginx
Image: nginx:alpine
Ports: 80, 443
Config: /etc/nginx/conf.d/
SSL: /etc/letsencrypt/
```

---

## 📊 Monitoring & Logging

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f db
docker compose logs -f cache

# Last 100 lines
docker compose logs --tail=100 api
```

### Container Status
```bash
# Check running containers
docker compose ps

# Resource usage
docker stats

# Health checks
docker inspect threat-detection-api | grep Health -A 10
```

### Application Metrics
```bash
# API health endpoint
curl http://localhost:5000/api/health

# Model status
curl http://localhost:5000/api/models/status

# Database connection
docker exec threat-detection-db pg_isready -U threat_user
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2Ban (SSH Protection)
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Docker Security
```bash
# Non-root user in container (already configured)
# Secrets management
docker secret create db_password <(echo "your-password")

# Network isolation (already configured)
# Read-only filesystem for static content
```

### 4. SSL/TLS Best Practices
- TLSv1.2 minimum (TLSv1.3 preferred)
- Strong cipher suites
- HSTS header enabled
- Certificate pinning (optional)

---

## 🔄 Maintenance

### Database Backup
```bash
# Backup
docker exec threat-detection-db pg_dump -U threat_user threat_detection > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i threat-detection-db psql -U threat_user threat_detection < backup_20251209.sql

# Automated daily backup (cron)
0 2 * * * cd /path/to/project && docker exec threat-detection-db pg_dump -U threat_user threat_detection | gzip > backups/db_$(date +\%Y\%m\%d).sql.gz
```

### Model Updates
```bash
# Copy new models
docker cp models/new_model.pkl threat-detection-api:/app/models/

# Reload models (API endpoint)
curl -X POST http://localhost:5000/api/models/reload

# Or restart container
docker compose restart api
```

### Application Updates
```bash
# Pull latest code
git pull origin main

# Rebuild images
docker compose build

# Rolling update (zero downtime)
docker compose up -d --no-deps --build api

# Or full restart
docker compose down && docker compose up -d
```

---

## 🚨 Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs api

# Check configuration
docker compose config

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Database connection failed
```bash
# Check database status
docker compose ps db

# Test connection
docker exec threat-detection-db pg_isready -U threat_user

# Reset database
docker compose down
docker volume rm unifiedcyberthreatdetectionsystem_postgres_data
docker compose up -d
```

### High memory usage
```bash
# Check resource limits
docker stats

# Reduce Gunicorn workers
# Edit .env: WORKERS=2

# Restart with new config
docker compose up -d
```

### SSL certificate renewal failed
```bash
# Manual renewal
sudo certbot renew --force-renewal

# Check certificate expiry
sudo certbot certificates

# Reload Nginx
docker compose restart nginx
```

---

## 📈 Performance Tuning

### Gunicorn Workers
```python
# Formula: (2 * CPU_CORES) + 1
WORKERS=9  # For 4-core CPU

# Worker class
WORKER_CLASS=sync         # Default, good for most cases
WORKER_CLASS=gevent       # For I/O bound tasks
WORKER_CLASS=eventlet     # Alternative async
```

### PostgreSQL
```bash
# Edit docker-compose.yml
POSTGRES_INITDB_ARGS: "-c shared_buffers=512MB -c effective_cache_size=2GB -c max_connections=200"
```

### Redis Cache
```bash
# Set maxmemory policy
CONFIG SET maxmemory 2gb
CONFIG SET maxmemory-policy allkeys-lru
```

---

## 📞 Support

- **Documentation**: [README.md](README.md)
- **API Reference**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Issues**: GitHub Issues
- **Email**: support@yourdomain.com

---

## ✅ Post-Deployment Checklist

- [ ] SSL certificate installed and auto-renewal configured
- [ ] Environment variables configured (.env)
- [ ] Database backup cron job running
- [ ] Firewall rules applied
- [ ] Monitoring alerts configured
- [ ] Health checks passing
- [ ] API endpoints responding
- [ ] Dashboard accessible via HTTPS
- [ ] Model predictions working
- [ ] Logs being written
- [ ] Resource usage within limits
- [ ] Documentation updated
- [ ] Team notified of deployment

---

**Deployment Date**: {{ DATE }}  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
