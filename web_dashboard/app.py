"""
Flask Web Dashboard for Unified Threat Detection Platform
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add src to path
sys.path.append('../src')
from src.unified_platform.platform import UnifiedThreatPlatform

app = Flask(__name__)
CORS(app)

# Global platform instance
platform = None

def initialize_platform():
    """Platform'u başlatır"""
    global platform
    
    if platform is None:
        print("🚀 Initializing platform for web dashboard...")
        
        # Sample training data
        emails = [
            {'subject': 'URGENT Account Suspended', 'body': 'Click here to verify...', 'sender': 'fake@scam.com', 'label': 1},
            {'subject': 'Meeting Tomorrow', 'body': 'Team meeting at 10 AM', 'sender': 'manager@company.com', 'label': 0}
        ]
        
        web_logs = [
            {'ip': '203.0.113.45', 'timestamp': '20/Sep/2025:14:01:01 +0200', 'method': 'POST', 
             'path': '/admin/login', 'status': '401', 'user_agent': 'Python-urllib/3.6'},
            {'ip': '192.168.1.100', 'timestamp': '20/Sep/2025:13:55:36 +0200', 'method': 'GET', 
             'path': '/', 'status': '200', 'user_agent': 'Mozilla/5.0'}
        ]
        
        platform = UnifiedThreatPlatform()
        
        try:
            emails_df = pd.DataFrame(emails)
            labels = emails_df['label'].tolist()
            logs_df = pd.DataFrame(web_logs)
            
            platform.initialize(
                email_data=(emails_df, labels),
                web_logs=logs_df
            )
            print("✅ Platform initialized successfully!")
        except Exception as e:
            print(f"❌ Platform initialization failed: {e}")
            platform = None

@app.route('/')
def dashboard():
    """Ana dashboard sayfası"""
    return render_template('dashboard.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_threat():
    """Tehdit analizi API endpoint'i"""
    try:
        # Initialize platform if not done
        if platform is None:
            initialize_platform()
            
        if platform is None:
            return jsonify({'error': 'Platform initialization failed'}), 500
        
        data = request.json
        
        # Extract input data
        email_content = data.get('email_content', '')
        email_sender = data.get('email_sender', '')
        email_subject = data.get('email_subject', '')
        ip_address = data.get('ip_address', '')
        request_count = int(data.get('request_count', 0))
        error_rate = float(data.get('error_rate', 0))
        
        # Prepare email data
        email_data = None
        if email_content:
            email_data = {
                'body': email_content,
                'sender': email_sender,
                'subject': email_subject
            }
        
        # Prepare web logs (simulated based on input)
        web_logs = None
        if ip_address and request_count > 0:
            web_logs = []
            status_code = 401 if error_rate > 50 else 200
            
            for i in range(min(request_count, 50)):  # Limit for demo
                web_logs.append({
                    'ip': ip_address,
                    'timestamp': f'20/Sep/2025:14:{i:02d}:01 +0200',
                    'method': 'POST' if error_rate > 30 else 'GET',
                    'path': '/admin/login' if error_rate > 50 else '/',
                    'status': str(status_code),
                    'user_agent': 'Python-urllib/3.6' if error_rate > 70 else 'Mozilla/5.0'
                })
        
        # Perform analysis
        results = platform.analyze_unified_threat(
            email_data=email_data,
            web_logs=web_logs,
            ip_address=ip_address
        )
        
        # Format response for frontend
        response = {
            'success': True,
            'unified_risk_score': results['unified_risk_score'],
            'threat_level': results['threat_level'],
            'timestamp': results['timestamp'],
            'email_analysis': results.get('email_analysis'),
            'web_analysis': results.get('web_analysis'),
            'correlation_analysis': results.get('correlation_analysis'),
            'recommendations': results.get('recommendations', {})
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo/<demo_type>')
def load_demo_data(demo_type):
    """Demo verilerini yükler"""
    demo_data = {
        'phishing': {
            'email_content': '''URGENT: Your PayPal account will be suspended!

Dear Customer,

We have detected suspicious activity on your account. Your PayPal account will be SUSPENDED in 24 HOURS unless you verify your identity immediately.

Click here to secure your account: http://payp4l-security.tk/verify?user=12345

You must provide your:
- Username and Password  
- Social Security Number
- Credit Card Information

Act NOW or lose access permanently!

PayPal Security Team''',
            'email_sender': 'security123@payp4l-fake.com',
            'email_subject': 'URGENT: Account Suspended - Immediate Action Required',
            'ip_address': '203.0.113.45',
            'request_count': 25,
            'error_rate': 80
        },
        'bruteforce': {
            'email_content': '''Password Reset Request
                
Hello,

Someone requested a password reset for your admin account.

If this was you, click here: http://admin-reset.suspicious-site.org/reset

If not, please ignore this email.

System Administrator''',
            'email_sender': 'admin@fake-company.org',
            'email_subject': 'Password Reset Request',
            'ip_address': '198.51.100.22',
            'request_count': 150,
            'error_rate': 95
        },
        'coordinated': {
            'email_content': '''WINNER NOTIFICATION - $50,000 PRIZE!!!
                
CONGRATULATIONS! You have won our MILLION DOLLAR lottery!

Your winning number: 7749-5582-3341

To claim your prize:
1. Click: http://lottery-winner.malicious.tk/claim
2. Enter your social security number
3. Provide bank account details

URGENT: Claim expires in 2 HOURS!

International Lottery Commission''',
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
    """Platform istatistiklerini döndürür"""
    stats = {
        'status': 'active' if platform else 'inactive',
        'models_trained': {
            'email_detector': platform.email_detector.is_trained if platform else False,
            'web_analyzer': platform.web_analyzer.is_trained if platform else False
        },
        'last_analysis': datetime.now().isoformat(),
        'total_features': {
            'email_features': len(platform.email_detector.feature_names) if platform and platform.email_detector.is_trained else 0,
            'web_features': len(platform.web_analyzer.feature_names) if platform and platform.web_analyzer.is_trained else 0
        }
    }
    
    return jsonify(stats)

if __name__ == '__main__':
    # Initialize platform on startup
    initialize_platform()
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
