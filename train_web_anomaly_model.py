"""
Web Log Anomaly Detection Model - AŞAMA 4.4
=============================================

Train anomaly detection model for web logs using:
1. Isolation Forest (unsupervised)
2. Feature extraction from HTTP logs
3. Attack pattern detection
4. Model evaluation
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
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_recall_curve, f1_score, confusion_matrix,
    classification_report, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))


class WebLogAnomalyDetector:
    """Train anomaly detection for web logs."""
    
    def __init__(self, data_path: str = "data/processed", models_path: str = "models"):
        self.data_path = Path(data_path)
        self.models_path = Path(models_path)
        self.models_path.mkdir(exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "model_type": "IsolationForest",
            "metrics": {}
        }
    
    def extract_log_features(self, log_text: str) -> Dict[str, Any]:
        """Extract features from HTTP log entries."""
        features = {
            "request_length": len(log_text),
            "has_sql_keywords": any(kw in log_text.lower() for kw in 
                                    ['select', 'union', 'drop', 'insert', 'delete', 'update', 'exec']),
            "has_xss_patterns": any(pat in log_text.lower() for pat in 
                                   ['<script', 'javascript:', 'onerror', 'onload']),
            "has_encoded_chars": len([c for c in log_text if ord(c) > 127]),
            "url_length": log_text.count('/'),
            "query_param_count": log_text.count('='),
            "special_char_ratio": len([c for c in log_text if not c.isalnum() and c != ' ']) / max(len(log_text), 1),
            "uppercase_ratio": len([c for c in log_text if c.isupper()]) / max(len(log_text), 1),
        }
        return features
    
    def load_web_log_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load web log data and extract features."""
        logger.info("="*60)
        logger.info("LOADING WEB LOG DATA")
        logger.info("="*60)
        
        all_features = []
        all_labels = []
        
        # Log files with presumed labels
        # (Normal: 0, Anomaly: 1 - based on dataset names)
        log_datasets = {
            "data/samples/demo_web_logs.txt": 0,  # Demo = normal
        }
        
        # Try to find additional log files
        for filepath in self.data_path.glob("**/*.csv"):
            if 'log' in filepath.name.lower() or 'http' in filepath.name.lower():
                log_datasets[str(filepath)] = 0  # Default normal unless named as attack
            if 'attack' in filepath.name.lower() or 'malicious' in filepath.name.lower():
                log_datasets[str(filepath)] = 1  # Attack
        
        for filepath_str, label in log_datasets.items():
            filepath = Path(filepath_str)
            
            if not filepath.exists():
                logger.warning(f"⚠️ File not found: {filepath}")
                continue
            
            try:
                if filepath.suffix == '.txt':
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    logger.info(f"📁 Loading: {filepath.name} ({len(lines)} logs, label={label})")
                    
                    for line in lines:
                        if line.strip():
                            features = self.extract_log_features(line)
                            all_features.append(features)
                            all_labels.append(label)
                
                elif filepath.suffix == '.csv':
                    df = pd.read_csv(filepath, low_memory=False)
                    logger.info(f"📁 Loading: {filepath.name} ({len(df)} rows, label={label})")
                    
                    # Find text column
                    text_cols = df.select_dtypes(include=['object']).columns
                    for col in text_cols:
                        texts = df[col].fillna("").astype(str)
                        for text in texts:
                            if len(text) > 5:
                                features = self.extract_log_features(text)
                                all_features.append(features)
                                all_labels.append(label)
                
            except Exception as e:
                logger.error(f"  ❌ Error loading {filepath}: {e}")
        
        if not all_features:
            logger.warning("⚠️ No log data found. Creating synthetic data...")
            all_features, all_labels = self._generate_synthetic_logs()
        
        X = pd.DataFrame(all_features)
        y = np.array(all_labels)
        
        logger.info(f"\n✅ Total samples: {len(X)}")
        logger.info(f"  • Normal (0): {(y == 0).sum()}")
        logger.info(f"  • Anomaly (1): {(y == 1).sum()}")
        
        return X, y
    
    def _generate_synthetic_logs(self) -> Tuple[list, list]:
        """Generate synthetic log data for demonstration."""
        np.random.seed(42)
        features = []
        labels = []
        
        # Normal logs
        for _ in range(1000):
            features.append({
                "request_length": np.random.normal(100, 30),
                "has_sql_keywords": 0,
                "has_xss_patterns": 0,
                "has_encoded_chars": np.random.poisson(2),
                "url_length": np.random.poisson(3),
                "query_param_count": np.random.poisson(2),
                "special_char_ratio": np.random.beta(2, 5),
                "uppercase_ratio": np.random.beta(2, 3),
            })
            labels.append(0)
        
        # Anomalous logs
        for _ in range(200):
            features.append({
                "request_length": np.random.normal(500, 100),
                "has_sql_keywords": np.random.choice([0, 1], p=[0.3, 0.7]),
                "has_xss_patterns": np.random.choice([0, 1], p=[0.4, 0.6]),
                "has_encoded_chars": np.random.poisson(10),
                "url_length": np.random.poisson(15),
                "query_param_count": np.random.poisson(10),
                "special_char_ratio": np.random.beta(5, 2),
                "uppercase_ratio": np.random.beta(5, 2),
            })
            labels.append(1)
        
        logger.info(f"  📊 Generated 1,200 synthetic log samples")
        return features, labels
    
    def train_anomaly_detector(self, X: pd.DataFrame, y: np.ndarray) -> Dict[str, Any]:
        """Train Isolation Forest model."""
        logger.info("\n" + "="*60)
        logger.info("TRAINING ISOLATION FOREST ANOMALY DETECTOR")
        logger.info("="*60)
        
        # Data split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"\n📊 Data split:")
        logger.info(f"  • Training: {len(X_train)} samples")
        logger.info(f"  • Testing: {len(X_test)} samples")
        
        # Feature scaling
        logger.info(f"\n📏 Feature scaling...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        logger.info(f"\n🔍 Training Isolation Forest...")
        model = IsolationForest(
            contamination=0.1,  # Expected ~10% anomalies
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_scaled)
        logger.info(f"  ✅ Model training complete")
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred = np.where(y_pred == -1, 1, 0)  # Convert -1 to 1 for anomaly
        
        y_pred_proba = -model.score_samples(X_test_scaled)  # Anomaly score
        y_pred_proba = (y_pred_proba - y_pred_proba.min()) / (y_pred_proba.max() - y_pred_proba.min())
        
        # Evaluation
        logger.info(f"\n📈 Model Evaluation:")
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        try:
            roc_auc = roc_auc_score(y_test, y_pred_proba)
        except:
            roc_auc = 0.0
        
        results = {
            "model_type": "IsolationForest",
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "roc_auc": float(roc_auc),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features": X.shape[1],
            "contamination": 0.1,
        }
        
        logger.info(f"  • Accuracy:  {results['accuracy']:.4f}")
        logger.info(f"  • Precision: {results['precision']:.4f}")
        logger.info(f"  • Recall:    {results['recall']:.4f}")
        logger.info(f"  • F1-Score:  {results['f1']:.4f}")
        logger.info(f"  • ROC-AUC:   {results['roc_auc']:.4f}")
        
        # Save models
        model_path = self.models_path / "web_anomaly_detector.pkl"
        scaler_path = self.models_path / "log_scaler.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        logger.info(f"\n💾 Models saved:")
        logger.info(f"   • Detector: {model_path}")
        logger.info(f"   • Scaler: {scaler_path}")
        
        # Feature importance (by anomaly score variance)
        feature_importance = np.abs(model.feature_importances_ if hasattr(model, 'feature_importances_') 
                                   else np.ones(X.shape[1]) / X.shape[1])
        
        results["feature_importance"] = {
            col: float(imp) 
            for col, imp in zip(X.columns, feature_importance)
        }
        
        return results, model, scaler, X_test, y_test, y_pred, y_pred_proba
    
    def train_all(self):
        """Train all models."""
        # Load data
        X, y = self.load_web_log_data()
        
        # Train model
        results, model, scaler, X_test, y_test, y_pred, y_pred_proba = \
            self.train_anomaly_detector(X, y)
        
        self.results["metrics"] = results
        
        # Save results
        report_file = Path("reports") / f"web_anomaly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"\n📄 Report saved: {report_file}")
        logger.info("\n" + "="*60)
        logger.info("✅ WEB ANOMALY DETECTION COMPLETE")
        logger.info("="*60)


def main():
    """Run anomaly detection training."""
    detector = WebLogAnomalyDetector()
    detector.train_all()


if __name__ == "__main__":
    main()
