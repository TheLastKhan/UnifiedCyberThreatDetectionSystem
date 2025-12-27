"""
Enhanced Email Detector with VirusTotal Integration
===================================================

Combines TF-IDF/BERT detection with VirusTotal URL reputation checks
for enhanced threat detection.

Features:
- URL extraction from emails
- VirusTotal reputation scoring
- Combined risk score calculation
- Detection method tracking
- Comprehensive logging
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
import re

from src.email_detector.detector import EmailPhishingDetector
from src.security.virustotal import VirusTotalAPI, VirusCheckResult

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedEmailPrediction:
    """Enhanced prediction with VirusTotal data"""
    text: str
    ml_score: float  # ML model score (0-1)
    ml_label: str  # phishing or legitimate
    ml_confidence: float
    
    # VirusTotal data
    urls_found: List[str]
    vt_scores: Dict[str, float]  # url -> score
    vt_detections: Dict[str, int]  # url -> detection count
    
    # Combined score
    combined_score: float  # 0-100
    combined_label: str  # phishing or legitimate
    detection_method: str  # "tfidf", "virustotal", "hybrid"
    risk_level: str  # critical, high, medium, low
    
    # Metadata
    timestamp: str
    explanation: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ml_score': self.ml_score,
            'ml_label': self.ml_label,
            'ml_confidence': self.ml_confidence,
            'urls_found': self.urls_found,
            'vt_scores': self.vt_scores,
            'vt_detections': self.vt_detections,
            'combined_score': self.combined_score,
            'combined_label': self.combined_label,
            'detection_method': self.detection_method,
            'risk_level': self.risk_level,
            'timestamp': self.timestamp,
            'explanation': self.explanation,
        }


class EnhancedEmailDetector:
    """
    Email detector with VirusTotal integration
    
    Combines machine learning with external reputation data for
    enhanced phishing detection accuracy.
    """
    
    # Scoring weights
    ML_WEIGHT = 0.6  # 60% - ML model
    VT_WEIGHT = 0.4  # 40% - VirusTotal
    
    # Risk thresholds
    CRITICAL_THRESHOLD = 75  # >= 75: CRITICAL
    HIGH_THRESHOLD = 50      # >= 50: HIGH
    MEDIUM_THRESHOLD = 25    # >= 25: MEDIUM
    # < 25: LOW
    
    def __init__(self, vt_api_key: Optional[str] = None):
        """
        Initialize enhanced detector
        
        Args:
            vt_api_key: VirusTotal API key (optional)
        """
        # Initialize ML detector
        self.ml_detector = EmailPhishingDetector()
        logger.info("✅ ML detector initialized")
        
        # Initialize VirusTotal API
        self.vt_api = VirusTotalAPI(api_key=vt_api_key)
        logger.info("✅ VirusTotal API initialized")
        
        # URL extraction pattern
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]*'
        )
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from email text"""
        urls = self.url_pattern.findall(text)
        return list(set(urls))  # Remove duplicates
    
    def _get_vt_score_for_url(self, url: str) -> Tuple[float, int]:
        """
        Get VirusTotal score for URL
        
        Args:
            url: URL to check
        
        Returns:
            Tuple of (score 0-100, detection_count)
        """
        try:
            result = self.vt_api.check_url(url)
            
            if result.error:
                logger.warning(f"⚠️ VT error for {url}: {result.error}")
                return 0.0, 0
            
            # Convert detection ratio (0-1) to score (0-100)
            score = result.detection_ratio * 100
            
            logger.info(
                f"✓ {url}: {result.detected_count}/{result.engine_count} "
                f"engines detected (score: {score:.1f})"
            )
            
            return score, result.detected_count
            
        except Exception as e:
            logger.error(f"Error checking URL {url}: {e}")
            return 0.0, 0
    
    def _calculate_url_reputation_score(
        self, urls: List[str]
    ) -> Tuple[float, Dict, Dict]:
        """
        Calculate overall URL reputation score
        
        Args:
            urls: List of URLs to check
        
        Returns:
            Tuple of (overall_score 0-100, scores_by_url, detections_by_url)
        """
        if not urls:
            return 0.0, {}, {}
        
        vt_scores = {}
        vt_detections = {}
        total_score = 0.0
        
        for url in urls:
            score, detections = self._get_vt_score_for_url(url)
            vt_scores[url] = score
            vt_detections[url] = detections
            total_score += score
        
        # Average score across all URLs
        avg_score = total_score / len(urls) if urls else 0.0
        
        return avg_score, vt_scores, vt_detections
    
    def _get_risk_level(self, score: float) -> str:
        """Classify risk level based on score"""
        if score >= self.CRITICAL_THRESHOLD:
            return "critical"
        elif score >= self.HIGH_THRESHOLD:
            return "high"
        elif score >= self.MEDIUM_THRESHOLD:
            return "medium"
        else:
            return "low"
    
    def predict(self, email_text: str) -> EnhancedEmailPrediction:
        """
        Predict if email is phishing with VirusTotal enhancement
        
        Args:
            email_text: Email text to analyze
        
        Returns:
            EnhancedEmailPrediction with combined scores
        """
        logger.info("="*60)
        logger.info("ENHANCED EMAIL DETECTION")
        logger.info("="*60)
        
        # Step 1: ML Detection
        logger.info("\n[Step 1] ML Model Detection")
        logger.info("-"*60)
        
        ml_pred = self.ml_detector.predict(email_text)
        ml_score = ml_pred['probability'][1]  # Phishing probability
        ml_label = "phishing" if ml_pred['prediction'] == 1 else "legitimate"
        
        logger.info(f"ML Score: {ml_score:.3f}")
        logger.info(f"ML Label: {ml_label}")
        
        # Step 2: Extract URLs
        logger.info("\n[Step 2] URL Extraction & VirusTotal Check")
        logger.info("-"*60)
        
        urls = self._extract_urls(email_text)
        logger.info(f"Found {len(urls)} unique URLs: {urls[:3]}{'...' if len(urls) > 3 else ''}")
        
        # Step 3: VirusTotal Check
        if urls:
            vt_score, vt_scores, vt_detections = self._calculate_url_reputation_score(urls)
            logger.info(f"VirusTotal Average Score: {vt_score:.1f}")
        else:
            vt_score = 0.0
            vt_scores = {}
            vt_detections = {}
            logger.info("No URLs found in email")
        
        # Step 4: Combined Scoring
        logger.info("\n[Step 3] Combined Scoring")
        logger.info("-"*60)
        
        # Normalize scores to 0-100 range
        ml_score_normalized = ml_score * 100
        
        # Weighted combination
        combined_score = (
            (ml_score_normalized * self.ML_WEIGHT) +
            (vt_score * self.VT_WEIGHT)
        )
        
        logger.info(f"ML Score (normalized): {ml_score_normalized:.1f}")
        logger.info(f"VT Score: {vt_score:.1f}")
        logger.info(f"Combined Score: {combined_score:.1f}")
        
        # Determine detection method
        if urls and vt_score > 0:
            detection_method = "hybrid"
            combined_label = "phishing" if combined_score >= 50 else "legitimate"
        elif urls:
            detection_method = "virustotal"
            combined_label = "phishing" if vt_score >= 50 else "legitimate"
        else:
            detection_method = "ml"
            combined_label = ml_label
        
        # Risk level
        risk_level = self._get_risk_level(combined_score)
        
        logger.info(f"Detection Method: {detection_method}")
        logger.info(f"Combined Label: {combined_label}")
        logger.info(f"Risk Level: {risk_level}")
        
        # Step 5: Build explanation
        logger.info("\n[Step 4] Building Explanation")
        logger.info("-"*60)
        
        explanation = {
            "ml_factors": ml_pred.get('explanation', {}),
            "url_reputation": {
                "urls_checked": urls,
                "average_score": vt_score,
                "individual_scores": vt_scores,
                "detections": vt_detections,
            },
            "combined_factors": {
                "ml_weight": self.ML_WEIGHT,
                "vt_weight": self.VT_WEIGHT,
                "ml_contribution": ml_score_normalized * self.ML_WEIGHT,
                "vt_contribution": vt_score * self.VT_WEIGHT,
            }
        }
        
        # Create result
        result = EnhancedEmailPrediction(
            text=email_text[:100] + "..." if len(email_text) > 100 else email_text,
            ml_score=ml_score,
            ml_label=ml_label,
            ml_confidence=ml_score,
            urls_found=urls,
            vt_scores=vt_scores,
            vt_detections=vt_detections,
            combined_score=combined_score,
            combined_label=combined_label,
            detection_method=detection_method,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat(),
            explanation=explanation,
        )
        
        logger.info("="*60)
        logger.info(f"✅ RESULT: {combined_label.upper()} ({risk_level})")
        logger.info("="*60)
        
        return result
    
    def batch_predict(
        self, emails: List[str], verbose: bool = False
    ) -> List[EnhancedEmailPrediction]:
        """
        Predict for multiple emails
        
        Args:
            emails: List of email texts
            verbose: Whether to show progress
        
        Returns:
            List of predictions
        """
        results = []
        
        for i, email in enumerate(emails, 1):
            if verbose:
                logger.info(f"\nProcessing email {i}/{len(emails)}")
            
            result = self.predict(email)
            results.append(result)
        
        return results


