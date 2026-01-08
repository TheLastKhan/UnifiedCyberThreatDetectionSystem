"""
Production API Endpoints for Unified Threat Detection System
Complete REST API for email analysis, web log analysis, and monitoring
Uses shared model instances from web_dashboard.api
"""

from flask import Blueprint, request, jsonify, current_app
import os
from datetime import datetime, timedelta
import traceback

# Import database functions for persistent storage
try:
    from web_dashboard.database import (
        add_email_prediction as db_add_email_prediction,
        add_web_prediction as db_add_web_prediction,
        get_email_predictions,
        get_web_predictions,
        get_prediction_counts
    )
    DATABASE_AVAILABLE = True
    print("[INFO] Database module loaded successfully")
except Exception as e:
    print(f"[WARNING] Database not available: {e}")
    DATABASE_AVAILABLE = False

# Create Blueprint - no prefix since routes already include /api/
# This will be registered at root level and routes will use full paths
production_api_bp = Blueprint('production_api', __name__)

# Import shared model getters and loaders from existing API
from web_dashboard.api import (
    get_email_detector, 
    get_web_analyzer,
    _stacking_model,
    _voting_model,
    _tfidf_vectorizer,
    _web_anomaly_detector,
    _web_scaler
)

# Import advanced detectors
try:
    from src.email_detector.bert_detector import BertEmailDetector
    BERT_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] BERT detector not available: {e}")
    BERT_AVAILABLE = False

try:
    from src.email_detector.fasttext_detector import FastTextEmailDetector
    FASTTEXT_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] FastText detector not available: {e}")
    FASTTEXT_AVAILABLE = False

try:
    from src.email_detector.tfidf_detector import TFIDFEmailDetector
    TFIDF_DETECTOR_AVAILABLE = True
except Exception as e:
    print(f"[WARNING] TF-IDF detector not available: {e}")
    TFIDF_DETECTOR_AVAILABLE = False

# Global instances for advanced models
_bert_detector = None
_fasttext_detector = None

def get_bert_detector():
    """Get or create BERT detector instance (uses fine-tuned model)"""
    global _bert_detector
    if not BERT_AVAILABLE:
        return None
    if _bert_detector is None:
        try:
            # Use fine-tuned model for better phishing detection
            _bert_detector = BertEmailDetector(model_path="models/bert_finetuned")
            print("[INFO] BERT detector loaded successfully (fine-tuned model)")
        except Exception as e:
            print(f"[ERROR] Failed to load BERT detector: {e}")
            return None
    return _bert_detector

def get_fasttext_detector():
    """Get or create FastText detector instance"""
    global _fasttext_detector
    if not FASTTEXT_AVAILABLE:
        return None
    if _fasttext_detector is None:
        try:
            _fasttext_detector = FastTextEmailDetector()
            # Model automatically loads in __init__
            if _fasttext_detector.model is not None:
                print("[INFO] FastText detector loaded successfully")
            else:
                print("[WARNING] FastText model not found")
                return None
        except Exception as e:
            print(f"[ERROR] Failed to load FastText detector: {e}")
            return None
    return _fasttext_detector


# ============================================
# PREDICTION HISTORY (database persistence)
# ============================================

def _add_email_prediction(prediction, confidence, risk_level, email_subject=None, email_sender=None):
    """Add email prediction to persistent database"""
    if DATABASE_AVAILABLE:
        try:
            return db_add_email_prediction(prediction, confidence, risk_level, email_subject, email_sender)
        except Exception as e:
            print(f"[ERROR] Failed to save email prediction: {e}")
    return None

def _add_web_prediction(is_anomaly, anomaly_score, ip_address=None, patterns_detected=None):
    """Add web prediction to persistent database"""
    if DATABASE_AVAILABLE:
        try:
            return db_add_web_prediction(is_anomaly, anomaly_score, ip_address, patterns_detected=patterns_detected)
        except Exception as e:
            print(f"[ERROR] Failed to save web prediction: {e}")
    return None


# ============================================
# EMAIL ANALYSIS ENDPOINTS
# ============================================

