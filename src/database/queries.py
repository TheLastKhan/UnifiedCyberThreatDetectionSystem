"""
Database Query Functions

Provides high-level query operations for emails, web logs, and threat correlations.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session
from .models import Email, WebLog, ThreatCorrelation, ThreatReport, AuditLog
from .connection import db_session_context


class EmailQueries:
    """Email-related database queries."""
    
    @staticmethod
    def get_all(session: Session, limit: int = 100, offset: int = 0) -> List[Email]:
        """Get all emails with pagination."""
        return session.query(Email).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_by_id(session: Session, email_id: str) -> Optional[Email]:
        """Get email by ID."""
        from uuid import UUID
        return session.query(Email).filter(Email.id == UUID(email_id)).first()
    
    @staticmethod
    def get_phishing(session: Session, limit: int = 100) -> List[Email]:
        """Get phishing emails (prediction=1)."""
        return session.query(Email).filter(
            Email.prediction == 1
        ).order_by(desc(Email.confidence)).limit(limit).all()
    
    @staticmethod
    def get_legitimate(session: Session, limit: int = 100) -> List[Email]:
        """Get legitimate emails (prediction=0)."""
        return session.query(Email).filter(
            Email.prediction == 0
        ).limit(limit).all()
    
    @staticmethod
    def get_by_risk_level(session: Session, risk_level: str, limit: int = 100) -> List[Email]:
        """Get emails by risk level (low, medium, high, critical)."""
        return session.query(Email).filter(
            Email.risk_level == risk_level
        ).order_by(desc(Email.risk_score)).limit(limit).all()
    
    @staticmethod
    def get_high_confidence_phishing(session: Session, confidence_threshold: float = 0.8, limit: int = 100) -> List[Email]:
        """Get high-confidence phishing emails."""
        return session.query(Email).filter(
            and_(Email.prediction == 1, Email.confidence >= confidence_threshold)
        ).order_by(desc(Email.confidence)).limit(limit).all()
    
    @staticmethod
    def get_by_sender(session: Session, sender: str, limit: int = 100) -> List[Email]:
        """Get emails from specific sender."""
        return session.query(Email).filter(
            Email.sender.ilike(f"%{sender}%")
        ).limit(limit).all()
    
    @staticmethod
    def get_by_date_range(
        session: Session,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100
    ) -> List[Email]:
        """Get emails within date range."""
        return session.query(Email).filter(
            and_(Email.date >= start_date, Email.date <= end_date)
        ).order_by(desc(Email.date)).limit(limit).all()
    
    @staticmethod
    def get_recent(session: Session, days: int = 7, limit: int = 100) -> List[Email]:
        """Get recent emails."""
        start_date = datetime.utcnow() - timedelta(days=days)
        return EmailQueries.get_by_date_range(session, start_date, datetime.utcnow(), limit)
    
    @staticmethod
    def get_statistics(session: Session) -> Dict[str, Any]:
        """Get email statistics."""
        total = session.query(func.count(Email.id)).scalar() or 0
        phishing = session.query(func.count(Email.id)).filter(Email.prediction == 1).scalar() or 0
        legitimate = session.query(func.count(Email.id)).filter(Email.prediction == 0).scalar() or 0
        
        risk_counts = session.query(
            Email.risk_level,
            func.count(Email.id).label('count')
        ).group_by(Email.risk_level).all()
        
        avg_confidence = session.query(func.avg(Email.confidence)).filter(
            Email.prediction == 1
        ).scalar() or 0.0
        
        return {
            'total_emails': total,
            'phishing_count': phishing,
            'legitimate_count': legitimate,
            'phishing_percentage': round((phishing / total * 100) if total > 0 else 0, 2),
            'risk_distribution': {level: count for level, count in risk_counts},
            'avg_phishing_confidence': round(avg_confidence, 3),
        }
    
    @staticmethod
    def count_by_prediction(session: Session) -> Dict[int, int]:
        """Count emails by prediction."""
        results = session.query(
            Email.prediction,
            func.count(Email.id)
        ).group_by(Email.prediction).all()
        return {pred: count for pred, count in results}


class WebLogQueries:
    """Web log-related database queries."""
    
    @staticmethod
    def get_all(session: Session, limit: int = 100, offset: int = 0) -> List[WebLog]:
        """Get all web logs with pagination."""
        return session.query(WebLog).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_by_id(session: Session, log_id: str) -> Optional[WebLog]:
        """Get web log by ID."""
        from uuid import UUID
        return session.query(WebLog).filter(WebLog.id == UUID(log_id)).first()
    
    @staticmethod
    def get_anomalies(session: Session, limit: int = 100) -> List[WebLog]:
        """Get anomalous web logs (is_anomaly=True)."""
        return session.query(WebLog).filter(
            WebLog.is_anomaly == True
        ).order_by(desc(WebLog.anomaly_score)).limit(limit).all()
    
    @staticmethod
    def get_by_ip(session: Session, ip_address: str, limit: int = 100) -> List[WebLog]:
        """Get logs from specific IP."""
        return session.query(WebLog).filter(
            WebLog.ip_address == ip_address
        ).order_by(desc(WebLog.created_at)).limit(limit).all()
    
    @staticmethod
    def get_suspicious_ips(session: Session, anomaly_threshold: float = 0.7, limit: int = 100) -> List[Tuple[str, int, float]]:
        """Get IP addresses with suspicious activity."""
        results = session.query(
            WebLog.ip_address,
            func.count(WebLog.id).label('log_count'),
            func.avg(WebLog.anomaly_score).label('avg_score')
        ).filter(WebLog.is_anomaly == True).group_by(
            WebLog.ip_address
        ).order_by(desc('avg_score')).limit(limit).all()
        
        return results
    
    @staticmethod
    def get_by_status_code(session: Session, status_code: int, limit: int = 100) -> List[WebLog]:
        """Get logs with specific HTTP status code."""
        return session.query(WebLog).filter(
            WebLog.status_code == status_code
        ).limit(limit).all()
    
    @staticmethod
    def get_by_path(session: Session, path: str, limit: int = 100) -> List[WebLog]:
        """Get logs for specific path."""
        return session.query(WebLog).filter(
            WebLog.path.ilike(f"%{path}%")
        ).limit(limit).all()
    
    @staticmethod
    def get_statistics(session: Session) -> Dict[str, Any]:
        """Get web log statistics."""
        total = session.query(func.count(WebLog.id)).scalar() or 0
        anomalies = session.query(func.count(WebLog.id)).filter(WebLog.is_anomaly == True).scalar() or 0
        
        risk_counts = session.query(
            WebLog.risk_level,
            func.count(WebLog.id).label('count')
        ).group_by(WebLog.risk_level).all()
        
        avg_anomaly_score = session.query(func.avg(WebLog.anomaly_score)).scalar() or 0.0
        
        status_codes = session.query(
            WebLog.status_code,
            func.count(WebLog.id).label('count')
        ).group_by(WebLog.status_code).all()
        
        return {
            'total_logs': total,
            'anomaly_count': anomalies,
            'anomaly_percentage': round((anomalies / total * 100) if total > 0 else 0, 2),
            'risk_distribution': {level: count for level, count in risk_counts},
            'avg_anomaly_score': round(avg_anomaly_score, 3),
            'status_code_distribution': {code: count for code, count in status_codes},
        }


class CorrelationQueries:
    """Threat correlation queries."""
    
    @staticmethod
    def get_all(session: Session, limit: int = 100) -> List[ThreatCorrelation]:
        """Get all threat correlations."""
        return session.query(ThreatCorrelation).order_by(
            desc(ThreatCorrelation.correlation_score)
        ).limit(limit).all()
    
    @staticmethod
    def get_by_email_id(session: Session, email_id: str) -> List[ThreatCorrelation]:
        """Get correlations for email."""
        from uuid import UUID
        return session.query(ThreatCorrelation).filter(
            ThreatCorrelation.email_id == UUID(email_id)
        ).all()
    
    @staticmethod
    def get_high_confidence(session: Session, threshold: float = 0.7, limit: int = 100) -> List[ThreatCorrelation]:
        """Get high-confidence correlations."""
        return session.query(ThreatCorrelation).filter(
            ThreatCorrelation.correlation_score >= threshold
        ).order_by(desc(ThreatCorrelation.correlation_score)).limit(limit).all()
    
    @staticmethod
    def get_statistics(session: Session) -> Dict[str, Any]:
        """Get correlation statistics."""
        total = session.query(func.count(ThreatCorrelation.id)).scalar() or 0
        avg_score = session.query(func.avg(ThreatCorrelation.correlation_score)).scalar() or 0.0
        
        type_counts = session.query(
            ThreatCorrelation.correlation_type,
            func.count(ThreatCorrelation.id).label('count')
        ).group_by(ThreatCorrelation.correlation_type).all()
        
        return {
            'total_correlations': total,
            'avg_correlation_score': round(avg_score, 3),
            'type_distribution': {t: c for t, c in type_counts},
        }


class ReportQueries:
    """Threat report queries."""
    
    @staticmethod
    def get_all(session: Session, limit: int = 100) -> List[ThreatReport]:
        """Get all reports."""
        return session.query(ThreatReport).order_by(
            desc(ThreatReport.created_at)
        ).limit(limit).all()
    
    @staticmethod
    def get_recent(session: Session, days: int = 7, limit: int = 100) -> List[ThreatReport]:
        """Get recent reports."""
        start_date = datetime.utcnow() - timedelta(days=days)
        return session.query(ThreatReport).filter(
            ThreatReport.created_at >= start_date
        ).order_by(desc(ThreatReport.created_at)).limit(limit).all()
    
    @staticmethod
    def get_by_type(session: Session, report_type: str, limit: int = 100) -> List[ThreatReport]:
        """Get reports by type."""
        return session.query(ThreatReport).filter(
            ThreatReport.report_type == report_type
        ).order_by(desc(ThreatReport.created_at)).limit(limit).all()
    
    @staticmethod
    def get_by_risk_level(session: Session, risk_level: str, limit: int = 100) -> List[ThreatReport]:
        """Get reports by risk level."""
        return session.query(ThreatReport).filter(
            ThreatReport.overall_risk_level == risk_level
        ).order_by(desc(ThreatReport.created_at)).limit(limit).all()


class AuditQueries:
    """Audit log queries."""
    
    @staticmethod
    def get_all(session: Session, limit: int = 100) -> List[AuditLog]:
        """Get all audit logs."""
        return session.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    @staticmethod
    def get_by_action(session: Session, action: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by action."""
        return session.query(AuditLog).filter(
            AuditLog.action == action
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    @staticmethod
    def get_by_user(session: Session, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by user."""
        return session.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()
    
    @staticmethod
    def get_recent(session: Session, days: int = 7, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs."""
        start_date = datetime.utcnow() - timedelta(days=days)
        return session.query(AuditLog).filter(
            AuditLog.created_at >= start_date
        ).order_by(desc(AuditLog.created_at)).limit(limit).all()
