"""
PostgreSQL Database Initialization Script
Creates tables for threat detection system
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'threat_detection'),
    'user': os.getenv('DB_USER', 'threat_user'),
    'password': os.getenv('DB_PASSWORD', 'threat_password')
}

# SQL Schema definitions
SCHEMA_SQL = """
-- Predictions table: Store all email/web predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    prediction_type VARCHAR(20) NOT NULL,  -- 'email' or 'web'
    content TEXT,
    prediction_result VARCHAR(50) NOT NULL,  -- 'phishing', 'legitimate', 'anomaly', etc.
    confidence FLOAT,
    model_used VARCHAR(50),  -- 'random_forest', 'bert', 'fasttext', 'tfidf'
    features JSONB,  -- Store feature vectors as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(50),
    user_id VARCHAR(100)
);

-- Threats table: Store detected threats
CREATE TABLE IF NOT EXISTS threats (
    id SERIAL PRIMARY KEY,
    threat_type VARCHAR(50) NOT NULL,  -- 'phishing', 'malware', 'dos', etc.
    severity VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high', 'critical'
    description TEXT,
    source VARCHAR(255),
    destination VARCHAR(255),
    indicators JSONB,  -- IOCs, patterns, etc.
    prediction_id INTEGER REFERENCES predictions(id),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP
);

-- Alerts table: Store sent notifications
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,  -- 'email', 'slack', 'sms'
    recipient VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    body TEXT,
    threat_id INTEGER REFERENCES threats(id),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'sent', 'failed'
    error_message TEXT
);

-- Model Metrics table: Store model performance over time
CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,  -- 'accuracy', 'precision', 'recall', 'f1'
    metric_value FLOAT NOT NULL,
    sample_count INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB  -- Additional info: confusion matrix, etc.
);

-- Drift Detection table: Store data drift metrics
CREATE TABLE IF NOT EXISTS drift_events (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(50) NOT NULL,
    drift_type VARCHAR(50) NOT NULL,  -- 'psi', 'kl_divergence', 'ks_test'
    drift_score FLOAT NOT NULL,
    threshold FLOAT NOT NULL,
    is_drifted BOOLEAN NOT NULL,
    feature_drifts JSONB,  -- Per-feature drift scores
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- A/B Test Results table
CREATE TABLE IF NOT EXISTS ab_test_results (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    variant VARCHAR(50) NOT NULL,  -- 'A', 'B', 'control', etc.
    model_name VARCHAR(50) NOT NULL,
    sample_count INTEGER DEFAULT 0,
    accuracy FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    f1_score FLOAT,
    avg_latency FLOAT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity);
CREATE INDEX IF NOT EXISTS idx_threats_detected ON threats(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_threats_resolved ON threats(resolved);
CREATE INDEX IF NOT EXISTS idx_alerts_sent ON alerts(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_model ON model_metrics(model_name, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_drift_detected ON drift_events(detected_at DESC);
"""


def init_database():
    """Initialize database with schema"""
    try:
        # Connect to PostgreSQL
        print(f"[*] Connecting to PostgreSQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("[*] Creating tables and indexes...")
        cursor.execute(SCHEMA_SQL)
        
        # Verify tables created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n[✓] Database initialized successfully!")
        print(f"[✓] Created {len(tables)} tables:")
        for table in tables:
            print(f"    - {table[0]}")
        
        # Show table row counts
        print("\n[*] Table status:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"    {table[0]}: {count} rows")
        
        cursor.close()
        conn.close()
        
        print("\n[✓] Database ready for use!")
        return True
        
    except psycopg2.Error as e:
        print(f"\n[✗] Database error: {e}")
        return False
    except Exception as e:
        print(f"\n[✗] Unexpected error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("  PostgreSQL Database Initialization")
    print("=" * 60)
    print()
    
    success = init_database()
    
    if success:
        print("\n" + "=" * 60)
        print("  Migration completed successfully! ✓")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  Migration failed! ✗")
        print("=" * 60)
        exit(1)
