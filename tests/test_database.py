"""
Database Integration Tests

Tests for database models, connections, queries, and import functionality.
"""

import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.database.models import Base, Email, WebLog, ThreatCorrelation, ThreatReport, AuditLog
from src.database.queries import EmailQueries, WebLogQueries, CorrelationQueries


@pytest.fixture
def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    
    yield SessionLocal()
    
    engine.dispose()


class TestEmailModel:
    """Tests for Email model."""
    
    def test_create_email(self, test_db):
        """Test creating an email record."""
        email = Email(
            email_text="Test email content",
            sender="test@example.com",
            receiver="recipient@example.com",
            subject="Test Subject",
            prediction=0,
            confidence=0.95,
            risk_score=10.0,
            risk_level="low"
        )
        
        test_db.add(email)
        test_db.commit()
        
        result = test_db.query(Email).first()
        assert result is not None
        assert result.sender == "test@example.com"
        assert result.prediction == 0
        assert result.confidence == 0.95
    
    def test_email_to_dict(self, test_db):
        """Test Email.to_dict() method."""
        email = Email(
            email_text="Test",
            sender="test@example.com",
            prediction=1,
            confidence=0.8,
            risk_score=50.0,
            risk_level="high"
        )
        
        test_db.add(email)
        test_db.commit()
        
        email_dict = email.to_dict()
        assert email_dict['sender'] == "test@example.com"
        assert email_dict['prediction'] == 1
        assert email_dict['risk_level'] == "high"


class TestWebLogModel:
    """Tests for WebLog model."""
    
    def test_create_web_log(self, test_db):
        """Test creating a web log record."""
        log = WebLog(
            log_line="192.168.1.1 - - [01/Jan/2024:12:00:00] GET /api/users HTTP/1.1 200",
            ip_address="192.168.1.1",
            method="GET",
            path="/api/users",
            status_code=200,
            anomaly_score=0.1,
            is_anomaly=False,
            risk_level="normal"
        )
        
        test_db.add(log)
        test_db.commit()
        
        result = test_db.query(WebLog).first()
        assert result is not None
        assert result.ip_address == "192.168.1.1"
        assert result.status_code == 200
        assert result.is_anomaly is False
    
    def test_web_log_to_dict(self, test_db):
        """Test WebLog.to_dict() method."""
        log = WebLog(
            log_line="test",
            ip_address="10.0.0.1",
            method="POST",
            anomaly_score=0.9,
            is_anomaly=True,
            risk_level="malicious"
        )
        
        test_db.add(log)
        test_db.commit()
        
        log_dict = log.to_dict()
        assert log_dict['ip_address'] == "10.0.0.1"
        assert log_dict['is_anomaly'] is True
        assert log_dict['risk_level'] == "malicious"


class TestThreatCorrelation:
    """Tests for ThreatCorrelation model."""
    
    def test_create_correlation(self, test_db):
        """Test creating a threat correlation."""
        email = Email(
            email_text="Test",
            prediction=1,
            confidence=0.8,
            risk_score=50.0,
            risk_level="high"
        )
        
        log = WebLog(
            log_line="test",
            anomaly_score=0.8,
            is_anomaly=True,
            risk_level="malicious"
        )
        
        test_db.add(email)
        test_db.add(log)
        test_db.flush()
        
        correlation = ThreatCorrelation(
            email_id=email.id,
            web_log_id=log.id,
            correlation_score=0.85,
            correlation_type="same_actor"
        )
        
        test_db.add(correlation)
        test_db.commit()
        
        result = test_db.query(ThreatCorrelation).first()
        assert result is not None
        assert result.correlation_score == 0.85
        assert result.correlation_type == "same_actor"


