"""
BERT Model Training Script
===========================

Fine-tune DistilBERT on phishing email dataset.
Trains on Enron, Nigerian Fraud, and Phishing datasets.

Training Steps:
1. Load and combine multiple email datasets
2. Prepare training/validation split
3. Fine-tune DistilBERT for 3 epochs
4. Evaluate on test set
5. Save fine-tuned model
6. Generate performance comparison report

Estimated time: 6-8 hours on CPU, 1-2 hours on GPU
"""

import os
import sys
import logging
from pathlib import Path
import json
import pandas as pd
import numpy as np
from typing import List, Tuple
import warnings

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.email_detector.bert_detector import BertTrainer, BertEmailDetector
from src.email_detector.detector import EmailDetector  # For TF-IDF comparison
from src.utils.data_loader import DataLoader

# Configuration
CONFIG = {
    "model_name": "distilbert-base-uncased",
    "epochs": 3,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "max_length": 512,
    "train_split": 0.8,
    "val_split": 0.1,
    "test_split": 0.1,
    "output_path": "models/bert_email_detector",
    "report_path": "reports/bert_training_report.json"
}


def load_email_datasets() -> Tuple[List[str], List[int]]:
    """
    Load multiple email datasets for training
    
    Sources:
    - Enron.csv: Legitimate business emails
    - Nigerian_Fraud.csv: Fraud/Phishing emails
    - phishing_email.csv: Phishing emails
    - CEAS_08.csv: Mixed spam/phishing
    
    Returns:
        (texts, labels) where labels are 0=legitimate, 1=phishing
    """
    logger.info("Loading email datasets...")
    
    dataset_path = Path("dataset")
    all_texts = []
    all_labels = []
    
    # Load legitimate emails (Enron)
    try:
        enron_df = pd.read_csv(dataset_path / "Enron.csv")
        # Use email body or subject
        if 'body' in enron_df.columns:
            texts = enron_df['body'].fillna('').astype(str).tolist()
        elif 'message' in enron_df.columns:
            texts = enron_df['message'].fillna('').astype(str).tolist()
        else:
            texts = enron_df.iloc[:, -1].fillna('').astype(str).tolist()
        
        all_texts.extend([t[:512] for t in texts if t.strip()])  # Truncate to 512 chars
        all_labels.extend([0] * len(texts))  # 0 = legitimate
        logger.info(f"Loaded {len(texts)} Enron emails (legitimate)")
    except Exception as e:
        logger.warning(f"Could not load Enron: {e}")
    
    # Load phishing emails (Nigerian Fraud)
    try:
        nigerian_df = pd.read_csv(dataset_path / "Nigerian_Fraud.csv")
        if 'email' in nigerian_df.columns:
            texts = nigerian_df['email'].fillna('').astype(str).tolist()
        else:
            texts = nigerian_df.iloc[:, 0].fillna('').astype(str).tolist()
        
        all_texts.extend([t[:512] for t in texts if t.strip()])
        all_labels.extend([1] * len(texts))  # 1 = phishing
        logger.info(f"Loaded {len(texts)} Nigerian Fraud emails (phishing)")
    except Exception as e:
        logger.warning(f"Could not load Nigerian Fraud: {e}")
    
    # Load phishing emails (phishing_email.csv)
    try:
        phishing_df = pd.read_csv(dataset_path / "phishing_email.csv")
        if 'body' in phishing_df.columns:
            texts = phishing_df['body'].fillna('').astype(str).tolist()
        elif 'text' in phishing_df.columns:
            texts = phishing_df['text'].fillna('').astype(str).tolist()
        else:
            texts = phishing_df.iloc[:, -1].fillna('').astype(str).tolist()
        
        all_texts.extend([t[:512] for t in texts if t.strip()])
        all_labels.extend([1] * len(texts))  # 1 = phishing
        logger.info(f"Loaded {len(texts)} Phishing emails")
    except Exception as e:
        logger.warning(f"Could not load phishing_email: {e}")
    
    # Load CEAS_08 (mixed spam/phishing)
    try:
        ceas_df = pd.read_csv(dataset_path / "CEAS_08.csv")
        # Usually these are spam/phishing labeled
        if 'body' in ceas_df.columns:
            texts = ceas_df['body'].fillna('').astype(str).tolist()
        else:
            texts = ceas_df.iloc[:, 0].fillna('').astype(str).tolist()
        
        # Assume CEAS are mostly phishing/spam
        all_texts.extend([t[:512] for t in texts if t.strip()])
        all_labels.extend([1] * len(texts))  # 1 = phishing
        logger.info(f"Loaded {len(texts)} CEAS_08 emails")
    except Exception as e:
        logger.warning(f"Could not load CEAS_08: {e}")
    
    # Remove empty texts
    valid_indices = [i for i, t in enumerate(all_texts) if t.strip()]
    texts = [all_texts[i] for i in valid_indices]
    labels = [all_labels[i] for i in valid_indices]
    
    logger.info(f"Total emails loaded: {len(texts)}")
    logger.info(f"Legitimate: {sum(1 for l in labels if l == 0)}")
    logger.info(f"Phishing: {sum(1 for l in labels if l == 1)}")
    
    return texts, labels


