# Deployment Guide

Unified Cyber Threat Detection System'i production ortamına deploy etmek için adım adım kılavuz.

---

## 1. Pre-Deployment Checklist

### Sistem Gereksinimleri
- [ ] Python 3.8+ yüklü
- [ ] 4GB+ RAM
- [ ] 2+ CPU cores
- [ ] 10GB+ disk space
- [ ] Linux/Windows/macOS işletim sistemi

### Software Gereksinimleri
- [ ] Git yüklü
- [ ] Docker yüklü (opsiyonel ama önerilen)
- [ ] PostgreSQL/MongoDB (opsiyonel, veri saklama için)
- [ ] Redis (opsiyonel, caching için)

### Network Gereksinimleri
- [ ] Firewall ayarları (5000 port açık)
- [ ] SSL/TLS sertifikası (production için)
- [ ] DNS konfigürasyonu
- [ ] Load balancer (yüksek traffic için)

---

## 2. Local Development to Production

### Adım 1: Repository'yi Klonla

```bash
# Repository'yi klonla
git clone https://github.com/TheLastKhan/UnifiedCyberThreatDetectionSystem.git
cd UnifiedCyberThreatDetectionSystem

# Production branch'ine geç (varsa)
git checkout production
```

### Adım 2: Environment'ı Hazırla

```bash
# Virtual environment oluştur
python -m venv venv

# Activate et
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Adım 3: Dependencies'i Yükle

```bash
# Gerekli paketleri yükle
pip install -r requirements.txt

# Production paketlerini ekle
pip install gunicorn
pip install psycopg2-binary  # PostgreSQL için
pip install redis            # Redis cache için
pip install python-dotenv    # Environment variables
```

### Adım 4: Configuration Dosyalarını Hazırla

```bash
# .env dosyasını oluştur (örnek: .env.example)
cp .env.example .env

# Production ayarlarını yapılandır
# Not: .env dosyasını git'e commit etme!
```

### Adım 5: Database Migrasyonları Çalıştır

```bash
# Veritabanı oluştur (varsa)
python manage.py migrate

# Test verisi yükle (opsiyonel)
python manage.py loaddata fixtures/sample_data.json
```

---

## 3. Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

# Çalışma dizini oluştur
WORKDIR /app

# Sistem paketlerini yükle
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Requirements'ı kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Uygulama kodunu kopyala
COPY . .

# Port'u expose et
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/v1/health')"

# Gunicorn ile başlat
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "sync", "--timeout", "120", "app:app"]
```

### Docker Build ve Run

```bash
# Image oluştur
docker build -t threat-detection:latest .

# Container'ı çalıştır
docker run -d \
  --name threat-detection \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  threat-detection:latest

# Logları kontrol et
docker logs -f threat-detection

# Container durumunu kontrol et
docker ps -a
```

### Docker Compose

Dosya: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # Threat Detection API
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/threat_detection
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      - db
      - cache
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: threat_user
      POSTGRES_PASSWORD: secure_password_123
      POSTGRES_DB: threat_detection
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U threat_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Docker Compose ile Başlat

```bash
# Tüm servisleri başlat
docker-compose up -d

# Servislerin durumunu kontrol et
docker-compose ps

# Logları izle
docker-compose logs -f api

# Servisleri durdur
docker-compose down
```

---

## 4. Nginx Configuration

