"""
Flask Web Dashboard for Unified Threat Detection Platform
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import API blueprints
from web_dashboard.api import api_bp, load_trained_models
from src.monitoring.api import monitoring_bp
from web_dashboard.production_api import production_api_bp
try:
    from web_dashboard.dashboard_endpoints import dashboard_bp
    DASHBOARD_AVAILABLE = True
except:
    DASHBOARD_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Enable template auto-reload for development
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Register API blueprints
app.register_blueprint(production_api_bp)
app.register_blueprint(api_bp)
app.register_blueprint(monitoring_bp)
if DASHBOARD_AVAILABLE:
    app.register_blueprint(dashboard_bp)

# Load models on startup
print("[Flask] Loading trained models...")
try:
    load_trained_models()
    print("[Flask] Models loaded successfully")
except Exception as e:
    print(f"[Flask] Warning: Could not load models: {e}")


# Routes
@app.route('/')
def dashboard():
    """Serve dashboard HTML"""
    return render_template('dashboard.html')


@app.route('/model-comparison')
def model_comparison():
    """Serve model comparison page"""
    return render_template('model_comparison.html')


@app.route('/api/demo/<demo_type>')
def load_demo_data(demo_type):
    """Provide demo data for testing"""
    demo_data = {
        'phishing': {
            'email_content': 'URGENT: Your PayPal account will be suspended!',
            'email_sender': 'security123@payp4l-fake.com',
            'email_subject': 'URGENT: Account Suspended - Immediate Action Required',
            'ip_address': '203.0.113.45',
            'request_count': 25,
            'error_rate': 80
        },
        'bruteforce': {
            'email_content': 'Password Reset Request',
            'email_sender': 'admin@fake-company.org',
            'email_subject': 'Password Reset Request',
            'ip_address': '198.51.100.22',
            'request_count': 150,
            'error_rate': 95
        },
        'coordinated': {
            'email_content': 'WINNER NOTIFICATION - $50,000 PRIZE!!!',
            'email_sender': 'winner-notification@lottery-scam.org',
            'email_subject': 'CONGRATULATIONS - You Won $50,000!!!',
            'ip_address': '172.16.0.88',
            'request_count': 300,
            'error_rate': 45
        }
    }
    
    if demo_type in demo_data:
        return jsonify(demo_data[demo_type])
    else:
        return jsonify({'error': 'Demo type not found'}), 404


@app.route('/api/stats')
def get_platform_stats():
    """Return platform statistics"""
    stats = {
        'status': 'active',
        'models_trained': {
            'email_detector_stacking': True,
            'email_detector_voting': True,
            'web_anomaly_detector': True
        },
        'last_analysis': datetime.now().isoformat(),
        'total_features': {
            'email_features': 5000,
            'web_features': 8
        }
    }
    return jsonify(stats)


if __name__ == '__main__':
    print("[Flask] Starting Flask application...")
    app.run(debug=False, host='0.0.0.0', port=5000)


