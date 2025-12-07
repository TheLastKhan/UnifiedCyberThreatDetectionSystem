"""
Web Log Analysis Routes

REST API endpoints for web log anomaly detection and analysis.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query

from src.api.schemas import (
    WebLogAnalysisRequest,
    WebLogAnomalyResponse,
    WebLogStorageRequest,
    WebLogResponse,
    WebLogStatisticsResponse,
    SuspiciousIPResponse,
    BulkWebLogAnalysisRequest,
    BulkWebLogAnalysisResponse,
)
from src.web_analyzer import WebLogAnalyzer
from src.database import get_db_session, WebLog
from src.database.queries import WebLogQueries

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize analyzer
analyzer = WebLogAnalyzer()


# ==================== Analysis Endpoints ====================

@router.post(
    "/analyze",
    response_model=WebLogAnomalyResponse,
    summary="Analyze Single Log",
    description="Analyze a single web server log for anomalies"
)
async def analyze_log(request: WebLogAnalysisRequest):
    """
    Analyze a single web server log for anomalies.
    
    Args:
        request: Web log analysis request
    
    Returns:
        WebLogAnomalyResponse: Anomaly score, risk assessment
    
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Analyzing web log: {request.log_line[:50]}...")
        
        # Analyze log
        anomaly_score, indicators = analyzer.analyze(request.log_line)
        
        # Determine risk level
        if anomaly_score < 0.3:
            risk_level = "normal"
        elif anomaly_score < 0.6:
            risk_level = "suspicious"
        else:
            risk_level = "malicious"
        
        is_anomaly = anomaly_score > 0.5
        
        logger.info(f"Log analysis complete: anomaly_score={anomaly_score:.3f}, risk={risk_level}")
        
        return WebLogAnomalyResponse(
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            indicators=indicators
        )
    
    except Exception as e:
        logger.error(f"Web log analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Web log analysis failed: {str(e)}"
        )


@router.post(
    "/analyze-bulk",
    response_model=BulkWebLogAnalysisResponse,
    summary="Analyze Multiple Logs",
    description="Analyze multiple web logs in a single request"
)
async def analyze_bulk_logs(request: BulkWebLogAnalysisRequest):
    """
    Analyze multiple web logs in bulk.
    
    Args:
        request: Bulk analysis request with list of logs
    
    Returns:
        BulkWebLogAnalysisResponse: Results for all logs
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        for log in request.logs:
            try:
                anomaly_score, indicators = analyzer.analyze(log.log_line)
                
                if anomaly_score < 0.3:
                    risk_level = "normal"
                elif anomaly_score < 0.6:
                    risk_level = "suspicious"
                else:
                    risk_level = "malicious"
                
                results.append(WebLogAnomalyResponse(
                    anomaly_score=anomaly_score,
                    is_anomaly=anomaly_score > 0.5,
                    risk_level=risk_level,
                    indicators=indicators
                ))
                successful += 1
            
            except Exception as e:
                logger.error(f"Error analyzing log: {e}")
                failed += 1
        
        logger.info(f"Bulk log analysis complete: {successful}/{len(request.logs)} successful")
        
        return BulkWebLogAnalysisResponse(
            results=results,
            total=len(request.logs),
            successful=successful,
            failed=failed
        )
    
    except Exception as e:
        logger.error(f"Bulk log analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Bulk analysis failed: {str(e)}"
        )


# ==================== Database Operations ====================

@router.post(
    "",
    response_model=WebLogResponse,
    status_code=201,
    summary="Create Web Log Record",
    description="Store analyzed web log in database"
)
async def create_weblog(request: WebLogStorageRequest, session = Depends(get_db_session)):
    """
    Create and store a web log record in the database.
    
    Args:
        request: Web log data to store
        session: Database session
    
    Returns:
        WebLogResponse: Created web log record
    """
    try:
        weblog = WebLog(
            log_line=request.log_line,
            ip_address=request.ip_address,
            method=request.method,
            path=request.path,
            status_code=request.status_code,
            user_agent=request.user_agent,
            response_size=request.response_size,
            timestamp=request.timestamp,
            anomaly_score=request.anomaly_score,
            is_anomaly=request.is_anomaly,
            risk_level=request.risk_level,
            indicators=request.indicators,
            attack_patterns=request.attack_patterns,
        )
        
        session.add(weblog)
        session.commit()
        session.refresh(weblog)
        
        logger.info(f"Web log stored: {weblog.id}")
        
        return WebLogResponse.from_orm(weblog)
    
    except Exception as e:
        session.rollback()
        logger.error(f"Web log storage error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Web log storage failed: {str(e)}"
        )
    
    finally:
        session.close()


@router.get(
    "",
    response_model=List[WebLogResponse],
    summary="List Web Logs",
    description="Get paginated list of web logs"
)
async def list_weblogs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get paginated list of web logs.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[WebLogResponse]: Web log records
    """
    try:
        logs = WebLogQueries.get_all(session, limit=limit, offset=skip)
        return [WebLogResponse.from_orm(log) for log in logs]
    
    except Exception as e:
        logger.error(f"List web logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/{log_id}",
    response_model=WebLogResponse,
    summary="Get Web Log",
    description="Get specific web log by ID"
)
async def get_weblog(log_id: str, session = Depends(get_db_session)):
    """
    Get a specific web log by ID.
    
    Args:
        log_id: Web log UUID
        session: Database session
    
    Returns:
        WebLogResponse: Web log record
    
    Raises:
        HTTPException: If web log not found
    """
    try:
        log = WebLogQueries.get_by_id(session, log_id)
        
        if not log:
            raise HTTPException(status_code=404, detail="Web log not found")
        
        return WebLogResponse.from_orm(log)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Get web log error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== Filtering Endpoints ====================

