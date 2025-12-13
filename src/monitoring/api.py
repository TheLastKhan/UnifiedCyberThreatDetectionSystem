"""
Monitoring API Endpoints
REST API endpoints for ML model monitoring, drift detection, A/B testing, and retraining.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import numpy as np
from typing import Dict, Any

# Import monitoring modules
from ..monitoring.metrics import ModelMetricsTracker, MetricsAggregator
from ..monitoring.drift_detector import DriftDetector
from ..monitoring.ab_testing import ABTestingFramework
from ..monitoring.retraining import AutoRetrainingPipeline

# Create Blueprint
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

# Initialize global instances
metrics_aggregator = MetricsAggregator()
drift_detectors: Dict[str, DriftDetector] = {}
ab_tests: Dict[str, ABTestingFramework] = {}
retraining_pipelines: Dict[str, AutoRetrainingPipeline] = {}


@monitoring_bp.route('/metrics/<model_name>', methods=['GET'])
def get_model_metrics(model_name: str):
    """
    Get performance metrics for a specific model.
    
    GET /api/monitoring/metrics/email_detector
    """
    try:
        tracker = metrics_aggregator.get_tracker(model_name)
        summary = tracker.get_metrics_summary()
        
        return jsonify({
            'status': 'success',
            'model': model_name,
            'metrics': summary
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/metrics/compare', methods=['GET'])
def compare_models():
    """
    Compare metrics across all tracked models.
    
    GET /api/monitoring/metrics/compare
    """
    try:
        comparison = metrics_aggregator.compare_models()
        
        return jsonify({
            'status': 'success',
            'comparison': comparison
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/metrics/log', methods=['POST'])
def log_prediction():
    """
    Log a prediction for metrics tracking.
    
    POST /api/monitoring/metrics/log
    Body: {
        "model_name": "email_detector",
        "input_data": {...},
        "prediction": "phishing",
        "confidence": 0.95,
        "prediction_time": 0.123,
        "ground_truth": "phishing"  # optional
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        model_name = data.get('model_name')
        if not model_name:
            return jsonify({
                'status': 'error',
                'message': 'model_name is required'
            }), 400
        
        tracker = metrics_aggregator.get_tracker(model_name)
        
        tracker.log_prediction(
            input_data=data.get('input_data', {}),
            prediction=data.get('prediction'),
            confidence=data.get('confidence', 0.0),
            prediction_time=data.get('prediction_time', 0.0),
            ground_truth=data.get('ground_truth')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Prediction logged successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/drift/<model_name>/check', methods=['POST'])
def check_drift(model_name: str):
    """
    Check for data drift in a model.
    
    POST /api/monitoring/drift/email_detector/check
    """
    try:
        if model_name not in drift_detectors:
            return jsonify({
                'status': 'error',
                'message': f'Drift detector not initialized for {model_name}'
            }), 404
        
        detector = drift_detectors[model_name]
        drift_report = detector.detect_drift()
        
        # Save report
        detector.save_drift_report(drift_report)
        
        return jsonify({
            'status': 'success',
            'drift_report': drift_report
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/drift/<model_name>/summary', methods=['GET'])
def get_drift_summary(model_name: str):
    """
    Get drift detection summary.
    
    GET /api/monitoring/drift/email_detector/summary
    """
    try:
        if model_name not in drift_detectors:
            return jsonify({
                'status': 'error',
                'message': f'Drift detector not initialized for {model_name}'
            }), 404
        
        detector = drift_detectors[model_name]
        summary = detector.get_drift_summary()
        
        return jsonify({
            'status': 'success',
            'model': model_name,
            'drift_summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/drift/<model_name>/sample', methods=['POST'])
def add_drift_sample(model_name: str):
    """
    Add a sample to drift detector.
    
    POST /api/monitoring/drift/email_detector/sample
    Body: {
        "features": {
            "feature1": 0.5,
            "feature2": 0.8
        }
    }
    """
    try:
        if model_name not in drift_detectors:
            # Initialize detector
            drift_detectors[model_name] = DriftDetector(model_name)
        
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        features = data.get('features', {})
        
        detector = drift_detectors[model_name]
        detector.add_sample(features)
        
        return jsonify({
            'status': 'success',
            'message': 'Sample added to drift detector'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/abtest/<experiment_name>/status', methods=['GET'])
def get_abtest_status(experiment_name: str):
    """
    Get A/B test status.
    
    GET /api/monitoring/abtest/email_model_comparison/status
    """
    try:
        if experiment_name not in ab_tests:
            return jsonify({
                'status': 'error',
                'message': f'A/B test {experiment_name} not found'
            }), 404
        
        test = ab_tests[experiment_name]
        summary = test.get_summary()
        
        return jsonify({
            'status': 'success',
            'summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/abtest/<experiment_name>/compare', methods=['GET'])
def compare_abtest_variants(experiment_name: str):
    """
    Compare A/B test variants.
    
    GET /api/monitoring/abtest/email_model_comparison/compare
    """
    try:
        if experiment_name not in ab_tests:
            return jsonify({
                'status': 'error',
                'message': f'A/B test {experiment_name} not found'
            }), 404
        
        test = ab_tests[experiment_name]
        comparison = test.compare_variants()
        
        return jsonify({
            'status': 'success',
            'comparison': comparison
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/retraining/<model_name>/status', methods=['GET'])
def get_retraining_status(model_name: str):
    """
    Get retraining pipeline status.
    
    GET /api/monitoring/retraining/email_detector/status
    """
    try:
        if model_name not in retraining_pipelines:
            return jsonify({
                'status': 'error',
                'message': f'Retraining pipeline not initialized for {model_name}'
            }), 404
        
        pipeline = retraining_pipelines[model_name]
        summary = pipeline.get_retraining_summary()
        buffer_stats = pipeline.get_training_buffer_stats()
        
        return jsonify({
            'status': 'success',
            'model': model_name,
            'retraining_summary': summary,
            'buffer_stats': buffer_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/retraining/<model_name>/check', methods=['POST'])
def check_retraining_needed(model_name: str):
    """
    Check if retraining is needed.
    
    POST /api/monitoring/retraining/email_detector/check
    Body: {
        "current_accuracy": 0.85,
        "drift_score": 0.15
    }
    """
    try:
        if model_name not in retraining_pipelines:
            # Initialize pipeline
            retraining_pipelines[model_name] = AutoRetrainingPipeline(model_name)
        
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        current_accuracy = data.get('current_accuracy', 1.0)
        drift_score = data.get('drift_score', 0.0)
        
        pipeline = retraining_pipelines[model_name]
        decision = pipeline.should_retrain(current_accuracy, drift_score)
        
        return jsonify({
            'status': 'success',
            'decision': decision
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/retraining/<model_name>/sample', methods=['POST'])
def add_training_sample(model_name: str):
    """
    Add a labeled sample to retraining buffer.
    
    POST /api/monitoring/retraining/email_detector/sample
    Body: {
        "features": {...},
        "label": "phishing",
        "metadata": {...}
    }
    """
    try:
        if model_name not in retraining_pipelines:
            retraining_pipelines[model_name] = AutoRetrainingPipeline(model_name)
        
        data = request.json
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        features = data.get('features', {})
        label = data.get('label')
        metadata = data.get('metadata', {})
        
        if not label:
            return jsonify({
                'status': 'error',
                'message': 'label is required'
            }), 400
        
        pipeline = retraining_pipelines[model_name]
        pipeline.add_training_sample(features, label, metadata)
        
        buffer_stats = pipeline.get_training_buffer_stats()
        
        return jsonify({
            'status': 'success',
            'message': 'Training sample added',
            'buffer_stats': buffer_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@monitoring_bp.route('/health', methods=['GET'])
def monitoring_health():
    """
    Health check for monitoring system.
    
    GET /api/monitoring/health
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {
            'metrics_tracker': {
                'status': 'operational',
                'tracked_models': len(metrics_aggregator.trackers)
            },
            'drift_detectors': {
                'status': 'operational',
                'active_detectors': len(drift_detectors)
            },
            'ab_tests': {
                'status': 'operational',
                'active_experiments': len(ab_tests)
            },
            'retraining_pipelines': {
                'status': 'operational',
                'active_pipelines': len(retraining_pipelines)
            }
        }
    }), 200