class TestThreatReport:
    """Tests for ThreatReport model."""
    
    def test_create_report(self, test_db):
        """Test creating a threat report."""
        report = ThreatReport(
            report_type="unified",
            title="Threat Analysis Report",
            email_threats=5,
            web_threats=3,
            correlation_count=2,
            overall_risk_score=65.0,
            overall_risk_level="high"
        )
        
        test_db.add(report)
        test_db.commit()
        
        result = test_db.query(ThreatReport).first()
        assert result is not None
        assert result.report_type == "unified"
        assert result.email_threats == 5
        assert result.overall_risk_level == "high"
    
    def test_report_to_dict(self, test_db):
        """Test ThreatReport.to_dict() method."""
        report = ThreatReport(
            report_type="email",
            title="Email Threats",
            email_threats=10,
            web_threats=0,
            correlation_count=0,
            overall_risk_score=45.0,
            overall_risk_level="medium"
        )
        
        test_db.add(report)
        test_db.commit()
        
        report_dict = report.to_dict()
        assert report_dict['report_type'] == "email"
        assert report_dict['email_threats'] == 10
        assert report_dict['overall_risk_level'] == "medium"


class TestAuditLog:
    """Tests for AuditLog model."""
    
    def test_create_audit_log(self, test_db):
        """Test creating an audit log."""
        log = AuditLog(
            action="email_analyzed",
            user_id="user123",
            resource_type="email",
            details={"model": "random_forest", "confidence": 0.95}
        )
        
        test_db.add(log)
        test_db.commit()
        
        result = test_db.query(AuditLog).first()
        assert result is not None
        assert result.action == "email_analyzed"
        assert result.user_id == "user123"


class TestEmailQueries:
    """Tests for email query functions."""
    
    def test_get_phishing_emails(self, test_db):
        """Test retrieving phishing emails."""
        # Create test data
        for i in range(3):
            email = Email(
                email_text=f"Phishing email {i}",
                prediction=1,
                confidence=0.8 + i * 0.05,
                risk_score=50.0,
                risk_level="high"
            )
            test_db.add(email)
        
        # Create legitimate email
        email = Email(
            email_text="Legitimate email",
            prediction=0,
            confidence=0.95,
            risk_score=10.0,
            risk_level="low"
        )
        test_db.add(email)
        test_db.commit()
        
        phishing = EmailQueries.get_phishing(test_db)
        assert len(phishing) == 3
        assert all(e.prediction == 1 for e in phishing)
    
    def test_get_legitimate_emails(self, test_db):
        """Test retrieving legitimate emails."""
        email1 = Email(
            email_text="Legitimate 1",
            prediction=0,
            confidence=0.95,
            risk_score=5.0,
            risk_level="low"
        )
        
        email2 = Email(
            email_text="Legitimate 2",
            prediction=0,
            confidence=0.92,
            risk_score=8.0,
            risk_level="low"
        )
        
        test_db.add(email1)
        test_db.add(email2)
        test_db.commit()
        
        legitimate = EmailQueries.get_legitimate(test_db)
        assert len(legitimate) == 2
        assert all(e.prediction == 0 for e in legitimate)
    
    def test_get_by_risk_level(self, test_db):
        """Test retrieving emails by risk level."""
        for level in ["low", "medium", "high", "critical"]:
            for i in range(2):
                email = Email(
                    email_text=f"{level} {i}",
                    prediction=1 if level != "low" else 0,
                    confidence=0.8,
                    risk_score={"low": 20, "medium": 40, "high": 60, "critical": 85}.get(level),
                    risk_level=level
                )
                test_db.add(email)
        
        test_db.commit()
        
        critical = EmailQueries.get_by_risk_level(test_db, "critical")
        assert len(critical) == 2
        assert all(e.risk_level == "critical" for e in critical)
    
    def test_get_statistics(self, test_db):
        """Test email statistics calculation."""
        # Create mixed emails
        for i in range(5):
            email = Email(
                email_text=f"Email {i}",
                prediction=i % 2,
                confidence=0.8,
                risk_score=50.0,
                risk_level="high" if i % 2 else "low"
            )
            test_db.add(email)
        
        test_db.commit()
        
        stats = EmailQueries.get_statistics(test_db)
        assert stats['total_emails'] == 5
        assert stats['phishing_count'] >= 2
        assert stats['legitimate_count'] >= 2
        assert 'phishing_percentage' in stats


