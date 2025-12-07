"""
Threat Report Routes

REST API endpoints for threat analysis reports and recommendations.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime

from src.api.schemas import (
    ThreatReportResponse,
    GenerateReportRequest,
)
from src.database import get_db_session, ThreatReport
from src.database.queries import ReportQueries

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== List Endpoints ====================

@router.get(
    "",
    response_model=List[ThreatReportResponse],
    summary="List Reports",
    description="Get paginated list of threat reports"
)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get paginated list of threat reports.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[ThreatReportResponse]: Report records
    """
    try:
        reports = ReportQueries.get_all(session, limit=limit)
        return [
            ThreatReportResponse(
                id=str(r.id),
                report_type=r.report_type,
                title=r.title,
                email_threats=r.email_threats,
                web_threats=r.web_threats,
                correlation_count=r.correlation_count,
                overall_risk_score=r.overall_risk_score,
                overall_risk_level=r.overall_risk_level,
                threat_counts=r.threat_counts,
                recommendations=r.recommendations,
                created_at=r.created_at
            )
            for r in reports
        ]
    
    except Exception as e:
        logger.error(f"List reports error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/{report_id}",
    response_model=ThreatReportResponse,
    summary="Get Report",
    description="Get specific threat report by ID"
)
async def get_report(
    report_id: str,
    session = Depends(get_db_session)
):
    """
    Get a specific threat report by ID.
    
    Args:
        report_id: Report UUID
        session: Database session
    
    Returns:
        ThreatReportResponse: Report record
    
    Raises:
        HTTPException: If report not found
    """
    try:
        report = session.query(ThreatReport).filter(
            ThreatReport.id == report_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return ThreatReportResponse(
            id=str(report.id),
            report_type=report.report_type,
            title=report.title,
            email_threats=report.email_threats,
            web_threats=report.web_threats,
            correlation_count=report.correlation_count,
            overall_risk_score=report.overall_risk_score,
            overall_risk_level=report.overall_risk_level,
            threat_counts=report.threat_counts,
            recommendations=report.recommendations,
            created_at=report.created_at
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Get report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== Filtering Endpoints ====================

@router.get(
    "/type/{report_type}",
    response_model=List[ThreatReportResponse],
    summary="Get Reports by Type",
    description="Get reports filtered by type"
)
async def get_by_type(
    report_type: str,
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get reports by type.
    
    Args:
        report_type: Report type (email, web, unified)
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[ThreatReportResponse]: Filtered reports
    
    Raises:
        HTTPException: If invalid report type
    """
    if report_type not in ['email', 'web', 'unified']:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    try:
        reports = ReportQueries.get_by_type(session, report_type, limit=limit)
        return [
            ThreatReportResponse(
                id=str(r.id),
                report_type=r.report_type,
                title=r.title,
                email_threats=r.email_threats,
                web_threats=r.web_threats,
                correlation_count=r.correlation_count,
                overall_risk_score=r.overall_risk_score,
                overall_risk_level=r.overall_risk_level,
                threat_counts=r.threat_counts,
                recommendations=r.recommendations,
                created_at=r.created_at
            )
            for r in reports
        ]
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Get reports by type error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/risk-level/{risk_level}",
    response_model=List[ThreatReportResponse],
    summary="Get Reports by Risk Level",
    description="Get reports filtered by overall risk level"
)
async def get_by_risk_level(
    risk_level: str,
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get reports by risk level.
    
    Args:
        risk_level: Risk level (low, medium, high, critical)
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[ThreatReportResponse]: Filtered reports
    
    Raises:
        HTTPException: If invalid risk level
    """
    if risk_level not in ['low', 'medium', 'high', 'critical']:
        raise HTTPException(status_code=400, detail="Invalid risk level")
    
    try:
        reports = ReportQueries.get_by_risk_level(session, risk_level, limit=limit)
        return [
            ThreatReportResponse(
                id=str(r.id),
                report_type=r.report_type,
                title=r.title,
                email_threats=r.email_threats,
                web_threats=r.web_threats,
                correlation_count=r.correlation_count,
                overall_risk_score=r.overall_risk_score,
                overall_risk_level=r.overall_risk_level,
                threat_counts=r.threat_counts,
                recommendations=r.recommendations,
                created_at=r.created_at
            )
            for r in reports
        ]
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Get reports by risk level error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/recent",
    response_model=List[ThreatReportResponse],
    summary="Get Recent Reports",
    description="Get recent threat reports"
)
async def get_recent(
    days: int = Query(7, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get recent reports.
    
    Args:
        days: Number of days to look back
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[ThreatReportResponse]: Recent reports
    """
    try:
        reports = ReportQueries.get_recent(session, days=days, limit=limit)
        return [
            ThreatReportResponse(
                id=str(r.id),
                report_type=r.report_type,
                title=r.title,
                email_threats=r.email_threats,
                web_threats=r.web_threats,
                correlation_count=r.correlation_count,
                overall_risk_score=r.overall_risk_score,
                overall_risk_level=r.overall_risk_level,
                threat_counts=r.threat_counts,
                recommendations=r.recommendations,
                created_at=r.created_at
            )
            for r in reports
        ]
    
    except Exception as e:
        logger.error(f"Get recent reports error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== Report Generation ====================

@router.post(
    "",
    response_model=ThreatReportResponse,
    status_code=201,
    summary="Generate Report",
    description="Generate a new threat analysis report"
)
async def generate_report(
    request: GenerateReportRequest,
    session = Depends(get_db_session)
):
    """
    Generate a new threat analysis report.
    
    Args:
        request: Report generation request
        session: Database session
    
    Returns:
        ThreatReportResponse: Generated report
    """
    try:
        from src.database.queries import EmailQueries, WebLogQueries, CorrelationQueries
        
        logger.info(f"Generating {request.report_type} report: {request.title}")
        
        # Get statistics based on report type
        if request.report_type == 'email':
            email_stats = EmailQueries.get_statistics(session)
            email_threats = email_stats['phishing_count']
            web_threats = 0
            risk_score = (email_stats['phishing_percentage'] / 100) * 100
        
        elif request.report_type == 'web':
            web_stats = WebLogQueries.get_statistics(session)
            email_threats = 0
            web_threats = web_stats['anomaly_count']
            risk_score = web_stats['avg_anomaly_score'] * 100
        
        else:  # unified
            email_stats = EmailQueries.get_statistics(session)
            web_stats = WebLogQueries.get_statistics(session)
            corr_stats = CorrelationQueries.get_statistics(session)
            
            email_threats = email_stats['phishing_count']
            web_threats = web_stats['anomaly_count']
            risk_score = (
                (email_stats['phishing_percentage'] + 
                 web_stats['anomaly_percentage']) / 2
            )
        
        # Determine risk level
        if risk_score < 20:
            risk_level = "low"
        elif risk_score < 50:
            risk_level = "medium"
        elif risk_score < 80:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Generate recommendations
        recommendations = []
        if email_threats > 0:
            recommendations.append("Review and block identified phishing senders")
            recommendations.append("Implement email security training for staff")
        
        if web_threats > 0:
            recommendations.append("Investigate anomalous web activity")
            recommendations.append("Review firewall and WAF rules")
        
        if risk_score > 60:
            recommendations.append("Escalate to security team for investigation")
            recommendations.append("Perform comprehensive security audit")
        
        # Create report
        report = ThreatReport(
            report_type=request.report_type,
            title=request.title,
            email_threats=email_threats,
            web_threats=web_threats,
            correlation_count=0,  # Would need correlation queries
            overall_risk_score=risk_score,
            overall_risk_level=risk_level,
            threat_counts={
                'phishing': email_threats,
                'anomalies': web_threats
            },
            recommendations=recommendations if request.include_recommendations else None
        )
        
        session.add(report)
        session.commit()
        session.refresh(report)
        
        logger.info(f"Report generated: {report.id}")
        
        return ThreatReportResponse(
            id=str(report.id),
            report_type=report.report_type,
            title=report.title,
            email_threats=report.email_threats,
            web_threats=report.web_threats,
            correlation_count=report.correlation_count,
            overall_risk_score=report.overall_risk_score,
            overall_risk_level=report.overall_risk_level,
            threat_counts=report.threat_counts,
            recommendations=report.recommendations,
            created_at=report.created_at
        )
    
    except Exception as e:
        session.rollback()
        logger.error(f"Report generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )
    
    finally:
        session.close()
