"""
Model Performance Metrics Tracker
Monitors model predictions, accuracy, and performance over time.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import numpy as np
from collections import defaultdict


class ModelMetricsTracker:
    """Tracks and stores model performance metrics."""
    
    def __init__(self, model_name: str, metrics_dir: str = "monitoring/metrics"):
        """
        Initialize metrics tracker.
        
        Args:
            model_name: Name of the model to track
            metrics_dir: Directory to store metrics
        """
        self.model_name = model_name
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage for current session
        self.predictions: List[Dict[str, Any]] = []
        self.ground_truth: List[Dict[str, Any]] = []
        self.metrics_history: List[Dict[str, Any]] = []
        
        # Performance counters
        self.total_predictions = 0
        self.correct_predictions = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0
        self.true_negatives = 0
        
        # Timing metrics
        self.prediction_times: List[float] = []
        
    def log_prediction(
        self,
        input_data: Dict[str, Any],
        prediction: Any,
        confidence: float,
        prediction_time: float,
        ground_truth: Optional[Any] = None
    ):
        """
        Log a single prediction.
        
        Args:
            input_data: Input features/data
            prediction: Model prediction
            confidence: Prediction confidence score
            prediction_time: Time taken for prediction (seconds)
            ground_truth: Actual label (if available)
        """
        timestamp = datetime.utcnow().isoformat()
        
        prediction_record = {
            'timestamp': timestamp,
            'model': self.model_name,
            'prediction': prediction,
            'confidence': confidence,
            'prediction_time': prediction_time,
            'input_hash': hash(str(input_data))
        }
        
        self.predictions.append(prediction_record)
        self.prediction_times.append(prediction_time)
        self.total_predictions += 1
        
        # If ground truth is available, update accuracy metrics
        if ground_truth is not None:
            self.ground_truth.append({
                'timestamp': timestamp,
                'label': ground_truth,
                'prediction': prediction
            })
            
            self._update_confusion_matrix(prediction, ground_truth)
    
    def _update_confusion_matrix(self, prediction: Any, ground_truth: Any):
        """Update confusion matrix counters."""
        if prediction == ground_truth:
            self.correct_predictions += 1
            if prediction == 1 or prediction == 'phishing':
                self.true_positives += 1
            else:
                self.true_negatives += 1
        else:
            if prediction == 1 or prediction == 'phishing':
                self.false_positives += 1
            else:
                self.false_negatives += 1
    
    def calculate_metrics(self) -> Dict[str, float]:
        """
        Calculate current performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        if self.total_predictions == 0:
            return {
                'accuracy': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'f1_score': 0.0,
                'avg_prediction_time': 0.0
            }
        
        # Accuracy
        accuracy = (
            self.correct_predictions / self.total_predictions
            if self.total_predictions > 0 else 0.0
        )
        
        # Precision
        precision = (
            self.true_positives / (self.true_positives + self.false_positives)
            if (self.true_positives + self.false_positives) > 0 else 0.0
        )
        
        # Recall
        recall = (
            self.true_positives / (self.true_positives + self.false_negatives)
            if (self.true_positives + self.false_negatives) > 0 else 0.0
        )
        
        # F1 Score
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0 else 0.0
        )
        
        # Average prediction time
        avg_prediction_time = (
            np.mean(self.prediction_times)
            if len(self.prediction_times) > 0 else 0.0
        )
        
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'model': self.model_name,
            'total_predictions': self.total_predictions,
            'accuracy': round(accuracy, 4),
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1_score, 4),
            'true_positives': self.true_positives,
            'true_negatives': self.true_negatives,
            'false_positives': self.false_positives,
            'false_negatives': self.false_negatives,
            'avg_prediction_time': round(avg_prediction_time, 6),
            'p95_prediction_time': round(
                np.percentile(self.prediction_times, 95), 6
            ) if len(self.prediction_times) > 0 else 0.0,
            'p99_prediction_time': round(
                np.percentile(self.prediction_times, 99), 6
            ) if len(self.prediction_times) > 0 else 0.0
        }
        
        self.metrics_history.append(metrics)
        return metrics
    
    def save_metrics(self):
        """Save current metrics to disk."""
        metrics = self.calculate_metrics()
        
        # Save to JSON file
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.model_name}_metrics_{timestamp}.json"
        filepath = self.metrics_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return filepath
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get summary of all tracked metrics.
        
        Returns:
            Summary dictionary
        """
        current_metrics = self.calculate_metrics()
        
        return {
            'current': current_metrics,
            'history': self.metrics_history[-10:],  # Last 10 snapshots
            'total_predictions': self.total_predictions,
            'monitoring_duration': len(self.metrics_history)
        }
    
    def reset(self):
        """Reset all metrics and counters."""
        self.predictions = []
        self.ground_truth = []
        self.total_predictions = 0
        self.correct_predictions = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.true_positives = 0
        self.true_negatives = 0
        self.prediction_times = []


class MetricsAggregator:
    """Aggregates metrics from multiple models."""
    
    def __init__(self, metrics_dir: str = "monitoring/metrics"):
        self.metrics_dir = Path(metrics_dir)
        self.trackers: Dict[str, ModelMetricsTracker] = {}
    
    def get_tracker(self, model_name: str) -> ModelMetricsTracker:
        """Get or create a tracker for a model."""
        if model_name not in self.trackers:
            self.trackers[model_name] = ModelMetricsTracker(
                model_name, str(self.metrics_dir)
            )
        return self.trackers[model_name]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics from all tracked models."""
        return {
            name: tracker.get_metrics_summary()
            for name, tracker in self.trackers.items()
        }
    
    def compare_models(self) -> Dict[str, Any]:
        """Compare performance across all models."""
        comparison = {
            'models': {},
            'best_accuracy': {'model': None, 'value': 0.0},
            'best_f1': {'model': None, 'value': 0.0},
            'fastest': {'model': None, 'value': float('inf')}
        }
        
        for name, tracker in self.trackers.items():
            metrics = tracker.calculate_metrics()
            comparison['models'][name] = metrics
            
            # Track best performers
            if metrics['accuracy'] > comparison['best_accuracy']['value']:
                comparison['best_accuracy'] = {
                    'model': name,
                    'value': metrics['accuracy']
                }
            
            if metrics['f1_score'] > comparison['best_f1']['value']:
                comparison['best_f1'] = {
                    'model': name,
                    'value': metrics['f1_score']
                }
            
            if metrics['avg_prediction_time'] < comparison['fastest']['value']:
                comparison['fastest'] = {
                    'model': name,
                    'value': metrics['avg_prediction_time']
                }
        
        return comparison
