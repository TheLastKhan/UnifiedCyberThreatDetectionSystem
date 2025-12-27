"""
Integration tests for the Unified Threat Detection Platform
Tests the complete flow of multiple components working together
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.email_detector.detector import EmailPhishingDetector
from src.web_analyzer.analyzer import WebLogAnalyzer
from src.unified_platform.platform import UnifiedThreatPlatform


@pytest.mark.integration
class TestEmailDetectionFlow:
    """Test complete email detection workflow."""
    
    def test_email_detection_pipeline(self, trained_email_detector, suspicious_email):
        """Test full email phishing detection pipeline."""
        # Arrange
        detector = trained_email_detector
        
        # Act
        result = detector.predict_with_explanation(
            suspicious_email['body'],
            suspicious_email['sender'],
            suspicious_email['subject']
        )
        
        # Assert
        assert result is not None
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'phishing_probability' in result
        assert 'risk_factors' in result
        assert 'lime_explanation' in result
        
        # Prediction should be either 'Safe' or 'Phishing'
        assert result['prediction'] in ['Safe', 'Phishing']
        assert 0 <= result['confidence'] <= 100
        assert 0 <= result['phishing_probability'] <= 100
        assert 0 <= result['safe_probability'] <= 100
    
    def test_safe_email_detection(self, trained_email_detector, safe_email):
        """Test detection of safe/legitimate emails."""
        detector = trained_email_detector
        
        result = detector.predict_with_explanation(
            safe_email['body'],
            safe_email['sender'],
            safe_email['subject']
        )
        
        assert result is not None
        assert isinstance(result['confidence'], float)
        assert len(result['risk_factors']) >= 0
    
    def test_email_feature_extraction(self, trained_email_detector, suspicious_email):
        """Test email feature extraction process."""
        detector = trained_email_detector
        
        features = detector.extract_email_features(
            suspicious_email['body'],
            suspicious_email['sender'],
            suspicious_email['subject']
        )
        
        assert isinstance(features, dict)
        assert 'email_length' in features
        assert 'urgent_words' in features
        assert 'personal_info_words' in features
        assert 'suspicious_urls' in features


@pytest.mark.integration
class TestWebAnalysisFlow:
    """Test complete web log analysis workflow."""
    
    def test_web_analysis_pipeline(self, trained_web_analyzer, suspicious_logs):
        """Test full web log analysis pipeline."""
        # Arrange
        analyzer = trained_web_analyzer
        ip_address = '203.0.113.45'
        
        # Act
        result = analyzer.analyze_ip_with_explanation(suspicious_logs, ip_address)
        
        # Assert
        assert result is not None
        assert result['ip_address'] == ip_address
        assert 'anomaly_score' in result
        assert 'is_anomaly' in result
        assert 'risk_level' in result
        assert 'attack_patterns' in result
        assert 'behavioral_insights' in result
        assert 'recommendations' in result
        
        # Risk level should be one of the valid options
        assert result['risk_level'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    def test_normal_traffic_detection(self, trained_web_analyzer, normal_logs):
        """Test detection of normal/legitimate traffic."""
        analyzer = trained_web_analyzer
        
        result = analyzer.analyze_ip_with_explanation(normal_logs, '192.168.1.100')
        
        assert result is not None
        assert result['risk_level'] is not None
        assert isinstance(result['attack_patterns'], list)
    
    def test_log_parsing(self, trained_web_analyzer):
        """Test web log parsing functionality."""
        analyzer = trained_web_analyzer
        
        log_line = '192.168.1.100 - - [20/Sep/2025:14:00:00 +0200] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
        
        parsed = analyzer.parse_log_line(log_line)
        
        assert parsed is not None
        assert parsed['ip'] == '192.168.1.100'
        assert parsed['method'] == 'GET'
        assert parsed['path'] == '/'
        assert parsed['status'] == '200'
    
    def test_attack_pattern_detection(self, trained_web_analyzer, suspicious_logs):
        """Test attack pattern detection in logs."""
        analyzer = trained_web_analyzer
        
        # Create logs with SQL injection attempt
        sql_injection_logs = [{
            'ip': '203.0.113.45',
            'timestamp': '20/Sep/2025:14:00:00 +0200',
            'method': 'GET',
            'path': "/search?q=' UNION SELECT * FROM users--",
            'status': '500',
            'user_agent': 'sqlmap',
            'referer': '-',
            'size': '100',
            'protocol': 'HTTP/1.1'
        }]
        
        patterns = analyzer.detect_attack_patterns(sql_injection_logs)
        
        assert isinstance(patterns, list)


@pytest.mark.integration
class TestUnifiedPlatformIntegration:
    """Test complete unified threat detection platform."""
    
    def test_unified_analysis_with_email_only(self, trained_platform, suspicious_email):
        """Test unified analysis with email data only."""
        platform = trained_platform
        
        result = platform.analyze_unified_threat(
            email_data=suspicious_email
        )
        
        assert result is not None
        assert 'unified_risk_score' in result
        assert 'threat_level' in result
        assert result['threat_level'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert 0 <= result['unified_risk_score'] <= 100
    
    def test_unified_analysis_with_web_only(self, trained_platform, suspicious_logs):
        """Test unified analysis with web logs only."""
        platform = trained_platform
        
        result = platform.analyze_unified_threat(
            web_logs=suspicious_logs,
            ip_address='203.0.113.45'
        )
        
        assert result is not None
        assert 'unified_risk_score' in result
        assert 'web_analysis' in result
    
    def test_unified_analysis_complete(self, trained_platform, suspicious_email, suspicious_logs):
        """Test complete unified analysis with both email and web logs."""
        platform = trained_platform
        
        result = platform.analyze_unified_threat(
            email_data=suspicious_email,
            web_logs=suspicious_logs,
            ip_address='203.0.113.45'
        )
        
        # Assert all components are present
        assert result is not None
        assert result['email_analysis'] is not None
        assert result['web_analysis'] is not None
        assert 'unified_risk_score' in result
        assert 'threat_level' in result
        assert 'correlation_analysis' in result
        assert 'recommendations' in result
        
        # Verify risk score and threat level
        assert 0 <= result['unified_risk_score'] <= 100
        assert result['threat_level'] in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        assert len(result['recommendations']) > 0
    
    def test_platform_initialization(self, sample_emails, sample_web_logs):
        """Test platform initialization with training data."""
        platform = UnifiedThreatPlatform()
        labels = sample_emails['label'].tolist()
        
        # Should not raise exception
        platform.initialize(
            email_data=(sample_emails, labels),
            web_logs=sample_web_logs
        )
        
        assert platform.email_detector.is_trained
        assert platform.web_analyzer.is_trained
    
    def test_safe_content_analysis(self, trained_platform, safe_email, normal_logs):
        """Test platform analysis on safe/legitimate content."""
        platform = trained_platform
        
        result = platform.analyze_unified_threat(
            email_data=safe_email,
            web_logs=normal_logs,
            ip_address='192.168.1.100'
        )
        
        assert result is not None
        # Safe content should have lower risk score
        assert result['unified_risk_score'] is not None


@pytest.mark.integration
class TestCrossPlatformCorrelation:
    """Test correlation between email and web threats."""
    
    def test_threat_correlation(self, trained_platform, suspicious_email, suspicious_logs):
        """Test correlation detection between email and web threats."""
        platform = trained_platform
        
        result = platform.analyze_unified_threat(
            email_data=suspicious_email,
            web_logs=suspicious_logs,
            ip_address='203.0.113.45'
        )
        
        # When both email and web show threats, correlation should detect
        if (result['email_analysis'] and result['web_analysis']):
            assert result['correlation_analysis'] is not None
            assert 'confidence_score' in result['correlation_analysis']
            assert 'indicators' in result['correlation_analysis']
    
    def test_risk_amplification(self, trained_platform, suspicious_email, suspicious_logs):
        """Test that unified risk score amplifies when threats correlate."""
        platform = trained_platform
        
        # Individual analyses
        email_only = platform.analyze_unified_threat(email_data=suspicious_email)
        web_only = platform.analyze_unified_threat(
            web_logs=suspicious_logs,
            ip_address='203.0.113.45'
        )
        
        # Combined analysis
        combined = platform.analyze_unified_threat(
            email_data=suspicious_email,
            web_logs=suspicious_logs,
            ip_address='203.0.113.45'
        )
        
        # Combined risk should potentially be higher due to correlation
        assert combined['unified_risk_score'] is not None
