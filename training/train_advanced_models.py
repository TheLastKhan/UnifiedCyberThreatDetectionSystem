"""
Train Advanced NLP Models (FastText and BERT)
==============================================

This script trains and tests both FastText and BERT models
for email phishing detection.
"""

import os
import sys
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_fasttext():
    """Train FastText model"""
    print("\n" + "="*70)
    print("TRAINING FASTTEXT MODEL")
    print("="*70)
    
    try:
        from src.email_detector.fasttext_detector import FastTextTrainer
        from src.utils.data_loader import DataLoader
        
        # Load data
        logger.info("Loading email dataset...")
        loader = DataLoader()
        texts, labels = loader.load_all_emails()
        
        # Split for training (use 80% for training)
        train_size = int(len(texts) * 0.8)
        train_texts = texts[:train_size]
        train_labels = labels[:train_size]
        
        logger.info(f"Training set: {len(train_texts)} emails")
        logger.info(f"Positive (phishing): {sum(train_labels)}")
        logger.info(f"Negative (legitimate): {len(train_labels) - sum(train_labels)}")
        
        # Train
        trainer = FastTextTrainer()
        logger.info("Starting FastText training... (this may take 30-60 seconds)")
        
        start_time = time.time()
        trainer.train(train_texts, train_labels, epochs=25, learning_rate=1.0)
        training_time = time.time() - start_time
        
        # Save model
        model_path = "models/fasttext_email_detector"
        trainer.save_model(model_path)
        
        logger.info(f"✅ FastText model trained in {training_time:.2f} seconds")
        logger.info(f"✅ Model saved to {model_path}.bin")
        
        # Test the model
        from src.email_detector.fasttext_detector import FastTextEmailDetector
        detector = FastTextEmailDetector(f"{model_path}.bin")
        
        # Test samples
        test_samples = [
            ("URGENT: Verify your PayPal account NOW!!!", "phishing"),
            ("Meeting scheduled for tomorrow at 3 PM", "legitimate"),
            ("You won $1,000,000! Click here to claim!", "phishing"),
            ("Please review the attached quarterly report", "legitimate")
        ]
        
        print("\n📊 Testing FastText model:")
        print("-" * 70)
        for text, expected in test_samples:
            result = detector.predict(text)
            status = "✅" if result.label == expected else "❌"
            print(f"{status} '{text[:50]}...'")
            print(f"   Predicted: {result.label} (score: {result.score:.3f})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error training FastText: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bert():
    """Test and download BERT model"""
    print("\n" + "="*70)
    print("TESTING BERT MODEL")
    print("="*70)
    
    try:
        from src.email_detector.bert_detector import BertEmailDetector
        import torch
        
        # Check device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        if device == "cuda":
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("Running on CPU (inference will be slower)")
        
        # Load model (will download on first use)
        logger.info("Loading BERT model...")
        logger.info("⏳ First time will download ~250 MB (may take 1-2 minutes)")
        
        start_time = time.time()
        detector = BertEmailDetector()
        load_time = time.time() - start_time
        
        logger.info(f"✅ BERT model loaded in {load_time:.2f} seconds")
        
        # Test samples
        test_samples = [
            "URGENT: Your account has been compromised! Click here immediately to verify your identity and prevent suspension!",
            "Hi team, reminder that our weekly standup is at 10 AM tomorrow. Please prepare your updates.",
            "CONGRATULATIONS! You've been selected to receive $5,000! Click this link to claim your prize NOW!",
            "Please find attached the invoice for your recent order. Payment is due within 30 days.",
            "SECURITY ALERT: Unusual activity detected. Verify your credit card details at this link or account will be closed!"
        ]
        
        print("\n📊 Testing BERT model:")
        print("-" * 70)
        
        total_time = 0
        for text in test_samples:
            start = time.time()
            result = detector.predict(text)
            inference_time = (time.time() - start) * 1000  # ms
            total_time += inference_time
            
            emoji = "🚨" if result.label == "phishing" else "✅"
            print(f"\n{emoji} '{text[:60]}...'")
            print(f"   Label: {result.label}")
            print(f"   Confidence: {result.confidence:.2%}")
            print(f"   Score: {result.score:.4f}")
            print(f"   Inference time: {inference_time:.2f}ms")
        
        avg_time = total_time / len(test_samples)
        print(f"\n⚡ Average inference time: {avg_time:.2f}ms per email")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing BERT: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_models():
    """Compare all three models"""
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    
    try:
        from src.email_detector.detector import EmailPhishingDetector
        from src.email_detector.fasttext_detector import FastTextEmailDetector
        from src.email_detector.bert_detector import BertEmailDetector
        
        # Initialize all models
        tfidf_detector = EmailPhishingDetector()
        fasttext_detector = FastTextEmailDetector("models/fasttext_email_detector.bin")
        bert_detector = BertEmailDetector()
        
        # Test email
        test_email = """
        URGENT ACTION REQUIRED!
        
        Your PayPal account will be suspended in 24 hours unless you verify immediately.
        
        Click here: http://payp4l-verify.tk/confirm
        
        Provide your:
        - Email and password
        - Credit card details
        - Social Security number
        
        Act NOW or lose access permanently!
        """
        
        print("\n🧪 Test Email:")
        print("-" * 70)
        print(test_email.strip())
        print("-" * 70)
        
        # TF-IDF
        print("\n1️⃣ TF-IDF + Random Forest:")
        start = time.time()
        result = tfidf_detector.predict_with_explanation(
            email_text=test_email,
            subject='URGENT ACTION REQUIRED',
            sender='noreply@suspicious.tk'
        )
        tfidf_time = (time.time() - start) * 1000
        print(f"   Prediction: {result['prediction']}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Time: {tfidf_time:.2f}ms")
        
        # FastText
        print("\n2️⃣ FastText:")
        start = time.time()
        result = fasttext_detector.predict(test_email)
        fasttext_time = (time.time() - start) * 1000
        print(f"   Prediction: {result.label}")
        print(f"   Score: {result.score:.4f}")
        print(f"   Time: {fasttext_time:.2f}ms")
        
        # BERT
        print("\n3️⃣ BERT (DistilBERT):")
        start = time.time()
        result = bert_detector.predict(test_email)
        bert_time = (time.time() - start) * 1000
        print(f"   Prediction: {result.label}")
        print(f"   Confidence: {result.confidence:.2%}")
        print(f"   Score: {result.score:.4f}")
        print(f"   Time: {bert_time:.2f}ms")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"TF-IDF:   {tfidf_time:>6.2f}ms  |  Fast baseline")
        print(f"FastText: {fasttext_time:>6.2f}ms  |  Balanced speed/accuracy")
        print(f"BERT:     {bert_time:>6.2f}ms  |  Highest accuracy")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error comparing models: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main execution"""
    print("\n🚀 ADVANCED NLP MODELS TRAINING")
    print("="*70)
    print("This will train and test FastText and BERT models")
    print("="*70)
    
    # Create directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    results = {
        'fasttext': False,
        'bert': False,
        'comparison': False
    }
    
    # 1. Train FastText
    print("\n[1/3] Training FastText...")
    results['fasttext'] = train_fasttext()
    
    # 2. Test BERT
    print("\n[2/3] Testing BERT...")
    results['bert'] = test_bert()
    
    # 3. Compare models
    if results['fasttext'] and results['bert']:
        print("\n[3/3] Comparing all models...")
        results['comparison'] = compare_models()
    
    # Final report
    print("\n" + "="*70)
    print("FINAL REPORT")
    print("="*70)
    print(f"FastText Training:  {'✅ SUCCESS' if results['fasttext'] else '❌ FAILED'}")
    print(f"BERT Testing:       {'✅ SUCCESS' if results['bert'] else '❌ FAILED'}")
    print(f"Model Comparison:   {'✅ SUCCESS' if results['comparison'] else '❌ FAILED'}")
    
    if all(results.values()):
        print("\n🎉 All advanced models are ready!")
        print("\nYou can now use:")
        print("  - TF-IDF (fast, baseline)")
        print("  - FastText (balanced)")
        print("  - BERT (highest accuracy)")
    else:
        print("\n⚠️ Some models failed. Check the logs above.")
    
    print("="*70)


if __name__ == "__main__":
    main()
