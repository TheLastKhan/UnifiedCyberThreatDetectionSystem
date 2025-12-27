"""
FastAPI Security Integration Endpoints
=======================================

REST API endpoints for enhanced threat detection with VirusTotal.

Endpoints:
- POST /api/email/detect/enhanced - Email detection with VirusTotal
- POST /api/weblog/detect/enhanced - Web log detection with VirusTotal
- GET /api/reputation/url - Check URL reputation
- GET /api/reputation/ip - Check IP reputation
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import logging

from src.email_detector.enhanced_detector import (
    EnhancedEmailDetector, EnhancedEmailPrediction
)
from src.web_analyzer.enhanced_analyzer import (
    EnhancedWebLogAnalyzer, EnhancedWebLogPrediction
)
from src.security.virustotal import VirusTotalAPI

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["security"])

# Initialize detectors (shared instances)
email_detector = EnhancedEmailDetector()
weblog_analyzer = EnhancedWebLogAnalyzer()
vt_api = VirusTotalAPI()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class EmailDetectRequest(BaseModel):
    """Email detection request"""
    email_text: str = Field(..., description="Email text to analyze", min_length=10)
    extract_urls: bool = Field(default=True, description="Extract and check URLs")


class EmailDetectResponse(BaseModel):
    """Email detection response"""
    ml_score: float
    ml_label: str
    combined_score: float
    combined_label: str
    risk_level: str
    detection_method: str
    urls_found: List[str]
    vt_scores: Dict[str, float]
    explanation: Dict


class WebLogDetectRequest(BaseModel):
    """Web log detection request"""
    log_line: str = Field(..., description="Web server log line", min_length=20)
    check_reputation: bool = Field(default=True, description="Check IP/URL reputation")


class WebLogDetectResponse(BaseModel):
    """Web log detection response"""
    ip_address: str
    request_path: str
    anomaly_score: float
    combined_score: float
    risk_level: str
    attack_type: str
    ip_reputation_score: float
    url_reputation_score: float
    explanation: Dict


class URLReputationResponse(BaseModel):
    """URL reputation response"""
    url: str
    detected: bool
    detection_ratio: float
    engine_count: int
    detected_count: int


class IPReputationResponse(BaseModel):
    """IP reputation response"""
    ip: str
    detected: bool
    detection_ratio: float
    engine_count: int
    detected_count: int


# ============================================================================
# EMAIL DETECTION ENDPOINTS
# ============================================================================

@router.post("/email/detect/enhanced", response_model=EmailDetectResponse)
async def detect_email_enhanced(request: EmailDetectRequest):
    """
    Detect phishing email with VirusTotal enhancement
    
    Args:
        request: Email detection request
    
    Returns:
        Enhanced detection results with VirusTotal data
    
    Example:
        ```
        POST /api/email/detect/enhanced
        {
            "email_text": "Click here to verify your account: http://...",
            "extract_urls": true
        }
        ```
    """
    try:
        logger.info(f"Detecting email ({len(request.email_text)} chars)")
        
        # Get prediction
        prediction = email_detector.predict(request.email_text)
        
        # Convert to response
        return EmailDetectResponse(
            ml_score=prediction.ml_score,
            ml_label=prediction.ml_label,
            combined_score=prediction.combined_score,
            combined_label=prediction.combined_label,
            risk_level=prediction.risk_level,
            detection_method=prediction.detection_method,
            urls_found=prediction.urls_found,
            vt_scores=prediction.vt_scores,
            explanation=prediction.explanation,
        )
        
    except Exception as e:
        logger.error(f"Email detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/detect/batch")
async def detect_email_batch(emails: List[EmailDetectRequest]):
    """
    Detect multiple emails (batch processing)
    
    Args:
        emails: List of email detection requests
    
    Returns:
        List of detection results
    """
    try:
        logger.info(f"Batch detecting {len(emails)} emails")
        
        email_texts = [e.email_text for e in emails]
        predictions = email_detector.batch_predict(email_texts)
        
        results = [
            EmailDetectResponse(
                ml_score=p.ml_score,
                ml_label=p.ml_label,
                combined_score=p.combined_score,
                combined_label=p.combined_label,
                risk_level=p.risk_level,
                detection_method=p.detection_method,
                urls_found=p.urls_found,
                vt_scores=p.vt_scores,
                explanation=p.explanation,
            )
            for p in predictions
        ]
        
        return {"count": len(results), "results": results}
        
    except Exception as e:
        logger.error(f"Batch detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEB LOG DETECTION ENDPOINTS
# ============================================================================

@router.post("/weblog/detect/enhanced", response_model=WebLogDetectResponse)
async def detect_weblog_enhanced(request: WebLogDetectRequest):
    """
    Detect malicious web log with VirusTotal enhancement
    
    Args:
        request: Web log detection request
    
    Returns:
        Enhanced detection results with VirusTotal data
    
    Example:
        ```
        POST /api/weblog/detect/enhanced
        {
            "log_line": "192.168.1.1 - - [...] GET /admin?id=1' OR '1'='1",
            "check_reputation": true
        }
        ```
    """
    try:
        logger.info("Detecting web log")
        
        # Get prediction
        prediction = weblog_analyzer.predict(request.log_line)
        
        # Convert to response
        return WebLogDetectResponse(
            ip_address=prediction.ip_address,
            request_path=prediction.request_path,
            anomaly_score=prediction.anomaly_score,
            combined_score=prediction.combined_score,
            risk_level=prediction.risk_level,
            attack_type=prediction.attack_type,
            ip_reputation_score=prediction.ip_reputation_score,
            url_reputation_score=prediction.url_reputation_score,
            explanation=prediction.explanation,
        )
        
    except Exception as e:
        logger.error(f"Web log detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weblog/detect/batch")
async def detect_weblog_batch(logs: List[WebLogDetectRequest]):
    """
    Detect multiple web logs (batch processing)
    
    Args:
        logs: List of web log detection requests
    
    Returns:
        List of detection results
    """
    try:
        logger.info(f"Batch detecting {len(logs)} logs")
        
        log_lines = [l.log_line for l in logs]
        predictions = weblog_analyzer.batch_predict(log_lines)
        
        results = [
            WebLogDetectResponse(
                ip_address=p.ip_address,
                request_path=p.request_path,
                anomaly_score=p.anomaly_score,
                combined_score=p.combined_score,
                risk_level=p.risk_level,
                attack_type=p.attack_type,
                ip_reputation_score=p.ip_reputation_score,
                url_reputation_score=p.url_reputation_score,
                explanation=p.explanation,
            )
            for p in predictions
        ]
        
        return {"count": len(results), "results": results}
        
    except Exception as e:
        logger.error(f"Batch detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# REPUTATION CHECK ENDPOINTS
# ============================================================================

@router.get("/reputation/url", response_model=URLReputationResponse)
async def check_url_reputation(url: str = Query(..., description="URL to check")):
    """
    Check URL reputation via VirusTotal
    
    Args:
        url: URL to check
    
    Returns:
        URL reputation data
    
    Example:
        GET /api/reputation/url?url=https://phishing-site.com
    """
    try:
        logger.info(f"Checking URL reputation: {url}")
        
        result = vt_api.check_url(url)
        
        if result.error:
            raise HTTPException(status_code=400, detail=result.error)
        
        return URLReputationResponse(
            url=url,
            detected=result.detected,
            detection_ratio=result.detection_ratio,
            engine_count=result.engine_count,
            detected_count=result.detected_count,
        )
        
    except Exception as e:
        logger.error(f"URL reputation check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reputation/ip", response_model=IPReputationResponse)
async def check_ip_reputation(ip: str = Query(..., description="IP address to check")):
    """
    Check IP reputation via VirusTotal
    
    Args:
        ip: IP address to check
    
    Returns:
        IP reputation data
    
    Example:
        GET /api/reputation/ip?ip=192.168.1.1
    """
    try:
        logger.info(f"Checking IP reputation: {ip}")
        
        result = vt_api.check_ip(ip)
        
        if result.error:
            raise HTTPException(status_code=400, detail=result.error)
        
        return IPReputationResponse(
            ip=ip,
            detected=result.detected,
            detection_ratio=result.detection_ratio,
            engine_count=result.engine_count,
            detected_count=result.detected_count,
        )
        
    except Exception as e:
        logger.error(f"IP reputation check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reputation/urls")
async def check_urls_batch(urls: List[str]):
    """
    Check multiple URLs (batch)
    
    Args:
        urls: List of URLs to check
    
    Returns:
        List of reputation data
    """
    try:
        logger.info(f"Batch checking {len(urls)} URLs")
        
        results = []
        for url in urls:
            result = vt_api.check_url(url)
            results.append({
                "url": url,
                "detected": result.detected,
                "detection_ratio": result.detection_ratio,
                "detected_count": result.detected_count,
            })
        
        return {"count": len(results), "results": results}
        
    except Exception as e:
        logger.error(f"Batch URL check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/security/status")
async def security_status():
    """
    Get security module status
    
    Returns:
        Status of all security modules
    """
    return {
        "status": "healthy",
        "modules": {
            "email_detector": "ready",
            "weblog_analyzer": "ready",
            "virustotal_api": "ready" if vt_api.api_key else "not_configured",
        },
        "timestamp": __import__('datetime').datetime.now().isoformat(),
    }
