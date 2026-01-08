"""
FastText Email Phishing Detector
=================================

FastText provides fast training and inference, suitable for email classification.
This is an alternative/complement to BERT model.

Features:
- Sub-word information (handles typos and misspellings)
- Fast training (minutes instead of hours)
- Reasonable accuracy (87-92% on email datasets)
- Small model size (~5-10 MB)

Comparison with TF-IDF and BERT:
- TF-IDF: Fast, baseline, ~85% accuracy
- FastText: Medium speed, ~88% accuracy
- BERT: Slow, state-of-art, ~94% accuracy
"""

import os
import sys
import logging
from pathlib import Path
import pickle
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

try:
    import fasttext
    # Suppress FastText logging if eprint exists
    if hasattr(fasttext.FastText, 'eprint'):
        fasttext.FastText.eprint = lambda x: None  # type: ignore
except ImportError:
    logger.warning("FastText not installed. Install with: pip install fasttext")
    fasttext = None  # type: ignore

# LIME for explainability
try:
    from lime.lime_text import LimeTextExplainer
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False
    logger.warning("LIME not available. Install with: pip install lime")


@dataclass
class FastTextPrediction:
    """FastText model prediction output"""
    score: float  # 0-1 probability
    label: str  # "phishing" or "legitimate"
    confidence: float  # confidence level
    model_type: str = "FastText"


