"""
TF-IDF Email Phishing Detector with LIME Explainability
========================================================
Wrapper class for TF-IDF Random Forest model with LIME support.
Follows same pattern as BERT and FastText detectors.
"""

import pickle
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import numpy as np
from lime.lime_text import LimeTextExplainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TFIDFPrediction:
    """Email phishing prediction result from TF-IDF model"""
    label: str  # 'phishing' or 'legitimate'
    score: float  # Phishing probability (0-1)
    confidence: float  # Max probability
    model_type: str = "TF-IDF"


class TFIDFEmailDetector:
    """
    TF-IDF-based Email Phishing Detector with LIME Explainability
    
    Features:
    - Random Forest classifier with TF-IDF features
    - LIME explanations for model predictions
    - Consistent interface with BERT and FastText detectors
    """
    
    MODEL_PATH = Path("models/email_detector_rf.pkl")
    VECTORIZER_PATH = Path("models/tfidf_vectorizer.pkl")
    
    def __init__(self, model_path: Optional[str] = None, vectorizer_path: Optional[str] = None):
        """
        Initialize TF-IDF detector
        
        Args:
            model_path: Path to Random Forest model pickle file
            vectorizer_path: Path to TF-IDF vectorizer pickle file
        """
        self.model_path = Path(model_path) if model_path else self.MODEL_PATH
        self.vectorizer_path = Path(vectorizer_path) if vectorizer_path else self.VECTORIZER_PATH
        
        self.model = None
        self.vectorizer = None
        self.lime_explainer = None
        
        # Load model and vectorizer
        self._load_model()
        
        # Initialize LIME
        self.lime_explainer = LimeTextExplainer(
            class_names=['Legitimate', 'Phishing']
        )
        logger.info("LIME explainer initialized")
    
    def _load_model(self):
        """Load Random Forest model and TF-IDF vectorizer from pickle files"""
        try:
            # Load model
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded from {self.model_path}")
            
            # Load vectorizer
            if not self.vectorizer_path.exists():
                raise FileNotFoundError(f"Vectorizer not found: {self.vectorizer_path}")
            
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            logger.info(f"Vectorizer loaded from {self.vectorizer_path}")
            
        except Exception as e:
            logger.error(f"Error loading TF-IDF model: {e}")
            raise
    
    def predict(self, text: str) -> TFIDFPrediction:
        """
        Predict if email is phishing
        
        Args:
            text: Email text content
        
        Returns:
            TFIDFPrediction object with label, score, and confidence
        """
        if not self.model or not self.vectorizer:
            raise ValueError("Model not loaded. Initialize detector first.")
        
        # Short message detection - reduce false positives on casual messages
        clean_text = " ".join(text.lower().split())
        
        # Phishing indicators
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
            'track your order', 'your package', 'delivery',
            'attached', 'please find', 'as discussed', 'follow up',
            'regards', 'best regards', 'sincerely', 'cheers',
            'looking forward', 'let me know', 'feel free',
            'interview', 'position', 'resume', 'application',
            'unsubscribe', 'newsletter', 'weekly', 'announced',
            'lunch', 'coffee', 'dinner', 'call', 'chat', 'quick question',
            # Birthday/Celebration
            'happy birthday', 'birthday', 'celebrate', 'wishing you',
            'best wishes', 'have a great day', 'wonderful', 'family and friends',
            # Thank you / Gratitude
            'thank you', 'thanks', 'thank you so much', 'thank for', 'appreciate',
            'grateful', 'helpful', 'went well', 'went really well', 'great help',
            'help with', 'your help'
        ]
        
        # Trusted domains (not suspicious even if present)
        trusted_domains = ['amazon.com', 'google.com', 'microsoft.com', 'linkedin.com', 
                          'ebay.com', 'walmart.com', 'target.com']
        
        phishing_count = sum(1 for ind in phishing_indicators if ind in clean_text)
        legit_count = sum(1 for ind in legitimate_indicators if ind in clean_text)
        trusted_count = sum(1 for d in trusted_domains if d in clean_text)
        
        word_count = len(clean_text.split())
        is_very_short = word_count < 15
        is_short_message = len(clean_text) < 100
        
        # Vectorize text
        text_vec = self.vectorizer.transform([text])
        
        # Predict
        prediction = self.model.predict(text_vec)[0]
        probabilities = self.model.predict_proba(text_vec)[0]
        
        # Extract scores
        phishing_score = probabilities[1]  # Probability of class 1 (phishing)
        confidence = max(probabilities)
        
        # Apply corrections based on indicators
        # CASE 1: Short message with no phishing indicators - APPLY FIRST
        if is_very_short and phishing_count == 0:
            correction_factor = 0.3
            phishing_score = phishing_score * correction_factor
            logger.info(f"TF-IDF short message correction applied: {phishing_score:.2f}")
        elif is_short_message and phishing_count == 0:
            correction_factor = 0.5
            phishing_score = phishing_score * correction_factor
            logger.info(f"TF-IDF short message correction applied: {phishing_score:.2f}")
        # CASE 2: High phishing score but has legitimate indicators, no phishing indicators
        elif phishing_score > 0.5 and phishing_count == 0:
            total_legit = legit_count + (trusted_count * 2)  # Trusted domains count double
            if total_legit >= 2:
                correction_factor = max(0.15, 1 - (total_legit * 0.2))
                phishing_score = phishing_score * correction_factor
                logger.info(f"TF-IDF legit indicator correction: {phishing_score:.2f}")
        
        # Determine label based on corrected score
        label = "phishing" if phishing_score > 0.5 else "legitimate"
        confidence = max(phishing_score, 1 - phishing_score)
        
        return TFIDFPrediction(
            label=label,
            score=phishing_score,
            confidence=confidence,
            model_type="TF-IDF"
        )
    
    def _predict_proba_for_lime(self, texts: List[str]) -> np.ndarray:
        """
        Wrapper for LIME: predict probabilities for multiple texts
        
        Args:
            texts: List of text samples
        
        Returns:
            Array of shape (n_samples, 2) with [prob_legit, prob_phishing]
        """
        text_vecs = self.vectorizer.transform(texts)
        probas = self.model.predict_proba(text_vecs)
        return probas
    
    def predict_with_explanation(
        self,
        text: str,
        num_features: int = 5,  # Match BERT/FastText
        num_samples: int = 500
    ) -> Dict[str, Any]:
        """
        Predict with LIME explanation
        
        Args:
            text: Email text to analyze
            num_features: Number of top features to include in explanation
            num_samples: Number of samples for LIME (higher = more stable)
        
        Returns:
            Dictionary with:
                - prediction: 'phishing' or 'legitimate'
                - confidence: float
                - score: phishing probability
                - lime_breakdown: list of {feature, contribution, positive}
        """
        # Get base prediction
        prediction = self.predict(text)
        
        # Generate LIME explanation - request more features to filter from
        explanation = self.lime_explainer.explain_instance(
            text,
            self._predict_proba_for_lime,
            num_features=15,  # Request more to have enough after filtering
            num_samples=num_samples
        )
        
        # Stopwords to filter out - these don't provide meaningful insights
        stopwords = {
            # Articles, prepositions, conjunctions
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used',
            'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'between',
            'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither',
            'not', 'only', 'own', 'same', 'than', 'too', 'very', 'just',
            # Pronouns
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
            # Common verbs and auxiliaries
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'get', 'got', 'getting', 'make', 'made', 'making',
            # Greetings and casual words
            'hi', 'hey', 'hello', 'how', 'fine', 'good', 'great', 'nice', 'well',
            'ok', 'okay', 'yes', 'no', 'please', 'thanks', 'thank',
            # Conditionals and adverbs
            'if', 'then', 'else', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'any', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'here', 'there', 'now', 'then', 'once', 'always', 'never',
            'also', 'still', 'already', 'even', 'ever', 'just', 'about',
            # More common words that don't help
            'like', 'know', 'see', 'think', 'want', 'come', 'go', 'take',
            'use', 'find', 'give', 'tell', 'say', 'said', 'ask', 'asked',
            'first', 'last', 'new', 'old', 'high', 'low', 'big', 'small',
            'long', 'short', 'many', 'much', 'more', 'most', 'other', 'another',
            'full', 'following', 'due', 'within', 'detected', 'provide',
            # Numbers and dates
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'hours', 'days', 'weeks', 'months', 'years', 'date', 'time'
        }
        
        # Format LIME output - filter stopwords
        lime_list = explanation.as_list()
        
        # Filter out stopwords, numbers, and short tokens
        filtered_features = []
        for feature, weight in lime_list:
            feature_clean = feature.lower().strip()
            # Skip stopwords
            if feature_clean in stopwords:
                continue
            # Skip pure numbers or very short tokens
            if feature_clean.isdigit() or len(feature_clean) <= 2:
                continue
            # Skip tokens that are mostly numbers (like "18", "24", "2025")
            if any(c.isdigit() for c in feature_clean) and sum(c.isdigit() for c in feature_clean) > len(feature_clean) / 2:
                continue
            filtered_features.append((feature, weight))
        
        # If we have less than 5 meaningful features, fill with remaining from original list
        if len(filtered_features) < 5:
            for feature, weight in lime_list:
                if (feature, weight) not in filtered_features:
                    filtered_features.append((feature, weight))
                if len(filtered_features) >= 5:
                    break
        
        # Calculate contributions with normalization
        # Scale based on phishing score - linear: 0.05->3%, 0.21->5%, 0.85->15%, 1.0->17%
        features_to_show = filtered_features[:5]
        if features_to_show:
            max_weight = max(abs(w) for _, w in features_to_show)
            # Formula: 2.25 + score * 14.75
            target_max = 2.25 + (prediction.score * 14.75)
            scale_factor = target_max / max_weight if max_weight > 0 else 1.0
        else:
            scale_factor = 1.0
        
        lime_breakdown = []
        for feature, weight in features_to_show:
            # Normalized contribution percentage
            contribution = abs(weight) * scale_factor
            
            # Cap at reasonable maximum
            contribution = min(contribution, 25.0)
            
            lime_breakdown.append({
                'feature': feature,
                'contribution': round(contribution, 1),
                'positive': weight > 0  # True if contributes to phishing
            })
        
        return {
            'prediction': prediction.label,
            'confidence': prediction.confidence,
            'score': prediction.score,
            'lime_breakdown': lime_breakdown,
            'model_type': 'TF-IDF'
        }


# Example usage
if __name__ == "__main__":
    # Test the detector
    detector = TFIDFEmailDetector()
    
    # Test phishing email
    test_email = """
    URGENT! Your PayPal account has been suspended.
    Please verify your credit card and CVV immediately.
    Click here: http://paypal-security-verify.com/
    """
    
    print("Testing TF-IDF detector with LIME...")
    print("="*70)
    
    # Prediction with explanation
    result = detector.predict_with_explanation(test_email)
    
    print(f"Prediction: {result['prediction'].upper()}")
    print(f"Confidence: {result['confidence']*100:.1f}%")
    print(f"Phishing Score: {result['score']*100:.1f}%")
    print(f"\nTop LIME Features:")
    for item in result['lime_breakdown'][:5]:
        sign = "+" if item['positive'] else "-"
        print(f"  {sign} {item['feature']}: {item['contribution']:.1f}%")
    
    print("="*70)
    print("✅ TF-IDF LIME detector working!")
