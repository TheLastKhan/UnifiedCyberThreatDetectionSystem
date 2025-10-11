"""
Email Detector Unit Tests
"""

import sys
sys.path.append('../src')

from src.email_detector.detector import EmailPhishingDetector
from src.utils.data_loader import create_sample_email_data

def test_email_detector_training():
    """Detector'ın eğitildiğini test eder"""
    detector = EmailPhishingDetector()
    
    emails_df = create_sample_email_data()
    labels = emails_df['label'].tolist()
    
    detector.train(emails_df, labels)
    
    assert detector.is_trained == True
    print("✅ Email detector training test passed")

def test_email_prediction():
    """Prediction fonksiyonunu test eder"""
    detector = EmailPhishingDetector()
    
    emails_df = create_sample_email_data()
    labels = emails_df['label'].tolist()
    
    detector.train(emails_df, labels)
    
    test_email = "URGENT! Your account will be suspended! Click here immediately!"
    result = detector.predict_with_explanation(test_email, "scam@fake.com", "URGENT")
    
    assert result['prediction'] in ['Safe', 'Phishing']
    assert 0 <= result['confidence'] <= 100
    print("✅ Email prediction test passed")

if __name__ == "__main__":
    test_email_detector_training()
    test_email_prediction()
    print("\n🎉 All email detector tests passed!")