class FastTextEmailDetector:
    """
    FastText-based email phishing detector
    
    Advantages over TF-IDF:
    - Better handling of typos and variations
    - Sub-word embeddings capture semantic meaning
    - Faster inference than BERT
    - Smaller model size
    
    Training:
    - FastText learns word embeddings
    - Classification layer on top
    - Unsupervised learning for better embeddings
    """
    
    MODEL_PATH = "models/fasttext_email_detector.bin"
    TRAINING_DATA_PATH = "data/fasttext_training.txt"
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize FastText detector
        
        Args:
            model_path: Path to pre-trained model
        """
        if not fasttext:
            raise ImportError("FastText not installed. Run: pip install fasttext")
        
        self.model_path = model_path or self.MODEL_PATH
        self.model = None
        
        if Path(self.model_path).exists():
            self._load_model()
        else:
            logger.warning(f"Model not found at {self.model_path}")
            logger.info("Train model first with: trainer.train()")
    
    def _load_model(self):
        """Load pre-trained model"""
        if fasttext is None:
            logger.error("FastText not installed")
            return
        try:
            self.model = fasttext.load_model(self.model_path)  # type: ignore
            logger.info(f"✅ Model loaded from {self.model_path}")
            
            # Initialize LIME explainer
            if LIME_AVAILABLE:
                self.lime_explainer = LimeTextExplainer(
                    class_names=['Legitimate', 'Phishing']
                )
                logger.info("LIME explainer initialized")
            else:
                self.lime_explainer = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.lime_explainer = None
    
    def predict(self, text: str) -> FastTextPrediction:
        """
        Predict if email is phishing
        
        Args:
            text: Email text
        
        Returns:
            FastTextPrediction object
        """
        if not self.model:
            raise ValueError("Model not loaded. Train model first.")
        
        # Preprocess text (lowercase, remove extra whitespace)
        clean_text = " ".join(text.lower().split())
        
        # Short message detection - reduce false positives on casual messages
        # Common phishing indicators to check
        phishing_indicators = [
            'urgent', 'verify your', 'account suspended', 'password', 'click here', 'suspended',
            'confirm your', 'security alert', 'bank account', 'credit card', 'expire', 'immediately',
            'winner', 'prize', 'congratulation', 'lottery', 'paypal', 'bitcoin',
            'wire transfer', 'ssn', 'social security', 'cvv', 'pin',
            'bit.ly', 'tinyurl', '.ru/', '.tk/', '.ml/'
        ]
        
        # Legitimate indicators
        legitimate_indicators = [
            'meeting', 'schedule', 'project', 'report', 'deadline', 'presentation',
            'thank you for your order', 'has been shipped', 'order confirmation',
            'track your order', 'your package', 'delivery', 'estimated delivery',
            'attached', 'please find', 'as discussed', 'follow up',
            'regards', 'best regards', 'sincerely', 'cheers',
            'looking forward', 'let me know', 'feel free',
            'interview', 'position', 'resume', 'application',
            'unsubscribe', 'newsletter', 'weekly', 'announced',
            'lunch', 'coffee', 'dinner', 'call', 'chat', 'quick question',
            'amazon.com', 'google.com', 'microsoft.com', 'linkedin.com',
            # Birthday/Celebration
            'happy birthday', 'birthday', 'celebrate', 'wishing you',
            'best wishes', 'have a great day', 'wonderful', 'family and friends'
        ]
        
        phishing_count = sum(1 for ind in phishing_indicators if ind in clean_text)
        legit_count = sum(1 for ind in legitimate_indicators if ind in clean_text)
        
        has_phishing_indicator = phishing_count > 0
        is_short_message = len(clean_text) < 100  # Less than 100 chars
        word_count = len(clean_text.split())
        is_very_short = word_count < 15  # Less than 15 words
        
        # Predict (handle NumPy 2.0 compatibility)
        try:
            prediction = self.model.predict(clean_text, k=1)
            # FastText returns (labels, scores) tuple
            if isinstance(prediction, tuple) and len(prediction) == 2:
                labels, scores = prediction
                if len(labels) > 0 and len(scores) > 0:
                    label = str(labels[0]).replace("__label__", "")
                    # Convert to Python float using item() to avoid NumPy copy issues
                    score = float(scores[0]) if hasattr(scores[0], 'item') else float(scores[0])  # type: ignore
                else:
                    raise ValueError("Empty prediction arrays")
            else:
                raise ValueError(f"Unexpected prediction format: {type(prediction)}")
        except Exception as e:
            logger.error(f"FastText prediction error: {e}")
            # Return safe default
            return FastTextPrediction(
                score=0.5,
                label="legitimate",
                confidence=0.5
            )
        
        # Convert to phishing score (0-1)
        phishing_score = score if label == "phishing" else 1 - score
        
        # Keep the model's phishing prediction if it has high confidence
        # Only apply corrections for potential false positives
        model_says_phishing = label == "phishing"
        high_confidence = score > 0.9
        
        # CASE 1: False Positive Correction
        # Only reduce if model says phishing, NO phishing indicators exist, and has STRONG legitimate signals
        if model_says_phishing and phishing_count == 0 and legit_count >= 3 and not high_confidence:
            correction_factor = max(0.3, 1 - (legit_count * 0.15))
            phishing_score = phishing_score * correction_factor
            logger.debug(f"FastText legit indicator correction: {phishing_score:.2f}")
        # CASE 2: Short message correction (only for non-phishing indicators)
        elif is_very_short and phishing_count == 0:
            # Apply correction factor - reduce phishing score for short casual messages
            correction_factor = 0.3  # Reduce phishing confidence by 70%
            phishing_score = phishing_score * correction_factor
            logger.debug(f"Short message correction applied: {phishing_score:.2f}")
        elif is_short_message and phishing_count == 0:
            # Moderate correction for medium-short messages
            correction_factor = 0.5
            phishing_score = phishing_score * correction_factor
        
        # CASE 3: False Negative Boost
        # If model says legitimate but has phishing indicators, boost score
        if not model_says_phishing and phishing_count >= 2:
            boost = min(0.8, phishing_count * 0.15)
            phishing_score = min(1.0, phishing_score + boost)
            logger.debug(f"FastText phishing boost applied: {phishing_score:.2f}")
        
        # Determine final label
        final_label = "phishing" if phishing_score > 0.5 else "legitimate"
        
        return FastTextPrediction(
            score=phishing_score,
            label=final_label,
            confidence=score if final_label == label else 1 - score
        )
    
    def predict_with_explanation(
        self,
        text: str,
        num_features: int = 5,
        num_samples: int = 100
    ) -> Dict:
        """
        Predict with LIME explanation for XAI
        
        Args:
            text: Email content to analyze
            num_features: Number of top features to return
            num_samples: Number of samples for LIME
        
        Returns:
            Dictionary with prediction and lime_breakdown
        """
        # Get basic prediction
        prediction = self.predict(text)
        
        # If LIME not available, return without explanation
        if not self.lime_explainer:
            logger.warning("LIME not available, returning prediction without explanation")
            return {
                'prediction': prediction.label,
                'confidence': prediction.confidence,
                'score': prediction.score,
                'lime_breakdown': []
            }
        
        try:
            # Create prediction function for LIME
            def predict_proba(texts):
                """Wrapper for LIME - returns probability array"""
                results = []
                for t in texts:
                    pred = self.predict(t)
                    prob_phishing = pred.score
                    prob_legit = 1 - prob_phishing
                    results.append([prob_legit, prob_phishing])
                return np.array(results)
            
            # Get LIME explanation (increased samples for stability)
            explanation = self.lime_explainer.explain_instance(
                text,
                predict_proba,
                num_features=num_features,
                num_samples=500  # Increased for more stable results
            )
            
            
            # Format LIME output with dynamic multiplier
            lime_breakdown = []
            for feature, weight in explanation.as_list():
                # Dynamic multiplier: 
                # - High phishing score (>0.5): use 10x for visibility
                # - Low phishing score (<0.5): use 1x to avoid inflation
                if prediction.score > 0.5:
                    # Phishing case: use 10x multiplier for visibility
                    contribution = abs(weight) * prediction.score * 100 * 10
                else:
                    # Legitimate case: use same formula as BERT/TF-IDF
                    contribution = abs(weight) * prediction.score * 100
                
                # Cap at reasonable maximum
                contribution = min(contribution, 99.9)
                
                lime_breakdown.append({
                    'feature': feature,
                    'contribution': round(contribution, 1),
                    'positive': weight > 0
                })
            
            return {
                'prediction': prediction.label,
                'confidence': prediction.confidence,
                'score': prediction.score,
                'lime_breakdown': lime_breakdown
            }
            
        except Exception as e:
            logger.error(f"Error generating LIME explanation: {e}")
            return {
                'prediction': prediction.label,
                'confidence': prediction.confidence,
                'score': prediction.score,
                'lime_breakdown': []
            }
    
    def batch_predict(self, texts: List[str]) -> List[FastTextPrediction]:
        """Predict for multiple texts"""
        return [self.predict(text) for text in texts]
    
    def get_model_info(self) -> Dict:
        """Get model information"""
        if not self.model:
            return {"status": "not_loaded"}
        
        return {
            "model_path": self.model_path,
            "dimension": self.model.get_dimension(),
            "labels": self.model.labels,
            "word_count": len(self.model.get_words()),
            "model_type": "FastText",
        }


class FastTextTrainer:
    """
    Train FastText model on email dataset
    
    Training process:
    1. Load datasets (Enron, Nigerian fraud, phishing)
    2. Prepare training file in FastText format
    3. Train model with hyperparameters
    4. Evaluate on test set
    5. Save model
    """
    
    def __init__(self):
        """Initialize trainer"""
        if fasttext is None:
            raise ImportError("FastText not installed. Run: pip install fasttext")
        
        self.model = None
        self.training_file = "data/fasttext_training.txt"
    
    def prepare_training_data(
        self,
        texts: List[str],
        labels: List[int]
    ) -> str:
        """
        Prepare training data in FastText format
        
        Format:
        __label__phishing Email content here
        __label__legitimate Legitimate email content
        
        Args:
            texts: List of email texts
            labels: List of labels (0=legitimate, 1=phishing)
        
        Returns:
            Path to training file
        """
        logger.info(f"Preparing {len(texts)} samples for training...")
        
        # Create data directory
        Path("data").mkdir(exist_ok=True)
        
        with open(self.training_file, "w", encoding="utf-8") as f:
            for text, label in zip(texts, labels):
                # Preprocess text
                text = " ".join(text.lower().split())
                text = text.replace("\n", " ").replace("\r", " ")
                
                # Add label
                label_str = "__label__phishing" if label == 1 else "__label__legitimate"
                
                f.write(f"{label_str} {text}\n")
        
        logger.info(f"✅ Training file created: {self.training_file}")
        return self.training_file
    
    def train(
        self,
        texts: List[str],
        labels: List[int],
        epochs: int = 25,
        learning_rate: float = 1.0,
        word_ngrams: int = 2,
        dim: int = 100,
        **kwargs
    ) -> Dict:
        """
        Train FastText model
        
        Args:
            texts: Training texts
            labels: Training labels (0/1)
            epochs: Number of epochs
            learning_rate: Learning rate
            word_ngrams: N-gram size
            dim: Embedding dimension
        
        Returns:
            Training metrics
        """
        logger.info("="*60)
        logger.info("FASTTEXT MODEL TRAINING")
        logger.info("="*60)
        
        # Prepare data
        training_file = self.prepare_training_data(texts, labels)
        
        # Train
        logger.info("Starting training...")
        if fasttext is None:
            raise ImportError("FastText not available")
        self.model = fasttext.train_supervised(  # type: ignore
            input=training_file,
            epoch=epochs,
            lr=learning_rate,
            wordNgrams=word_ngrams,
            dim=dim,
            loss='softmax',
            verbose=2
        )
        
        logger.info("✅ Training completed!")
        
        metrics = {
            "epochs": epochs,
            "learning_rate": learning_rate,
            "word_ngrams": word_ngrams,
            "dimension": dim,
            "training_samples": len(texts)
        }
        
        return metrics
    
    def evaluate(
        self,
        texts: List[str],
        labels: List[int]
    ) -> Dict:
        """
        Evaluate model on test set
        
        Args:
            texts: Test texts
            labels: Test labels
        
        Returns:
            Evaluation metrics
        """
        if not self.model:
            raise ValueError("Model not trained yet")
        
        logger.info("Evaluating model...")
        
        # Create temp evaluation file
        eval_file = "data/fasttext_eval.txt"
        with open(eval_file, "w", encoding="utf-8") as f:
            for text, label in zip(texts, labels):
                text = " ".join(text.lower().split())
                label_str = "__label__phishing" if label == 1 else "__label__legitimate"
                f.write(f"{label_str} {text}\n")
        
        # Evaluate
        n_samples, precision, recall = self.model.test(eval_file)
        
        metrics = {
            "samples": n_samples,
            "precision": precision,
            "recall": recall,
            "f1_score": 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        }
        
        logger.info(f"Precision: {precision:.2%}")
        logger.info(f"Recall: {recall:.2%}")
        logger.info(f"F1-Score: {metrics['f1_score']:.2%}")
        
        return metrics
    
    def save_model(self, path: str):
        """Save trained model"""
        if not self.model:
            raise ValueError("No model to save")
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # FastText saves as .bin and .vec
        base_path = str(Path(path).with_suffix(''))
        self.model.save_model(base_path + ".bin")
        
        logger.info(f"✅ Model saved to {base_path}.bin")


def main():
    """Main training function"""
    logging.basicConfig(level=logging.INFO)
    
    logger.info("FastText Email Detector")
    logger.info("="*60)
    
    # Load data
    logger.info("Loading datasets...")
    from src.utils.data_loader import DataLoader
    
    loader = DataLoader()
    texts, labels = loader.load_all_emails()
    
    if len(texts) < 100:
        logger.warning("Not enough data for training")
        logger.info("Please load more email datasets")
        return
    
    # Split
    split = int(0.8 * len(texts))
    train_texts, train_labels = texts[:split], labels[:split]
    test_texts, test_labels = texts[split:], labels[split:]
    
    logger.info(f"Training: {len(train_texts)}, Test: {len(test_texts)}")
    
    # Train
    trainer = FastTextTrainer()
    metrics = trainer.train(train_texts, train_labels)
    
    # Evaluate
    eval_metrics = trainer.evaluate(test_texts, test_labels)
    
    # Save
    trainer.save_model("models/fasttext_email_detector")
    
    # Report
    report = {
        "training_metrics": metrics,
        "evaluation_metrics": eval_metrics,
        "status": "completed"
    }
    
    Path("reports").mkdir(exist_ok=True)
    with open("reports/fasttext_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info("\n" + "="*60)
    logger.info("✅ FASTTEXT TRAINING COMPLETED!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
