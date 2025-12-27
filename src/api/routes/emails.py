"""
Email Analysis Routes

REST API endpoints for email phishing detection and analysis.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime

from src.api.schemas import (
    EmailAnalysisRequest,
    EmailPredictionResponse,
    EmailStorageRequest,
    EmailResponse,
    EmailStatisticsResponse,
    BulkEmailAnalysisRequest,
    BulkEmailAnalysisResponse,
    PaginationParams,
)
from src.email_detector import EmailPhishingDetector
from src.database import get_db_session, Email
from src.database.queries import EmailQueries

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize detectors
detector = EmailPhishingDetector()

# Try to initialize BERT detector (optional)
try:
    from src.email_detector import BertEmailDetector
    bert_detector = BertEmailDetector(model_path="models/bert_finetuned")
    logger.info("BERT detector initialized successfully")
except Exception as e:
    logger.warning(f"BERT detector not available: {e}")
    bert_detector = None


# ==================== Analysis Endpoints ====================

@router.post(
    "/analyze",
    response_model=EmailPredictionResponse,
    summary="Analyze Single Email",
    description="Analyze a single email for phishing threats"
)
async def analyze_email(request: EmailAnalysisRequest):
    """
    Analyze a single email for phishing threats.
    
    Args:
        request: Email analysis request with text, sender, etc.
    
    Returns:
        EmailPredictionResponse: Prediction, confidence, risk assessment
    
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Analyzing email from {request.sender}")
        
        # Detect phishing
        prediction, confidence, factors = detector.detect(request.text)
        
        # Calculate risk
        risk_score = confidence * 100 if prediction == 1 else (1 - confidence) * 10
        
        # Determine risk level
        if risk_score < 20:
            risk_level = "low"
        elif risk_score < 50:
            risk_level = "medium"
        elif risk_score < 80:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        logger.info(f"Email analysis complete: prediction={prediction}, confidence={confidence:.3f}")
        
        return EmailPredictionResponse(
            prediction=prediction,
            confidence=confidence,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=factors,
            urls=request.text  # Placeholder - extract actual URLs
        )
    
    except Exception as e:
        logger.error(f"Email analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Email analysis failed: {str(e)}"
        )


@router.post(
    "/analyze-bulk",
    response_model=BulkEmailAnalysisResponse,
    summary="Analyze Multiple Emails",
    description="Analyze multiple emails in a single request"
)
async def analyze_bulk_emails(request: BulkEmailAnalysisRequest):
    """
    Analyze multiple emails in bulk.
    
    Args:
        request: Bulk analysis request with list of emails
    
    Returns:
        BulkEmailAnalysisResponse: Results for all emails
    """
    try:
        results = []
        successful = 0
        failed = 0
        
        for email in request.emails:
            try:
                prediction, confidence, factors = detector.detect(email.text)
                risk_score = confidence * 100 if prediction == 1 else (1 - confidence) * 10
                
                if risk_score < 20:
                    risk_level = "low"
                elif risk_score < 50:
                    risk_level = "medium"
                elif risk_score < 80:
                    risk_level = "high"
                else:
                    risk_level = "critical"
                
                results.append(EmailPredictionResponse(
                    prediction=prediction,
                    confidence=confidence,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    risk_factors=factors
                ))
                successful += 1
            
            except Exception as e:
                logger.error(f"Error analyzing email: {e}")
                failed += 1
        
        logger.info(f"Bulk analysis complete: {successful}/{len(request.emails)} successful")
        
        return BulkEmailAnalysisResponse(
            results=results,
            total=len(request.emails),
            successful=successful,
            failed=failed
        )
    
    except Exception as e:
        logger.error(f"Bulk analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Bulk analysis failed: {str(e)}"
        )


# ==================== Database Operations ====================

@router.post(
    "",
    response_model=EmailResponse,
    status_code=201,
    summary="Create Email Record",
    description="Store analyzed email in database"
)
async def create_email(request: EmailStorageRequest, session = Depends(get_db_session)):
    """
    Create and store an email record in the database.
    
    Args:
        request: Email data to store
        session: Database session
    
    Returns:
        EmailResponse: Created email record
    """
    try:
        email = Email(
            email_text=request.email_text,
            sender=request.sender,
            receiver=request.receiver,
            subject=request.subject,
            date=request.date,
            prediction=request.prediction,
            confidence=request.confidence,
            risk_score=request.risk_score,
            risk_level=request.risk_level,
            risk_factors=request.risk_factors,
            urls=request.urls,
        )
        
        session.add(email)
        session.commit()
        session.refresh(email)
        
        logger.info(f"Email stored: {email.id}")
        
        return EmailResponse.from_orm(email)
    
    except Exception as e:
        session.rollback()
        logger.error(f"Email storage error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Email storage failed: {str(e)}"
        )
    
    finally:
        session.close()


