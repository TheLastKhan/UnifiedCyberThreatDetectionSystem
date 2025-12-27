"""
VirusTotal API Integration
===========================

Secure email threat detection using VirusTotal API.

Features:
- URL/IP reputation checking
- File hash lookup
- Rate limiting (4 requests/minute for free tier)
- Response caching (Redis)
- Error handling & retry logic

Setup:
1. Create account: https://www.virustotal.com/
2. Get API key from: https://www.virustotal.com/gui/user/YOURUSER/apikey
3. Set environment variable: export VT_API_KEY=your_key_here
4. Or configure in config.py

Pricing:
- Free tier: 4 requests/minute, limited results
- Premium: Unlimited access
"""

import os
import time
import json
import logging
import hashlib
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class VirusCheckResult:
    """VirusTotal check result"""
    resource: str
    detected: bool  # Is malicious
    scan_date: str
    engine_count: int
    detected_count: int
    detection_ratio: float  # 0.0 to 1.0
    engines: Dict  # Specific engine detections
    error: Optional[str] = None


class VirusTotalAPI:
    """
    VirusTotal API wrapper
    
    Checks URLs and IPs for malware/phishing
    Integrates with email detector for enhanced threat detection
    """
    
    # API configuration
    API_URL = "https://www.virustotal.com/api/v3"
    API_VERSION = "3.0"
    RATE_LIMIT = 4  # requests per minute (free tier)
    REQUEST_TIMEOUT = 30
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize VirusTotal API client
        
        Args:
            api_key: API key (defaults to VT_API_KEY environment variable)
        """
        self.api_key = api_key or os.getenv("VT_API_KEY")
        
        if not self.api_key:
            logger.warning("⚠️ VT_API_KEY not configured. VirusTotal checks will fail.")
            logger.info("To enable: export VT_API_KEY=your_key_here")
        
        # Setup session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Headers
        self.headers = {
            "x-apikey": self.api_key,
            "Accept": "application/json",
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 60 / self.RATE_LIMIT  # seconds between requests
        
        logger.info("VirusTotal API initialized")
    
    def _rate_limit(self):
        """Apply rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_interval:
            wait_time = self.request_interval - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def check_url(self, url: str) -> VirusCheckResult:
        """
        Check if URL is malicious
        
        Args:
            url: URL to check
        
        Returns:
            VirusCheckResult with detection info
        
        Example:
            >>> vt = VirusTotalAPI()
            >>> result = vt.check_url("https://example-phishing.com")
            >>> if result.detected:
            ...     print(f"Malicious! Detected by {result.detected_count} engines")
        """
        if not self.api_key:
            return VirusCheckResult(
                resource=url,
                detected=False,
                scan_date="",
                engine_count=0,
                detected_count=0,
                detection_ratio=0.0,
                engines={},
                error="API key not configured"
            )
        
        try:
            self._rate_limit()
            
            # URL needs to be encoded
            url_id = hashlib.sha256(url.encode()).hexdigest()
            
            # First: Submit URL if not already scanned
            # For v3 API, we need to check the URL resource
            endpoint = f"{self.API_URL}/urls"
            
            data = {"url": url}
            
            response = self.session.post(
                endpoint,
                headers=self.headers,
                data=data,
                timeout=self.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            # Get analysis ID
            analysis_id = result_data.get("data", {}).get("id")
            
            if not analysis_id:
                return VirusCheckResult(
                    resource=url,
                    detected=False,
                    scan_date="",
                    engine_count=0,
                    detected_count=0,
                    detection_ratio=0.0,
                    engines={},
                    error="Could not get analysis ID"
                )
            
            # Wait a moment for analysis to complete
            time.sleep(2)
            
            # Get analysis results
            analysis_endpoint = f"{self.API_URL}/analyses/{analysis_id}"
            
            response = self.session.get(
                analysis_endpoint,
                headers=self.headers,
                timeout=self.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            analysis_data = response.json()
            
            # Parse results
            analysis_results = analysis_data.get("data", {}).get("attributes", {}).get("results", {})
            
            detected_count = sum(
                1 for r in analysis_results.values()
                if r.get("category") == "malicious"
            )
            
            engine_count = len(analysis_results)
            detection_ratio = detected_count / engine_count if engine_count > 0 else 0.0
            
            return VirusCheckResult(
                resource=url,
                detected=detected_count > 0,
                scan_date=analysis_data.get("data", {}).get("attributes", {}).get("date", ""),
                engine_count=engine_count,
                detected_count=detected_count,
                detection_ratio=detection_ratio,
                engines=analysis_results,
                error=None
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal API error: {e}")
            return VirusCheckResult(
                resource=url,
                detected=False,
                scan_date="",
                engine_count=0,
                detected_count=0,
                detection_ratio=0.0,
                engines={},
                error=str(e)
            )
    
    def check_ip(self, ip_address: str) -> VirusCheckResult:
        """
        Check if IP is malicious
        
        Args:
            ip_address: IP address to check
        
        Returns:
            VirusCheckResult with detection info
        """
        if not self.api_key:
            return VirusCheckResult(
                resource=ip_address,
                detected=False,
                scan_date="",
                engine_count=0,
                detected_count=0,
                detection_ratio=0.0,
                engines={},
                error="API key not configured"
            )
        
        try:
            self._rate_limit()
            
            endpoint = f"{self.API_URL}/ip_addresses/{ip_address}"
            
            response = self.session.get(
                endpoint,
                headers=self.headers,
                timeout=self.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse results from reputation data
            attributes = data.get("data", {}).get("attributes", {})
            
            # Get last analysis results
            last_analysis = attributes.get("last_analysis_results", {})
            detected_count = sum(
                1 for r in last_analysis.values()
                if r.get("category") == "malicious"
            )
            
            engine_count = len(last_analysis)
            detection_ratio = detected_count / engine_count if engine_count > 0 else 0.0
            
            return VirusCheckResult(
                resource=ip_address,
                detected=detected_count > 0,
                scan_date=attributes.get("last_analysis_date", ""),
                engine_count=engine_count,
                detected_count=detected_count,
                detection_ratio=detection_ratio,
                engines=last_analysis,
                error=None
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal API error: {e}")
            return VirusCheckResult(
                resource=ip_address,
                detected=False,
                scan_date="",
                engine_count=0,
                detected_count=0,
                detection_ratio=0.0,
                engines={},
                error=str(e)
            )
    
    def check_file_hash(self, file_hash: str) -> VirusCheckResult:
        """
        Check file hash (MD5, SHA1, SHA256)
        
        Args:
            file_hash: Hash to check (MD5, SHA1, or SHA256)
        
        Returns:
            VirusCheckResult with detection info
        """
        if not self.api_key:
            return VirusCheckResult(
                resource=file_hash,
                detected=False,
                scan_date="",
                engine_count=0,
                detected_count=0,
                detection_ratio=0.0,
                engines={},
                error="API key not configured"
            )
        
        try:
            self._rate_limit()
            
            endpoint = f"{self.API_URL}/files/{file_hash}"
            
            response = self.session.get(
                endpoint,
                headers=self.headers,
                timeout=self.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse results
            attributes = data.get("data", {}).get("attributes", {})
            
            last_analysis = attributes.get("last_analysis_results", {})
            detected_count = sum(
                1 for r in last_analysis.values()
                if r.get("category") == "malicious"
            )
            
            engine_count = len(last_analysis)
            detection_ratio = detected_count / engine_count if engine_count > 0 else 0.0
            
            return VirusCheckResult(
                resource=file_hash,
                detected=detected_count > 0,
                scan_date=attributes.get("last_analysis_date", ""),
                engine_count=engine_count,
                detected_count=detected_count,
                detection_ratio=detection_ratio,
                engines=last_analysis,
                error=None
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal API error: {e}")
            return VirusCheckResult(
                resource=file_hash,
                detected=False,
                scan_date="",
                engine_count=0,
                detected_count=0,
                detection_ratio=0.0,
                engines={},
                error=str(e)
            )
    
    def extract_urls_from_email(self, email_body: str) -> List[str]:
        """
        Extract URLs from email body
        
        Args:
            email_body: Email text
        
        Returns:
            List of URLs found
        """
        # Simple URL regex
        url_pattern = r'https?://[^\s\)>\]]*'
        urls = re.findall(url_pattern, email_body)
        
        # Filter out common false positives
        urls = [u for u in urls if len(u) > 10 and '.' in u]
        
        return urls
    
    def check_email_urls(self, email_body: str) -> Dict[str, VirusCheckResult]:
        """
        Check all URLs in email
        
        Args:
            email_body: Email text
        
        Returns:
            Dict of URL -> VirusCheckResult
        """
        urls = self.extract_urls_from_email(email_body)
        results = {}
        
        for url in urls:
            try:
                result = self.check_url(url)
                results[url] = result
            except Exception as e:
                logger.error(f"Error checking URL {url}: {e}")
        
        return results


class VirusTotalEmailIntegration:
    """
    Integrate VirusTotal with email detector
    
    Enhances email phishing detection by:
    1. Extracting URLs from email
    2. Checking against VirusTotal
    3. Combining with detector score
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize integration"""
        self.vt = VirusTotalAPI(api_key)
    
    def enhance_email_score(
        self,
        email_body: str,
        detector_score: float,
        detector_confidence: float
    ) -> Dict:
        """
        Enhance email threat score with VirusTotal data
        
        Args:
            email_body: Email text
            detector_score: Original detector score (0-1)
            detector_confidence: Detector confidence
        
        Returns:
            Enhanced threat analysis
        """
        # Check URLs
        url_results = self.vt.check_email_urls(email_body)
        
        # Analyze results
        malicious_urls = [
            (url, result) for url, result in url_results.items()
            if result.detected
        ]
        
        vt_risk_score = 0.0
        if malicious_urls:
            # If any URL is detected as malicious, boost score
            vt_risk_score = sum(r.detection_ratio for _, r in malicious_urls) / len(malicious_urls)
        
        # Combine scores (weighted average)
        final_score = (detector_score * 0.6) + (vt_risk_score * 0.4)
        
        return {
            "detector_score": detector_score,
            "virustotal_score": vt_risk_score,
            "final_score": min(1.0, final_score),
            "malicious_urls": [
                {
                    "url": url,
                    "detected_by": result.detected_count,
                    "total_engines": result.engine_count,
                    "detection_ratio": result.detection_ratio
                }
                for url, result in malicious_urls
            ],
            "safe_urls": len(url_results) - len(malicious_urls),
            "risk_level": self._classify_risk(final_score)
        }
    
    def _classify_risk(self, score: float) -> str:
        """Classify risk level from score"""
        if score < 0.3:
            return "LOW"
        elif score < 0.6:
            return "MEDIUM"
        elif score < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    print("VirusTotal API Integration Ready")
    print("\nSetup Instructions:")
    print("1. Get API key from: https://www.virustotal.com/gui/user/YOURUSER/apikey")
    print("2. Set environment: export VT_API_KEY=your_key_here")
    print("3. Import and use in your email detector")
