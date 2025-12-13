"""
A/B Testing Framework
Allows testing multiple model versions in production.
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
from collections import defaultdict
import numpy as np


class ABTestingFramework:
    """Framework for A/B testing multiple model versions."""
    
    def __init__(
        self,
        experiment_name: str,
        results_dir: str = "monitoring/ab_tests"
    ):
        """
        Initialize A/B testing framework.
        
        Args:
            experiment_name: Name of the experiment
            results_dir: Directory to store test results
        """
        self.experiment_name = experiment_name
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Model variants
        self.variants: Dict[str, Dict[str, Any]] = {}
        
        # Traffic allocation (model_name -> percentage)
        self.traffic_allocation: Dict[str, float] = {}
        
        # Results tracking
        self.results: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Experiment metadata
        self.start_time = datetime.utcnow()
        self.total_requests = 0
        
    def add_variant(
        self,
        model_name: str,
        model_callable: Callable,
        traffic_percentage: float,
        description: str = ""
    ):
        """
        Add a model variant to the experiment.
        
        Args:
            model_name: Name of the model variant
            model_callable: Function that makes predictions
            traffic_percentage: Percentage of traffic (0-100)
            description: Description of this variant
        """
        if not 0 <= traffic_percentage <= 100:
            raise ValueError("Traffic percentage must be between 0 and 100")
        
        self.variants[model_name] = {
            'model': model_callable,
            'description': description,
            'traffic': traffic_percentage,
            'request_count': 0
        }
        
        self.traffic_allocation[model_name] = traffic_percentage
        
        # Normalize traffic allocation
        self._normalize_traffic()
    
    def _normalize_traffic(self):
        """Normalize traffic allocation to sum to 100%."""
        total = sum(self.traffic_allocation.values())
        if total > 0:
            for name in self.traffic_allocation:
                self.traffic_allocation[name] = (
                    self.traffic_allocation[name] / total * 100
                )
    
    def select_variant(self, user_id: Optional[str] = None) -> str:
        """
        Select a model variant based on traffic allocation.
        
        Args:
            user_id: Optional user ID for consistent variant assignment
            
        Returns:
            Name of selected variant
        """
        if not self.variants:
            raise ValueError("No variants configured")
        
        # Deterministic selection based on user_id
        if user_id is not None:
            hash_value = hash(user_id)
            threshold = (hash_value % 100) / 100.0
        else:
            # Random selection
            threshold = random.random()
        
        # Select variant based on traffic allocation
        cumulative = 0.0
        for name, percentage in self.traffic_allocation.items():
            cumulative += percentage / 100.0
            if threshold <= cumulative:
                return name
        
        # Fallback to first variant
        return list(self.variants.keys())[0]
    
    def run_prediction(
        self,
        input_data: Any,
        user_id: Optional[str] = None,
        ground_truth: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Run prediction using selected variant.
        
        Args:
            input_data: Input data for prediction
            user_id: Optional user ID
            ground_truth: Optional ground truth label
            
        Returns:
            Prediction result with metadata
        """
        # Select variant
        variant_name = self.select_variant(user_id)
        variant = self.variants[variant_name]
        
        # Make prediction
        start_time = datetime.utcnow()
        try:
            prediction = variant['model'](input_data)
            success = True
            error = None
        except Exception as e:
            prediction = None
            success = False
            error = str(e)
        
        end_time = datetime.utcnow()
        prediction_time = (end_time - start_time).total_seconds()
        
        # Record result
        result = {
            'timestamp': start_time.isoformat(),
            'variant': variant_name,
            'prediction': prediction,
            'success': success,
            'error': error,
            'prediction_time': prediction_time,
            'user_id': user_id,
            'ground_truth': ground_truth
        }
        
        self.results[variant_name].append(result)
        self.variants[variant_name]['request_count'] += 1
        self.total_requests += 1
        
        return result
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Calculate statistics for all variants.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'experiment': self.experiment_name,
            'start_time': self.start_time.isoformat(),
            'total_requests': self.total_requests,
            'variants': {}
        }
        
        for variant_name, variant_results in self.results.items():
            if not variant_results:
                continue
            
            # Calculate metrics
            total = len(variant_results)
            successes = sum(1 for r in variant_results if r['success'])
            
            # Predictions with ground truth
            labeled = [
                r for r in variant_results
                if r['ground_truth'] is not None and r['success']
            ]
            
            accuracy = 0.0
            if labeled:
                correct = sum(
                    1 for r in labeled
                    if r['prediction'] == r['ground_truth']
                )
                accuracy = correct / len(labeled)
            
            # Timing metrics
            times = [
                r['prediction_time'] for r in variant_results
                if r['success']
            ]
            
            variant_stats = {
                'total_requests': total,
                'successful_requests': successes,
                'success_rate': successes / total if total > 0 else 0.0,
                'accuracy': accuracy,
                'labeled_samples': len(labeled),
                'avg_prediction_time': np.mean(times) if times else 0.0,
                'p95_prediction_time': np.percentile(times, 95) if times else 0.0,
                'traffic_allocation': self.traffic_allocation[variant_name],
                'actual_traffic': (total / self.total_requests * 100)
                if self.total_requests > 0 else 0.0
            }
            
            stats['variants'][variant_name] = variant_stats
        
        return stats
    
    def compare_variants(self) -> Dict[str, Any]:
        """
        Compare performance across variants.
        
        Returns:
            Comparison report
        """
        stats = self.calculate_statistics()
        
        if len(stats['variants']) < 2:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 2 variants to compare'
            }
        
        # Find best performers
        best_accuracy = {'variant': None, 'value': 0.0}
        best_speed = {'variant': None, 'value': float('inf')}
        
        for variant_name, variant_stats in stats['variants'].items():
            if variant_stats['accuracy'] > best_accuracy['value']:
                best_accuracy = {
                    'variant': variant_name,
                    'value': variant_stats['accuracy']
                }
            
            if variant_stats['avg_prediction_time'] < best_speed['value']:
                best_speed = {
                    'variant': variant_name,
                    'value': variant_stats['avg_prediction_time']
                }
        
        comparison = {
            'experiment': self.experiment_name,
            'timestamp': datetime.utcnow().isoformat(),
            'total_requests': stats['total_requests'],
            'best_accuracy': best_accuracy,
            'best_speed': best_speed,
            'variants': stats['variants'],
            'recommendation': self._generate_recommendation(stats)
        }
        
        return comparison
    
    def _generate_recommendation(
        self,
        stats: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate recommendation based on results."""
        variants = stats['variants']
        
        if not variants:
            return {
                'action': 'continue',
                'reason': 'Insufficient data for recommendation'
            }
        
        # Check if any variant is significantly better
        accuracies = [
            (name, v['accuracy'])
            for name, v in variants.items()
            if v['labeled_samples'] >= 30
        ]
        
        if len(accuracies) < 2:
            return {
                'action': 'continue',
                'reason': 'Need more labeled data (min 30 samples per variant)'
            }
        
        # Sort by accuracy
        accuracies.sort(key=lambda x: x[1], reverse=True)
        best_name, best_acc = accuracies[0]
        second_name, second_acc = accuracies[1]
        
        # Statistical significance (simple check)
        improvement = (best_acc - second_acc) / second_acc if second_acc > 0 else 0
        
        if improvement > 0.05:  # 5% improvement
            return {
                'action': 'promote',
                'winner': best_name,
                'reason': f'{best_name} shows {improvement*100:.1f}% improvement over {second_name}',
                'confidence': 'high' if improvement > 0.1 else 'medium'
            }
        else:
            return {
                'action': 'continue',
                'reason': 'No significant difference between variants',
                'note': 'Consider running test longer'
            }
    
    def save_results(self) -> Path:
        """Save experiment results to disk."""
        comparison = self.compare_variants()
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.experiment_name}_results_{timestamp}.json"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        return filepath
    
    def get_summary(self) -> Dict[str, Any]:
        """Get experiment summary."""
        return {
            'experiment': self.experiment_name,
            'start_time': self.start_time.isoformat(),
            'duration_seconds': (
                datetime.utcnow() - self.start_time
            ).total_seconds(),
            'total_requests': self.total_requests,
            'variants': list(self.variants.keys()),
            'traffic_allocation': self.traffic_allocation,
            'statistics': self.calculate_statistics(),
            'comparison': self.compare_variants()
        }
