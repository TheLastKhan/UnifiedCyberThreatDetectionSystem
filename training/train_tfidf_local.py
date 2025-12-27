"""
TF-IDF Model Training Script (Local Version)
=============================================

Train TF-IDF + Ensemble Models with Balanced Dataset
Same approach as BERT training - uses local CSV files

Training Steps:
1. Load and combine multiple email datasets from dataset/ folder
2. Balance with SMOTE
3. Train Voting + Stacking classifiers
4. Evaluate on test set
5. Save models to models/ folder

Estimated time: 10-15 minutes on any machine
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

try:
    from imblearn.over_sampling import SMOTE
except ImportError:
    logger.error("SMOTE not available. Install with: pip install imbalanced-learn")
    sys.exit(1)

def load_email_datasets():
    """
    Load multiple email datasets for training
    Same datasets as BERT training
    
    Returns:
        (texts, labels) where labels are 0=legitimate, 1=phishing
    """
    logger.info("="*70)
    logger.info("Loading email datasets from dataset/ folder...")
    logger.info("="*70)
    
    dataset_dir = Path("dataset")
    dataset_files = {
        'CEAS_08': dataset_dir / 'CEAS_08.csv',
        'Enron': dataset_dir / 'Enron.csv',
        'Ling': dataset_dir / 'Ling.csv',
        'Nazario': dataset_dir / 'Nazario.csv',
        'Nigerian_Fraud': dataset_dir / 'Nigerian_Fraud.csv',
        'SpamAssasin': dataset_dir / 'SpamAssasin.csv',
        'phishing_email': dataset_dir / 'phishing_email.csv'
    }
    
    all_texts = []
    all_labels = []
    
    for name, path in tqdm(dataset_files.items(), desc="Loading datasets"):
        try:
            if not path.exists():
                logger.warning(f"⚠️  Skipping {name}: File not found")
                continue
                
            df = pd.read_csv(path)
            
            # Find text column
            text_col = None
            for col in ['text', 'email_text', 'body', 'message', 'content', 'Email Text']:
                if col in df.columns:
                    text_col = col
                    break
            
            # Find label column
            label_col = None
            for col in ['label', 'Label', 'target', 'class', 'spam']:
                if col in df.columns:
                    label_col = col
                    break
            
            if text_col is None or label_col is None:
                logger.warning(f"⚠️  Skipping {name}: Could not find text or label column")
                logger.warning(f"    Available columns: {df.columns.tolist()}")
                continue
            
            texts = df[text_col].fillna('').astype(str).tolist()
            labels = df[label_col].tolist()
            labels = [1 if str(label).lower() in ['1', 'spam', 'phishing', 'yes', 'true'] else 0 for label in labels]
            
            all_texts.extend(texts)
            all_labels.extend(labels)
            
            logger.info(f"✅ Loaded {name}: {len(texts)} emails")
            
        except Exception as e:
            logger.error(f"❌ Error loading {name}: {str(e)}")
    
    logger.info(f"\n📊 Total emails loaded: {len(all_texts)}")
    logger.info(f"   Phishing: {sum(all_labels)} ({sum(all_labels)/len(all_labels)*100:.1f}%)")
    logger.info(f"   Legitimate: {len(all_labels)-sum(all_labels)} ({(len(all_labels)-sum(all_labels))/len(all_labels)*100:.1f}%)")
    
    return all_texts, all_labels

def train_tfidf_model():
    """
    Main training function
    """
    logger.info("\n" + "="*70)
    logger.info("🚀 TF-IDF + ENSEMBLE TRAINING (Local Version)")
    logger.info("="*70)
    
    # Step 1: Load data
    all_texts, all_labels = load_email_datasets()
    
    if len(all_texts) == 0:
        logger.error("No emails loaded! Please check dataset folder.")
        sys.exit(1)
    
    # Step 2: Split dataset
    logger.info("\n[2/10] Splitting dataset (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        all_texts, all_labels, test_size=0.2, random_state=42, stratify=all_labels
    )
    logger.info(f"✅ Training: {len(X_train)} emails, Testing: {len(X_test)} emails")
    
    # Step 3: TF-IDF Vectorization
    logger.info("\n[3/10] Creating TF-IDF features...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        stop_words='english'
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    logger.info(f"✅ TF-IDF features created: {X_train_vec.shape[1]} features")
    
    # Step 4: Balance with SMOTE
    logger.info("\n[4/10] Balancing dataset with SMOTE...")
    smote = SMOTE(random_state=42, k_neighbors=3)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train_vec, y_train)
    logger.info(f"✅ Dataset balanced:")
    logger.info(f"   Before: {sum(y_train)} phishing, {len(y_train)-sum(y_train)} legitimate")
    logger.info(f"   After: {sum(y_train_balanced)} phishing, {len(y_train_balanced)-sum(y_train_balanced)} legitimate")
    
    # Step 5: Train Random Forest
    logger.info("\n[5/10] Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train_balanced, y_train_balanced)
    logger.info("✅ Random Forest trained")
    
    # Step 6: Train XGBoost
    logger.info("\n[6/10] Training XGBoost...")
    xgb = XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss', n_jobs=-1)
    xgb.fit(X_train_balanced, y_train_balanced)
    logger.info("✅ XGBoost trained")
    
    # Step 7: Train LightGBM
    logger.info("\n[7/10] Training LightGBM...")
    lgbm = LGBMClassifier(n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
    lgbm.fit(X_train_balanced, y_train_balanced)
    logger.info("✅ LightGBM trained")
    
    # Step 8: Create Voting Classifier
    logger.info("\n[8/10] Creating Voting Classifier...")
    voting_clf = VotingClassifier(
        estimators=[('rf', rf), ('xgb', xgb), ('lgbm', lgbm)],
        voting='soft'
    )
    voting_clf.fit(X_train_balanced, y_train_balanced)
    logger.info("✅ Voting Classifier trained")
    
    # Step 9: Create Stacking Classifier
    logger.info("\n[9/10] Creating Stacking Classifier...")
    stacking_clf = StackingClassifier(
        estimators=[('rf', rf), ('xgb', xgb), ('lgbm', lgbm)],
        final_estimator=LogisticRegression(max_iter=1000),
        cv=5
    )
    stacking_clf.fit(X_train_balanced, y_train_balanced)
    logger.info("✅ Stacking Classifier trained")
    
    # Step 10: Evaluate
    logger.info("\n[10/10] Evaluating models...")
    
    # Test with obvious phishing email
    test_email = """
    URGENT! Your PayPal account has been suspended due to suspicious activity.
    You must verify your identity immediately to avoid permanent account closure.
    Click here: http://fake-paypal-verify.com/account/login.php
    Enter your full name, SSN, credit card number, and CVV to verify.
    This is your FINAL WARNING! Act now or lose access forever!
    """
    
    test_vec = vectorizer.transform([test_email])
    voting_proba = voting_clf.predict_proba(test_vec)[0]
    stacking_proba = stacking_clf.predict_proba(test_vec)[0]
    
    logger.info("\n📧 Test Email (Obvious Phishing):")
    logger.info(f"   Voting Classifier: {voting_proba[1]*100:.1f}% phishing")
    logger.info(f"   Stacking Classifier: {stacking_proba[1]*100:.1f}% phishing")
    
    avg_phishing = (voting_proba[1] + stacking_proba[1]) / 2
    if avg_phishing > 0.8:
        logger.info(f"   🎉 SUCCESS! Average: {avg_phishing*100:.1f}% (>80%)")
    else:
        logger.warning(f"   ⚠️  WARNING: Average: {avg_phishing*100:.1f}% (<80%)")
    
    # Full test set evaluation
    y_pred_voting = voting_clf.predict(X_test_vec)
    y_pred_stacking = stacking_clf.predict(X_test_vec)
    
    logger.info("\n📊 Test Set Performance:")
    logger.info("\nVoting Classifier:")
    print(classification_report(y_test, y_pred_voting, target_names=['Legitimate', 'Phishing']))
    logger.info(f"AUC-ROC: {roc_auc_score(y_test, voting_clf.predict_proba(X_test_vec)[:, 1]):.4f}")
    
    logger.info("\nStacking Classifier:")
    print(classification_report(y_test, y_pred_stacking, target_names=['Legitimate', 'Phishing']))
    logger.info(f"AUC-ROC: {roc_auc_score(y_test, stacking_clf.predict_proba(X_test_vec)[:, 1]):.4f}")
    
    # Save models
    logger.info("\n" + "="*70)
    logger.info("Saving models to models/ folder...")
    logger.info("="*70)
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    joblib.dump(vectorizer, models_dir / 'tfidf_vectorizer.pkl')
    logger.info("✅ Saved: tfidf_vectorizer.pkl")
    
    joblib.dump(voting_clf, models_dir / 'email_detector_voting.pkl')
    logger.info("✅ Saved: email_detector_voting.pkl")
    
    joblib.dump(stacking_clf, models_dir / 'email_detector_stacking.pkl')
    logger.info("✅ Saved: email_detector_stacking.pkl")
    
    logger.info("\n" + "="*70)
    logger.info("✅ Training Complete!")
    logger.info("="*70)
    logger.info(f"📦 Models saved in: models/")
    logger.info("   • tfidf_vectorizer.pkl (~180 KB)")
    logger.info("   • email_detector_voting.pkl (~30 MB)")
    logger.info("   • email_detector_stacking.pkl (~30 MB)")
    logger.info(f"\n🎯 Phishing detection: {avg_phishing*100:.1f}% (target: 80%+)")

if __name__ == "__main__":
    try:
        train_tfidf_model()
        print("\n✅ TF-IDF Model training completed!")
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)
