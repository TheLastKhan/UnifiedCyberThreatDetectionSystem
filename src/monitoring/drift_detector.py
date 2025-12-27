"""
Data Drift Detection Module
Detects changes in data distribution using statistical methods.
"""

import numpy as np
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from scipy import stats
from collections import defaultdict


class DriftDetector:
    """Detects data drift using multiple statistical methods."""
    
    def __init__(
        self,
        model_name: str,
        drift_dir: str = "monitoring/drift",
        psi_threshold: float = 0.2,
        ks_threshold: float = 0.05
    ):
        """
        Initialize drift detector.
        
        Args:
            model_name: Name of the model to monitor
            drift_dir: Directory to store drift reports
            psi_threshold: PSI threshold for drift detection (0.2 = significant)
            ks_threshold: KS test p-value threshold
        """
        self.model_name = model_name
        self.drift_dir = Path(drift_dir)
        self.drift_dir.mkdir(parents=True, exist_ok=True)
        
        self.psi_threshold = psi_threshold
        self.ks_threshold = ks_threshold
        
        # Store reference distribution (training data)
        self.reference_distribution: Optional[Dict[str, np.ndarray]] = None
        self.reference_stats: Optional[Dict[str, Any]] = None
        
        # Current distribution (production data)
        self.current_distribution: Dict[str, List[float]] = defaultdict(list)
        
        # Drift history
        self.drift_history: List[Dict[str, Any]] = []
    
    def set_reference_distribution(
        self,
        features: Dict[str, np.ndarray]
    ):
        """
        Set reference distribution from training data.
        
        Args:
            features: Dictionary of feature names to arrays
        """
        self.reference_distribution = {
            name: np.array(values)
            for name, values in features.items()
        }
        
        # Calculate reference statistics
        self.reference_stats = {}
        for name, values in self.reference_distribution.items():
            self.reference_stats[name] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values)),
                'q25': float(np.percentile(values, 25)),
                'q75': float(np.percentile(values, 75))
            }
    
    def add_sample(self, features: Dict[str, float]):
        """
        Add a new sample to current distribution.
        
        Args:
            features: Dictionary of feature names to values
        """
        for name, value in features.items():
            self.current_distribution[name].append(value)
    
    def calculate_psi(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        bins: int = 10
    ) -> float:
        """
        Calculate Population Stability Index (PSI).
        
        PSI < 0.1: No significant change
        0.1 <= PSI < 0.2: Slight change
        PSI >= 0.2: Significant change (drift detected)
        
        Args:
            reference: Reference distribution
            current: Current distribution
            bins: Number of bins for histogram
            
        Returns:
            PSI value
        """
        # Create bins based on reference distribution
        breakpoints = np.linspace(
            np.min(reference),
            np.max(reference),
            bins + 1
        )
        
        # Calculate distributions
        ref_counts, _ = np.histogram(reference, bins=breakpoints)
        curr_counts, _ = np.histogram(current, bins=breakpoints)
        
        # Normalize to percentages
        ref_percents = ref_counts / len(reference)
        curr_percents = curr_counts / len(current)
        
        # Avoid division by zero
        ref_percents = np.where(ref_percents == 0, 0.0001, ref_percents)
        curr_percents = np.where(curr_percents == 0, 0.0001, curr_percents)
        
        # Calculate PSI
        psi = np.sum(
            (curr_percents - ref_percents) * np.log(curr_percents / ref_percents)
        )
        
        return float(psi)
    
    def calculate_kl_divergence(
        self,
        reference: np.ndarray,
        current: np.ndarray,
        bins: int = 10
    ) -> float:
        """
        Calculate Kullback-Leibler divergence.
        
        Args:
            reference: Reference distribution
            current: Current distribution
            bins: Number of bins
            
        Returns:
            KL divergence value
        """
        # Create bins
        breakpoints = np.linspace(
            min(np.min(reference), np.min(current)),
            max(np.max(reference), np.max(current)),
            bins + 1
        )
        
        # Calculate distributions
        ref_counts, _ = np.histogram(reference, bins=breakpoints)
        curr_counts, _ = np.histogram(current, bins=breakpoints)
        
        # Normalize
        ref_dist = (ref_counts + 1) / (len(reference) + bins)
        curr_dist = (curr_counts + 1) / (len(current) + bins)
        
        # Calculate KL divergence
        kl_div = np.sum(curr_dist * np.log(curr_dist / ref_dist))
        
        return float(kl_div)
    
    def kolmogorov_smirnov_test(
        self,
        reference: np.ndarray,
        current: np.ndarray
    ) -> Tuple[float, float]:
        """
        Perform Kolmogorov-Smirnov test.
        
        Args:
            reference: Reference distribution
            current: Current distribution
            
        Returns:
            Tuple of (statistic, p_value)
        """
        result = stats.ks_2samp(reference, current)
        statistic = float(result.statistic)  # type: ignore[attr-defined]
        p_value = float(result.pvalue)  # type: ignore[attr-defined]
        return statistic, p_value
    
    def detect_drift(self) -> Dict[str, Any]:
        """
        Detect drift in all features.
        
        Returns:
            Drift detection report
        """
        if self.reference_distribution is None:
            raise ValueError("Reference distribution not set")
        
        if not self.current_distribution:
            raise ValueError("No current samples collected")
        
        timestamp = datetime.utcnow().isoformat()
        drift_report = {
            'timestamp': timestamp,
            'model': self.model_name,
            'features': {},
            'drift_detected': False,
            'severity': 'none'
        }
        
        max_psi = 0.0
        drift_count = 0
        
        for feature_name in self.reference_distribution.keys():
            if feature_name not in self.current_distribution:
                continue
            
            reference = self.reference_distribution[feature_name]
            current = np.array(self.current_distribution[feature_name])
            
            if len(current) < 30:
                # Not enough samples
                continue
            
            # Calculate drift metrics
            psi = self.calculate_psi(reference, current)
            kl_div = self.calculate_kl_divergence(reference, current)
            ks_stat, ks_pvalue = self.kolmogorov_smirnov_test(reference, current)
            
            # Current statistics
            current_stats = {
                'mean': float(np.mean(current)),
                'std': float(np.std(current)),
                'median': float(np.median(current))
            }
            
            # Drift status
            psi_drift = psi >= self.psi_threshold
            ks_drift = ks_pvalue < self.ks_threshold
            
            # Get reference stats safely
            ref_stats = (
                self.reference_stats.get(feature_name, {})
                if self.reference_stats else {}
            )
            
            feature_drift = {
                'psi': round(psi, 4),
                'kl_divergence': round(kl_div, 4),
                'ks_statistic': round(ks_stat, 4),
                'ks_pvalue': round(ks_pvalue, 4),
                'reference_stats': ref_stats,
                'current_stats': current_stats,
                'drift_detected': psi_drift or ks_drift,
                'methods': {
                    'psi': 'drift' if psi_drift else 'stable',
                    'ks_test': 'drift' if ks_drift else 'stable'
                }
            }
            
            drift_report['features'][feature_name] = feature_drift
            
            if feature_drift['drift_detected']:
                drift_count += 1
            
            max_psi = max(max_psi, psi)
        
        # Overall drift assessment
        total_features = len(drift_report['features'])
        if total_features > 0:
            drift_ratio = drift_count / total_features
            
            if drift_ratio >= 0.5 or max_psi >= 0.3:
                drift_report['drift_detected'] = True
                drift_report['severity'] = 'high'
            elif drift_ratio >= 0.3 or max_psi >= 0.2:
                drift_report['drift_detected'] = True
                drift_report['severity'] = 'medium'
            elif drift_ratio > 0:
                drift_report['drift_detected'] = True
                drift_report['severity'] = 'low'
        
        drift_report['drift_count'] = drift_count
        drift_report['total_features'] = total_features
        drift_report['max_psi'] = round(max_psi, 4)
        
        self.drift_history.append(drift_report)
        return drift_report
    
    def save_drift_report(self, report: Optional[Dict[str, Any]] = None):
        """Save drift report to disk."""
        if report is None:
            report = self.detect_drift()
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.model_name}_drift_{timestamp}.json"
        filepath = self.drift_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
    
    def reset_current_distribution(self):
        """Reset current distribution for new monitoring period."""
        self.current_distribution = defaultdict(list)
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get summary of drift detection history."""
        if not self.drift_history:
            return {
                'total_checks': 0,
                'drift_detected_count': 0,
                'latest_check': None
            }
        
        drift_detected_count = sum(
            1 for report in self.drift_history
            if report['drift_detected']
        )
        
        return {
            'total_checks': len(self.drift_history),
            'drift_detected_count': drift_detected_count,
            'drift_ratio': round(
                drift_detected_count / len(self.drift_history), 4
            ),
            'latest_check': self.drift_history[-1],
            'history': self.drift_history[-5:]  # Last 5 checks
        }