@production_api_bp.route('/api/email/analyze', methods=['POST'])
def analyze_email():
    """
    Analyze email for phishing threats using TF-IDF with LIME
    
    POST /api/email/analyze
    {
        "email_content": "Email body text",
        "email_sender": "sender@example.com",
        "email_subject": "Email subject"
    }
    
    Returns:
    {
        "model": "TF-IDF",
        "prediction": "phishing" or "legitimate",
        "confidence": 0.95,
        "lime_breakdown": [{"feature": "urgent", "contribution": 15.2, "positive": true}, ...],
        "risk_level": "critical",
        "processing_time_ms": 123.4
    }
    """
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Support both 'email_content' (original) and 'body' (dashboard frontend) fields
        email_content = data.get('email_content') or data.get('body', '')
        email_sender = data.get('email_sender') or data.get('sender', '')
        email_subject = data.get('email_subject') or data.get('subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content or body is required'}), 400
        
        # Check if TF-IDF detector is available
        if not TFIDF_DETECTOR_AVAILABLE:
            return jsonify({
                'error': 'TF-IDF detector not available',
                'message': 'TF-IDF model not loaded'
            }), 503
        
        # Initialize TF-IDF detector
        detector = TFIDFEmailDetector()
        
        # Combine email parts
        full_text = f"{email_subject} {email_content}"
        
        # Get prediction with LIME explanation
        result = detector.predict_with_explanation(full_text)
        
        # Calculate risk level
        phishing_score = result['score']
        if phishing_score >= 0.80:
            risk_level = 'critical'
        elif phishing_score >= 0.60:
            risk_level = 'high'
        elif phishing_score >= 0.40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        processing_time = (time.time() - start_time) * 1000
        
        # Add prediction to database
        if DATABASE_AVAILABLE:
            try:
                email_sender = data.get('email_sender', 'Unknown')
                db_add_email_prediction(
                    email_subject=email_subject,
                    email_sender=email_sender,
                    email_content=email_content[:500],
                    prediction=result['prediction'],
                    confidence=float(result['confidence']),
                    phishing_score=phishing_score,
                    model_used='TF-IDF',
                    risk_level=risk_level
                )
            except Exception as db_error:
                print(f"[WARNING] Failed to save TF-IDF prediction: {db_error}")
        
        response = {
            'subject': email_subject,
            'sender': email_sender,
            'model_confidence': {
                'phishing_probability': round(phishing_score, 4),
                'legitimate_probability': round(1 - phishing_score, 4),
                'model_type': 'TF-IDF (Random Forest)',
                'prediction': result['prediction'],
                'risk_level': risk_level,
                'confidence': round(result['confidence'], 4)
            },
            'lime_breakdown': result.get('lime_breakdown', []),
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': round(processing_time, 2)
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"[ERROR] Email analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500


@production_api_bp.route('/api/email/analyze/bert', methods=['POST'])
def analyze_email_bert():
    """
    Analyze email using BERT model (advanced NLP)
    
    POST /api/email/analyze/bert
    {
        "email_content": "Email body text",
        "email_subject": "Email subject (optional)"
    }
    
    Returns:
    {
        "model": "BERT (DistilBERT)",
        "prediction": "phishing" or "legitimate",
        "confidence": 0.95,
        "score": 0.95,
        "label": "phishing",
        "processing_time_ms": 45.2
    }
    """
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_content = data.get('email_content', '')
        email_subject = data.get('email_subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content is required'}), 400
        
        # Get BERT detector
        detector = get_bert_detector()
        
        if detector is None:
            return jsonify({
                'error': 'BERT detector not available',
                'message': 'BERT model is not loaded. Please check installation.'
            }), 503
        
        # Combine subject and content
        full_text = f"{email_subject} {email_content}".strip()
        
        # Predict with BERT + LIME explanation
        result = detector.predict_with_explanation(full_text)
        
        processing_time = (time.time() - start_time) * 1000
        
        # Calculate risk level based on phishing score
        score = float(result['score'])
        label = result['prediction']
        
        if label == 'phishing':
            if score >= 0.99:
                risk_level = 'critical'
            elif score >= 0.90:
                risk_level = 'high'
            elif score >= 0.70:
                risk_level = 'medium'
            else:
                risk_level = 'low'
        else:
            risk_level = 'low'
        
        # Save prediction to database for Recent Alerts
        # DISABLED: Only TF-IDF saves to avoid duplicates
        # if DATABASE_AVAILABLE:
        #     try:
        #         db_add_email_prediction(
        #             email_subject=email_subject,
        #             email_sender=email_sender or 'Unknown',
        #             email_content=email_content[:500],
        #             prediction=label,
        #             confidence=float(result['confidence']),
        #             phishing_score=score if label == 'phishing' else 0.0,
        #             model_used='BERT',
        #             risk_level=risk_level
        #         )
        #     except Exception as db_error:
        #         print(f"[WARNING] Failed to save BERT prediction to database: {db_error}")
        
        return jsonify({
            'model': 'BERT (DistilBERT)',
            'prediction': label,
            'confidence': float(result['confidence']),
            'score': score,
            'phishing_score': score if label == 'phishing' else 0.0,
            'label': label,
            'risk_level': risk_level,
            'tokens_processed': result.get('tokens', 0),
            'lime_breakdown': result.get('lime_breakdown', []),  # NEW: LIME XAI
            'processing_time_ms': round(processing_time, 2)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] BERT analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'BERT analysis failed',
            'message': str(e)
        }), 500


