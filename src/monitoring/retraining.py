"""
Auto-Retraining Pipeline
Automatically retrain models when drift is detected or performance degrades.
"""

import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import numpy as np


class AutoRetrainingPipeline:
    """Automated model retraining pipeline."""
    
    def __init__(
        self,
        model_name: str,
        retraining_dir: str = "monitoring/retraining",
        performance_threshold: float = 0.8,
        drift_threshold: float = 0.2,
        min_samples: int = 100
    ):
        """
        Initialize auto-retraining pipeline.
        
        Args:
            model_name: Name of the model
            retraining_dir: Directory for retraining artifacts
            performance_threshold: Minimum acceptable accuracy
            drift_threshold: Maximum acceptable drift PSI
            min_samples: Minimum samples needed for retraining
        """
        self.model_name = model_name
        self.retraining_dir = Path(retraining_dir)
        self.retraining_dir.mkdir(parents=True, exist_ok=True)
        
        self.performance_threshold = performance_threshold
        self.drift_threshold = drift_threshold
        self.min_samples = min_samples
        
        # Training data buffer
        self.training_buffer: List[Dict[str, Any]] = []
        
        # Retraining history
        self.retraining_history: List[Dict[str, Any]] = []
        
        # Current model version
        self.current_version = 1
        self.last_retraining_time: Optional[datetime] = None
        
    def add_training_sample(
        self,
        features: Dict[str, Any],
        label: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a new labeled sample to training buffer.
        
        Args:
            features: Input features
            label: Ground truth label
            metadata: Optional metadata
        """
        sample = {
            'timestamp': datetime.utcnow().isoformat(),
            'features': features,
            'label': label,
            'metadata': metadata or {}
        }
        
        self.training_buffer.append(sample)
    
    def should_retrain(
        self,
        current_accuracy: float,
        drift_score: float
    ) -> Dict[str, Any]:
        """
        Determine if retraining is needed.
        
        Args:
            current_accuracy: Current model accuracy
            drift_score: Current drift PSI score
            
        Returns:
            Decision dictionary
        """
        reasons = []
        should_retrain = False
        
        # Check performance degradation
        if current_accuracy < self.performance_threshold:
            reasons.append(
                f"Accuracy {current_accuracy:.3f} below threshold {self.performance_threshold}"
            )
            should_retrain = True
        
        # Check data drift
        if drift_score > self.drift_threshold:
            reasons.append(
                f"Drift PSI {drift_score:.3f} above threshold {self.drift_threshold}"
            )
            should_retrain = True
        
        # Check if enough samples are available
        if len(self.training_buffer) < self.min_samples:
            if should_retrain:
                reasons.append(
                    f"Insufficient samples: {len(self.training_buffer)}/{self.min_samples}"
                )
            should_retrain = False
        
        # Check time since last retraining (minimum 1 day)
        if self.last_retraining_time:
            time_since = datetime.utcnow() - self.last_retraining_time
            if time_since < timedelta(days=1):
                if should_retrain:
                    reasons.append(
                        f"Last retraining was {time_since.total_seconds()/3600:.1f}h ago (min 24h)"
                    )
                should_retrain = False
        
        return {
            'should_retrain': should_retrain,
            'reasons': reasons,
            'buffer_size': len(self.training_buffer),
            'current_accuracy': current_accuracy,
            'drift_score': drift_score
        }
    
    def prepare_training_data(self) -> Dict[str, Any]:
        """
        Prepare training data from buffer.
        
        Returns:
            Dictionary with X (features), y (labels), and sample_count
        """
        if not self.training_buffer:
            raise ValueError("No training samples in buffer")
        
        # Extract features and labels
        # Note: This is a simplified version
        # In practice, you'd need to handle feature extraction properly
        
        X = []
        y = []
        
        for sample in self.training_buffer:
            # Convert features dict to array (simplified)
            feature_values = list(sample['features'].values())
            X.append(feature_values)
            y.append(sample['label'])
        
        return {
            'X': np.array(X),
            'y': np.array(y),
            'sample_count': len(X)
        }
    
    def retrain_model(
        self,
        training_function: Callable,
        validation_function: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Retrain the model.
        
        Args:
            training_function: Function that trains the model
            validation_function: Optional function to validate the new model
            
        Returns:
            Retraining report
        """
        start_time = datetime.utcnow()
        
        # Prepare data
        try:
            data = self.prepare_training_data()
        except Exception as e:
            return {
                'success': False,
                'error': f"Data preparation failed: {str(e)}",
                'timestamp': start_time.isoformat()
            }
        
        # Train model
        try:
            new_model = training_function(data['X'], data['y'])
            training_success = True
            training_error = None
        except Exception as e:
            return {
                'success': False,
                'error': f"Training failed: {str(e)}",
                'timestamp': start_time.isoformat()
            }
        
        # Validate new model
        validation_metrics = {}
        if validation_function:
            try:
                validation_metrics = validation_function(new_model, data)
            except Exception as e:
                validation_metrics = {'error': str(e)}
        
        end_time = datetime.utcnow()
        training_duration = (end_time - start_time).total_seconds()
        
        # Update version
        self.current_version += 1
        self.last_retraining_time = end_time
        
        # Create report
        report = {
            'success': True,
            'timestamp': start_time.isoformat(),
            'model_name': self.model_name,
            'version': self.current_version,
            'training_samples': data['sample_count'],
            'training_duration': training_duration,
            'validation_metrics': validation_metrics
        }
        
        # Save report
        self.retraining_history.append(report)
        
        # Save model
        model_path = self._save_model(new_model, self.current_version)
        report['model_path'] = str(model_path)
        
        # Clear training buffer
        self.training_buffer = []
        
        return report
    
    def _save_model(self, model: Any, version: int) -> Path:
        """Save trained model to disk."""
        filename = f"{self.model_name}_v{version}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pkl"
        filepath = self.retraining_dir / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(model, f)
        
        return filepath
    
    def save_retraining_report(
        self,
        report: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Save retraining report to disk."""
        if report is None:
            if not self.retraining_history:
                raise ValueError("No retraining history available")
            report = self.retraining_history[-1]
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.model_name}_retraining_{timestamp}.json"
        filepath = self.retraining_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
    
    def get_retraining_summary(self) -> Dict[str, Any]:
        """Get summary of retraining history."""
        if not self.retraining_history:
            return {
                'total_retrainings': 0,
                'current_version': self.current_version,
                'last_retraining': None,
                'buffer_size': len(self.training_buffer)
            }
        
        return {
            'total_retrainings': len(self.retraining_history),
            'current_version': self.current_version,
            'last_retraining': self.retraining_history[-1],
            'buffer_size': len(self.training_buffer),
            'history': self.retraining_history[-5:]  # Last 5 retrainings
        }
    
    def get_training_buffer_stats(self) -> Dict[str, Any]:
        """Get statistics about training buffer."""
        if not self.training_buffer:
            return {
                'size': 0,
                'ready_for_training': False,
                'min_samples_needed': self.min_samples
            }
        
        # Label distribution
        labels = [sample['label'] for sample in self.training_buffer]
        unique_labels, counts = np.unique(labels, return_counts=True)
        
        return {
            'size': len(self.training_buffer),
            'ready_for_training': len(self.training_buffer) >= self.min_samples,
            'min_samples_needed': self.min_samples,
            'label_distribution': dict(zip(
                [str(label) for label in unique_labels],
                [int(count) for count in counts]
            )),
            'oldest_sample': self.training_buffer[0]['timestamp'],
            'newest_sample': self.training_buffer[-1]['timestamp']
        }
