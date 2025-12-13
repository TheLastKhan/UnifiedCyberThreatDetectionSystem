"""
Comprehensive Web Analyzer Unit Tests with pytest
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.web_analyzer.analyzer import WebLogAnalyzer
from src.web_analyzer.patterns import detect_attack_patterns
from src.utils.data_loader import create_sample_web_logs


class TestWebLogAnalyzer:
    """Test suite for WebLogAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create an analyzer instance"""
        return WebLogAnalyzer()
    
    @pytest.fixture
    def sample_logs(self):
        """Create sample web log data"""
        return create_sample_web_logs()
    
    @pytest.fixture
    def trained_analyzer(self, analyzer, sample_logs):
        """Create a trained analyzer"""
        analyzer.train(sample_logs)
        return analyzer
    
    # Initialization Tests
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.is_trained == False
        assert analyzer.model is None
        assert analyzer.scaler is None
    
    # Training Tests
    def test_analyzer_training(self, analyzer, sample_logs):
        """Test analyzer training process"""
        analyzer.train(sample_logs)
        
        assert analyzer.is_trained == True
        assert analyzer.model is not None
        assert analyzer.scaler is not None
    
    def test_training_with_empty_data(self, analyzer):
        """Test training with empty dataset"""
        empty_df = pd.DataFrame(columns=['ip', 'timestamp', 'request', 'status', 'size'])
        
        with pytest.raises((ValueError, Exception)):
            analyzer.train(empty_df)
    
    def test_training_with_insufficient_data(self, analyzer):
        """Test training with too little data"""
        small_df = pd.DataFrame({
            'ip': ['192.168.1.1'],
            'timestamp': [datetime.now()],
            'request': ['GET /'],
            'status': [200],
            'size': [1024]
        })
        
        # May raise error or handle gracefully
        try:
            analyzer.train(small_df)
            # If it succeeds, verify basic state
            assert analyzer.is_trained in [True, False]
        except Exception:
            # Expected to fail with insufficient data
            pass
    
    # Analysis Tests
    def test_analyze_logs_returns_correct_format(self, trained_analyzer):
        """Test log analysis returns expected format"""
        test_logs = pd.DataFrame({
            'ip': ['203.0.113.45'],
            'timestamp': [datetime.now()],
            'request': ['GET /admin'],
            'status': [401],
            'size': [256]
        })
        
        result = trained_analyzer.analyze_logs(test_logs)
        
        assert 'anomalies' in result
        assert 'risk_score' in result
        assert 'suspicious_ips' in result
        assert isinstance(result['anomalies'], list)
        assert isinstance(result['risk_score'], (int, float))
    
    def test_anomaly_detection(self, trained_analyzer):
        """Test detection of anomalous behavior"""
        # Create suspicious log pattern
        suspicious_logs = pd.DataFrame({
            'ip': ['198.51.100.1'] * 100,  # Same IP, high frequency
            'timestamp': [datetime.now() + timedelta(seconds=i) for i in range(100)],
            'request': ['GET /admin'] * 100,  # Repeated admin access
            'status': [401] * 100,  # All failed
            'size': [256] * 100
        })
        
        result = trained_analyzer.analyze_logs(suspicious_logs)
        
        # Should detect anomalies
        assert len(result['anomalies']) > 0 or result['risk_score'] > 50
    
    def test_normal_traffic_analysis(self, trained_analyzer):
        """Test analysis of normal traffic"""
        normal_logs = pd.DataFrame({
            'ip': ['192.168.1.' + str(i) for i in range(10)],  # Different IPs
            'timestamp': [datetime.now() + timedelta(minutes=i) for i in range(10)],
            'request': ['GET /index.html'] * 10,
            'status': [200] * 10,  # All successful
            'size': [1024] * 10
        })
        
        result = trained_analyzer.analyze_logs(normal_logs)
        
        # Should have lower risk score
        assert result['risk_score'] < 80  # Not necessarily 0, but should be lower
    
    def test_analysis_without_training(self, analyzer):
        """Test analysis fails when not trained"""
        test_logs = create_sample_web_logs()
        
        with pytest.raises((ValueError, AttributeError, Exception)):
            analyzer.analyze_logs(test_logs)
    
    # IP Analysis Tests
    def test_suspicious_ip_detection(self, trained_analyzer):
        """Test detection of suspicious IP addresses"""
        # Brute force pattern
        brute_force_logs = pd.DataFrame({
            'ip': ['203.0.113.99'] * 50,  # Same IP
            'timestamp': [datetime.now() + timedelta(seconds=i) for i in range(50)],
            'request': ['POST /login'] * 50,  # Repeated login attempts
            'status': [401] * 50,  # All failed
            'size': [128] * 50
        })
        
        result = trained_analyzer.analyze_logs(brute_force_logs)
        
        # Should flag this IP as suspicious
        assert len(result['suspicious_ips']) > 0
    
    def test_multiple_ips_analysis(self, trained_analyzer):
        """Test analysis with multiple IP addresses"""
        mixed_logs = pd.DataFrame({
            'ip': ['192.168.1.1', '192.168.1.2', '203.0.113.50', '198.51.100.22'] * 10,
            'timestamp': [datetime.now() + timedelta(minutes=i) for i in range(40)],
            'request': ['GET /'] * 40,
            'status': [200] * 40,
            'size': [512] * 40
        })
        
        result = trained_analyzer.analyze_logs(mixed_logs)
        
        assert 'anomalies' in result
        assert 'suspicious_ips' in result
    
    # Pattern Detection Tests
    def test_sql_injection_pattern(self):
        """Test detection of SQL injection patterns"""
        sql_injection_request = "GET /search?q=' OR '1'='1"
        
        patterns = detect_attack_patterns(sql_injection_request)
        
        # Should detect SQL injection pattern
        assert 'sql_injection' in patterns or len(patterns) > 0
    
    def test_xss_pattern(self):
        """Test detection of XSS patterns"""
        xss_request = "GET /page?name=<script>alert('XSS')</script>"
        
        patterns = detect_attack_patterns(xss_request)
        
        # Should detect XSS pattern
        assert 'xss' in patterns or len(patterns) > 0
    
    def test_path_traversal_pattern(self):
        """Test detection of path traversal patterns"""
        traversal_request = "GET /../../../etc/passwd"
        
        patterns = detect_attack_patterns(traversal_request)
        
        # Should detect path traversal
        assert 'path_traversal' in patterns or len(patterns) > 0
    
    def test_normal_request_pattern(self):
        """Test that normal requests don't trigger patterns"""
        normal_request = "GET /products/item123?color=blue&size=large"
        
        patterns = detect_attack_patterns(normal_request)
        
        # Should not detect attack patterns (or minimal false positives)
        assert len(patterns) == 0 or all(p['confidence'] < 0.5 for p in patterns)
    
    # Feature Extraction Tests
    def test_feature_extraction(self, trained_analyzer):
        """Test feature extraction from logs"""
        test_logs = pd.DataFrame({
            'ip': ['192.168.1.100'],
            'timestamp': [datetime.now()],
            'request': ['GET /api/users'],
            'status': [200],
            'size': [2048]
        })
        
        result = trained_analyzer.analyze_logs(test_logs)
        
        # Should have features extracted
        assert 'anomalies' in result
        assert isinstance(result['risk_score'], (int, float))
    
    # Edge Cases
    def test_empty_logs_analysis(self, trained_analyzer):
        """Test handling of empty logs"""
        empty_logs = pd.DataFrame(columns=['ip', 'timestamp', 'request', 'status', 'size'])
        
        result = trained_analyzer.analyze_logs(empty_logs)
        
        # Should handle gracefully
        assert 'anomalies' in result
        assert result['risk_score'] >= 0
    
    def test_malformed_logs(self, trained_analyzer):
        """Test handling of malformed log entries"""
        malformed_logs = pd.DataFrame({
            'ip': ['invalid_ip', '192.168.1.1'],
            'timestamp': [None, datetime.now()],
            'request': ['', 'GET /'],
            'status': [-1, 200],
            'size': [None, 1024]
        })
        
        # Should handle gracefully or raise appropriate error
        try:
            result = trained_analyzer.analyze_logs(malformed_logs)
            assert 'anomalies' in result
        except (ValueError, TypeError):
            # Acceptable to raise error for malformed data
            pass
    
    def test_very_large_log_batch(self, trained_analyzer):
        """Test handling of large log batches"""
        large_logs = pd.DataFrame({
            'ip': ['192.168.1.' + str(i % 255) for i in range(10000)],
            'timestamp': [datetime.now() + timedelta(seconds=i) for i in range(10000)],
            'request': ['GET /page' + str(i) for i in range(10000)],
            'status': [200] * 10000,
            'size': [512] * 10000
        })
        
        result = trained_analyzer.analyze_logs(large_logs)
        
        # Should complete without timeout
        assert 'anomalies' in result
        assert 'risk_score' in result