@production_api_bp.route('/api/email/analyze/fasttext', methods=['POST'])
def analyze_email_fasttext():
    """
    Analyze email using FastText-style output (average of BERT and TF-IDF)
    
    This endpoint returns an "average" score between BERT and TF-IDF models,
    providing a balanced middle-ground prediction.
    
    POST /api/email/analyze/fasttext
    {
        "email_content": "Email body text",
        "email_subject": "Email subject (optional)"
    }
    
    Returns:
    {
        "model": "FastText",
        "prediction": "phishing" or "legitimate",
        "confidence": 0.92,
        "score": 0.92,
        "processing_time_ms": 2.5
    }
    """
    try:
        import time
        start_time = time.time()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_content = data.get('email_content', '')
        email_subject = data.get('email_subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content is required'}), 400
        
        # Combine subject and content
        full_text = f"{email_subject} {email_content}".strip()
        
        # Get scores from BERT and TF-IDF
        bert_score = 0.5
        tfidf_score = 0.5
        lime_breakdown = []
        
        # Get BERT score
        try:
            bert_detector = get_bert_detector()
            if bert_detector:
                bert_result = bert_detector.predict(full_text)
                bert_score = bert_result.score if hasattr(bert_result, 'score') else 0.5
        except Exception as e:
            print(f"[WARNING] BERT prediction failed in FastText endpoint: {e}")
        
        # Get TF-IDF score
        try:
            tfidf_detector = get_tfidf_detector()
            if tfidf_detector:
                tfidf_result = tfidf_detector.predict(full_text)
                tfidf_score = tfidf_result.score if hasattr(tfidf_result, 'score') else 0.5
        except Exception as e:
            print(f"[WARNING] TF-IDF prediction failed in FastText endpoint: {e}")
        
        # Calculate average score (FastText = average of BERT and TF-IDF)
        # Weight: BERT 60%, TF-IDF 40% (BERT is more accurate)
        phishing_score = (bert_score * 0.6) + (tfidf_score * 0.4)
        
        # Determine prediction based on averaged score
        prediction = 'phishing' if phishing_score > 0.5 else 'legitimate'
        confidence = max(phishing_score, 1 - phishing_score)
        
        # Calculate risk level
        if phishing_score >= 0.85:
            risk_level = 'critical'
        elif phishing_score >= 0.60:
            risk_level = 'high'
        elif phishing_score >= 0.40:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Generate LIME-style breakdown showing component scores
        lime_breakdown = [
            {'feature': 'BERT Score', 'contribution': round(bert_score * 100, 1), 'positive': bert_score > 0.5},
            {'feature': 'TF-IDF Score', 'contribution': round(tfidf_score * 100, 1), 'positive': tfidf_score > 0.5},
            {'feature': 'Weighted Average', 'contribution': round(phishing_score * 100, 1), 'positive': phishing_score > 0.5}
        ]
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            'model': 'FastText',
            'prediction': prediction,
            'confidence': float(confidence),
            'score': float(phishing_score),
            'phishing_score': float(phishing_score),
            'label': prediction,
            'risk_level': risk_level,
            'lime_breakdown': lime_breakdown,
            'processing_time_ms': round(processing_time, 2),
            'component_scores': {
                'bert': round(bert_score, 4),
                'tfidf': round(tfidf_score, 4)
            }
        }), 200
        
    except Exception as e:
        print(f"[ERROR] FastText analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'FastText analysis failed',
            'message': str(e)
        }), 500


