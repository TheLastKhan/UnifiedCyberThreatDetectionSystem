"""
Pydantic Request/Response Schemas for API Validation

Defines data models for:
- Email analysis requests and responses
- Web log analysis requests and responses
- Threat correlation data
- Reports and statistics
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator


# ==================== Email Schemas ====================

class EmailAnalysisRequest(BaseModel):
    """Request schema for email analysis."""
    text: str = Field(..., min_length=1, max_length=50000, description="Email body text")
    sender: Optional[EmailStr] = Field(None, description="Sender email address")
    receiver: Optional[EmailStr] = Field(None, description="Recipient email address")
    subject: Optional[str] = Field(None, max_length=500, description="Email subject")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Click here to verify your account...",
                "sender": "attacker@phishing.com",
                "receiver": "user@example.com",
                "subject": "Urgent: Verify Your Account"
            }
        }


class EmailPredictionResponse(BaseModel):
    """Response schema for email prediction."""
    prediction: int = Field(..., ge=0, le=1, description="0=legitimate, 1=phishing")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence (0-1)")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    risk_factors: Optional[Dict[str, Any]] = Field(None, description="LIME explanation factors")
    urls: Optional[List[str]] = Field(None, description="Extracted URLs")


class EmailStorageRequest(BaseModel):
    """Request schema for storing email in database."""
    email_text: str = Field(..., min_length=1, max_length=50000)
    sender: Optional[str] = Field(None, max_length=255)
    receiver: Optional[str] = Field(None, max_length=255)
    subject: Optional[str] = Field(None, max_length=500)
    date: Optional[datetime] = None
    prediction: int = Field(..., ge=0, le=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str = Field(...)
    risk_factors: Optional[Dict[str, Any]] = None
    urls: Optional[List[str]] = None


class EmailResponse(BaseModel):
    """Response schema for email record."""
    id: str = Field(..., description="Email UUID")
    sender: Optional[str] = None
    receiver: Optional[str] = None
    subject: Optional[str] = None
    date: Optional[datetime] = None
    prediction: int
    confidence: float
    risk_score: float
    risk_level: str
    risk_factors: Optional[Dict[str, Any]] = None
    urls: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailStatisticsResponse(BaseModel):
    """Response schema for email statistics."""
    total_emails: int = Field(..., description="Total email records")
    phishing_count: int = Field(..., description="Number of phishing emails")
    legitimate_count: int = Field(..., description="Number of legitimate emails")
    phishing_percentage: float = Field(..., description="Phishing percentage")
    risk_distribution: Dict[str, int] = Field(..., description="Count by risk level")
    avg_phishing_confidence: float = Field(..., description="Average phishing confidence")


# ==================== Web Log Schemas ====================

class WebLogAnalysisRequest(BaseModel):
    """Request schema for web log analysis."""
    log_line: str = Field(..., min_length=1, max_length=5000, description="Web server log line")
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_line": '192.168.1.1 - - [01/Jan/2024:12:00:00] "GET /admin HTTP/1.1" 200'
            }
        }


class WebLogAnomalyResponse(BaseModel):
    """Response schema for web log anomaly detection."""
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score (0-1)")
    is_anomaly: bool = Field(..., description="Is anomalous")
    risk_level: str = Field(..., description="Risk level: normal, suspicious, malicious")
    indicators: Optional[Dict[str, Any]] = Field(None, description="Detected indicators")
    attack_patterns: Optional[Dict[str, Any]] = Field(None, description="Attack patterns")


class WebLogStorageRequest(BaseModel):
    """Request schema for storing web log in database."""
    log_line: str = Field(..., min_length=1, max_length=5000)
    ip_address: Optional[str] = Field(None, max_length=45)
    method: Optional[str] = Field(None, max_length=10)
    path: Optional[str] = Field(None, max_length=1000)
    status_code: Optional[int] = None
    user_agent: Optional[str] = Field(None, max_length=500)
    response_size: Optional[int] = None
    timestamp: Optional[datetime] = None
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    is_anomaly: bool = Field(...)
    risk_level: str = Field(...)
    indicators: Optional[Dict[str, Any]] = None
    attack_patterns: Optional[Dict[str, Any]] = None


class WebLogResponse(BaseModel):
    """Response schema for web log record."""
    id: str = Field(..., description="WebLog UUID")
    log_line: str
    ip_address: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[int] = None
    timestamp: Optional[datetime] = None
    anomaly_score: float
    is_anomaly: bool
    risk_level: str
    indicators: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebLogStatisticsResponse(BaseModel):
    """Response schema for web log statistics."""
    total_logs: int = Field(..., description="Total log records")
    anomaly_count: int = Field(..., description="Number of anomalies")
    anomaly_percentage: float = Field(..., description="Anomaly percentage")
    risk_distribution: Dict[str, int] = Field(..., description="Count by risk level")
    avg_anomaly_score: float = Field(..., description="Average anomaly score")
    status_code_distribution: Dict[str, int] = Field(..., description="HTTP status codes")


class SuspiciousIPResponse(BaseModel):
    """Response schema for suspicious IP address."""
    ip_address: str = Field(..., description="IP address")
    log_count: int = Field(..., description="Number of anomalous logs")
    avg_anomaly_score: float = Field(..., description="Average anomaly score")


# ==================== Correlation Schemas ====================

class ThreatCorrelationResponse(BaseModel):
    """Response schema for threat correlation."""
    id: str = Field(..., description="Correlation UUID")
    email_id: Optional[str] = Field(None, description="Email UUID")
    web_log_id: Optional[str] = Field(None, description="WebLog UUID")
    correlation_score: float = Field(..., ge=0.0, le=1.0, description="Correlation strength")
    correlation_type: Optional[str] = Field(None, description="Type of correlation")
    details: Optional[Dict[str, Any]] = Field(None, description="Correlation details")
    created_at: datetime


class CorrelationStatisticsResponse(BaseModel):
    """Response schema for correlation statistics."""
    total_correlations: int = Field(..., description="Total correlations")
    avg_correlation_score: float = Field(..., description="Average correlation score")
    type_distribution: Dict[str, int] = Field(..., description="Count by correlation type")


# ==================== Report Schemas ====================

class ThreatReportResponse(BaseModel):
    """Response schema for threat report."""
    id: str = Field(..., description="Report UUID")
    report_type: str = Field(..., description="email, web, or unified")
    title: str = Field(..., description="Report title")
    email_threats: int = Field(..., description="Email threats count")
    web_threats: int = Field(..., description="Web threats count")
    correlation_count: int = Field(..., description="Correlations count")
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    overall_risk_level: str = Field(...)
    threat_counts: Optional[Dict[str, int]] = Field(None, description="Count by risk level")
    recommendations: Optional[List[str]] = Field(None, description="Security recommendations")
    created_at: datetime


class GenerateReportRequest(BaseModel):
    """Request schema for generating report."""
    report_type: str = Field(..., description="email, web, or unified")
    title: str = Field(..., min_length=5, max_length=500)
    include_recommendations: bool = Field(True, description="Include recommendations")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        if v not in ['email', 'web', 'unified']:
            raise ValueError('report_type must be email, web, or unified')
        return v


# ==================== Pagination & Filtering ====================

class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")


class DateRangeFilter(BaseModel):
    """Date range filtering."""
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")


class RiskLevelFilter(BaseModel):
    """Risk level filtering."""
    risk_level: str = Field(..., description="low, medium, high, or critical")
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        if v not in ['low', 'medium', 'high', 'critical']:
            raise ValueError('risk_level must be low, medium, high, or critical')
        return v


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional details")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    error: str = "Validation Error"
    details: List[Dict[str, Any]] = Field(..., description="Field validation errors")
    status_code: int = 422


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="ok or error")
    database: str = Field(..., description="Database connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="API version")


# ==================== Bulk Operations ====================

class BulkEmailAnalysisRequest(BaseModel):
    """Request schema for bulk email analysis."""
    emails: List[EmailAnalysisRequest] = Field(..., min_items=1, max_items=100)


class BulkEmailAnalysisResponse(BaseModel):
    """Response schema for bulk email analysis."""
    results: List[EmailPredictionResponse]
    total: int
    successful: int
    failed: int


class BulkWebLogAnalysisRequest(BaseModel):
    """Request schema for bulk web log analysis."""
    logs: List[WebLogAnalysisRequest] = Field(..., min_items=1, max_items=100)


class BulkWebLogAnalysisResponse(BaseModel):
    """Response schema for bulk web log analysis."""
    results: List[WebLogAnomalyResponse]
    total: int
    successful: int
    failed: int