@router.get(
    "/anomalies",
    response_model=List[WebLogResponse],
    summary="Get Anomalous Logs",
    description="Get detected anomalous web logs"
)
async def get_anomalies(
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get anomalous web logs.
    
    Args:
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[WebLogResponse]: Anomalous logs
    """
    try:
        logs = WebLogQueries.get_anomalies(session, limit=limit)
        return [WebLogResponse.from_orm(log) for log in logs]
    
    except Exception as e:
        logger.error(f"Get anomalies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/by-ip/{ip_address}",
    response_model=List[WebLogResponse],
    summary="Get Logs by IP",
    description="Get logs from specific IP address"
)
async def get_by_ip(
    ip_address: str,
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get logs from specific IP address.
    
    Args:
        ip_address: IP address to filter
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[WebLogResponse]: Filtered logs
    """
    try:
        logs = WebLogQueries.get_by_ip(session, ip_address, limit=limit)
        return [WebLogResponse.from_orm(log) for log in logs]
    
    except Exception as e:
        logger.error(f"Get logs by IP error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/risk-level/{level}",
    response_model=List[WebLogResponse],
    summary="Get Logs by Risk Level",
    description="Get web logs filtered by risk level"
)
async def get_by_risk_level(
    level: str,
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get web logs by risk level.
    
    Args:
        level: Risk level (normal, suspicious, malicious)
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[WebLogResponse]: Filtered logs
    """
    if level not in ['normal', 'suspicious', 'malicious']:
        raise HTTPException(status_code=400, detail="Invalid risk level")
    
    try:
        logs = session.query(WebLog).filter(WebLog.risk_level == level).limit(limit).all()
        return [WebLogResponse.from_orm(log) for log in logs]
    
    except Exception as e:
        logger.error(f"Get logs by risk level error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== Suspicious IPs ====================

@router.get(
    "/suspicious-ips",
    response_model=List[SuspiciousIPResponse],
    summary="Get Suspicious IPs",
    description="Get IP addresses with suspicious activity"
)
async def get_suspicious_ips(
    limit: int = Query(50, ge=1, le=500),
    session = Depends(get_db_session)
):
    """
    Get IP addresses with suspicious activity.
    
    Args:
        limit: Number of IPs to return
        session: Database session
    
    Returns:
        List[SuspiciousIPResponse]: Suspicious IP addresses
    """
    try:
        ips = WebLogQueries.get_suspicious_ips(session, limit=limit)
        return [
            SuspiciousIPResponse(
                ip_address=ip[0],
                log_count=ip[1],
                avg_anomaly_score=ip[2]
            )
            for ip in ips
        ]
    
    except Exception as e:
        logger.error(f"Get suspicious IPs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== Statistics ====================

@router.get(
    "/statistics",
    response_model=WebLogStatisticsResponse,
    summary="Web Log Statistics",
    description="Get web log analysis statistics"
)
async def get_statistics(session = Depends(get_db_session)):
    """
    Get web log statistics.
    
    Args:
        session: Database session
    
    Returns:
        WebLogStatisticsResponse: Statistics data
    """
    try:
        stats = WebLogQueries.get_statistics(session)
        return WebLogStatisticsResponse(**stats)
    
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()
