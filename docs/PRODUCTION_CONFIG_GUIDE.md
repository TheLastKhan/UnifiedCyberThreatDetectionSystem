# 🔧 PRODUCTION CONFIGURATION GUIDE

## 📋 Overview
This guide will help you configure production credentials for the Unified Cyber Threat Detection System.

---

## 1️⃣ VirusTotal API Key (Required)

### Get Your Free API Key:
1. Go to: https://www.virustotal.com/
2. Sign up for a free account (or login)
3. Go to your profile → API Key section
4. Copy your API key

### Add to .env:
```env
VIRUSTOTAL_API_KEY=your_actual_api_key_here_64_chars
```

### Free Tier Limits:
- 4 requests per minute
- 500 requests per day
- Perfect for testing and small deployments

### Test Your Key:
```bash
curl --request GET \
  --url 'https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8' \
  --header 'x-apikey: YOUR_API_KEY'
```

---

## 2️⃣ Email SMTP Configuration (Required for Alerts)

### Option A: Gmail (Recommended for Testing)

**Step 1**: Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification"

**Step 2**: Create App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Other (Custom name)" → "Threat Detection System"
4. Click "Generate"
5. Copy the 16-character password

**Step 3**: Update .env
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
ALERT_EMAIL_RECIPIENTS=admin@example.com,security@example.com
```

### Option B: Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your.email@outlook.com
SMTP_PASSWORD=your_password
```

### Option C: Custom SMTP Server
```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=alerts@yourdomain.com
SMTP_PASSWORD=your_password
```

### Test Email:
```bash
python -c "
from src.integrations.notifications import EmailNotifier
notifier = EmailNotifier()
notifier.send_alert(
    severity='LOW',
    threat_data={'test': 'Email configuration test'},
    recipients=['admin@example.com']
)
print('[OK] Email sent successfully!')
"
```

---

## 3️⃣ Flask Secret Key (Required)

### Generate Strong Secret Key:

**Method 1**: Python (Recommended)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Method 2**: OpenSSL
```bash
openssl rand -hex 32
```

**Method 3**: PowerShell
```powershell
-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
```

### Update .env:
```env
SECRET_KEY=your_64_character_random_hex_string_here_production_use_only
```

**⚠️ Important**: 
- Never commit this to git
- Use different keys for dev/staging/production
- Minimum 32 characters (64 recommended)

---

## 4️⃣ Slack Webhook (Optional)

### Setup:
1. Go to: https://api.slack.com/apps
2. Create New App → "From scratch"
3. Name: "Threat Detection Alerts"
4. Select your workspace
5. Go to "Incoming Webhooks" → Activate
6. Click "Add New Webhook to Workspace"
7. Select channel: #security-alerts
8. Copy webhook URL

### Add to .env:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
SLACK_CHANNEL=#security-alerts
```

### Test Slack:
```bash
python -c "
from src.integrations.notifications import SlackNotifier
notifier = SlackNotifier()
notifier.send_alert(
    severity='LOW',
    threat_data={'test': 'Slack configuration test'}
)
print('[OK] Slack message sent!')
"
```

---

## 5️⃣ PostgreSQL Database (Production)

### Current Setup (Docker):
```env
DATABASE_URL=postgresql://threat_user:threat_password@db:5432/threat_detection
```

### Production Recommendations:

**Option A**: Managed Database (Recommended)
- AWS RDS PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases

**Option B**: Self-hosted
```env
DATABASE_URL=postgresql://prod_user:strong_password@your-db-server:5432/threat_detection
DATABASE_POOL_SIZE=50
DATABASE_POOL_RECYCLE=3600
```

**Security Best Practices**:
- Use strong passwords (16+ chars, mixed case, numbers, symbols)
- Enable SSL/TLS connections
- Restrict IP access (firewall rules)
- Regular backups
- Connection pooling

---

## 6️⃣ SSL/TLS Certificates

### Option A: Let's Encrypt (Free, Recommended)

**Install Certbot**:
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

**Get Certificate**:
```bash
sudo certbot --nginx -d api.yourdomain.com
```

**Auto-renewal** (Cron):
```bash
0 12 * * * /usr/bin/certbot renew --quiet
```

### Option B: Self-Signed (Testing Only)
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/selfsigned.key \
  -out /etc/ssl/certs/selfsigned.crt
```

---

## 7️⃣ Environment Variables Summary

### Minimal Production Setup:
```env
# Flask
SECRET_KEY=<64_char_hex_string>

# VirusTotal
VIRUSTOTAL_API_KEY=<your_api_key>

# Email
SMTP_USERNAME=<your_email>
SMTP_PASSWORD=<app_password>
ALERT_EMAIL_RECIPIENTS=<admin_email>

# Database (if external)
DATABASE_URL=<production_db_url>
```

### Optional but Recommended:
```env
# Slack
SLACK_WEBHOOK_URL=<webhook_url>

# Redis (if external)
REDIS_URL=<redis_connection_string>

# Monitoring
SENTRY_DSN=<sentry_project_dsn>
```

---

## 8️⃣ Deployment Checklist

### Pre-Deployment:
- [ ] All API keys configured
- [ ] Email notifications tested
- [ ] Secret key generated (64 chars)
- [ ] Database backups enabled
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Log rotation setup

### Post-Deployment:
- [ ] Health check: `curl https://your-domain/api/health`
- [ ] Test email alerts
- [ ] Test Slack alerts (if configured)
- [ ] Verify VirusTotal integration
- [ ] Check logs: `docker logs threat-detection-api`
- [ ] Monitor resource usage

---

## 9️⃣ Quick Start Commands

### Update .env file:
```bash
nano .env
# Or use any text editor
```

### Restart services:
```bash
docker compose down
docker compose up -d --build
```

### Check logs:
```bash
docker compose logs -f api
```

### Health check:
```bash
curl http://localhost:5000/api/health
```

---

## 🆘 Troubleshooting

### Issue: Email not sending
```bash
# Test SMTP connection
python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).connect()"
```

### Issue: VirusTotal 403 Forbidden
- Check API key is correct
- Verify you haven't exceeded rate limits (4/min, 500/day)

### Issue: Redis connection failed
```bash
# Test Redis
redis-cli -h localhost -p 6379 ping
# Should return: PONG
```

### Issue: Database connection error
```bash
# Test PostgreSQL
psql -h localhost -U threat_user -d threat_detection -c "SELECT 1"
```

---

## 📞 Support

- **Documentation**: See `docs/` folder
- **Issues**: GitHub Issues
- **Email**: Contact your system administrator

---

**Last Updated**: December 13, 2025
**Status**: Production Ready ✅
