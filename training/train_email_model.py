"""
AŞAMA 4.4: Model Training Script
==================================

Train email phishing detection models:
1. Random Forest (TF-IDF features)
2. BERT-based detection (if available)
3. Ensemble model
4. Model evaluation and reporting
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import json
from typing import Tuple, Dict, Any
import pickle
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_detector.detector import EmailPhishingDetector


class ModelTrainer:
    """Train and evaluate email detection models."""
    
    def __init__(self, data_path: str = "data/processed", models_path: str = "models"):
        self.data_path = Path(data_path)
        self.models_path = Path(models_path)
        self.models_path.mkdir(exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "models": {}
        }
    
    def load_training_data(self) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """Load and prepare training data from cleaned datasets."""
        logger.info("="*60)
        logger.info("LOADING TRAINING DATA")
        logger.info("="*60)
        
        all_texts = []
        all_labels = []
        all_metadata = []
        
        # Search for CSV files recursively
        csv_files = list(self.data_path.glob("**/*.csv"))
        logger.info(f"\n📁 Found {len(csv_files)} CSV files\n")
        
        for filepath in csv_files:
            try:
                df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
                
                # Check if dataset has label column (prioritize this!)
                has_label_column = False
                label_col = None
                for col in ['label', 'Label', 'class', 'Class', 'is_spam', 'is_phishing']:
                    if col in df.columns:
                        has_label_column = True
                        label_col = col
                        break
                
                # If no label column, infer from filename
                if not has_label_column:
                    filename = filepath.name.lower()
                    if 'phishing' in filename or 'spam' in filename or 'nigerian' in filename or 'fraud' in filename:
                        default_label = 1  # Phishing/Spam
                    else:
                        default_label = 0  # Legitimate
                    logger.info(f"📁 Loading: {filepath.relative_to(self.data_path)} ({len(df)} rows, inferred_label={default_label})")
                else:
                    logger.info(f"📁 Loading: {filepath.relative_to(self.data_path)} ({len(df)} rows, using column '{label_col}')")
                
                # Detect text columns
                text_columns = df.select_dtypes(include=['object']).columns.tolist()
                
                # Use most relevant column
                text_col = None
                for col in ['body', 'text', 'message', 'Message', 'email_text', 'Body', 'content', 'Content']:
                    if col in text_columns:
                        text_col = col
                        break
                
                if text_col is None and text_columns:
                    text_col = text_columns[0]
                
                if text_col is None:
                    logger.warning(f"  ⚠️ No text column found")
                    continue
                
                # Extract texts
                texts = df[text_col].fillna("").astype(str)
                
                # Clean empty texts
                mask = texts.str.len() > 10
                texts = texts[mask]
                
                # Get corresponding labels
                if has_label_column:
                    # Use actual labels from dataset
                    labels = df[label_col][mask].astype(int).tolist()
                else:
                    # Use inferred label for all rows
                    labels = [default_label] * len(texts)
                
                logger.info(f"  ✅ Extracted {len(texts)} texts from '{text_col}'")
                if has_label_column:
                    label_counts = pd.Series(labels).value_counts().to_dict()
                    logger.info(f"  📊 Label distribution: {label_counts}")
                
                all_texts.extend(texts.tolist())
                all_labels.extend(labels)
                
                # Store metadata
                for i, (text, label) in enumerate(zip(texts, labels)):
                    all_metadata.append({
                        "source": filepath.name,
                        "label": label,
                        "length": len(text)
                    })
                
            except Exception as e:
                logger.error(f"  ❌ Error loading {filepath.name}: {e}")
        
        if not all_texts:
            logger.error("❌ No text data found! Exiting...")
            raise ValueError("No text data loaded")
        
        # Sample to avoid memory issues (max 50K samples)
        if len(all_texts) > 50000:
            logger.info(f"\n📉 Sampling data to avoid memory issues ({len(all_texts)} → 50000)")
            indices = np.random.choice(len(all_texts), size=50000, replace=False)
            all_texts = [all_texts[i] for i in indices]
            all_labels = [all_labels[i] for i in indices]
        
        # Keep as lists, not numpy arrays (to save memory)
        y = np.array(all_labels)
        metadata = pd.DataFrame(all_metadata)
        
        logger.info(f"\n✅ Total samples loaded: {len(all_texts)}")
        logger.info(f"  • Legitimate (0): {(y == 0).sum()}")
        logger.info(f"  • Phishing/Spam (1): {(y == 1).sum()}")
        
        return all_texts, y, metadata
    
    def train_random_forest_model(self, texts_list: list, y: np.ndarray) -> Dict[str, Any]:
        """Train Random Forest model with TF-IDF features."""
        logger.info("\n" + "="*60)
        logger.info("TRAINING RANDOM FOREST MODEL")
        logger.info("="*60)
        
        logger.info(f"\n🔤 TF-IDF Vectorization...")
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=2
        )
        
        # Fit and transform texts
        X = vectorizer.fit_transform(texts_list)
        logger.info(f"  ✅ Feature matrix shape: {X.shape}")
        
        # Split data (on vectorized sparse matrix)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"\n📊 Data split:")
        logger.info(f"  • Training: {X_train.shape[0]} samples")
        logger.info(f"  • Testing: {X_test.shape[0]} samples")
        
        # Train Random Forest
        logger.info(f"\n🌲 Training Random Forest classifier...")
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            n_jobs=-1,
            random_state=42,
            verbose=1
        )
        
        model.fit(X_train, y_train)
        logger.info(f"  ✅ Model training complete")
        
        # Evaluation
        logger.info(f"\n📈 Model Evaluation:")
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        results = {
            "model_type": "RandomForest",
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "f1": float(f1_score(y_test, y_pred)),
            "roc_auc": float(roc_auc_score(y_test, y_pred_proba)),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "train_samples": X_train.shape[0],
            "test_samples": X_test.shape[0],
            "feature_count": X.shape[1],
        }
        
        logger.info(f"  • Accuracy:  {results['accuracy']:.4f}")
        logger.info(f"  • Precision: {results['precision']:.4f}")
        logger.info(f"  • Recall:    {results['recall']:.4f}")
        logger.info(f"  • F1-Score:  {results['f1']:.4f}")
        logger.info(f"  • ROC-AUC:   {results['roc_auc']:.4f}")
        
        # Save model
        model_path = self.models_path / "email_detector_rf.pkl"
        vectorizer_path = self.models_path / "tfidf_vectorizer.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(vectorizer, vectorizer_path)
        
        logger.info(f"\n💾 Model saved: {model_path}")
        logger.info(f"   Vectorizer saved: {vectorizer_path}")
        
        # Feature importance
        feature_names = vectorizer.get_feature_names_out()
        importances = model.feature_importances_
        top_indices = np.argsort(importances)[-20:][::-1]
        
        logger.info(f"\n⭐ Top 20 Important Features:")
        for i, idx in enumerate(top_indices, 1):
            logger.info(f"  {i:2d}. {feature_names[idx]:20s} (importance: {importances[idx]:.4f})")
        
        results["top_features"] = [
            {"feature": feature_names[idx], "importance": float(importances[idx])}
            for idx in top_indices
        ]
        
        return results, model, vectorizer, X_test, y_test, y_pred, y_pred_proba
    
    def generate_visualizations(self, model_results: Dict, y_test, y_pred, y_pred_proba):
        """Generate model evaluation visualizations."""
        logger.info(f"\n📊 Generating visualizations...")
        
        viz_dir = self.models_path / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # Confusion Matrix
        cm = np.array(model_results["confusion_matrix"])
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Legitimate', 'Phishing'],
                   yticklabels=['Legitimate', 'Phishing'])
        plt.title('Confusion Matrix - Email Detector')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(viz_dir / "confusion_matrix.png", dpi=150)
        plt.close()
        logger.info(f"  ✅ Confusion matrix saved")
        
        # ROC Curve
        from sklearn.metrics import roc_curve, auc
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve - Email Detector')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(viz_dir / "roc_curve.png", dpi=150)
        plt.close()
        logger.info(f"  ✅ ROC curve saved")
        
        # Metrics comparison
        metrics = {
            'Accuracy': model_results['accuracy'],
            'Precision': model_results['precision'],
            'Recall': model_results['recall'],
            'F1-Score': model_results['f1'],
        }
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(metrics.keys(), metrics.values(), color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        plt.ylim([0, 1])
        plt.ylabel('Score')
        plt.title('Model Performance Metrics')
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(viz_dir / "metrics_comparison.png", dpi=150)
        plt.close()
        logger.info(f"  ✅ Metrics comparison saved")
    
    def train_all_models(self):
        """Train all models and generate reports."""
        # Load data
        texts_list, y, metadata = self.load_training_data()
        
        # Train Random Forest (texts_list is already a list)
        rf_results, rf_model, vectorizer, X_test, y_test, y_pred, y_pred_proba = \
            self.train_random_forest_model(texts_list, y)
        
        self.results["models"]["random_forest"] = rf_results
        
        # Generate visualizations
        self.generate_visualizations(rf_results, y_test, y_pred, y_pred_proba)
        
        # Save results
        self._save_results()
        
        logger.info("\n" + "="*60)
        logger.info("✅ MODEL TRAINING COMPLETE")
        logger.info("="*60)
    
    def _save_results(self):
        """Save training results to JSON."""
        report_file = Path("reports") / f"model_training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"📄 Report saved: {report_file}")


def main():
    """Run model training."""
    trainer = ModelTrainer()
    trainer.train_all_models()


if __name__ == "__main__":
    main()