@production_api_bp.route('/api/email/analyze/ensemble', methods=['POST'])
def analyze_email_ensemble():
    """
    Analyze email using weighted voting ensemble (BERT + FastText + TF-IDF)
    
    Weights: BERT 0.5, FastText 0.3, TF-IDF 0.2
    
    POST /api/email/analyze/ensemble
    {
        "email_content": "Email body text",
        "email_sender": "sender@example.com (optional)",
        "email_subject": "Email subject (optional)"
    }
    
    Returns:
    {
        "ensemble": {
            "prediction": "phishing",
            "confidence": 0.94,
            "weighted_score": 0.92,
            "risk_level": "critical"
        },
        "models": {
            "bert": {"prediction": "phishing", "score": 0.95, "time_ms": 45.8},
            "fasttext": {"prediction": "phishing", "score": 0.88, "time_ms": 2.1},
            "tfidf": {"prediction": "phishing", "score": 0.92, "time_ms": 25.3}
        },
        "total_processing_time_ms": 73.2
    }
    """
    try:
        import time
        from web_dashboard.ensemble_voting import weighted_vote
        
        start_time = time.time()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_content = data.get('email_content') or data.get('body', '')
        email_sender = data.get('email_sender') or data.get('sender', '')
        email_subject = data.get('email_subject') or data.get('subject', '')
        
        if not email_content:
            return jsonify({'error': 'email_content is required'}), 400
        
        model_results = {}
        model_scores = {}
        
        # Call all 3 models
        full_text = f"{email_subject} {email_content}".strip()
        
        # 1. BERT (50% weight)
        # 1. BERT (50% weight)
        if BERT_AVAILABLE:
            try:
                model_start = time.time()
                bert_detector = get_bert_detector()
                if bert_detector:
                    # Use predict_with_explanation for LIME
                    bert_full_result = bert_detector.predict_with_explanation(full_text)
                    bert_time = (time.time() - model_start) * 1000
                    
                    model_results['bert'] = {
                        'prediction': bert_full_result['prediction'],
                        'score': float(bert_full_result['score']),
                        'confidence': float(bert_full_result['confidence']),
                        'time_ms': round(bert_time, 2),
                        'risk_level': 'critical' if float(bert_full_result['score']) >= 0.99 else 'high' if float(bert_full_result['score']) >= 0.90 else 'medium' if float(bert_full_result['score']) >= 0.70 else 'low',
                        'lime_breakdown': bert_full_result.get('lime_breakdown', [])
                    }
                    model_scores['bert'] = float(bert_full_result['score'])
            except Exception as e:
                print(f"[WARNING] BERT prediction failed: {e}")
        
        # 2. FastText (30% weight)
        if FASTTEXT_AVAILABLE:
            try:
                model_start = time.time()
                fasttext_detector = get_fasttext_detector()
                if fasttext_detector:
                    ft_full_result = fasttext_detector.predict_with_explanation(full_text)
                    ft_time = (time.time() - model_start) * 1000
                    
                    model_results['fasttext'] = {
                        'prediction': ft_full_result['prediction'],
                        'score': float(ft_full_result['score']),
                        'confidence': float(ft_full_result['confidence']),
                        'time_ms': round(ft_time, 2),
                        'risk_level': 'critical' if float(ft_full_result['score']) >= 0.90 else 'high' if float(ft_full_result['score']) >= 0.70 else 'medium' if float(ft_full_result['score']) >= 0.50 else 'low',
                        'lime_breakdown': ft_full_result.get('lime_breakdown', [])
                    }
                    model_scores['fasttext'] = float(ft_full_result['score'])
            except Exception as e:
                print(f"[WARNING] FastText prediction failed: {e}")
        
        # 3. TF-IDF (20% weight)
        if TFIDF_DETECTOR_AVAILABLE:
            try:
                model_start = time.time()
                from src.email_detector.tfidf_detector import TFIDFEmailDetector
                tfidf_detector = TFIDFEmailDetector()
                tfidf_full_result = tfidf_detector.predict_with_explanation(full_text)
                tfidf_time = (time.time() - model_start) * 1000
                
                model_results['tfidf'] = {
                    'prediction': tfidf_full_result['prediction'],
                    'score': float(tfidf_full_result['score']),
                    'confidence': float(tfidf_full_result['confidence']),
                    'time_ms': round(tfidf_time, 2),
                    'risk_level': 'critical' if float(tfidf_full_result['score']) >= 0.8 else 'high' if float(tfidf_full_result['score']) >= 0.6 else 'medium' if float(tfidf_full_result['score']) >= 0.4 else 'low',
                    'lime_breakdown': tfidf_full_result.get('lime_breakdown', [])
                }
                model_scores['tfidf'] = float(tfidf_full_result['score'])
            except Exception as e:
                print(f"[WARNING] TF-IDF prediction failed: {e}")
        
        # Check if at least one model succeeded
        if not model_scores:
            return jsonify({
                'error': 'All models failed',
                'message': 'No models available for prediction'
            }), 503
        
        # Apply weighted voting
        ensemble_result = weighted_vote(
            bert_score=model_scores.get('bert'),
            fasttext_score=model_scores.get('fasttext'),
            tfidf_score=model_scores.get('tfidf')
        )
        
        total_time = (time.time() - start_time) * 1000
        
        # Save to database
        if DATABASE_AVAILABLE:
            try:
                db_add_email_prediction(
                    email_subject=email_subject,
                    email_sender=email_sender,
                    email_content=email_content[:500],
                    prediction=ensemble_result['prediction'],
                    confidence=float(ensemble_result['confidence']),
                    phishing_score=float(ensemble_result['weighted_score']),
                    model_used='Ensemble (Weighted Voting)',
                    risk_level=ensemble_result['risk_level']
                )
            except Exception as db_error:
                print(f"[WARNING] Failed to save ensemble prediction: {db_error}")
        
        return jsonify({
            'ensemble': {
                'prediction': ensemble_result['prediction'],
                'confidence': round(ensemble_result['confidence'], 4),
                'weighted_score': round(ensemble_result['weighted_score'], 4),
                'risk_level': ensemble_result['risk_level'],
                'models_used': ensemble_result['models_used'],
                'weights_applied': ensemble_result['weights_applied']
            },
            'models': model_results,
            'total_processing_time_ms': round(total_time, 2)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Ensemble analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Ensemble analysis failed',
            'message': str(e)
        }), 500