def main():
    """Test enhanced detector"""
    # Test emails
    test_emails = [
        # Phishing example
        """
        Subject: Urgent: Verify Your Account
        
        Dear User,
        
        Your account has been compromised. Click here to verify:
        http://phishing-site.com/verify-account
        
        Regards,
        Security Team
        """,
        
        # Legitimate example
        """
        Subject: Meeting Tomorrow at 2 PM
        
        Hi,
        
        Don't forget about our meeting tomorrow at 2 PM.
        See you then!
        
        Best regards,
        John
        """,
    ]
    
    # Initialize detector
    detector = EnhancedEmailDetector()
    
    # Predict
    logger.info("\n" + "="*70)
    logger.info("ENHANCED EMAIL DETECTION - BATCH PROCESSING")
    logger.info("="*70)
    
    results = detector.batch_predict(test_emails, verbose=True)
    
    # Print results
    logger.info("\n" + "="*70)
    logger.info("RESULTS SUMMARY")
    logger.info("="*70)
    
    for i, result in enumerate(results, 1):
        logger.info(f"\nEmail {i}:")
        logger.info(f"  ML Score: {result.ml_score:.3f}")
        logger.info(f"  Combined Score: {result.combined_score:.1f}")
        logger.info(f"  Label: {result.combined_label.upper()}")
        logger.info(f"  Risk Level: {result.risk_level.upper()}")
        logger.info(f"  Detection Method: {result.detection_method}")
        logger.info(f"  URLs: {len(result.urls_found)} found")


if __name__ == "__main__":
    main()
