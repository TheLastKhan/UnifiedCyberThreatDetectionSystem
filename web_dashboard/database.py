"""
Database models and connection for persistent storage
Stores predictions in PostgreSQL for dashboard persistence
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import os

# Database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://threat_user:threat_password@localhost:5432/threat_detection')

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

# Create session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()


# ============================================
# MODELS
# ============================================

class EmailPrediction(Base):
    """Store email analysis predictions"""
    __tablename__ = 'email_predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction = Column(String(50), nullable=False)  # 'phishing' or 'legitimate'
    confidence = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # 'critical', 'high', 'medium', 'low'
    model_used = Column(String(100), nullable=True)  # BERT, FastText, TF-IDF
    email_subject = Column(Text, nullable=True)
    email_sender = Column(String(255), nullable=True)
    email_content = Column(Text, nullable=True)
    phishing_score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'risk_level': self.risk_level,
            'email_subject': self.email_subject,
            'email_sender': self.email_sender,
            'timestamp': self.timestamp.isoformat()
        }


class WebPrediction(Base):
    """Store web log analysis predictions"""
    __tablename__ = 'web_predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_anomaly = Column(Boolean, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    patterns_detected = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'is_anomaly': self.is_anomaly,
            'anomaly_score': self.anomaly_score,
            'ip_address': self.ip_address,
            'patterns_detected': self.patterns_detected,
            'timestamp': self.timestamp.isoformat()
        }


class Settings(Base):
    """Settings model for storing user preferences"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(String(500))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'setting_key': self.setting_key,
            'setting_value': self.setting_value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# ============================================
# DATABASE FUNCTIONS
# ============================================

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("[INFO] Database tables created successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create database tables: {e}")
        return False


def get_db():
    """Get database session (use with context manager)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_email_prediction(prediction, confidence, risk_level, model_used=None, email_subject=None, email_sender=None, email_content=None, phishing_score=None, timestamp=None):
    """Add email prediction to database"""
    try:
        db = SessionLocal()
        pred = EmailPrediction(
            prediction=prediction,
            confidence=confidence,
            risk_level=risk_level,
            model_used=model_used[:100] if model_used else 'Unknown',
            email_subject=email_subject[:500] if email_subject else None,
            email_sender=email_sender[:255] if email_sender else None,
            email_content=email_content[:1000] if email_content else None,
            phishing_score=phishing_score if phishing_score is not None else confidence,
            timestamp=timestamp if timestamp else datetime.now()
        )
        db.add(pred)
        db.commit()
        db.refresh(pred)
        db.close()
        return pred.id
    except Exception as e:
        print(f"[ERROR] Failed to add email prediction: {e}")
        import traceback; traceback.print_exc()
        if db:
            db.rollback()
            db.close()
        return None


def add_web_prediction(is_anomaly, anomaly_score, ip_address=None, patterns_detected=None, timestamp=None):
    """Add web prediction to database"""
    try:
        db = SessionLocal()
        
        # Convert patterns list to comma-separated string
        if patterns_detected:
            if isinstance(patterns_detected, list):
                patterns_str = ', '.join(patterns_detected)
            else:
                patterns_str = str(patterns_detected)
            patterns_str = patterns_str[:1000] if patterns_str else None
        else:
            patterns_str = None
        
        pred = WebPrediction(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            ip_address=ip_address[:45] if ip_address else None,
            patterns_detected=patterns_str,
            timestamp=timestamp if timestamp else datetime.now()
        )
        db.add(pred)
        db.commit()
        db.refresh(pred)
        db.close()
        return pred.id
    except Exception as e:
        print(f"[ERROR] Failed to add web prediction: {e}")
        if db:
            db.rollback()
            db.close()
        return None


def get_email_predictions(limit=1000, hours=None):
    """Get email predictions from database"""
    try:
        db = SessionLocal()
        query = db.query(EmailPrediction).order_by(EmailPrediction.timestamp.desc())
        
        if hours:
            from datetime import timedelta
            since = datetime.now() - timedelta(hours=hours)
            query = query.filter(EmailPrediction.timestamp >= since)
        
        predictions = query.limit(limit).all()
        result = [p.to_dict() for p in predictions]
        db.close()
        return result
    except Exception as e:
        print(f"[ERROR] Failed to get email predictions: {e}")
        if db:
            db.close()
        return []


def get_web_predictions(limit=1000, hours=None):
    """Get web predictions from database"""
    try:
        db = SessionLocal()
        query = db.query(WebPrediction).order_by(WebPrediction.timestamp.desc())
        
        if hours:
            from datetime import timedelta
            since = datetime.now() - timedelta(hours=hours)
            query = query.filter(WebPrediction.timestamp >= since)
        
        predictions = query.limit(limit).all()
        result = [p.to_dict() for p in predictions]
        db.close()
        return result
    except Exception as e:
        print(f"[ERROR] Failed to get web predictions: {e}")
        if db:
            db.close()
        return []


def get_prediction_counts():
    """Get total prediction counts"""
    try:
        db = SessionLocal()
        email_count = db.query(EmailPrediction).count()
        web_count = db.query(WebPrediction).count()
        db.close()
        return {'email': email_count, 'web': web_count}
    except Exception as e:
        print(f"[ERROR] Failed to get prediction counts: {e}")
        if db:
            db.close()
        return {'email': 0, 'web': 0}


def clear_all_predictions():
    """Clear all predictions from database"""
    try:
        db = SessionLocal()
        email_deleted = db.query(EmailPrediction).delete()
        web_deleted = db.query(WebPrediction).delete()
        db.commit()
        db.close()
        print(f"[INFO] Cleared {email_deleted} email and {web_deleted} web predictions")
        return {'email_deleted': email_deleted, 'web_deleted': web_deleted}
    except Exception as e:
        print(f"[ERROR] Failed to clear predictions: {e}")
        if db:
            db.rollback()
            db.close()
        return {'email_deleted': 0, 'web_deleted': 0}


def get_settings():
    """Get all settings as a dictionary"""
    try:
        db = SessionLocal()
        settings = db.query(Settings).all()
        result = {s.setting_key: s.setting_value for s in settings}
        db.close()
        return result
    except Exception as e:
        print(f"[ERROR] Failed to get settings: {e}")
        if db:
            db.close()
        return {}


def save_setting(key, value):
    """Save or update a single setting"""
    try:
        db = SessionLocal()
        setting = db.query(Settings).filter(Settings.setting_key == key).first()
        
        if setting:
            setting.setting_value = str(value)
            setting.updated_at = datetime.now()
        else:
            setting = Settings(setting_key=key, setting_value=str(value))
            db.add(setting)
        
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save setting {key}: {e}")
        if db:
            db.rollback()
            db.close()
        return False


def save_settings(settings_dict):
    """Save multiple settings at once"""
    try:
        for key, value in settings_dict.items():
            save_setting(key, value)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save settings: {e}")
        return False


# Initialize database on import
try:
    init_db()
    print("[INFO] Database initialized successfully")
except Exception as e:
    print(f"[WARNING] Database initialization failed: {e}")
