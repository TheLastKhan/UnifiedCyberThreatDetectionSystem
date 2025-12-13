"""
Comprehensive API Integration Tests with pytest
Tests for REST API endpoints and monitoring system
"""

import pytest
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Flask test client
from web_dashboard.app import app as flask_app


@pytest.fixture
def client():
    """Create Flask test client"""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


class TestAPIHealth:
    """Test suite for API health endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] in ['healthy', 'ok', 'active']
    
    def test_monitoring_health(self, client):
        """Test monitoring health endpoint"""
        response = client.get('/api/monitoring/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data


class TestEmailAnalysisAPI:
    """Test suite for email analysis endpoints"""
    
    def test_email_analyze_endpoint(self, client):
        """Test email analysis endpoint"""
        payload = {
            'email_content': 'URGENT! Click here to verify your account',
            'email_sender': 'phishing@fake.com',
            'email_subject': 'URGENT: Verify Account'
        }
        
        response = client.post(
            '/api/email/analyze',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'prediction' in data
        assert 'confidence' in data
        assert data['prediction'] in ['Safe', 'Phishing', 'safe', 'phishing']
    
    def test_email_analyze_missing_fields(self, client):
        """Test email analysis with missing fields"""
        payload = {
            'email_content': 'Test email'
            # Missing sender and subject
        }
        
        response = client.post(
            '/api/email/analyze',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return 400 or handle gracefully
        assert response.status_code in [200, 400]
    
    def test_email_analyze_empty_content(self, client):
        """Test email analysis with empty content"""
        payload = {
            'email_content': '',
            'email_sender': 'test@test.com',
            'email_subject': 'Test'
        }
        
        response = client.post(
            '/api/email/analyze',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]


class TestWebAnalysisAPI:
    """Test suite for web analysis endpoints"""
    
    def test_web_analyze_endpoint(self, client):
        """Test web log analysis endpoint"""
        payload = {
            'ip_address': '203.0.113.45',
            'request_count': 150,
            'error_rate': 95,
            'avg_response_time': 50
        }
        
        response = client.post(
            '/api/web/analyze',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'risk_score' in data or 'anomalies' in data
    
    def test_web_analyze_invalid_ip(self, client):
        """Test web analysis with invalid IP"""
        payload = {
            'ip_address': 'invalid_ip',
            'request_count': 10,
            'error_rate': 5
        }
        
        response = client.post(
            '/api/web/analyze',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return error or handle gracefully
        assert response.status_code in [200, 400]


class TestMonitoringAPI:
    """Test suite for monitoring endpoints"""
    
    def test_log_prediction_endpoint(self, client):
        """Test prediction logging endpoint"""
        payload = {
            'model_name': 'random_forest',
            'prediction': 1,
            'true_label': 1,
            'confidence': 0.95,
            'latency': 0.025
        }
        
        response = client.post(
            '/api/monitoring/log_prediction',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_get_metrics_endpoint(self, client):
        """Test metrics retrieval endpoint"""
        response = client.get('/api/monitoring/metrics/random_forest')
        
        assert response.status_code in [200, 404]  # 404 if no data yet
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'model_name' in data or 'metrics' in data
    
    def test_compare_models_endpoint(self, client):
        """Test model comparison endpoint"""
        response = client.get('/api/monitoring/metrics/compare')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'status' in data
        assert 'comparison' in data
    
    def test_drift_detection_endpoint(self, client):
        """Test drift detection endpoint"""
        payload = {
            'model_name': 'random_forest',
            'features': [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        response = client.post(
            '/api/monitoring/drift/check',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # May return 200 or 400 depending on implementation
        assert response.status_code in [200, 400]
    
    def test_retraining_status_endpoint(self, client):
        """Test retraining status endpoint"""
        response = client.get('/api/monitoring/retraining/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'status' in data


class TestEnrichmentAPI:
    """Test suite for enrichment endpoints"""
    
    @pytest.mark.skipif(
        os.getenv('VIRUSTOTAL_API_KEY') is None,
        reason="VirusTotal API key not configured"
    )
    def test_enrich_ip_endpoint(self, client):
        """Test IP enrichment endpoint"""
        payload = {
            'ip': '8.8.8.8'
        }
        
        response = client.post(
            '/api/enrich/ip',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 429]  # 429 if rate limited
        
        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'ip' in data or 'data' in data
    
    @pytest.mark.skipif(
        os.getenv('VIRUSTOTAL_API_KEY') is None,
        reason="VirusTotal API key not configured"
    )
    def test_enrich_domain_endpoint(self, client):
        """Test domain enrichment endpoint"""
        payload = {
            'domain': 'google.com'
        }
        
        response = client.post(
            '/api/enrich/domain',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 429]


class TestAlertAPI:
    """Test suite for alert endpoints"""
    
    @pytest.mark.skipif(
        os.getenv('SMTP_USERNAME') is None,
        reason="SMTP not configured"
    )
    def test_send_alert_endpoint(self, client):
        """Test alert sending endpoint"""
        payload = {
            'subject': 'Test Alert',
            'body': 'This is a test alert',
            'recipients': ['test@example.com']
        }
        
        response = client.post(
            '/api/alert/send',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # May return 200 or error depending on SMTP config
        assert response.status_code in [200, 400, 500]


class TestAPIErrorHandling:
    """Test suite for API error handling"""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            '/api/email/analyze',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]
    
    def test_missing_content_type(self, client):
        """Test handling of missing content type"""
        response = client.post(
            '/api/email/analyze',
            data=json.dumps({'test': 'data'})
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 415]
    
    def test_nonexistent_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get('/api/nonexistent')
        
        assert response.status_code == 404
    
    def test_wrong_method(self, client):
        """Test using wrong HTTP method"""
        response = client.get('/api/email/analyze')  # Should be POST
        
        assert response.status_code in [405, 400]  # Method not allowed


class TestAPIIntegration:
    """Integration tests for complete workflows"""
    
    def test_email_to_monitoring_flow(self, client):
        """Test complete email analysis + monitoring flow"""
        # 1. Analyze email
        email_payload = {
            'email_content': 'Suspicious phishing email',
            'email_sender': 'scam@fake.com',
            'email_subject': 'URGENT'
        }
        
        email_response = client.post(
            '/api/email/analyze',
            data=json.dumps(email_payload),
            content_type='application/json'
        )
        
        assert email_response.status_code == 200
        
        # 2. Log prediction to monitoring
        prediction_payload = {
            'model_name': 'random_forest',
            'prediction': 1,
            'true_label': 1,
            'confidence': 0.95,
            'latency': 0.03
        }
        
        monitoring_response = client.post(
            '/api/monitoring/log_prediction',
            data=json.dumps(prediction_payload),
            content_type='application/json'
        )
        
        assert monitoring_response.status_code == 200
        
        # 3. Check metrics
        metrics_response = client.get('/api/monitoring/metrics/random_forest')
        
        # May be 200 or 404 depending on implementation
        assert metrics_response.status_code in [200, 404]
    
    def test_web_to_enrichment_flow(self, client):
        """Test web analysis + enrichment flow"""
        # 1. Analyze web traffic
        web_payload = {
            'ip_address': '203.0.113.45',
            'request_count': 150,
            'error_rate': 95
        }
        
        web_response = client.post(
            '/api/web/analyze',
            data=json.dumps(web_payload),
            content_type='application/json'
        )
        
        assert web_response.status_code == 200
        
        # 2. Enrich suspicious IP (if VirusTotal configured)
        if os.getenv('VIRUSTOTAL_API_KEY'):
            enrich_payload = {
                'ip': '203.0.113.45'
            }
            
            enrich_response = client.post(
                '/api/enrich/ip',
                data=json.dumps(enrich_payload),
                content_type='application/json'
            )
            
            assert enrich_response.status_code in [200, 429]


class TestAPIConcurrency:
    """Test API concurrent request handling"""
    
    def test_multiple_simultaneous_requests(self, client):
        """Test handling multiple simultaneous requests"""
        import concurrent.futures
        
        def make_request():
            payload = {
                'email_content': 'Test email',
                'email_sender': 'test@test.com',
                'email_subject': 'Test'
            }
            return client.post(
                '/api/email/analyze',
                data=json.dumps(payload),
                content_type='application/json'
            )
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
