"""
Enhanced Web Log Analyzer with VirusTotal Integration
=====================================================

Combines anomaly detection with VirusTotal IP/URL reputation checks
for enhanced attack detection.

Features:
- Anomaly detection (Isolation Forest)
- IP reputation checking
- URL/path analysis
- Combined threat scoring
- Attack type classification
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime
import re

from src.web_analyzer.analyzer import WebLogAnalyzer
from src.security.virustotal import VirusTotalAPI, VirusCheckResult

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EnhancedWebLogPrediction:
    """Enhanced web log prediction with VirusTotal data"""
    ip_address: str
    request_path: str
    
    # Anomaly detection
    anomaly_score: float  # 0-1
    is_anomaly: bool
    
    # VirusTotal IP reputation
    ip_reputation_score: float  # 0-100
    ip_detections: int
    
    # VirusTotal URL reputation
    url_reputation_score: float  # 0-100
    url_detections: int
    
    # Combined score
    combined_score: float  # 0-100
    risk_level: str  # critical, high, medium, low
    attack_type: str  # sql_injection, xss, ddos, etc.
    
    # Metadata
    timestamp: str
    explanation: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'ip_address': self.ip_address,
            'request_path': self.request_path,
            'anomaly_score': self.anomaly_score,
            'is_anomaly': self.is_anomaly,
            'ip_reputation_score': self.ip_reputation_score,
            'ip_detections': self.ip_detections,
            'url_reputation_score': self.url_reputation_score,
            'url_detections': self.url_detections,
            'combined_score': self.combined_score,
            'risk_level': self.risk_level,
            'attack_type': self.attack_type,
            'timestamp': self.timestamp,
            'explanation': self.explanation,
        }


class EnhancedWebLogAnalyzer:
    """
    Web log analyzer with VirusTotal integration
    
    Combines anomaly detection with external reputation data for
    enhanced attack detection.
    """
    
    # Scoring weights
    ANOMALY_WEIGHT = 0.5  # 50% - Anomaly detection
    IP_WEIGHT = 0.3       # 30% - IP reputation
    URL_WEIGHT = 0.2      # 20% - URL/path reputation
    
    # Risk thresholds
    CRITICAL_THRESHOLD = 75  # >= 75: CRITICAL
    HIGH_THRESHOLD = 50      # >= 50: HIGH
    MEDIUM_THRESHOLD = 25    # >= 25: MEDIUM
    # < 25: LOW
    
    # Attack type detection patterns
    ATTACK_PATTERNS = {
        'sql_injection': [
            r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
            r"(\w*((\%27)|(\'))((\s)*(or|and|union))+)",
        ],
        'xss': [
            r"(<|%3C).*?(script|img|svg|iframe).*?(>|%3E)",
            r"javascript:",
        ],
        'ddos': [
            r"HEAD|GET|POST.*?\*{5,}",  # Repeated requests
        ],
        'brute_force': [
            r"/login|/admin|/authenticate",
            r"(401|403|404){3,}",  # Multiple auth failures
        ],
        'path_traversal': [
            r"\.\./|\.\.\\",
            r"%2e%2e|\.\.%2f",
        ],
        'command_injection': [
            r"[;|&`\$\(\)]",
            r"exec|system|passthru|shell_exec",
        ],
    }
    
    def __init__(self, vt_api_key: Optional[str] = None):
        """
        Initialize enhanced web log analyzer
        
        Args:
            vt_api_key: VirusTotal API key (optional)
        """
        # Initialize anomaly detector
        self.analyzer = WebLogAnalyzer()
        logger.info("✅ Web log analyzer initialized")
        
        # Initialize VirusTotal API
        self.vt_api = VirusTotalAPI(api_key=vt_api_key)
        logger.info("✅ VirusTotal API initialized")
    
    def _extract_ip_and_url(self, log_line: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract IP and URL from log line"""
        # Simple extraction - can be improved
        ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', log_line)
        url_match = re.search(r'(GET|POST|PUT|DELETE)\s+([^\s]+)', log_line)
        
        ip = ip_match.group(0) if ip_match else None
        url = url_match.group(2) if url_match else None
        
        return ip, url
    
    def _detect_attack_type(self, log_line: str) -> str:
        """Detect attack type from log patterns"""
        log_lower = log_line.lower()
        
        for attack_type, patterns in self.ATTACK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, log_lower):
                    return attack_type
        
        return "unknown"
    
    def _check_ip_reputation(self, ip: str) -> Tuple[float, int]:
        """
        Check IP reputation via VirusTotal
        
        Args:
            ip: IP address to check
        
        Returns:
            Tuple of (score 0-100, detection_count)
        """
        try:
            result = self.vt_api.check_ip(ip)
            
            if result.error:
                logger.warning(f"⚠️ VT error for IP {ip}: {result.error}")
                return 0.0, 0
            
            score = result.detection_ratio * 100
            logger.info(f"✓ IP {ip}: {result.detected_count} detections")
            
            return score, result.detected_count
            
        except Exception as e:
            logger.error(f"Error checking IP {ip}: {e}")
            return 0.0, 0
    
    def _check_url_reputation(self, url: str) -> Tuple[float, int]:
        """
        Check URL reputation via VirusTotal
        
        Args:
            url: URL to check
        
        Returns:
            Tuple of (score 0-100, detection_count)
        """
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            result = self.vt_api.check_url(url)
            
            if result.error:
                logger.warning(f"⚠️ VT error for URL {url}: {result.error}")
                return 0.0, 0
            
            score = result.detection_ratio * 100
            logger.info(f"✓ URL {url}: {result.detected_count} detections")
            
            return score, result.detected_count
            
        except Exception as e:
            logger.error(f"Error checking URL {url}: {e}")
            return 0.0, 0
    
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
    
    def predict(self, log_line: str) -> EnhancedWebLogPrediction:
        """
        Predict if web log is malicious with VirusTotal enhancement
        
        Args:
            log_line: Web server log line to analyze
        
        Returns:
            EnhancedWebLogPrediction with combined scores
        """
        logger.info("="*60)
        logger.info("ENHANCED WEB LOG DETECTION")
        logger.info("="*60)
        
        # Step 1: Anomaly Detection
        logger.info("\n[Step 1] Anomaly Detection")
        logger.info("-"*60)
        
        anomaly_result = self.analyzer.predict(log_line)
        anomaly_score = anomaly_result.get('anomaly_score', 0.0)
        is_anomaly = anomaly_result.get('is_anomaly', False)
        
        logger.info(f"Anomaly Score: {anomaly_score:.3f}")
        logger.info(f"Is Anomaly: {is_anomaly}")
        
        # Step 2: Extract IP and URL
        logger.info("\n[Step 2] IP/URL Extraction")
        logger.info("-"*60)
        
        ip, url = self._extract_ip_and_url(log_line)
        logger.info(f"IP: {ip}")
        logger.info(f"URL: {url}")
        
        # Step 3: VirusTotal Checks
        logger.info("\n[Step 3] VirusTotal Reputation Checks")
        logger.info("-"*60)
        
        ip_score, ip_detections = self._check_ip_reputation(ip) if ip else (0.0, 0)
        url_score, url_detections = self._check_url_reputation(url) if url else (0.0, 0)
        
        logger.info(f"IP Reputation Score: {ip_score:.1f}")
        logger.info(f"URL Reputation Score: {url_score:.1f}")
        
        # Step 4: Attack Type Detection
        logger.info("\n[Step 4] Attack Type Detection")
        logger.info("-"*60)
        
        attack_type = self._detect_attack_type(log_line)
        logger.info(f"Detected Attack Type: {attack_type}")
        
        # Step 5: Combined Scoring
        logger.info("\n[Step 5] Combined Scoring")
        logger.info("-"*60)
        
        # Normalize anomaly score (0-1) to percentage (0-100)
        anomaly_score_normalized = anomaly_score * 100
        
        # Weighted combination
        combined_score = (
            (anomaly_score_normalized * self.ANOMALY_WEIGHT) +
            (ip_score * self.IP_WEIGHT) +
            (url_score * self.URL_WEIGHT)
        )
        
        logger.info(f"Anomaly Score (normalized): {anomaly_score_normalized:.1f}")
        logger.info(f"IP Score: {ip_score:.1f}")
        logger.info(f"URL Score: {url_score:.1f}")
        logger.info(f"Combined Score: {combined_score:.1f}")
        
        # Risk level
        risk_level = self._get_risk_level(combined_score)
        logger.info(f"Risk Level: {risk_level}")
        
        # Step 6: Build explanation
        logger.info("\n[Step 6] Building Explanation")
        logger.info("-"*60)
        
        explanation = {
            "anomaly_detection": {
                "score": anomaly_score,
                "is_anomaly": is_anomaly,
            },
            "reputation_checks": {
                "ip_address": ip,
                "ip_score": ip_score,
                "ip_detections": ip_detections,
                "url": url,
                "url_score": url_score,
                "url_detections": url_detections,
            },
            "attack_detection": {
                "attack_type": attack_type,
            },
            "scoring": {
                "anomaly_weight": self.ANOMALY_WEIGHT,
                "ip_weight": self.IP_WEIGHT,
                "url_weight": self.URL_WEIGHT,
                "anomaly_contribution": anomaly_score_normalized * self.ANOMALY_WEIGHT,
                "ip_contribution": ip_score * self.IP_WEIGHT,
                "url_contribution": url_score * self.URL_WEIGHT,
            }
        }
        
        # Create result
        result = EnhancedWebLogPrediction(
            ip_address=ip or "unknown",
            request_path=url or "unknown",
            anomaly_score=anomaly_score,
            is_anomaly=is_anomaly,
            ip_reputation_score=ip_score,
            ip_detections=ip_detections,
            url_reputation_score=url_score,
            url_detections=url_detections,
            combined_score=combined_score,
            risk_level=risk_level,
            attack_type=attack_type,
            timestamp=datetime.now().isoformat(),
            explanation=explanation,
        )
        
        logger.info("="*60)
        logger.info(f"✅ RESULT: {attack_type.upper()} ({risk_level})")
        logger.info("="*60)
        
        return result
    
    def batch_predict(
        self, logs: List[str], verbose: bool = False
    ) -> List[EnhancedWebLogPrediction]:
        """
        Predict for multiple log lines
        
        Args:
            logs: List of log lines
            verbose: Whether to show progress
        
        Returns:
            List of predictions
        """
        results = []
        
        for i, log in enumerate(logs, 1):
            if verbose:
                logger.info(f"\nProcessing log {i}/{len(logs)}")
            
            result = self.predict(log)
            results.append(result)
        
        return results


