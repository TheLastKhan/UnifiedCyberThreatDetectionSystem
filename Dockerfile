FROM python:3.10-slim

# Metadata
LABEL maintainer="Unified Threat Detection Team"
LABEL description="Unified Cyber Threat Detection System API"
LABEL version="1.0.0"

# Çalışma dizini oluştur
WORKDIR /app

# Sistem paketlerini yükle
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user oluştur
RUN useradd -m -u 1000 threatdetection

# Requirements'ı kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Uygulama kodunu kopyala
COPY . .

# Logs ve data dizinlerini oluştur
RUN mkdir -p logs data models && \
    chown -R threatdetection:threatdetection /app

# Non-root user'a geç
USER threatdetection

# Port'u expose et
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Gunicorn ile başlat
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "web_dashboard.app:app"]
