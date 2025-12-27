"""
Database Models for Unified Cyber Threat Detection System

Defines SQLAlchemy ORM models for:
- Email threat data
- Web log analysis
- Threat correlations
- System reports and audit logs
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class Email(Base):
    """
    Email threat analysis records.
    
    Attributes:
        id: Unique identifier
        email_text: Full email content
        sender: Sender email address
        receiver: Recipient email address
        subject: Email subject
        date: Email date
        prediction: Binary prediction (0=legitimate, 1=phishing)
        confidence: Prediction confidence score (0-1)
        risk_score: Risk score (0-100)
        risk_level: Risk level (low, medium, high, critical)
        risk_factors: JSON with detailed risk factors from LIME
        urls: Extracted URLs from email
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "emails"
    __table_args__ = (
        Index('idx_email_created_at', 'created_at'),
        Index('idx_email_sender', 'sender'),
        Index('idx_email_prediction', 'prediction'),
        Index('idx_email_risk_level', 'risk_level'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_text = Column(Text, nullable=False)
    sender = Column(String(255), nullable=True, index=True)
    receiver = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    date = Column(DateTime, nullable=True)
    
    # Prediction fields
    prediction = Column(Integer, nullable=False, index=True)  # 0 or 1
    confidence = Column(Float, nullable=False)  # 0-1
    risk_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    
    # LIME explanation
    risk_factors = Column(JSON, nullable=True)  # List of risk factors with importance
    urls = Column(JSON, nullable=True)  # Extracted URLs
    
    # New fields (AŞAMA 4 addition)
    severity = Column(String(20), nullable=True, index=True)  # phishing, malware, spam, suspicious, legitimate
    detection_method = Column(String(50), nullable=True, index=True)  # tfidf, bert, fasttext, ensemble
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    threat_correlations = relationship("ThreatCorrelation", back_populates="email", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Email(id={self.id}, sender={self.sender}, prediction={self.prediction}, risk_level={self.risk_level})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'sender': self.sender,
            'receiver': self.receiver,
            'subject': self.subject,
            'date': self.date.isoformat() if self.date else None,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'severity': self.severity,
            'detection_method': self.detection_method,
            'risk_factors': self.risk_factors,
            'urls': self.urls,
            'created_at': self.created_at.isoformat(),
        }


class WebLog(Base):
    """
    Web server log analysis records.
    
    Attributes:
        id: Unique identifier
        log_line: Original log line
        ip_address: Source IP address
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        user_agent: Client user agent
        response_size: Response size in bytes
        timestamp: Request timestamp
        anomaly_score: Isolation Forest anomaly score (0-1)
        is_anomaly: Boolean flag for anomaly
        risk_level: Risk level (normal, suspicious, malicious)
        indicators: JSON with detected attack indicators
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "web_logs"
    __table_args__ = (
        Index('idx_created_at', 'created_at'),
        Index('idx_ip_address', 'ip_address'),
        Index('idx_is_anomaly', 'is_anomaly'),
        Index('idx_risk_level', 'risk_level'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_line = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True, index=True)  # IPv4 or IPv6
    method = Column(String(10), nullable=True)  # GET, POST, etc.
    path = Column(String(1000), nullable=True)
    status_code = Column(Integer, nullable=True)
    user_agent = Column(String(500), nullable=True)
    response_size = Column(Integer, nullable=True)
    timestamp = Column(DateTime, nullable=True)
    
    # Anomaly detection fields
    anomaly_score = Column(Float, nullable=False)  # 0-1
    is_anomaly = Column(Boolean, default=False, index=True)
    risk_level = Column(String(20), nullable=False, index=True)  # normal, suspicious, malicious
    
    # LIME explanation and indicators
    indicators = Column(JSON, nullable=True)  # List of detected indicators
    attack_patterns = Column(JSON, nullable=True)  # Detected attack patterns
    
    # New fields (AŞAMA 4 addition)
    attack_type = Column(String(50), nullable=True, index=True)  # sql_injection, xss, ddos, etc.
    ml_confidence = Column(Float, nullable=True)  # Anomaly detection confidence
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    threat_correlations = relationship("ThreatCorrelation", back_populates="web_log", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WebLog(id={self.id}, ip={self.ip_address}, is_anomaly={self.is_anomaly}, risk_level={self.risk_level})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'ip_address': self.ip_address,
            'method': self.method,
            'path': self.path,
            'status_code': self.status_code,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'anomaly_score': self.anomaly_score,
            'is_anomaly': self.is_anomaly,
            'risk_level': self.risk_level,
            'attack_type': self.attack_type,
            'ml_confidence': self.ml_confidence,
            'indicators': self.indicators,
            'attack_patterns': self.attack_patterns,
            'created_at': self.created_at.isoformat(),
        }


class ThreatCorrelation(Base):
    """
    Cross-platform threat correlations between email and web logs.
    
    Attributes:
        id: Unique identifier
        email_id: Reference to Email record
        web_log_id: Reference to WebLog record
        correlation_score: Correlation strength (0-1)
        correlation_type: Type of correlation (same_actor, timeline_match, etc.)
        details: JSON with correlation details
        created_at: Record creation timestamp
    """
    __tablename__ = "threat_correlations"
    __table_args__ = (
        Index('idx_email_id', 'email_id'),
        Index('idx_web_log_id', 'web_log_id'),
        Index('idx_correlation_score', 'correlation_score'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id = Column(UUID(as_uuid=True), ForeignKey('emails.id'), nullable=True, index=True)
    web_log_id = Column(UUID(as_uuid=True), ForeignKey('web_logs.id'), nullable=True, index=True)
    
    # Correlation fields
    correlation_score = Column(Float, nullable=False)  # 0-1
    correlation_type = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    email = relationship("Email", back_populates="threat_correlations")
    web_log = relationship("WebLog", back_populates="threat_correlations")
    
    def __repr__(self):
        return f"<ThreatCorrelation(id={self.id}, email={self.email_id}, web_log={self.web_log_id}, score={self.correlation_score})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'email_id': str(self.email_id) if self.email_id else None,
            'web_log_id': str(self.web_log_id) if self.web_log_id else None,
            'correlation_score': self.correlation_score,
            'correlation_type': self.correlation_type,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
        }


class ThreatReport(Base):
    """
    Generated threat analysis reports.
    
    Attributes:
        id: Unique identifier
        report_type: Type of report (email, web, unified)
        title: Report title
        summary: Report summary
        threat_counts: JSON with threat count breakdown
        overall_risk_score: Overall risk score (0-100)
        overall_risk_level: Overall risk level
        recommendations: JSON with security recommendations
        email_threats: Count of email threats detected
        web_threats: Count of web threats detected
        correlation_count: Number of correlations found
        created_at: Report creation timestamp
    """
    __tablename__ = "threat_reports"
    __table_args__ = (
        Index('idx_report_created_at', 'created_at'),
        Index('idx_report_type', 'report_type'),
        Index('idx_report_risk_level', 'overall_risk_level'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report metadata
    report_type = Column(String(20), nullable=False, index=True)  # email, web, unified
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    
    # Threat counts
    email_threats = Column(Integer, default=0)
    web_threats = Column(Integer, default=0)
    correlation_count = Column(Integer, default=0)
    
    # Risk assessment
    overall_risk_score = Column(Float, nullable=False)  # 0-100
    overall_risk_level = Column(String(20), nullable=False, index=True)
    
    # Details
    threat_counts = Column(JSON, nullable=True)  # Breakdown by risk level
    recommendations = Column(JSON, nullable=True)  # List of recommendations
    report_data = Column(JSON, nullable=True)  # Full report data
    
    # Metadata
    generated_by = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ThreatReport(id={self.id}, type={self.report_type}, risk_level={self.overall_risk_level})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'report_type': self.report_type,
            'title': self.title,
            'email_threats': self.email_threats,
            'web_threats': self.web_threats,
            'correlation_count': self.correlation_count,
            'overall_risk_score': self.overall_risk_score,
            'overall_risk_level': self.overall_risk_level,
            'threat_counts': self.threat_counts,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat(),
        }


class AuditLog(Base):
    """
    Audit trail for system actions.
    
    Attributes:
        id: Unique identifier
        action: Action performed
        user_id: User who performed the action
        resource_type: Type of resource affected
        resource_id: ID of resource affected
        details: JSON with additional details
        ip_address: IP address of action source
        created_at: Action timestamp
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_created_at', 'created_at'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_user_id', 'user_id'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(100), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.user_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': str(self.id),
            'action': self.action,
            'user_id': self.user_id,
            'resource_type': self.resource_type,
            'resource_id': str(self.resource_id) if self.resource_id else None,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat(),
        }