Dosya: `nginx.conf`

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=1000r/m;

    # Upstream API
    upstream threat_detection_api {
        least_conn;
        server api:5000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name api.unifiedthreat.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        location /api/v1/ {
            limit_req zone=api burst=50 nodelay;

            proxy_pass http://threat_detection_api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location / {
            limit_req zone=general burst=10 nodelay;
            root /usr/share/nginx/html;
            try_files $uri $uri/ =404;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

---

## 5. Environment Configuration

Dosya: `.env.example`

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_APP=app:app
DEBUG=False
SECRET_KEY=your-secret-key-change-this

# Server Configuration
HOST=0.0.0.0
PORT=5000
WORKERS=4

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/threat_detection
DATABASE_POOL_SIZE=20
DATABASE_POOL_RECYCLE=3600

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_TIMEOUT=10

# Model Configuration
MODEL_PATH=/app/models
MAX_EMAIL_LENGTH=50000
MAX_LOGS_BATCH=10000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
LOG_MAX_SIZE=10485760  # 10MB

# Security Configuration
CORS_ORIGINS=https://api.unifiedthreat.com
API_KEY_REQUIRED=True
API_KEY_SECRET=your-api-key-secret

# Email Configuration (untuk SMTP alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring Configuration
SENTRY_DSN=https://your-sentry-dsn
DATADOG_API_KEY=your-datadog-key
```

---

## 6. Systemd Service (Linux)

Dosya: `/etc/systemd/system/threat-detection.service`

```ini
[Unit]
Description=Unified Cyber Threat Detection System
After=network.target

[Service]
Type=notify
User=threat-detection
WorkingDirectory=/opt/threat-detection
Environment="PATH=/opt/threat-detection/venv/bin"
Environment="FLASK_ENV=production"
EnvironmentFile=/opt/threat-detection/.env
ExecStart=/opt/threat-detection/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile /var/log/threat-detection/access.log \
    --error-logfile /var/log/threat-detection/error.log \
    app:app

# Restart policy
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Systemd Komutları

```bash
# Service dosyasını daemon'a yükle
sudo systemctl daemon-reload

# Servisi başlat
sudo systemctl start threat-detection

# Otomatik başlatmayı etkinleştir
sudo systemctl enable threat-detection

# Servis durumunu kontrol et
sudo systemctl status threat-detection

# Logları izle
journalctl -u threat-detection -f
```

---

## 7. SSL/TLS Configuration

### Self-Signed Sertifika (Test için)

```bash
# Private key oluştur
openssl genrsa -out ssl/key.pem 2048

# Certificate oluştur (365 gün geçerli)
openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 \
    -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Organization/CN=api.unifiedthreat.com"
```

### Let's Encrypt (Production için)

```bash
# Certbot yükle
sudo apt-get install certbot python3-certbot-nginx

# Sertifika oluştur
sudo certbot certonly --nginx -d api.unifiedthreat.com

# Auto-renewal etkinleştir
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Sertifikayı kontrol et
sudo certbot certificates
```

---

## 8. Monitoring & Logging

### Prometheus Metrics

Dosya: `prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'threat-detection'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

```docker
docker run -d --name elasticsearch \
  -e "discovery.type=single-node" \
  -p 9200:9200 \
  docker.elastic.co/elasticsearch/elasticsearch:8.0.0

docker run -d --name kibana \
  -p 5601:5601 \
  -e "ELASTICSEARCH_HOSTS=http://elasticsearch:9200" \
  docker.elastic.co/kibana/kibana:8.0.0
```

### Application Logging

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    log_handler.setFormatter(formatter)
    
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)

setup_logging()
```

---

## 9. Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump -U threat_user -h localhost threat_detection > backup.sql

# Restore
psql -U threat_user -h localhost threat_detection < backup.sql

# Automated daily backup
0 2 * * * pg_dump -U threat_user threat_detection > /backups/db_$(date +\%Y\%m\%d).sql
```

### Model Backup

```bash
# Models dizinini backup et
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Remote'a gönder
rsync -avz models_backup_*.tar.gz backup@backup-server:/backups/
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective):** 1 saat
2. **RPO (Recovery Point Objective):** 15 dakika
3. **Backup Strategy:** Daily incremental + Weekly full
4. **Backup Location:** Remote storage (AWS S3, etc.)
5. **Recovery Test:** Monthly

---

## 10. Production Checklist

- [ ] SSL/TLS sertifikası yapılandırıldı
- [ ] Database yedekleri otomatik
- [ ] Monitoring kuruldu (Prometheus, Grafana)
- [ ] Logging yapılandırıldı (ELK, Datadog)
- [ ] Alert rules tanımlandı
- [ ] Load balancer kuruldu
- [ ] Auto-scaling rules tanımlandı
- [ ] Security scanning yapıldı
- [ ] Performance test'ı geçti
- [ ] Disaster recovery plan hazır
- [ ] Documentation tamamlandı
- [ ] Team eğitimi yapıldı

---

## 11. Performance Tuning

### Python/Gunicorn Tuning

```bash
# Worker sayısı = (2 x CPU cores) + 1
# CPU cores sayısını öğren:
nproc

# Örnek: 4 cores için: (2 x 4) + 1 = 9 workers
gunicorn --workers 9 --worker-class sync app:app
```

### Database Tuning

```sql
-- Connection pooling
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';

-- Indexes
CREATE INDEX idx_email_sender ON emails(sender);
CREATE INDEX idx_log_ip ON web_logs(ip_address);
```

### Cache Optimization

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/v1/email/analyze', methods=['POST'])
@cache.cached(timeout=3600, key_prefix='email_')
def analyze_email():
    # ... endpoint code
    pass
```

---

## 12. Troubleshooting

### Port Already in Use

```bash
# Port'u kullanıp kullanan process'i bul
lsof -i :5000

# Process'i öldür
kill -9 <PID>
```

### High Memory Usage

```bash
# Memory kullanımını kontrol et
free -h

# Process'in memory'sini kontrol et
ps aux | grep gunicorn

# Worker sayısını azalt
```

### Slow Queries

```bash
# Database query log'unu enable et
ALTER SYSTEM SET log_min_duration_statement = 1000;  # 1000ms

# Query performansını analiz et
EXPLAIN ANALYZE SELECT ...;
```

---

## Kaynaklar

- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/deployment/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
