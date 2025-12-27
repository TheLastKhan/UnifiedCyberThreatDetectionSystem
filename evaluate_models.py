#!/usr/bin/env python3
"""
Model Performance Comparison & Weighted Voting Validation
Evaluates BERT, FastText, and TF-IDF on same test set to validate voting weights.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_test_data(n_samples=1000):
    """Load test data from phishing_email.csv"""
    logger.info("Loading test data...")
    df = pd.read_csv('data/processed/dataset/phishing_email.csv', encoding='utf-8')
    
    # Find text column
    text_col = None
    for col in ['body', 'text', 'text_combined', 'message']:
        if col in df.columns:
            text_col = col
            break
    
    df = df[[text_col, 'label']].dropna()
    df = df[df[text_col].str.len() > 20]
    
    # Sample for faster evaluation
    if len(df) > n_samples:
        df = df.sample(n=n_samples, random_state=42)
        # CRITICAL: Reset index to prevent label/text mismatch!
        df = df.reset_index(drop=True)
    
    logger.info(f"   ✅ Loaded {len(df)} test samples")
    logger.info(f"   📊 Phishing: {sum(df['label']==1)}, Legitimate: {sum(df['label']==0)}")
    
    return df[text_col].values, df['label'].values

def evaluate_tfidf(texts, y_true):
    """Evaluate TF-IDF model"""
    logger.info("\n1️⃣ Evaluating TF-IDF...")
    try:
        model = pickle.load(open('models/email_detector_rf.pkl', 'rb'))
        vectorizer = pickle.load(open('models/tfidf_vectorizer.pkl', 'rb'))
        
        X = vectorizer.transform(texts)
        y_pred = model.predict(X)
        y_pred_proba = model.predict_proba(X)[:, 1]  # Phishing probability
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_pred_proba)
        }
        
        logger.info(f"   ✅ TF-IDF Evaluated")
        return metrics, y_pred_proba
    except Exception as e:
        logger.error(f"   ❌ TF-IDF Error: {e}")
        return None, None

def evaluate_bert(texts, y_true):
    """Evaluate BERT model"""
    logger.info("\n2️⃣ Evaluating BERT...")
    try:
        import sys
        sys.path.append('src')
        from email_detector.bert_detector import BertEmailDetector
        
        # Load BERT model via constructor
        detector = BertEmailDetector(model_path='models/bert_phishing_detector')
        
        y_pred = []
        y_pred_proba = []
        
        # Test first sample for debugging
        logger.info(f"   🔍 Testing first sample...")
        first_result = detector.predict(texts[0])
        logger.info(f"      Label: {first_result.label}, Score: {first_result.score:.3f}")
        logger.info(f"      True label: {y_true[0]} (1=phishing, 0=legitimate)")
        
        for i, text in enumerate(texts):
            result = detector.predict(text)
            # CRITICAL: label is "phishing" or "legitimate"
            # result.score is phishing probability (0-1)
            pred_label = 1 if result.label == 'phishing' else 0
            y_pred.append(pred_label)
            y_pred_proba.append(result.score)
            
            # Debug first 5 predictions
            if i < 5:
                logger.info(f"      Sample {i}: pred={pred_label} (score={result.score:.3f}), true={y_true[i]}")
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_pred_proba)
        }
        
        logger.info(f"   ✅ BERT Evaluated")
        return metrics, np.array(y_pred_proba)
    except Exception as e:
        logger.error(f"   ❌ BERT Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def evaluate_fasttext(texts, y_true):
    """Evaluate FastText model"""
    logger.info("\n3️⃣ Evaluating FastText...")
    try:
        import sys
        sys.path.append('src')
        from email_detector.fasttext_detector import FastTextEmailDetector
        
        # Load FastText model via constructor
        detector = FastTextEmailDetector(model_path='models/fasttext_email_detector.bin')
        
        y_pred = []
        y_pred_proba = []
        
        # Test first sample for debugging
        logger.info(f"   🔍 Testing first sample...")
        first_result = detector.predict(texts[0])
        logger.info(f"      Label: {first_result.label}, Score: {first_result.score:.3f}")
        logger.info(f"      True label: {y_true[0]} (1=phishing, 0=legitimate)")
        
        for i, text in enumerate(texts):
            result = detector.predict(text)
            # CRITICAL: label is "phishing" or "legitimate"
            # result.score is phishing probability (0-1)
            pred_label = 1 if result.label == 'phishing' else 0
            y_pred.append(pred_label)
            y_pred_proba.append(result.score)
            
            # Debug first 5 predictions
            if i < 5:
                logger.info(f"      Sample {i}: pred={pred_label} (score={result.score:.3f}), true={y_true[i]}")
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred),
            'recall': recall_score(y_true, y_pred),
            'f1': f1_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_pred_proba)
        }
        
        logger.info(f"   ✅ FastText Evaluated")
        return metrics, np.array(y_pred_proba)
    except Exception as e:
        logger.error(f"   ❌ FastText Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def print_comparison(results):
    """Print comparison table"""
    logger.info("\n" + "="*70)
    logger.info("MODEL PERFORMANCE COMPARISON")
    logger.info("="*70)
    
    # Table header
    print(f"\n{'Metric':<15} {'BERT':<12} {'FastText':<12} {'TF-IDF':<12}")
    print("-" * 55)
    
    metrics_order = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    for metric in metrics_order:
        bert_val = results['bert'].get(metric, 0) * 100 if results['bert'] else 0
        fast_val = results['fasttext'].get(metric, 0) * 100 if results['fasttext'] else 0
        tfidf_val = results['tfidf'].get(metric, 0) * 100 if results['tfidf'] else 0
        
        print(f"{metric.upper():<15} {bert_val:>10.2f}%  {fast_val:>10.2f}%  {tfidf_val:>10.2f}%")
    
    logger.info("\n" + "="*70)

def validate_weights(results, weights={'bert': 0.5, 'fasttext': 0.3, 'tfidf': 0.2}):
    """Validate if proposed weights match model performance"""
    logger.info("\n4️⃣ Validating Weighted Voting Weights...")
    logger.info(f"   Proposed: BERT={weights['bert']}, FastText={weights['fasttext']}, TF-IDF={weights['tfidf']}")
    
    # Calculate performance-based weights (using F1 score)
    f1_scores = {
        'bert': results['bert']['f1'] if results['bert'] else 0,
        'fasttext': results['fasttext']['f1'] if results['fasttext'] else 0,
        'tfidf': results['tfidf']['f1'] if results['tfidf'] else 0
    }
    
    total_f1 = sum(f1_scores.values())
    recommended_weights = {k: v/total_f1 for k, v in f1_scores.items()}
    
    logger.info(f"\n   📊 Recommended (F1-based):")
    for model, weight in recommended_weights.items():
        logger.info(f"      {model.upper()}: {weight:.2f}")
    
    logger.info(f"\n   🔍 Comparison:")
    for model in weights:
        diff = abs(weights[model] - recommended_weights[model])
        status = "✅" if diff < 0.1 else "⚠️"
        logger.info(f"      {model.upper()}: Proposed={weights[model]:.2f}, Recommended={recommended_weights[model]:.2f}, Diff={diff:.2f} {status}")
    
    return recommended_weights

def main():
    logger.info("="*70)
    logger.info("MODEL EVALUATION & WEIGHT VALIDATION")
    logger.info("="*70)
    
    # Load test data
    texts, y_true = load_test_data(n_samples=500)  # Reduced for speed
    
    # Evaluate models
    results = {}
    probas = {}
    
    tfidf_metrics, tfidf_proba = evaluate_tfidf(texts, y_true)
    results['tfidf'] = tfidf_metrics
    probas['tfidf'] = tfidf_proba
    
    bert_metrics, bert_proba = evaluate_bert(texts, y_true)
    results['bert'] = bert_metrics
    probas['bert'] = bert_proba
    
    fasttext_metrics, fasttext_proba = evaluate_fasttext(texts, y_true)
    results['fasttext'] = fasttext_metrics
    probas['fasttext'] = fasttext_proba
    
    # Print comparison
    print_comparison(results)
    
    # Validate weights
    recommended = validate_weights(results)
    
    # Test weighted voting
    if all(v is not None for v in probas.values()):
        logger.info("\n5️⃣ Testing Weighted Voting...")
        weights = {'bert': 0.5, 'fasttext': 0.3, 'tfidf': 0.2}
        
        weighted_proba = (
            probas['bert'] * weights['bert'] +
            probas['fasttext'] * weights['fasttext'] +
            probas['tfidf'] * weights['tfidf']
        )
        weighted_pred = (weighted_proba > 0.5).astype(int)
        
        weighted_accuracy = accuracy_score(y_true, weighted_pred)
        logger.info(f"   🎯 Weighted Voting Accuracy: {weighted_accuracy:.2%}")
        
        # Compare with individual models
        logger.info(f"\n   📊 Comparison:")
        if results['bert']:
            logger.info(f"      BERT alone: {results['bert']['accuracy']:.2%}")
        if results['fasttext']:
            logger.info(f"      FastText alone: {results['fasttext']['accuracy']:.2%}")
        if results['tfidf']:
            logger.info(f"      TF-IDF alone: {results['tfidf']['accuracy']:.2%}")
        logger.info(f"      Weighted Ensemble: {weighted_accuracy:.2%}")
    
    logger.info("\n" + "="*70)
    logger.info("✅ EVALUATION COMPLETE")
    logger.info("="*70)

if __name__ == "__main__":
    main()