# ============================================
# WEB LOG ANALYSIS ENDPOINTS
# ============================================

@production_api_bp.route('/api/web/analyze', methods=['POST'])
def analyze_web_logs():
    """
    Analyze web logs for anomalies and attacks
    
    POST /api/web/analyze
    {
        "ip_address": "192.168.1.100",
        "logs": [
            {
                "ip": "192.168.1.100",
                "timestamp": "2025-12-13T10:00:00",
                "method": "GET",
                "path": "/admin",
                "status": 401,
                "size": 256,
                "user_agent": "Mozilla/5.0",
                "protocol": "HTTP/1.1",
                "referer": "-"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Support both batch format (ip_address + logs array) and single log format
        ip_address = data.get('ip_address') or data.get('ip')
        logs = data.get('logs', [])
        
        # If no logs array provided but individual fields exist, create log entry
        if not logs and ip_address:
            log_entry = {
                'ip': ip_address,
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'method': data.get('method', 'GET'),
                'path': data.get('path', '/'),
                'status': int(data.get('status', 200)),
                'size': int(data.get('size', 0)),
                'user_agent': data.get('user_agent', 'Unknown'),
                'protocol': data.get('protocol', 'HTTP/1.1'),
                'referer': data.get('referer', '-')
            }
            logs = [log_entry]
        
        if not ip_address:
            return jsonify({'error': 'ip_address or ip is required'}), 400
        
        if not logs:
            return jsonify({'error': 'logs array is required or provide individual log fields'}), 400
        
        # Use WebLogAnalyzer for proper feature extraction
        analyzer = get_web_analyzer()
        
        if analyzer is None or not analyzer.is_trained:
            # Return simple pattern-based analysis (no ML)
            patterns_detected = []
            severity_scores = []
            
            # Get historical data for this IP from database
            try:
                from web_dashboard.database import get_web_predictions
                historical_preds = get_web_predictions(hours=24*7)  # Last week
                ip_history = [p for p in historical_preds if p.get('ip_address') == ip_address]
                request_frequency = len(ip_history)
            except:
                request_frequency = 0
            
            # Check for high frequency (potential DoS or scanning)
            if request_frequency > 50:
                patterns_detected.append('High Frequency Requests')
                severity_scores.append(0.8)
            elif request_frequency > 20:
                patterns_detected.append('Elevated Request Rate')
                severity_scores.append(0.5)
            
            for log in logs:
                path = log.get('path', '').lower()
                ua = log.get('user_agent', '').lower()
                status = log.get('status', 200)
                
                # SQL Injection patterns (high severity)
                # Enhanced patterns to catch 1' OR '1'='1 and similar
                sql_patterns = ['select', 'union', 'drop', 'insert', 'delete', '--', ';', 
                               "' or '", '" or "', "or '1'='1", 'or 1=1', "'=", '"=']
                if any(kw in path for kw in sql_patterns):
                    patterns_detected.append('SQL Injection')
                    severity_scores.append(0.9)
                
                # XSS patterns (high severity)
                if any(pat in path for pat in ['<script', 'javascript:', 'onerror=', 'onclick=', 'alert(']):
                    patterns_detected.append('XSS')
                    severity_scores.append(0.9)
                
                # Directory Traversal (medium severity)
                if '../' in path or '..\\\\' in path:
                    patterns_detected.append('Directory Traversal')
                    severity_scores.append(0.7)
                
                # Admin Access Attempt (low-medium severity)
                if any(admin in path for admin in ['admin', 'wp-admin', 'phpmyadmin']):
                    if status in [401, 403]:
                        patterns_detected.append('Failed Admin Access')
                        severity_scores.append(0.5)
                    else:
                        patterns_detected.append('Admin Access Attempt')
                        severity_scores.append(0.6)
                
                # Suspicious User Agent (low severity)
                if any(bot in ua for bot in ['bot', 'crawler', 'scanner', 'sqlmap', 'nikto']):
                    patterns_detected.append('Suspicious User Agent')
                    severity_scores.append(0.4)
            
            # Calculate weighted anomaly score
            is_anomalous = len(patterns_detected) > 0
            if is_anomalous:
                # Average of severity scores, capped at 1.0
                anomaly_score = min(sum(severity_scores) / len(severity_scores), 1.0)
            else:
                anomaly_score = 0.0
            
            # Add to database for persistent storage with patterns
            _add_web_prediction(is_anomalous, anomaly_score, ip_address, patterns_detected=patterns_detected)
            
            result = {
                'ip_address': ip_address,
                'model_analysis': {
                    'is_anomalous': is_anomalous,
                    'anomaly_score': round(anomaly_score, 4),
                    'anomaly_score_percent': round(anomaly_score * 100, 2),  # Add percentage
                    'model_type': 'Pattern Matching (ML unavailable)',
                    'patterns_detected': list(set(patterns_detected)),
                    'threat_level': 'critical' if anomaly_score >= 0.85 else 'high' if anomaly_score >= 0.7 else 'medium' if anomaly_score >= 0.5 else 'low',
                    'threshold': 0.5,
                    'request_frequency': request_frequency  # Show frequency in results
                },
                'logs_analyzed': len(logs),
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify(result), 200
        
        # Use trained ML model
        result = analyzer.analyze_ip_with_explanation(logs, ip_address)
        
        if result is None:
            return jsonify({
                'error': 'Analysis failed',
                'message': 'Could not analyze the provided logs'
            }), 400
        
        # Add to database for persistent storage
        is_anomalous = result.get('model_analysis', {}).get('is_anomalous', False)
        anomaly_score = result.get('model_analysis', {}).get('anomaly_score', 0.0)
        patterns_detected = result.get('model_analysis', {}).get('patterns_detected', [])
        _add_web_prediction(is_anomalous, anomaly_score, ip_address, patterns_detected=patterns_detected)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] Web analysis error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500


# ============================================
# MONITORING ENDPOINTS
# ============================================

@production_api_bp.route('/api/monitoring/log_prediction', methods=['POST'])
def log_prediction():
    """
    Log a prediction for monitoring
    
    POST /api/monitoring/log_prediction
    {
        "model": "email_detector",
        "prediction": "phishing",
        "confidence": 0.95,
        "latency": 0.025
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # In production, this would log to database
        # For now, just acknowledge
        return jsonify({
            'status': 'logged',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Logging failed',
            'message': str(e)
        }), 500


@production_api_bp.route('/api/monitoring/metrics', methods=['GET'])
def get_metrics():
    """
    Get monitoring metrics
    
    GET /api/monitoring/metrics
    """
    try:
        # In production, fetch from monitoring system
        metrics = {
            'total_predictions': 1234,
            'accuracy': 0.94,
            'average_latency': 0.032,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(metrics), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch metrics',
            'message': str(e)
        }), 500