@router.get(
    "",
    response_model=List[EmailResponse],
    summary="List Emails",
    description="Get paginated list of emails"
)
async def list_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get paginated list of emails.
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[EmailResponse]: Email records
    """
    try:
        emails = EmailQueries.get_all(session, limit=limit, offset=skip)
        return [EmailResponse.from_orm(e) for e in emails]
    
    except Exception as e:
        logger.error(f"List emails error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/{email_id}",
    response_model=EmailResponse,
    summary="Get Email",
    description="Get specific email by ID"
)
async def get_email(email_id: str, session = Depends(get_db_session)):
    """
    Get a specific email by ID.
    
    Args:
        email_id: Email UUID
        session: Database session
    
    Returns:
        EmailResponse: Email record
    
    Raises:
        HTTPException: If email not found
    """
    try:
        email = EmailQueries.get_by_id(session, email_id)
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return EmailResponse.from_orm(email)
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Get email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== Filtering Endpoints ====================

@router.get(
    "/phishing",
    response_model=List[EmailResponse],
    summary="Get Phishing Emails",
    description="Get detected phishing emails"
)
async def get_phishing_emails(
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get phishing emails (prediction=1).
    
    Args:
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[EmailResponse]: Phishing emails
    """
    try:
        emails = EmailQueries.get_phishing(session, limit=limit)
        return [EmailResponse.from_orm(e) for e in emails]
    
    except Exception as e:
        logger.error(f"Get phishing emails error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/legitimate",
    response_model=List[EmailResponse],
    summary="Get Legitimate Emails",
    description="Get legitimate emails"
)
async def get_legitimate_emails(
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get legitimate emails (prediction=0).
    
    Args:
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[EmailResponse]: Legitimate emails
    """
    try:
        emails = EmailQueries.get_legitimate(session, limit=limit)
        return [EmailResponse.from_orm(e) for e in emails]
    
    except Exception as e:
        logger.error(f"Get legitimate emails error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


@router.get(
    "/risk-level/{level}",
    response_model=List[EmailResponse],
    summary="Get Emails by Risk Level",
    description="Get emails filtered by risk level"
)
async def get_by_risk_level(
    level: str,
    limit: int = Query(100, ge=1, le=1000),
    session = Depends(get_db_session)
):
    """
    Get emails by risk level.
    
    Args:
        level: Risk level (low, medium, high, critical)
        limit: Number of records to return
        session: Database session
    
    Returns:
        List[EmailResponse]: Filtered emails
    
    Raises:
        HTTPException: If invalid risk level
    """
    if level not in ['low', 'medium', 'high', 'critical']:
        raise HTTPException(status_code=400, detail="Invalid risk level")
    
    try:
        emails = EmailQueries.get_by_risk_level(session, level, limit=limit)
        return [EmailResponse.from_orm(e) for e in emails]
    
    except Exception as e:
        logger.error(f"Get emails by risk level error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()


# ==================== BERT Analysis Endpoint ====================

@router.post(
    "/analyze-bert",
    response_model=EmailPredictionResponse,
    summary="Analyze Email with BERT",
    description="Analyze email using fine-tuned BERT model (higher accuracy)"
)
async def analyze_email_bert(request: EmailAnalysisRequest):
    """
    Analyze email using BERT model for higher accuracy.
    
    Args:
        request: Email analysis request with text, sender, etc.
    
    Returns:
        EmailPredictionResponse: BERT prediction, confidence, risk assessment
    
    Raises:
        HTTPException: If BERT not available or analysis fails
    """
    if bert_detector is None:
        raise HTTPException(
            status_code=503,
            detail="BERT detector not available. Please ensure transformers library is installed and model is in models/bert_finetuned/"
        )
    
    try:
        logger.info(f"Analyzing email with BERT from {request.sender}")
        
        # Get BERT prediction
        bert_result = bert_detector.predict(request.text)
        
        # Convert to API format
        prediction = 1 if bert_result.label == "phishing" else 0
        confidence = bert_result.confidence
        
        # Calculate risk score
        risk_score = bert_result.score * 100 if prediction == 1 else (1 - bert_result.score) * 10
        
        # Determine risk level
        if risk_score < 20:
            risk_level = "low"
        elif risk_score < 50:
            risk_level = "medium"
        elif risk_score < 80:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Create risk factors
        risk_factors = [{
            "factor": "BERT Model Analysis",
            "importance": confidence,
            "evidence": f"Model processed {bert_result.tokens} tokens with {confidence:.1%} confidence"
        }]
        
        logger.info(f"BERT analysis complete: prediction={prediction}, confidence={confidence:.3f}, tokens={bert_result.tokens}")
        
        return EmailPredictionResponse(
            prediction=prediction,
            confidence=confidence,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            urls=request.text  # Placeholder
        )
    
    except Exception as e:
        logger.error(f"BERT analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"BERT analysis failed: {str(e)}"
        )


# ==================== Statistics ====================

@router.get(
    "/statistics",
    response_model=EmailStatisticsResponse,
    summary="Email Statistics",
    description="Get email analysis statistics"
)
async def get_statistics(session = Depends(get_db_session)):
    """
    Get email statistics.
    
    Args:
        session: Database session
    
    Returns:
        EmailStatisticsResponse: Statistics data
    """
    try:
        stats = EmailQueries.get_statistics(session)
        return EmailStatisticsResponse(**stats)
    
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        session.close()
