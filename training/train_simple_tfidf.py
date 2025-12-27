#!/usr/bin/env python3
"""
Simple TF-IDF Email Phishing Detector Trainer
Clean, focused script that trains ONLY on the known-good phishing_email.csv dataset.
"""

import pandas as pd
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 70)
    logger.info("SIMPLE TF-IDF PHISHING DETECTOR TRAINING")
    logger.info("=" * 70)
    
    # 1. LOAD DATA
    logger.info("\n📁 Loading phishing_email.csv...")
    try:
        df = pd.read_csv('data/processed/dataset/phishing_email.csv', encoding='utf-8')
        logger.info(f"   ✅ Loaded {len(df)} emails")
        logger.info(f"   📊 Label distribution:\n{df['label'].value_counts()}")
    except Exception as e:
        logger.error(f"   ❌ Failed to load dataset: {e}")
        return
    
    # 2. PREPARE DATA
    logger.info("\n🔧 Preparing data...")
    
    # Find text column
    text_col = None
    for col in ['body', 'text', 'text_combined', 'message', 'email_text']:
        if col in df.columns:
            text_col = col
            break
    
    if text_col is None:
        logger.error(f"   ❌ No text column found! Available columns: {df.columns.tolist()}")
        return
    
    logger.info(f"   ✅ Using text column: '{text_col}'")
    
    # Clean data
    df = df[[text_col, 'label']].copy()
    df = df.dropna()
    df = df[df[text_col].str.len() > 20]  # Remove very short texts
    
    X = df[text_col].values
    y = df['label'].values
    
    logger.info(f"   ✅ Final dataset: {len(X)} emails")
    logger.info(f"   📊 Phishing: {sum(y==1)}, Legitimate: {sum(y==0)}")
    
    # 3. SPLIT DATA
    logger.info("\n✂️ Splitting train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(f"   ✅ Train: {len(X_train)}, Test: {len(X_test)}")
    
    # 4. TF-IDF VECTORIZATION
    logger.info("\n🔤 Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        min_df=2,
        max_df=0.95,
        ngram_range=(1, 2),
        stop_words='english'
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    logger.info(f"   ✅ Vocabulary size: {len(vectorizer.vocabulary_)}")
    logger.info(f"   ✅ Train shape: {X_train_vec.shape}")
    
    # 5. TRAIN RANDOM FOREST
    logger.info("\n🌲 Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=50,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train_vec, y_train)
    logger.info(f"   ✅ Training complete!")
    
    # 6. EVALUATE
    logger.info("\n📊 Evaluating model...")
    y_pred = model.predict(X_test_vec)
    y_pred_proba = model.predict_proba(X_test_vec)
    
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"\n   🎯 ACCURACY: {accuracy:.2%}")
    
    logger.info(f"\n   📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))
    
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"\n   📊 Confusion Matrix:")
    logger.info(f"        Pred Legit  Pred Phishing")
    logger.info(f"   Legit:    {cm[0][0]:5d}      {cm[0][1]:5d}")
    logger.info(f"   Phish:    {cm[1][0]:5d}      {cm[1][1]:5d}")
    
    # 7. TEST WITH KNOWN PHISHING EMAIL
    logger.info("\n🧪 Testing with known phishing email...")
    test_email = """
    Dear customer,
    Your account has been SUSPENDED! 
    Verify urgently: http://paypal-security-verify.com/login.php
    Provide your credit card, CVV, and social security number NOW!
    """
    
    test_vec = vectorizer.transform([test_email])
    test_pred = model.predict(test_vec)[0]
    test_proba = model.predict_proba(test_vec)[0]
    
    logger.info(f"   Prediction: {'PHISHING' if test_pred == 1 else 'LEGITIMATE'}")
    logger.info(f"   Confidence: Legit={test_proba[0]:.1%}, Phishing={test_proba[1]:.1%}")
    
    if test_pred == 1:
        logger.info(f"   ✅ CORRECT! Successfully detected phishing.")
    else:
        logger.info(f"   ❌ WRONG! Model failed to detect phishing!")
        logger.warning(f"   ⚠️ Model may need more training or better features.")
    
    # 8. SAVE MODEL
    if test_pred == 1 and accuracy > 0.85:
        logger.info("\n💾 Saving model and vectorizer...")
        
        Path("models").mkdir(exist_ok=True)
        
        with open('models/email_detector_rf.pkl', 'wb') as f:
            pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"   ✅ Saved: models/email_detector_rf.pkl")
        
        with open('models/tfidf_vectorizer.pkl', 'wb') as f:
            pickle.dump(vectorizer, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"   ✅ Saved: models/tfidf_vectorizer.pkl")
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ TRAINING COMPLETE AND SUCCESSFUL!")
        logger.info(f"   Accuracy: {accuracy:.2%}")
        logger.info(f"   Test phishing detection: PASSED")
        logger.info("=" * 70)
    else:
        logger.error("\n❌ Model quality check FAILED! Not saving model.")
        logger.error(f"   Accuracy: {accuracy:.2%} (need >85%)")
        logger.error(f"   Phishing test: {'PASSED' if test_pred == 1 else 'FAILED'}")

if __name__ == "__main__":
    main()
