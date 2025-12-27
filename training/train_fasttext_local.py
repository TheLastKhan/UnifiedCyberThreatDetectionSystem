"""
FastText Model Training Script (Local Version)
==============================================

Train FastText model for email phishing detection
Same approach as BERT training - uses local CSV files

Training Steps:
1. Load and combine multiple email datasets from dataset/ folder
2. Preprocess text
3. Create FastText format files
4. Train FastText model
5. Evaluate on test set
6. Save model to models/ folder

Estimated time: 5-10 minutes on any machine
"""

import os
import sys
import re
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import fasttext
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Suppress FastText warnings
if hasattr(fasttext.FastText, 'eprint'):
    fasttext.FastText.eprint = lambda x: None

def load_email_datasets():
    """
    Load multiple email datasets for training
    Same datasets as BERT training
    
    Returns:
        (texts, labels) where labels are 'legitimate' or 'phishing'
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
                continue
            
            texts = df[text_col].fillna('').astype(str).tolist()
            labels = df[label_col].tolist()
            labels = ['phishing' if str(l).lower() in ['1', 'spam', 'phishing', 'yes', 'true'] else 'legitimate' for l in labels]
            
            all_texts.extend(texts)
            all_labels.extend(labels)
            
            logger.info(f"✅ Loaded {name}: {len(texts)} emails")
            
        except Exception as e:
            logger.error(f"❌ Error loading {name}: {str(e)}")
    
    logger.info(f"\n📊 Total emails loaded: {len(all_texts)}")
    phishing_count = sum(1 for l in all_labels if l == 'phishing')
    logger.info(f"   Phishing: {phishing_count} ({phishing_count/len(all_labels)*100:.1f}%)")
    logger.info(f"   Legitimate: {len(all_labels)-phishing_count} ({(len(all_labels)-phishing_count)/len(all_labels)*100:.1f}%)")
    
    return all_texts, all_labels

def preprocess_text(text):
    """
    Preprocess text for FastText training
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def train_fasttext_model():
    """
    Main training function
    """
    logger.info("\n" + "="*70)
    logger.info("🚀 FASTTEXT TRAINING (Local Version)")
    logger.info("="*70)
    
    # Step 1: Load data
    all_texts, all_labels = load_email_datasets()
    
    if len(all_texts) == 0:
        logger.error("No emails loaded! Please check dataset folder.")
        sys.exit(1)
    
    # Step 2: Preprocess text
    logger.info("\n[2/8] Preprocessing text...")
    processed_texts = [preprocess_text(text) for text in tqdm(all_texts, desc="Processing")]
    logger.info("✅ Text preprocessed")
    
    # Step 3: Split dataset
    logger.info("\n[3/8] Splitting dataset (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        processed_texts, all_labels, test_size=0.2, random_state=42, stratify=all_labels
    )
    logger.info(f"✅ Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Step 4: Create FastText format files
    logger.info("\n[4/8] Creating FastText format files...")
    
    with open('train_fasttext.txt', 'w', encoding='utf-8') as f:
        for text, label in zip(X_train, y_train):
            f.write(f'__label__{label} {text}\n')
    
    with open('test_fasttext.txt', 'w', encoding='utf-8') as f:
        for text, label in zip(X_test, y_test):
            f.write(f'__label__{label} {text}\n')
    
    logger.info("✅ Training files created")
    
    # Step 5: Train FastText model
    logger.info("\n[5/8] Training FastText model...")
    logger.info("⏱️  This will take 5-10 minutes...")
    
    model = fasttext.train_supervised(
        input='train_fasttext.txt',
        lr=0.5,
        epoch=25,
        wordNgrams=2,
        dim=100,
        loss='softmax'
    )
    
    logger.info("✅ Model trained!")
    
    # Step 6: Test with obvious phishing email
    logger.info("\n[6/8] Testing model...")
    
    test_email = """
    urgent your paypal account suspended verify identity immediately
    click here http fake paypal verify com enter ssn credit card
    final warning act now or lose access forever
    """
    
    labels, scores = model.predict(test_email)
    label = labels[0].replace('__label__', '')
    confidence = float(scores[0])
    
    logger.info(f"\n📧 Test Email (Obvious Phishing):")
    logger.info(f"   Prediction: {label}")
    logger.info(f"   Confidence: {confidence*100:.1f}%")
    
    if label == 'phishing' and confidence > 0.8:
        logger.info("   🎉 SUCCESS! Model working correctly")
    else:
        logger.warning("   ⚠️  Model needs improvement")
    
    # Step 7: Evaluate on test set
    logger.info("\n[7/8] Evaluating on full test set...")
    
    y_pred = []
    for text in tqdm(X_test, desc="Predicting"):
        pred_labels, _ = model.predict(text)
        pred = pred_labels[0].replace('__label__', '')
        y_pred.append(pred)
    
    logger.info("\n📊 Test Set Results:")
    print(classification_report(y_test, y_pred, target_names=['legitimate', 'phishing']))
    logger.info(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
    
    # Step 8: Save model
    logger.info("\n[8/8] Saving model...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = models_dir / 'fasttext_email_detector.bin'
    model.save_model(str(model_path))
    
    logger.info("\n" + "="*70)
    logger.info("✅ Training Complete!")
    logger.info("="*70)
    logger.info(f"📦 Model saved: {model_path}")
    logger.info("   Size: ~885 MB")
    logger.info(f"\n🎯 Phishing detection: {confidence*100:.1f}% (target: 80%+)")
    
    # Cleanup training files
    try:
        os.remove('train_fasttext.txt')
        os.remove('test_fasttext.txt')
        logger.info("\n🧹 Cleaned up temporary files")
    except:
        pass

if __name__ == "__main__":
    try:
        train_fasttext_model()
        print("\n✅ FastText Model training completed!")
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)