def main():
    """Test enhanced web log analyzer"""
    # Test logs
    test_logs = [
        "192.168.1.100 - - [01/Dec/2025:10:15:30 +0000] \"GET /admin/users.php?id=1' OR '1'='1 HTTP/1.1\" 200 1234",
        "192.168.1.101 - - [01/Dec/2025:10:16:45 +0000] \"GET /index.html HTTP/1.1\" 200 5678",
        "192.168.1.102 - - [01/Dec/2025:10:17:12 +0000] \"POST /api/login HTTP/1.1\" 401 0",
    ]
    
    # Initialize analyzer
    analyzer = EnhancedWebLogAnalyzer()
    
    # Predict
    logger.info("\n" + "="*70)
    logger.info("ENHANCED WEB LOG ANALYSIS - BATCH PROCESSING")
    logger.info("="*70)
    
    results = analyzer.batch_predict(test_logs, verbose=True)
    
    # Print results
    logger.info("\n" + "="*70)
    logger.info("RESULTS SUMMARY")
    logger.info("="*70)
    
    for i, result in enumerate(results, 1):
        logger.info(f"\nLog {i}:")
        logger.info(f"  IP: {result.ip_address}")
        logger.info(f"  Anomaly Score: {result.anomaly_score:.3f}")
        logger.info(f"  Combined Score: {result.combined_score:.1f}")
        logger.info(f"  Attack Type: {result.attack_type}")
        logger.info(f"  Risk Level: {result.risk_level.upper()}")


if __name__ == "__main__":
    main()
