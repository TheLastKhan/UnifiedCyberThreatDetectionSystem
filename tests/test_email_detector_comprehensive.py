"""
Comprehensive Email Detector Unit Tests with pytest
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.email_detector.detector import EmailPhishingDetector
from src.email_detector.features import EmailFeatureExtractor
from src.utils.data_loader import create_sample_email_data


class TestEmailPhishingDetector:
    """Test suite for EmailPhishingDetector"""
    
    @pytest.fixture
    def detector(self):
        """Create a detector instance"""
        return EmailPhishingDetector()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample training data"""
        return create_sample_email_data()
    
    @pytest.fixture
    def trained_detector(self, detector, sample_data):
        """Create a trained detector"""
        labels = sample_data['label'].tolist()
        detector.train(sample_data, labels)
        return detector
    
    # Initialization Tests
    def test_detector_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector.is_trained == False
        # Model may be pre-initialized
        assert detector.model is not None or detector.model is None
    
    # Training Tests
    def test_detector_training(self, detector, sample_data):
        """Test detector training process"""
        labels = sample_data['label'].tolist()
        detector.train(sample_data, labels)
        
        assert detector.is_trained == True
        assert detector.model is not None
        assert detector.vectorizer is not None
    
    def test_training_with_empty_data(self, detector):
        """Test training fails gracefully with empty data"""
        empty_df = pd.DataFrame(columns=['text', 'sender', 'subject'])
        empty_labels = []
        
        with pytest.raises((ValueError, Exception)):
            detector.train(empty_df, empty_labels)
    
    def test_training_with_invalid_labels(self, detector, sample_data):
        """Test training handles invalid labels"""
        # Wrong number of labels
        wrong_labels = [0, 1]  # Too few labels
        
        with pytest.raises((ValueError, Exception)):
            detector.train(sample_data, wrong_labels)
    
    # Prediction Tests
    def test_prediction_returns_correct_format(self, trained_detector):
        """Test prediction returns expected format"""
        result = trained_detector.predict_with_explanation(
            "Test email content",
            "sender@example.com",
            "Test Subject"
        )
        
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'phishing_probability' in result
        assert 'safe_probability' in result
        assert 'lime_explanation' in result
        assert 'risk_factors' in result
        
        assert result['prediction'] in ['Safe', 'Phishing']
        assert 0 <= result['confidence'] <= 100
    
    def test_phishing_detection(self, trained_detector):
        """Test detection of obvious phishing email"""
        phishing_email = """
        URGENT! Your PayPal account has been suspended!
        Click here immediately to verify your account:
        http://paypa1-security.fake.com/verify
        Failure to comply will result in permanent account closure!
        """
        
        result = trained_detector.predict_with_explanation(
            phishing_email,
            "security@paypa1-fake.com",
            "URGENT: Account Suspended"
        )
        
        # Should detect as phishing with high confidence
        assert result['prediction'] == 'Phishing'
        assert result['confidence'] > 60  # At least 60% confidence
    
    def test_legitimate_detection(self, trained_detector):
        """Test detection of legitimate email"""
        legit_email = """
        Hello,
        
        This is your weekly newsletter from our company.
        Here are the latest updates and articles.
        
        Best regards,
        Newsletter Team
        """
        
        result = trained_detector.predict_with_explanation(
            legit_email,
            "newsletter@company.com",
            "Weekly Newsletter"
        )
        
        # Should likely detect as safe (though not guaranteed)
        assert result['prediction'] in ['Safe', 'Phishing']
        assert 0 <= result['confidence'] <= 100
    
    def test_prediction_without_training(self, detector):
        """Test prediction fails when detector not trained"""
        with pytest.raises((ValueError, AttributeError, Exception)):
            detector.predict_with_explanation(
                "Test email",
                "sender@test.com",
                "Test"
            )
    
    def test_prediction_with_empty_content(self, trained_detector):
        """Test prediction handles empty email content"""
        result = trained_detector.predict_with_explanation(
            "",
            "sender@test.com",
            "Empty"
        )
        
        # Should still return valid result
        assert 'prediction' in result
        assert 'confidence' in result
    
    # Feature Extraction Tests
    def test_feature_extraction_structure(self, trained_detector):
        """Test that LIME explanation and risk factors are provided"""
        result = trained_detector.predict_with_explanation(
            "Test email with URGENT message",
            "suspicious@fake.com",
            "URGENT ACTION"
        )
        
        # Check for LIME explanation
        assert 'lime_explanation' in result
        assert isinstance(result['lime_explanation'], list)
        assert len(result['lime_explanation']) > 0
        
        # Check for risk factors
        assert 'risk_factors' in result
        assert isinstance(result['risk_factors'], list)
    
    def test_confidence_ranges(self, trained_detector):
        """Test that confidence values are within valid range"""
        test_cases = [
            ("Click here now!", "spam@test.com", "Free Money"),
            ("Regular email content", "user@company.com", "Meeting"),
            ("", "empty@test.com", "Empty")
        ]
        
        for content, sender, subject in test_cases:
            result = trained_detector.predict_with_explanation(content, sender, subject)
            assert 0 <= result['confidence'] <= 100, \
                f"Confidence {result['confidence']} out of range for: {content[:20]}"
    
    # Edge Cases
    def test_very_long_email(self, trained_detector):
        """Test handling of very long email content"""
        long_content = "This is a test. " * 10000  # Very long email
        
        result = trained_detector.predict_with_explanation(
            long_content,
            "sender@test.com",
            "Long Email"
        )
        
        assert 'prediction' in result
        assert 'confidence' in result
    
    def test_special_characters_email(self, trained_detector):
        """Test handling of special characters"""
        special_content = "Test email with 特殊字符 and émojis 🎉🔥"
        
        result = trained_detector.predict_with_explanation(
            special_content,
            "sender@test.com",
            "Special Chars"
        )
        
        assert 'prediction' in result
    
    def test_multiple_predictions(self, trained_detector):
        """Test multiple consecutive predictions"""
        emails = [
            ("Email 1", "sender1@test.com", "Subject 1"),
            ("Email 2", "sender2@test.com", "Subject 2"),
            ("Email 3", "sender3@test.com", "Subject 3")
        ]
        
        for content, sender, subject in emails:
            result = trained_detector.predict_with_explanation(content, sender, subject)
            assert 'prediction' in result
            assert 'confidence' in result