def split_dataset(
    texts: List[str],
    labels: List[int],
    train_split: float = 0.8,
    val_split: float = 0.1,
    test_split: float = 0.1,
) -> Tuple[List[str], List[int], List[str], List[int], List[str], List[int]]:
    """
    Split dataset into train/validation/test
    
    Returns:
        (train_texts, train_labels, val_texts, val_labels, test_texts, test_labels)
    """
    # Shuffle
    indices = np.random.permutation(len(texts))
    texts = [texts[i] for i in indices]
    labels = [labels[i] for i in indices]
    
    n = len(texts)
    train_end = int(n * train_split)
    val_end = train_end + int(n * val_split)
    
    train_texts = texts[:train_end]
    train_labels = labels[:train_end]
    
    val_texts = texts[train_end:val_end]
    val_labels = labels[train_end:val_end]
    
    test_texts = texts[val_end:]
    test_labels = labels[val_end:]
    
    logger.info(f"Dataset split:")
    logger.info(f"  Train: {len(train_texts)} samples")
    logger.info(f"  Val:   {len(val_texts)} samples")
    logger.info(f"  Test:  {len(test_texts)} samples")
    
    return train_texts, train_labels, val_texts, val_labels, test_texts, test_labels


def train_bert_model():
    """
    Main training function
    
    1. Load datasets
    2. Split into train/val/test
    3. Fine-tune DistilBERT
    4. Evaluate
    5. Save model
    6. Generate report
    """
    logger.info("="*60)
    logger.info("BERT MODEL TRAINING")
    logger.info("="*60)
    
    # Load data
    texts, labels = load_email_datasets()
    
    if len(texts) < 100:
        logger.warning("Dataset is very small! Training may not be effective.")
        logger.info("Try loading more datasets or using data augmentation.")
    
    # Split dataset
    train_texts, train_labels, val_texts, val_labels, test_texts, test_labels = split_dataset(
        texts, labels,
        train_split=CONFIG["train_split"],
        val_split=CONFIG["val_split"],
        test_split=CONFIG["test_split"],
    )
    
    # Initialize trainer
    logger.info(f"Initializing trainer with model: {CONFIG['model_name']}")
    trainer = BertTrainer(model_name=CONFIG["model_name"])
    
    # Train model
    logger.info("Starting training...")
    training_stats = trainer.train(
        train_texts=train_texts,
        train_labels=train_labels,
        val_texts=val_texts,
        val_labels=val_labels,
        epochs=CONFIG["epochs"],
        learning_rate=CONFIG["learning_rate"],
        batch_size=CONFIG["batch_size"],
    )
    
    # Evaluate on test set
    logger.info("Evaluating on test set...")
    test_loss, test_accuracy = trainer.evaluate(
        texts=test_texts,
        labels=test_labels,
        batch_size=CONFIG["batch_size"]
    )
    
    logger.info(f"Test Loss: {test_loss:.4f}")
    logger.info(f"Test Accuracy: {test_accuracy:.2%}")
    
    # Save model
    logger.info(f"Saving model to {CONFIG['output_path']}...")
    trainer.save_model(CONFIG["output_path"])
    
    # Load saved model and test
    logger.info("Loading saved model for verification...")
    detector = BertEmailDetector(model_path=CONFIG["output_path"])
    
    # Test on sample phishing emails
    test_samples = [
        "Click here to verify your account now or it will be closed!",
        "Confirm your password by clicking this link immediately",
        "Update your payment information to avoid service interruption",
        "You have won $1,000,000! Click to claim your prize!",
    ]
    
    logger.info("\nSample predictions on phishing emails:")
    for sample in test_samples:
        result = detector.predict(sample)
        logger.info(f"  '{sample[:50]}...' -> {result.label.upper()} ({result.score:.1%})")
    
    # Generate report
    report = {
        "model_name": CONFIG["model_name"],
        "training_date": str(pd.Timestamp.now()),
        "dataset_info": {
            "total_samples": len(texts),
            "train_samples": len(train_texts),
            "val_samples": len(val_texts),
            "test_samples": len(test_texts),
            "legitimate_count": sum(1 for l in labels if l == 0),
            "phishing_count": sum(1 for l in labels if l == 1),
        },
        "hyperparameters": {
            "epochs": CONFIG["epochs"],
            "batch_size": CONFIG["batch_size"],
            "learning_rate": CONFIG["learning_rate"],
            "max_length": CONFIG["max_length"],
        },
        "training_stats": training_stats,
        "test_metrics": {
            "loss": float(test_loss),
            "accuracy": float(test_accuracy),
        },
        "model_path": CONFIG["output_path"],
        "status": "completed",
    }
    
    # Save report
    Path(CONFIG["report_path"]).parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG["report_path"], "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report saved to {CONFIG['report_path']}")
    logger.info("\n" + "="*60)
    logger.info("TRAINING COMPLETED SUCCESSFULLY!")
    logger.info("="*60)
    
    return report


if __name__ == "__main__":
    try:
        report = train_bert_model()
        print("\n✅ BERT Model training completed!")
        print(f"Model saved to: {CONFIG['output_path']}")
        print(f"Test Accuracy: {report['test_metrics']['accuracy']:.2%}")
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)
