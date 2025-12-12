"""
AŞAMA 4.5: Model Optimization & Ensemble
==========================================

1. GridSearchCV ile hyperparameter tuning
2. Ensemble methods (Voting + Stacking)
3. Feature selection optimization
4. Model comparison report
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import json
import joblib
from typing import Dict, Any, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    VotingClassifier, StackingClassifier
)
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))


class ModelOptimizer:
    """Optimize and ensemble email detection models."""
    
    def __init__(self, data_path: str = "data/processed", models_path: str = "models"):
        self.data_path = Path(data_path)
        self.models_path = Path(models_path)
        self.models_path.mkdir(exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "hyperparameter_tuning": {},
            "ensemble_results": {},
            "comparison": {}
        }
        self.vectorizer = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
    
    def load_training_data(self) -> Tuple[list, np.ndarray]:
        """Load training data."""
        logger.info("="*60)
        logger.info("LOADING TRAINING DATA")
        logger.info("="*60)
        
        all_texts = []
        all_labels = []
        
        csv_files = list(self.data_path.glob("**/*.csv"))
        logger.info(f"\n📁 Found {len(csv_files)} CSV files\n")
        
        for filepath in csv_files:
            try:
                df = pd.read_csv(filepath, encoding='utf-8', low_memory=False)
                
                filename = filepath.name.lower()
                if 'phishing' in filename or 'spam' in filename or 'nigerian' in filename or 'fraud' in filename:
                    label = 1
                else:
                    label = 0
                
                text_columns = df.select_dtypes(include=['object']).columns.tolist()
                text_col = None
                for col in ['body', 'text', 'message', 'Message', 'email_text', 'Body', 'content', 'Content']:
                    if col in text_columns:
                        text_col = col
                        break
                
                if text_col is None and text_columns:
                    text_col = text_columns[0]
                
                if text_col is None:
                    continue
                
                texts = df[text_col].fillna("").astype(str)
                mask = texts.str.len() > 10
                texts = texts[mask]
                
                all_texts.extend(texts.tolist())
                all_labels.extend([label] * len(texts))
                
                logger.info(f"  ✅ {filepath.name}: {len(texts)} texts (label={label})")
                
            except Exception as e:
                logger.error(f"  ❌ Error: {e}")
        
        # Sample data
        if len(all_texts) > 50000:
            logger.info(f"\n📉 Sampling 50K from {len(all_texts)} samples")
            indices = np.random.choice(len(all_texts), size=50000, replace=False)
            all_texts = [all_texts[i] for i in indices]
            all_labels = [all_labels[i] for i in indices]
        
        y = np.array(all_labels)
        logger.info(f"\n✅ Total: {len(all_texts)} samples (0:{(y==0).sum()}, 1:{(y==1).sum()})")
        
        return all_texts, y
    
    def prepare_features(self, texts_list: list, y: np.ndarray):
        """Prepare TF-IDF features and train-test split."""
        logger.info("\n" + "="*60)
        logger.info("PREPARING FEATURES")
        logger.info("="*60)
        
        # TF-IDF
        logger.info(f"\n🔤 TF-IDF Vectorization...")
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=2
        )
        X = self.vectorizer.fit_transform(texts_list)
        logger.info(f"  ✅ Shape: {X.shape}")
        
        # Split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        logger.info(f"\n📊 Split: Train {self.X_train.shape[0]}, Test {self.X_test.shape[0]}")
    
    def tune_random_forest(self) -> Dict[str, Any]:
        """Tune Random Forest hyperparameters."""
        logger.info("\n" + "="*60)
        logger.info("TUNING RANDOM FOREST")
        logger.info("="*60)
        
        params = {
            'n_estimators': [100, 200],
            'max_depth': [15, 20, 25],
            'min_samples_split': [3, 5],
            'min_samples_leaf': [1, 2]
        }
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        logger.info(f"\n🔍 GridSearch with {len(params['n_estimators'])*len(params['max_depth'])*len(params['min_samples_split'])*len(params['min_samples_leaf'])} combinations...")
        
        grid = GridSearchCV(rf, params, cv=3, scoring='f1', n_jobs=-1, verbose=1)
        grid.fit(self.X_train, self.y_train)
        
        logger.info(f"\n✅ Best params: {grid.best_params_}")
        logger.info(f"   Best CV F1-Score: {grid.best_score_:.4f}")
        
        # Evaluate
        y_pred = grid.best_estimator_.predict(self.X_test)
        y_pred_proba = grid.best_estimator_.predict_proba(self.X_test)[:, 1]
        
        results = {
            "model": "RandomForest",
            "best_params": grid.best_params_,
            "best_cv_score": float(grid.best_score_),
            "accuracy": float(accuracy_score(self.y_test, y_pred)),
            "precision": float(precision_score(self.y_test, y_pred)),
            "recall": float(recall_score(self.y_test, y_pred)),
            "f1": float(f1_score(self.y_test, y_pred)),
            "roc_auc": float(roc_auc_score(self.y_test, y_pred_proba))
        }
        
        logger.info(f"\n📈 Test Performance:")
        logger.info(f"  • Accuracy: {results['accuracy']:.4f}")
        logger.info(f"  • F1-Score: {results['f1']:.4f}")
        logger.info(f"  • ROC-AUC: {results['roc_auc']:.4f}")
        
        # Save model
        joblib.dump(grid.best_estimator_, self.models_path / "email_detector_rf_tuned.pkl")
        logger.info(f"\n💾 Saved: email_detector_rf_tuned.pkl")
        
        return results, grid.best_estimator_
    
    def build_ensemble(self, rf_model) -> Dict[str, Any]:
        """Build ensemble model with voting + stacking."""
        logger.info("\n" + "="*60)
        logger.info("BUILDING ENSEMBLE MODEL")
        logger.info("="*60)
        
        # Base learners
        gb = GradientBoostingClassifier(n_estimators=100, max_depth=10, random_state=42)
        svc = SVC(kernel='rbf', probability=True, random_state=42)
        
        # Voting ensemble
        logger.info(f"\n🗳️ Training Voting Classifier...")
        voting = VotingClassifier(
            estimators=[
                ('rf', rf_model),
                ('gb', gb),
                ('svc', svc)
            ],
            voting='soft'
        )
        voting.fit(self.X_train, self.y_train)
        
        y_pred = voting.predict(self.X_test)
        y_pred_proba = voting.predict_proba(self.X_test)[:, 1]
        
        voting_results = {
            "model": "VotingClassifier",
            "accuracy": float(accuracy_score(self.y_test, y_pred)),
            "precision": float(precision_score(self.y_test, y_pred)),
            "recall": float(recall_score(self.y_test, y_pred)),
            "f1": float(f1_score(self.y_test, y_pred)),
            "roc_auc": float(roc_auc_score(self.y_test, y_pred_proba))
        }
        
        logger.info(f"  ✅ Voting F1-Score: {voting_results['f1']:.4f}")
        
        # Stacking ensemble
        logger.info(f"\n📚 Training Stacking Classifier...")
        stacking = StackingClassifier(
            estimators=[
                ('rf', rf_model),
                ('gb', gb),
                ('svc', SVC(kernel='rbf', probability=True, random_state=42))
            ],
            final_estimator=LogisticRegression(random_state=42, n_jobs=-1),
            cv=3
        )
        stacking.fit(self.X_train, self.y_train)
        
        y_pred = stacking.predict(self.X_test)
        y_pred_proba = stacking.predict_proba(self.X_test)[:, 1]
        
        stacking_results = {
            "model": "StackingClassifier",
            "accuracy": float(accuracy_score(self.y_test, y_pred)),
            "precision": float(precision_score(self.y_test, y_pred)),
            "recall": float(recall_score(self.y_test, y_pred)),
            "f1": float(f1_score(self.y_test, y_pred)),
            "roc_auc": float(roc_auc_score(self.y_test, y_pred_proba))
        }
        
        logger.info(f"  ✅ Stacking F1-Score: {stacking_results['f1']:.4f}")
        
        # Save ensemble models
        joblib.dump(voting, self.models_path / "email_detector_voting.pkl")
        joblib.dump(stacking, self.models_path / "email_detector_stacking.pkl")
        logger.info(f"\n💾 Saved ensemble models")
        
        return voting_results, stacking_results, voting, stacking
    
    def compare_models(self, rf_results: Dict, voting_results: Dict, stacking_results: Dict):
        """Compare all models."""
        logger.info("\n" + "="*60)
        logger.info("MODEL COMPARISON")
        logger.info("="*60)
        
        comparison = pd.DataFrame([
            {
                "Model": "RandomForest (Tuned)",
                "Accuracy": rf_results["accuracy"],
                "Precision": rf_results["precision"],
                "Recall": rf_results["recall"],
                "F1-Score": rf_results["f1"],
                "ROC-AUC": rf_results["roc_auc"]
            },
            {
                "Model": "Voting Ensemble",
                "Accuracy": voting_results["accuracy"],
                "Precision": voting_results["precision"],
                "Recall": voting_results["recall"],
                "F1-Score": voting_results["f1"],
                "ROC-AUC": voting_results["roc_auc"]
            },
            {
                "Model": "Stacking Ensemble",
                "Accuracy": stacking_results["accuracy"],
                "Precision": stacking_results["precision"],
                "Recall": stacking_results["recall"],
                "F1-Score": stacking_results["f1"],
                "ROC-AUC": stacking_results["roc_auc"]
            }
        ])
        
        logger.info("\n")
        logger.info(comparison.to_string(index=False))
        
        # Best model
        best_f1_idx = comparison["F1-Score"].idxmax()
        best_model = comparison.loc[best_f1_idx, "Model"]
        best_f1 = comparison.loc[best_f1_idx, "F1-Score"]
        
        logger.info(f"\n🏆 Best Model: {best_model} (F1-Score: {best_f1:.4f})")
        
        self.results["comparison"] = comparison.to_dict('records')
        self.results["best_model"] = best_model
        
        # Visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Metrics comparison
        metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
        x = np.arange(len(metrics))
        width = 0.25
        
        for i, model in enumerate(comparison['Model']):
            values = comparison.loc[comparison['Model'] == model, metrics].values[0]
            axes[0].bar(x + i*width, values, width, label=model)
        
        axes[0].set_ylabel('Score')
        axes[0].set_title('Model Metrics Comparison')
        axes[0].set_xticks(x + width)
        axes[0].set_xticklabels(metrics, rotation=45, ha='right')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)
        
        # F1-Score comparison
        axes[1].barh(comparison['Model'], comparison['F1-Score'], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        axes[1].set_xlabel('F1-Score')
        axes[1].set_title('F1-Score Comparison')
        axes[1].set_xlim([0, 1])
        for i, v in enumerate(comparison['F1-Score']):
            axes[1].text(v + 0.02, i, f'{v:.4f}', va='center')
        
        plt.tight_layout()
        plt.savefig(self.models_path / "model_comparison.png", dpi=150)
        plt.close()
        
        logger.info(f"📊 Comparison chart saved")
    
    def optimize_all(self):
        """Run full optimization pipeline."""
        # Load data
        texts_list, y = self.load_training_data()
        
        # Prepare features
        self.prepare_features(texts_list, y)
        
        # Tune RF
        rf_results, rf_model = self.tune_random_forest()
        self.results["hyperparameter_tuning"] = rf_results
        
        # Build ensemble
        voting_results, stacking_results, _, _ = self.build_ensemble(rf_model)
        self.results["ensemble_results"]["voting"] = voting_results
        self.results["ensemble_results"]["stacking"] = stacking_results
        
        # Compare
        self.compare_models(rf_results, voting_results, stacking_results)
        
        # Save results
        report_file = Path("reports") / f"model_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"\n📄 Report saved: {report_file}")
        logger.info("\n" + "="*60)
        logger.info("✅ MODEL OPTIMIZATION COMPLETE")
        logger.info("="*60)


def main():
    """Run model optimization."""
    optimizer = ModelOptimizer()
    optimizer.optimize_all()


if __name__ == "__main__":
    main()