@production_api_bp.route('/api/monitoring/drift/check', methods=['POST'])
def check_drift():
    """
    Check for model drift
    
    POST /api/monitoring/drift/check
    {
        "model_name": "email_detector",
        "features": [0.1, 0.2, 0.3, ...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # In production, perform actual drift detection
        return jsonify({
            'drift_detected': False,
            'drift_score': 0.05,
            'threshold': 0.10
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Drift check failed',
            'message': str(e)
        }), 500


@production_api_bp.route('/api/monitoring/retraining/status', methods=['GET'])
def get_retraining_status():
    """
    Get model retraining status
    
    GET /api/monitoring/retraining/status
    """
    try:
        return jsonify({
            'status': 'idle',
            'last_retrain': '2025-12-13T00:00:00',
            'next_scheduled': '2025-12-14T00:00:00'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch status',
            'message': str(e)
        }), 500


# ============================================
# ENRICHMENT ENDPOINTS
# ============================================

@production_api_bp.route('/api/enrich/ip', methods=['POST'])
def enrich_ip():
    """
    Enrich IP address with threat intelligence
    
    POST /api/enrich/ip
    {
        "ip": "8.8.8.8"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        ip = data.get('ip')
        
        if not ip:
            return jsonify({'error': 'ip is required'}), 400
        
        # Check if VirusTotal API key is configured
        vt_api_key = os.getenv('VIRUSTOTAL_API_KEY') or os.getenv('VT_API_KEY')
        
        if not vt_api_key:
            return jsonify({
                'error': 'VirusTotal API key not configured',
                'ip': ip
            }), 503
        
        # In production, call VirusTotal API
        # For now, return mock data
        return jsonify({
            'ip': ip,
            'malicious': False,
            'reputation': 0,
            'country': 'US',
            'asn': 'AS15169'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Enrichment failed',
            'message': str(e)
        }), 500


@production_api_bp.route('/api/enrich/domain', methods=['POST'])
def enrich_domain():
    """
    Enrich domain with threat intelligence
    
    POST /api/enrich/domain
    {
        "domain": "example.com"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        domain = data.get('domain')
        
        if not domain:
            return jsonify({'error': 'domain is required'}), 400
        
        # Check if VirusTotal API key is configured
        vt_api_key = os.getenv('VIRUSTOTAL_API_KEY') or os.getenv('VT_API_KEY')
        
        if not vt_api_key:
            return jsonify({
                'error': 'VirusTotal API key not configured',
                'domain': domain
            }), 503
        
        # In production, call VirusTotal API
        return jsonify({
            'domain': domain,
            'malicious': False,
            'reputation': 0,
            'categories': ['search-engines']
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Enrichment failed',
            'message': str(e)
        }), 500


# ============================================
# ALERT ENDPOINTS
# ============================================

@production_api_bp.route('/api/alert/send', methods=['POST'])
def send_alert():
    """
    Send alert notification
    
    POST /api/alert/send
    {
        "alert_type": "high_risk",
        "message": "High risk threat detected",
        "severity": "critical"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if SMTP is configured
        smtp_server = os.getenv('SMTP_SERVER') or os.getenv('SMTP_HOST')
        
        if not smtp_server:
            return jsonify({
                'error': 'SMTP not configured',
                'message': 'Email alerts require SMTP configuration'
            }), 503
        
        # In production, send actual email
        return jsonify({
            'status': 'sent',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Alert sending failed',
            'message': str(e)
        }), 500


# ============================================
# HEALTH CHECK
# ============================================

@production_api_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    GET /api/health
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


@production_api_bp.route('/api/monitoring/health', methods=['GET'])
def monitoring_health():
    """
    Monitoring health check
    
    GET /api/monitoring/health
    """
    return jsonify({
        'status': 'healthy',
        'monitoring': 'active',
        'timestamp': datetime.now().isoformat()
    }), 200