class TestWebLogQueries:
    """Tests for web log query functions."""
    
    def test_get_anomalies(self, test_db):
        """Test retrieving anomalous logs."""
        # Create normal logs
        for i in range(3):
            log = WebLog(
                log_line=f"normal {i}",
                ip_address=f"192.168.1.{i}",
                anomaly_score=0.1,
                is_anomaly=False,
                risk_level="normal"
            )
            test_db.add(log)
        
        # Create anomalous logs
        for i in range(2):
            log = WebLog(
                log_line=f"anomaly {i}",
                ip_address=f"10.0.0.{i}",
                anomaly_score=0.9,
                is_anomaly=True,
                risk_level="malicious"
            )
            test_db.add(log)
        
        test_db.commit()
        
        anomalies = WebLogQueries.get_anomalies(test_db)
        assert len(anomalies) == 2
        assert all(log.is_anomaly for log in anomalies)
    
    def test_get_by_ip(self, test_db):
        """Test retrieving logs by IP."""
        ip = "192.168.1.1"
        
        for i in range(3):
            log = WebLog(
                log_line=f"log {i}",
                ip_address=ip,
                anomaly_score=0.1,
                is_anomaly=False,
                risk_level="normal"
            )
            test_db.add(log)
        
        test_db.commit()
        
        logs = WebLogQueries.get_by_ip(test_db, ip)
        assert len(logs) == 3
        assert all(log.ip_address == ip for log in logs)
    
    def test_get_statistics(self, test_db):
        """Test web log statistics calculation."""
        for i in range(5):
            log = WebLog(
                log_line=f"log {i}",
                anomaly_score=0.5,
                is_anomaly=i % 2 == 0,
                risk_level="normal" if i % 2 else "suspicious"
            )
            test_db.add(log)
        
        test_db.commit()
        
        stats = WebLogQueries.get_statistics(test_db)
        assert stats['total_logs'] == 5
        assert 'anomaly_count' in stats
        assert 'anomaly_percentage' in stats


class TestCorrelationQueries:
    """Tests for correlation query functions."""
    
    def test_get_high_confidence_correlations(self, test_db):
        """Test retrieving high-confidence correlations."""
        email = Email(
            email_text="Test",
            prediction=1,
            confidence=0.8,
            risk_score=50.0,
            risk_level="high"
        )
        
        log = WebLog(
            log_line="test",
            anomaly_score=0.8,
            is_anomaly=True,
            risk_level="malicious"
        )
        
        test_db.add(email)
        test_db.add(log)
        test_db.flush()
        
        # Create high and low confidence correlations
        corr1 = ThreatCorrelation(
            email_id=email.id,
            web_log_id=log.id,
            correlation_score=0.9,
            correlation_type="same_actor"
        )
        
        corr2 = ThreatCorrelation(
            correlation_score=0.5,
            correlation_type="timeline_match"
        )
        
        test_db.add(corr1)
        test_db.add(corr2)
        test_db.commit()
        
        high_conf = CorrelationQueries.get_high_confidence(test_db, threshold=0.7)
        assert len(high_conf) == 1
        assert high_conf[0].correlation_score >= 0.7
    
    def test_get_statistics(self, test_db):
        """Test correlation statistics."""
        for i in range(3):
            corr = ThreatCorrelation(
                correlation_score=0.5 + i * 0.1,
                correlation_type="same_actor"
            )
            test_db.add(corr)
        
        test_db.commit()
        
        stats = CorrelationQueries.get_statistics(test_db)
        assert stats['total_correlations'] == 3
        assert 'avg_correlation_score' in stats
