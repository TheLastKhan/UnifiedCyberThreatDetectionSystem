#!/usr/bin/env python
"""
Test script to verify improvements made to the project
Tests error handling, documentation, and basic functionality
"""

import sys
sys.path.insert(0, './src')

import pandas as pd
from src.email_detector.detector import EmailPhishingDetector
from src.web_analyzer.analyzer import WebLogAnalyzer
from src.unified_platform.platform import UnifiedThreatPlatform

def test_email_detector():
    """Test email detector with improved error handling"""
    print("\n" + "="*60)
    print("📧 Testing Email Phishing Detector")
    print("="*60)
    
    try:
        # Create detector
        detector = EmailPhishingDetector()
        print("✅ EmailPhishingDetector initialized")
        
        # Prepare training data
        emails = pd.DataFrame([
            {'subject': 'URGENT: Account Suspended!', 'body': 'Click here to verify...', 'sender': 'fake@scam.com', 'label': 1},
            {'subject': 'Team Meeting Tomorrow', 'body': 'We have our weekly meeting at 10 AM.', 'sender': 'manager@company.com', 'label': 0},
            {'subject': 'You Won Prize!', 'body': 'Congratulations! You won $1,000,000!!!', 'sender': 'lottery@fake.org', 'label': 1},
            {'subject': 'Project Update', 'body': 'Please find the latest project update attached.', 'sender': 'colleague@company.com', 'label': 0}
        ])
        labels = emails['label'].tolist()
        
        # Train model
        detector.train(emails, labels)
        print("✅ Email detector trained successfully")
        
        # Test prediction
        test_email = "URGENT! Your PayPal account will be suspended! Click here immediately!"
        result = detector.predict_with_explanation(test_email, "security@fake.com", "URGENT")
        
        print(f"\n📊 Test Prediction:")
        print(f"   Prediction: {result['prediction']}")
        print(f"   Confidence: {result['confidence']:.1f}%")
        print(f"   Risk Factors: {len(result['risk_factors'])} identified")
        print("✅ Email detector prediction successful")
        
        # Assert successful completion
        assert detector.is_trained
        assert 'prediction' in result
        
    except Exception as e:
        print(f"❌ Email detector test failed: {e}")
        raise


def test_web_analyzer():
    """Test web analyzer with improved error handling"""
    print("\n" + "="*60)
    print("🌐 Testing Web Log Analyzer")
    print("="*60)
    
    try:
        # Create analyzer
        analyzer = WebLogAnalyzer()
        print("✅ WebLogAnalyzer initialized")
        
        # Prepare training data
        logs = pd.DataFrame([
            {'ip': '192.168.1.100', 'timestamp': '20/Sep/2025:14:00:00 +0200', 'method': 'GET', 
             'path': '/', 'status': '200', 'user_agent': 'Mozilla/5.0', 'referer': '-', 'size': '1234', 'protocol': 'HTTP/1.1'},
            {'ip': '203.0.113.45', 'timestamp': '20/Sep/2025:14:01:01 +0200', 'method': 'POST', 
             'path': '/admin/login', 'status': '401', 'user_agent': 'Python-urllib/3.6', 'referer': '-', 'size': '567', 'protocol': 'HTTP/1.1'},
            {'ip': '192.168.1.200', 'timestamp': '20/Sep/2025:14:02:00 +0200', 'method': 'GET', 
             'path': '/dashboard', 'status': '200', 'user_agent': 'Mozilla/5.0', 'referer': '-', 'size': '2345', 'protocol': 'HTTP/1.1'},
        ])
        
        # Train model
        features_df, ip_list = analyzer.train_anomaly_detector(logs)
        print(f"✅ Web analyzer trained on {len(ip_list)} IPs")
        
        # Test analysis
        test_logs = [
            {'ip': '203.0.113.45', 'timestamp': '20/Sep/2025:14:03:00 +0200', 'method': 'POST', 
             'path': '/admin/login', 'status': '401', 'user_agent': 'sqlmap', 'referer': '-', 'size': '789', 'protocol': 'HTTP/1.1'}
        ]
        
        result = analyzer.analyze_ip_with_explanation(test_logs, '203.0.113.45')
        
        print(f"\n📊 Test Analysis:")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Anomaly Score: {result['anomaly_score']:.3f}")
        print(f"   Attack Patterns: {len(result['attack_patterns'])} detected")
        print("✅ Web analyzer analysis successful")
        
        # Assert successful completion
        assert analyzer.is_trained
        assert result is not None
        
    except Exception as e:
        print(f"❌ Web analyzer test failed: {e}")
        raise


def test_unified_platform():
    """Test unified platform"""
    print("\n" + "="*60)
    print("🎯 Testing Unified Threat Detection Platform")
    print("="*60)
    
    try:
        platform = UnifiedThreatPlatform()
        print("✅ UnifiedThreatPlatform initialized")
        
        # Prepare data
        emails = pd.DataFrame([
            {'subject': 'URGENT: Account Suspended!', 'body': 'Click here...', 'sender': 'fake@scam.com', 'label': 1},
            {'subject': 'Meeting', 'body': 'Team meeting at 10 AM.', 'sender': 'manager@company.com', 'label': 0},
        ])
        
        logs = pd.DataFrame([
            {'ip': '192.168.1.100', 'timestamp': '20/Sep/2025:14:00:00 +0200', 'method': 'GET', 
             'path': '/', 'status': '200', 'user_agent': 'Mozilla/5.0', 'referer': '-', 'size': '1234', 'protocol': 'HTTP/1.1'},
            {'ip': '203.0.113.45', 'timestamp': '20/Sep/2025:14:01:01 +0200', 'method': 'POST', 
             'path': '/admin', 'status': '401', 'user_agent': 'Bot', 'referer': '-', 'size': '567', 'protocol': 'HTTP/1.1'},
        ])
        
        # Initialize
        platform.initialize(
            email_data=(emails, [1, 0]),
            web_logs=logs
        )
        print("✅ Platform initialized successfully")
        
        # Test unified analysis
        result = platform.analyze_unified_threat(
            email_data={'body': 'URGENT! Click here!', 'sender': 'scam@fake.com', 'subject': 'URGENT'},
            web_logs=[{'ip': '203.0.113.45', 'timestamp': '20/Sep/2025:14:02:00 +0200', 'method': 'POST', 
                      'path': '/admin', 'status': '401', 'user_agent': 'Bot', 'referer': '-', 'size': '100', 'protocol': 'HTTP/1.1'}],
            ip_address='203.0.113.45'
        )
        
        print(f"\n📊 Unified Analysis Results:")
        print(f"   Risk Score: {result['unified_risk_score']:.1f}/100")
        print(f"   Threat Level: {result['threat_level']}")
        print(f"   Recommendations: {len(result['recommendations'])} provided")
        print("✅ Unified platform analysis successful")
        
        # Assert successful completion
        assert platform.email_detector is not None
        assert platform.web_analyzer is not None
        assert 'unified_risk_score' in result
        
    except Exception as e:
        print(f"❌ Unified platform test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING IMPROVEMENTS - FAZ 1")
    print("="*60)
    
    results = {
        'Email Detector': test_email_detector(),
        'Web Analyzer': test_web_analyzer(),
        'Unified Platform': test_unified_platform()
    }
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All improvements working correctly!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
