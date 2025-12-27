"""
Dashboard Endpoints - Stats and Alerts
Simple endpoints for dashboard without ensemble complexity
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import traceback

# Import database
try:
    from web_dashboard.database import get_email_predictions, get_prediction_counts, SessionLocal, EmailPrediction
    DATABASE_AVAILABLE = True
except:
    DATABASE_AVAILABLE = False

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({'email_detection': {'total_predictions': 0, 'phishing_detected': 0, 'accuracy': 89.6}, 'web_analysis': {'total_predictions': 0, 'anomalies_detected': 0}}), 200
        
        counts = get_prediction_counts()
        db = SessionLocal()
        phishing = db.query(EmailPrediction).filter(EmailPrediction.prediction == 'phishing').count()
        db.close()
        
        return jsonify({
            'email_detection': {'total_predictions': counts.get('email', 0), 'phishing_detected': phishing, 'accuracy': 89.6, 'avg_confidence': 0.85},
            'web_analysis': {'total_predictions': counts.get('web', 0), 'anomalies_detected': 0, 'avg_score': 0.0}
        }), 200
    except Exception as e:
        print(f"[ERROR] Stats: {e}")
        traceback.print_exc()
        return jsonify({'email_detection': {'total_predictions': 0, 'phishing_detected': 0}, 'web_analysis': {'total_predictions': 0, 'anomalies_detected': 0}}), 200


@dashboard_bp.route('/api/dashboard/alerts', methods=['GET'])
def get_alerts():
    """Get recent alerts"""
    try:
        limit = request.args.get('limit', 50, type=int)
        if not DATABASE_AVAILABLE:
            return jsonify({'alerts': [], 'total': 0}), 200
        
        preds = get_email_predictions(limit=limit)
        alerts = []
        for p in preds:
            try:
                alert = {
                    'id': p.get('id'),
                    'title': f"Email {p.get('prediction', 'UNKNOWN').upper()} Detected",
                    'description': f"{p.get('email_subject', 'No subject')} from {p.get('email_sender', 'Unknown')}",
                    'severity': 'high' if p.get('risk_level') in ['critical', 'high'] else ('medium' if p.get('risk_level') == 'medium' else 'low'),
                    'severity_badge': p.get('risk_level', 'UNKNOWN').upper(),
                    'time_ago': 'Recently',
                    'confidence': int(p.get('confidence', 0) * 100),
                    'prediction': p.get('prediction'),
                    'risk_level': p.get('risk_level')
                }
                alerts.append(alert)
            except:
                pass
        
        return jsonify({'alerts': alerts, 'total': len(alerts)}), 200
    except Exception as e:
        print(f"[ERROR] Alerts: {e}")
        traceback.print_exc()
        return jsonify({'alerts': [], 'total': 0}), 200
