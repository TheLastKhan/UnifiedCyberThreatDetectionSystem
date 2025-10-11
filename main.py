"""
Main execution script for Unified Threat Detection Platform
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add src to Python path
sys.path.append('./src')

from src.email_detector.detector import EmailPhishingDetector
from src.web_analyzer.analyzer import WebLogAnalyzer
from src.unified_platform.platform import UnifiedThreatPlatform
from config import *

def create_sample_data():
    """Demo için örnek veri oluşturur"""
    
    # Sample emails
    emails = [
        {
            'subject': 'URGENT: Account Suspended!',
            'body': '''Dear Customer,
            
Your PayPal account will be suspended in 24 hours unless you verify immediately.
Click here: http://payp4l-security.tk/verify?user=12345

Provide your:
- Username and password
- Social security number  
- Credit card details

Act NOW!''',
            'sender': 'security@payp4l-fake.com',
            'label': 1
        },
        {
            'subject': 'Team Meeting Tomorrow',
            'body': '''Hi team,
            
We have our weekly meeting tomorrow at 10 AM in Conference Room B.
Please prepare your project updates.

Best regards,
Manager''',
            'sender': 'manager@company.com',
            'label': 0
        },
        {
            'subject': 'You Won $50,000!!!',
            'body': '''CONGRATULATIONS!
            
You are our GRAND WINNER of $50,000 cash prize!
Claim immediately: http://winner-notification.scam.ml/claim

Enter your bank details to receive payment.
LIMITED TIME OFFER!''',
            'sender': 'lottery@winner-scam.org',
            'label': 1
        }
    ]
    
    # Sample web logs
    web_logs = [
        '203.0.113.45 - - [20/Sep/2025:14:01:01 +0200] "POST /admin/login HTTP/1.1" 401 1234 "-" "Python-urllib/3.6"',
        '203.0.113.45 - - [20/Sep/2025:14:01:02 +0200] "POST /admin/login HTTP/1.1" 401 1234 "-" "Python-urllib/3.6"',
        '203.0.113.45 - - [20/Sep/2025:14:01:03 +0200] "POST /admin/login HTTP/1.1" 401 1234 "-" "Python-urllib/3.6"',
        '192.168.1.100 - - [20/Sep/2025:13:55:36 +0200] "GET / HTTP/1.1" 200 2326 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"',
        '198.51.100.22 - - [20/Sep/2025:14:05:10 +0200] "GET /search?q=\' UNION SELECT * FROM users-- HTTP/1.1" 500 0 "-" "sqlmap/1.6.2"',
    ]
    
    return pd.DataFrame(emails), web_logs

def parse_web_logs(log_lines):
    """Web loglarını DataFrame'e çevirir"""
    analyzer = WebLogAnalyzer()
    parsed_logs = []
    
    for line in log_lines:
        parsed = analyzer.parse_log_line(line)
        if parsed:
            parsed_logs.append(parsed)
    
    return pd.DataFrame(parsed_logs)

def main():
    """Ana demo fonksiyonu"""
    print("🛡️ UNIFIED CYBER THREAT DETECTION PLATFORM")
    print("=" * 60)
    
    # Create directories
    os.makedirs('data/samples', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Generate sample data
    print("📊 Creating sample data...")
    emails_df, web_logs = create_sample_data()
    
    # Prepare data
    email_labels = emails_df['label'].tolist()
    logs_df = parse_web_logs(web_logs)
    
    # Initialize platform
    print("\n🚀 Initializing platform...")
    platform = UnifiedThreatPlatform()
    platform.initialize(
        email_data=(emails_df, email_labels),
        web_logs=logs_df
    )
    
    # Test unified analysis
    print("\n🔍 Running unified threat analysis...")
    
    test_email = {
        'subject': 'CRITICAL: Security Breach Detected!',
        'body': '''URGENT ACTION REQUIRED!
        
Your account has been compromised. Click here immediately:
http://security-alert.malicious-domain.tk/verify

Provide your login credentials within 1 HOUR or account will be deleted!''',
        'sender': 'security-team@fake-bank.org'
    }
    
    test_web_logs = [
        {'ip': '203.0.113.45', 'timestamp': '20/Sep/2025:14:30:01 +0200', 
         'method': 'POST', 'path': '/admin/login', 'status': '401', 
         'user_agent': 'Python-urllib/3.6'},
        {'ip': '203.0.113.45', 'timestamp': '20/Sep/2025:14:30:02 +0200',
         'method': 'POST', 'path': '/admin/login', 'status': '401',
         'user_agent': 'Python-urllib/3.6'}
    ]
    
    results = platform.analyze_unified_threat(
        email_data=test_email,
        web_logs=test_web_logs,
        ip_address='203.0.113.45'
    )
    
    # Display results
    print(f"\n🎯 ANALYSIS RESULTS:")
    print(f"📊 Unified Risk Score: {results['unified_risk_score']}/100")
    print(f"⚠️  Threat Level: {results['threat_level']}")
    
    if results['email_analysis']:
        print(f"📧 Email: {results['email_analysis']['prediction']} "
              f"({results['email_analysis']['confidence']:.1f}% confidence)")
    
    if results['web_analysis']:
        print(f"🌐 Web: {results['web_analysis']['risk_level']} risk level")
        if results['web_analysis']['attack_patterns']:
            print(f"   Attack patterns: {', '.join(results['web_analysis']['attack_patterns'])}")
    
    print(f"\n🛠️  RECOMMENDATIONS:")
    for category, recs in results['recommendations'].items():
        if recs:
            print(f"  {category.upper()}:")
            for rec in recs[:2]:  # Show first 2
                print(f"    • {rec}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/threat_analysis_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        import json
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Full report saved to: {report_file}")
    print("✅ Demo completed successfully!")

if __name__ == "__main__":
    main()