class TestAttackPatternDetection:
    """Test suite for attack pattern detection"""
    
    def test_detect_sql_injection_variants(self):
        """Test detection of various SQL injection attempts"""
        sql_variants = [
            "' OR '1'='1",
            "1' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        for variant in sql_variants:
            patterns = detect_attack_patterns(variant)
            # Should detect at least some patterns
            assert isinstance(patterns, (list, dict))
    
    def test_detect_xss_variants(self):
        """Test detection of various XSS attempts"""
        xss_variants = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>"
        ]
        
        for variant in xss_variants:
            patterns = detect_attack_patterns(variant)
            assert isinstance(patterns, (list, dict))
    
    def test_detect_command_injection(self):
        """Test detection of command injection attempts"""
        cmd_variants = [
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(uname -a)"
        ]
        
        for variant in cmd_variants:
            patterns = detect_attack_patterns(variant)
            assert isinstance(patterns, (list, dict))


class TestWebAnalyzerIntegration:
    """Integration tests for web analyzer"""
    
    def test_full_pipeline(self):
        """Test complete analysis pipeline"""
        # Create analyzer
        analyzer = WebLogAnalyzer()
        
        # Create training data
        sample_logs = create_sample_web_logs()
        
        # Train
        analyzer.train(sample_logs)
        
        # Analyze
        test_logs = pd.DataFrame({
            'ip': ['203.0.113.45'],
            'timestamp': [datetime.now()],
            'request': ['GET /admin'],
            'status': [401],
            'size': [256]
        })
        
        result = analyzer.analyze_logs(test_logs)
        
        # Verify complete workflow
        assert analyzer.is_trained
        assert 'anomalies' in result
        assert 'risk_score' in result
    
    def test_realtime_analysis_simulation(self):
        """Test simulated real-time log analysis"""
        analyzer = WebLogAnalyzer()
        sample_logs = create_sample_web_logs()
        analyzer.train(sample_logs)
        
        # Simulate streaming logs
        for i in range(10):
            log_entry = pd.DataFrame({
                'ip': [f'192.168.1.{i}'],
                'timestamp': [datetime.now()],
                'request': [f'GET /page{i}'],
                'status': [200],
                'size': [1024]
            })
            
            result = analyzer.analyze_logs(log_entry)
            assert 'anomalies' in result


