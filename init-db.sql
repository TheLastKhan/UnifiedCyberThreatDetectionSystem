-- ========================================
-- Unified Cyber Threat Detection System
-- Database Initialization Script (PostgreSQL)
-- ========================================
-- Language: PostgreSQL

-- Create extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- Emails Table
CREATE TABLE IF NOT EXISTS emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email_text TEXT NOT NULL,
    sender VARCHAR(255),
    subject VARCHAR(500),
    prediction INTEGER CHECK (prediction IN (0, 1)),
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    risk_score FLOAT CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    risk_factors JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_sender (sender),
    INDEX idx_prediction (prediction),
    INDEX idx_risk_level (risk_level)
);

-- Web Logs Table
CREATE TABLE IF NOT EXISTS web_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_line TEXT NOT NULL,
    ip_address INET,
    method VARCHAR(10),
    path VARCHAR(1000),
    status_code INTEGER,
    anomaly_score FLOAT CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    is_anomaly BOOLEAN DEFAULT FALSE,
    risk_level VARCHAR(20) CHECK (risk_level IN ('normal', 'suspicious', 'malicious')),
    indicators JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_ip_address (ip_address),
    INDEX idx_is_anomaly (is_anomaly),
    INDEX idx_risk_level (risk_level)
);

-- Threat Correlations Table
CREATE TABLE IF NOT EXISTS threat_correlations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email_id UUID REFERENCES emails(id) ON DELETE CASCADE,
    web_log_id UUID REFERENCES web_logs(id) ON DELETE CASCADE,
    correlation_score FLOAT CHECK (correlation_score >= 0 AND correlation_score <= 1),
    correlation_type VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email_id (email_id),
    INDEX idx_web_log_id (web_log_id),
    INDEX idx_correlation_score (correlation_score)
);

-- Threat Reports Table
CREATE TABLE IF NOT EXISTS threat_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_type VARCHAR(20) CHECK (report_type IN ('email', 'web', 'unified')),
    title VARCHAR(500),
    summary TEXT,
    email_threats_count INTEGER,
    web_threats_count INTEGER,
    correlation_count INTEGER,
    overall_risk_score FLOAT CHECK (overall_risk_score >= 0 AND overall_risk_score <= 100),
    overall_risk_level VARCHAR(20),
    recommendations JSONB,
    report_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(255),
    INDEX idx_created_at (created_at),
    INDEX idx_report_type (report_type),
    INDEX idx_overall_risk_level (overall_risk_level)
);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_action (action),
    INDEX idx_user_id (user_id)
);

-- API Keys Table (for future API authentication)
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    user_id VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_active (active)
);

-- System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    data_type VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_key (key)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_emails_created_at ON emails(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_web_logs_created_at ON web_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_threat_reports_created_at ON threat_reports(created_at DESC);

-- Create views for reporting
CREATE OR REPLACE VIEW email_statistics AS
SELECT
    DATE_TRUNC('day', created_at)::DATE as date,
    COUNT(*) as total_emails,
    SUM(CASE WHEN prediction = 1 THEN 1 ELSE 0 END) as phishing_count,
    AVG(confidence) as avg_confidence,
    AVG(risk_score) as avg_risk_score
FROM emails
GROUP BY DATE_TRUNC('day', created_at);

CREATE OR REPLACE VIEW web_statistics AS
SELECT
    DATE_TRUNC('day', created_at)::DATE as date,
    COUNT(*) as total_logs,
    SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomaly_count,
    COUNT(DISTINCT ip_address) as unique_ips,
    AVG(anomaly_score) as avg_anomaly_score
FROM web_logs
GROUP BY DATE_TRUNC('day', created_at);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_emails_updated_at
BEFORE UPDATE ON emails
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_web_logs_updated_at
BEFORE UPDATE ON web_logs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_threat_reports_updated_at
BEFORE UPDATE ON threat_reports
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO threat_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO threat_user;

-- Insert default system settings
INSERT INTO system_settings (key, value, description, data_type) VALUES
('email_phishing_threshold', '0.7', 'Email phishing detection threshold', 'float'),
('web_anomaly_threshold', '0.6', 'Web anomaly detection threshold', 'float'),
('correlation_threshold', '0.5', 'Threat correlation threshold', 'float'),
('max_email_length', '50000', 'Maximum email text length', 'integer'),
('max_logs_batch', '10000', 'Maximum logs in single batch', 'integer'),
('backup_retention_days', '30', 'Backup retention period in days', 'integer'),
('cache_ttl', '3600', 'Cache time-to-live in seconds', 'integer')
ON CONFLICT (key) DO NOTHING;

-- Create initial admin user (password should be changed!)
-- Note: This is a placeholder and should be replaced with proper user management

COMMIT;
