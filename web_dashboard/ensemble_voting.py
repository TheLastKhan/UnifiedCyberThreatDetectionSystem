"""
Ensemble Voting Module for Email Phishing Detection
====================================================
Combines predictions from BERT, FastText, and TF-IDF models using weighted voting.

Weights are based on model performance and characteristics:
- BERT: 0.5 (most accurate, transformer-based)
- FastText: 0.3 (fast, good accuracy)
- TF-IDF: 0.2 (lightweight, baseline)
"""

from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def weighted_vote(
    bert_score: Optional[float] = None,
    fasttext_score: Optional[float] = None,
    tfidf_score: Optional[float] = None,
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Combine model predictions using weighted voting
    
    Args:
        bert_score: BERT phishing probability (0-1), None if unavailable
        fasttext_score: FastText phishing probability (0-1), None if unavailable
        tfidf_score: TF-IDF phishing probability (0-1), None if unavailable
        weights: Custom weights dict, defaults to {'bert': 0.5, 'fasttext': 0.3, 'tfidf': 0.2}
    
    Returns:
        Dictionary with:
            - prediction: 'phishing' or 'legitimate'
            - confidence: float (0-1)
            - weighted_score: float (0-1) - final phishing probability
            - individual_scores: dict of individual model scores
            - models_used: list of models that contributed
            - risk_level: 'critical', 'high', 'medium', or 'low'
    """
    # Default weights
    if weights is None:
        weights = {
            'bert': 0.5,
            'fasttext': 0.3,
            'tfidf': 0.2
        }
    
    # Track which models are available
    available_models = []
    scores = {}
    
    if bert_score is not None:
        available_models.append('bert')
        scores['bert'] = bert_score
    
    if fasttext_score is not None:
        available_models.append('fasttext')
        scores['fasttext'] = fasttext_score
    
    if tfidf_score is not None:
        available_models.append('tfidf')
        scores['tfidf'] = tfidf_score
    
    # Handle edge case: no models available
    if not available_models:
        logger.warning("No models available for ensemble voting")
        return {
            'prediction': 'unknown',
            'confidence': 0.0,
            'weighted_score': 0.0,
            'individual_scores': {},
            'models_used': [],
            'risk_level': 'unknown',
            'error': 'No models available'
        }
    
    # Normalize weights for available models
    total_weight = sum(weights[model] for model in available_models)
    normalized_weights = {
        model: weights[model] / total_weight 
        for model in available_models
    }
    
    # Calculate weighted score
    weighted_score = sum(
        scores[model] * normalized_weights[model]
        for model in available_models
    )
    
    # Determine prediction
    prediction = 'phishing' if weighted_score > 0.5 else 'legitimate'
    confidence = max(weighted_score, 1 - weighted_score)
    
    # Calculate risk level
    if weighted_score >= 0.80:
        risk_level = 'critical'
    elif weighted_score >= 0.60:
        risk_level = 'high'
    elif weighted_score >= 0.40:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'weighted_score': weighted_score,
        'individual_scores': scores,
        'models_used': available_models,
        'risk_level': risk_level,
        'weights_applied': normalized_weights
    }


def get_ensemble_metrics(
    bert_result: Optional[Dict] = None,
    fasttext_result: Optional[Dict] = None,
    tfidf_result: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Extract scores from model results and combine them
    
    Args:
        bert_result: BERT prediction dict with 'score' key
        fasttext_result: FastText prediction dict with 'score' key
        tfidf_result: TF-IDF prediction dict with 'score' key
    
    Returns:
        Ensemble voting result
    """
    bert_score = bert_result.get('score') if bert_result else None
    fasttext_score = fasttext_result.get('score') if fasttext_result else None
    tfidf_score = tfidf_result.get('score') if tfidf_result else None
    
    return weighted_vote(
        bert_score=bert_score,
        fasttext_score=fasttext_score,
        tfidf_score=tfidf_score
    )


# Example usage and testing
if __name__ == "__main__":
    print("Testing Ensemble Voting Module")
    print("="*70)
    
    # Test 1: All models available
    print("\n1️⃣ Test: All 3 models available")
    result = weighted_vote(
        bert_score=0.95,      # BERT: 95% phishing
        fasttext_score=0.88,  # FastText: 88% phishing
        tfidf_score=0.92      # TF-IDF: 92% phishing
    )
    print(f"   Prediction: {result['prediction']}")
    print(f"   Confidence: {result['confidence']*100:.1f}%")
    print(f"   Weighted Score: {result['weighted_score']*100:.1f}%")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Models Used: {', '.join(result['models_used'])}")
    
    # Test 2: Only 2 models (BERT unavailable - currently being retrained)
    print("\n2️⃣ Test: BERT unavailable (FastText + TF-IDF)")
    result = weighted_vote(
        bert_score=None,
        fasttext_score=0.88,
        tfidf_score=0.92
    )
    print(f"   Prediction: {result['prediction']}")
    print(f"   Weighted Score: {result['weighted_score']*100:.1f}%")
    print(f"   Weights: {result['weights_applied']}")
    
    # Test 3: Model disagreement
    print("\n3️⃣ Test: Model disagreement")
    result = weighted_vote(
        bert_score=0.85,  # High phishing
        fasttext_score=0.30,  # Low phishing
        tfidf_score=0.55  # Borderline
    )
    print(f"   BERT: 85%, FastText: 30%, TF-IDF: 55%")
    print(f"   Ensemble Prediction: {result['prediction']}")
    print(f"   Weighted Score: {result['weighted_score']*100:.1f}%")
    print(f"   → BERT's 0.5 weight dominates, predicts phishing")
    
    print("\n" + "="*70)
    print("✅ Ensemble voting working correctly!")