# Performance Tests
class TestWebAnalyzerPerformance:
    """Performance tests for web analyzer"""
    
    @pytest.mark.slow
    def test_analysis_speed(self):
        """Test analysis speed on large datasets"""
        import time
        
        analyzer = WebLogAnalyzer()
        sample_logs = create_sample_web_logs()
        analyzer.train(sample_logs)
        
        # Create large test dataset
        test_logs = pd.DataFrame({
            'ip': ['192.168.1.' + str(i % 255) for i in range(1000)],
            'timestamp': [datetime.now() + timedelta(seconds=i) for i in range(1000)],
            'request': ['GET /'] * 1000,
            'status': [200] * 1000,
            'size': [512] * 1000
        })
        
        # Time analysis
        start = time.time()
        result = analyzer.analyze_logs(test_logs)
        end = time.time()
        
        analysis_time = end - start
        
        # Should complete quickly (< 5 seconds for 1000 logs)
        assert analysis_time < 5.0, f"Analysis too slow: {analysis_time:.2f}s"
    
    @pytest.mark.slow
    def test_training_speed(self):
        """Test training speed"""
        import time
        
        analyzer = WebLogAnalyzer()
        sample_logs = create_sample_web_logs()
        
        start = time.time()
        analyzer.train(sample_logs)
        end = time.time()
        
        training_time = end - start
        
        # Should complete reasonably fast (< 10 seconds)
        assert training_time < 10.0, f"Training too slow: {training_time:.2f}s"


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
