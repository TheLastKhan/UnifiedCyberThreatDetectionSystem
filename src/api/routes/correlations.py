"""
Threat Correlation Routes

REST API endpoints for threat correlations between emails and web logs.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query

from src.api.schemas import (
    ThreatCorrelationResponse,
    CorrelationStatisticsResponse,
)
from src.database import get_db_session
from src.database.queries import CorrelationQueries

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== List Endpoints ====================

@router.get(
    "",
    response_model=List[ThreatCorrelationResponse],
    summary="List Correlations",
    description="Get paginated list of threat correlations"
)
async def list_correlations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get paginated list of threat correlations.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[ThreatCorrelationResponse]: Correlation records
    """
    try:
        # Manual pagination since query function doesn't support it
        correlations = CorrelationQueries.get_all(session, limit=limit)
        return [
            ThreatCorrelationResponse(
                id=str(c.id),
                email_id=str(c.email_id) if c.email_id else None,
                web_log_id=str(c.web_log_id) if c.web_log_id else None,
                correlation_score=c.correlation_score,
                correlation_type=c.correlation_type,
                details=c.details,
                created_at=c.created_at
            )
            for c in correlations
        ]
    
    except Exception as e:
        logger.error(f"List correlations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/by-email/{email_id}",
    response_model=List[ThreatCorrelationResponse],
    summary="Get Correlations by Email",
    description="Get threat correlations for specific email"
)
async def get_by_email(
    email_id: str,
    session = Depends(get_db_session)
):
    """
    Get correlations for specific email.
    
    Args:
        email_id: Email UUID
        session: Database session
    
    Returns:
        List[ThreatCorrelationResponse]: Correlation records
    
    Raises:
        HTTPException: If email ID is invalid
    """
    try:
        correlations = CorrelationQueries.get_by_email_id(session, email_id)
        
        return [
            ThreatCorrelationResponse(
                id=str(c.id),
                email_id=str(c.email_id) if c.email_id else None,
                web_log_id=str(c.web_log_id) if c.web_log_id else None,
                correlation_score=c.correlation_score,
                correlation_type=c.correlation_type,
                details=c.details,
                created_at=c.created_at
            )
            for c in correlations
        ]
    
    except Exception as e:
        logger.error(f"Get correlations by email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/high-confidence",
    response_model=List[ThreatCorrelationResponse],
    summary="Get High-Confidence Correlations",
    description="Get correlations with high confidence scores"
)
async def get_high_confidence(
    threshold: float = Query(0.7, ge=0.0, le=1.0),
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get high-confidence correlations.
    
    Args:
        threshold: Minimum confidence threshold (0.0-1.0)
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[ThreatCorrelationResponse]: High-confidence correlations
    """
    try:
        correlations = CorrelationQueries.get_high_confidence(
            session,
            threshold=threshold,
            limit=limit
        )
        
        return [
            ThreatCorrelationResponse(
                id=str(c.id),
                email_id=str(c.email_id) if c.email_id else None,
                web_log_id=str(c.web_log_id) if c.web_log_id else None,
                correlation_score=c.correlation_score,
                correlation_type=c.correlation_type,
                details=c.details,
                created_at=c.created_at
            )
            for c in correlations
        ]
    
    except Exception as e:
        logger.error(f"Get high-confidence correlations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== Statistics ====================

@router.get(
    "/statistics",
    response_model=CorrelationStatisticsResponse,
    summary="Correlation Statistics",
    description="Get correlation analysis statistics"
)
async def get_statistics(session = Depends(get_db_session)):
    """
    Get correlation statistics.
    
    Args:
        session: Database session
    
    Returns:
        CorrelationStatisticsResponse: Statistics data
    """
    try:
        stats = CorrelationQueries.get_statistics(session)
        return CorrelationStatisticsResponse(**stats)
    
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()