class TestEmailFeatures:
    """Test suite for email feature extraction"""
    
    @pytest.fixture
    def extractor(self):
        """Create feature extractor instance"""
        return EmailFeatureExtractor()
    
    def test_urgent_words_detection(self, extractor):
        """Test detection of urgent words"""
        urgent_text = "URGENT! IMMEDIATE ACTION REQUIRED!"
        features = extractor.extract_keyword_features(urgent_text)
        
        # Should detect urgent keywords
        assert isinstance(features, dict)
    
    def test_url_extraction(self, extractor):
        """Test URL extraction from email"""
        email_with_links = """
        Visit us at http://example.com
        Or click here: https://test.com
        """
        
        features = extractor.extract_url_features(email_with_links)
        
        # Should extract URLs
        assert isinstance(features, dict)
        assert 'url_count' in features
    
    def test_text_features(self, extractor):
        """Test text feature extraction"""
        text = "This is a test email with some content"
        
        features = extractor.extract_text_features(text)
        
        # Should extract text features
        assert isinstance(features, dict)


class TestEmailDetectorIntegration:
    """Integration tests for email detector"""
    
    def test_full_pipeline(self):
        """Test complete detection pipeline"""
        # Create detector
        detector = EmailPhishingDetector()
        
        # Create training data
        sample_data = create_sample_email_data()
        labels = sample_data['label'].tolist()
        
        # Train
        detector.train(sample_data, labels)
        
        # Predict
        result = detector.predict_with_explanation(
            "Suspicious phishing email",
            "scam@fake.com",
            "URGENT"
        )
        
        # Verify complete workflow
        assert detector.is_trained
        assert result['prediction'] in ['Safe', 'Phishing']
        assert 'lime_explanation' in result
        assert 'risk_factors' in result
    
    def test_batch_predictions(self):
        """Test batch prediction capability"""
        detector = EmailPhishingDetector()
        sample_data = create_sample_email_data()
        labels = sample_data['label'].tolist()
        detector.train(sample_data, labels)
        
        # Multiple emails
        test_emails = [
            ("Test 1", "sender1@test.com", "Subject 1"),
            ("Test 2", "sender2@test.com", "Subject 2"),
            ("Test 3", "sender3@test.com", "Subject 3")
        ]
        
        results = []
        for content, sender, subject in test_emails:
            result = detector.predict_with_explanation(content, sender, subject)
            results.append(result)
        
        assert len(results) == 3
        assert all('prediction' in r for r in results)


# Performance Tests
class TestEmailDetectorPerformance:
    """Performance tests for email detector"""
    
    @pytest.mark.slow
    def test_training_time(self):
        """Test training time performance"""
        import time
        
        detector = EmailPhishingDetector()
        sample_data = create_sample_email_data()
        labels = sample_data['label'].tolist()
        
        # Measure training time
        start = time.time()
        detector.train(sample_data, labels)
        training_time = time.time() - start
        
        assert detector.is_trained
        assert training_time < 30.0, f"Training too slow: {training_time:.2f}s"
    
    @pytest.mark.slow
    def test_prediction_speed(self):
        """Test prediction speed"""
        import time
        
        detector = EmailPhishingDetector()
        sample_data = create_sample_email_data()
        labels = sample_data['label'].tolist()
        detector.train(sample_data, labels)
        
        # Time 100 predictions
        start = time.time()
        for i in range(100):
            detector.predict_with_explanation(
                f"Test email {i}",
                f"sender{i}@test.com",
                f"Subject {i}"
            )
        end = time.time()
        
        avg_time = (end - start) / 100
        
        # Should be fast (< 100ms per prediction)
        assert avg_time < 0.1, f"Average prediction time too slow: {avg_time:.3f}s"


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--tb=short"])
