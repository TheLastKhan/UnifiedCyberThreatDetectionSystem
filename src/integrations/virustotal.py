"""
VirusTotal API Integration
Enriches threat analysis with reputation checks for IPs, domains, and file hashes
"""

import os
import requests
import time
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class VirusTotalClient:
    """
    VirusTotal API v3 client for threat intelligence enrichment
    Rate limits: Free tier = 4 requests/minute
    """
    
    BASE_URL = "https://www.virustotal.com/api/v3"
    RATE_LIMIT_DELAY = 15  # seconds between requests (free tier)
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize VirusTotal client
        
        Args:
            api_key: VirusTotal API key (or use VIRUSTOTAL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('VIRUSTOTAL_API_KEY')
        if not self.api_key:
            logger.warning("VirusTotal API key not configured. Integration disabled.")
            self.enabled = False
        else:
            self.enabled = True
            
        self.last_request_time = None
        self.session = requests.Session()
        self.session.headers.update({  # type: ignore[arg-type]
            'x-apikey': self.api_key,
            'Accept': 'application/json'
        })
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting for free tier"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.RATE_LIMIT_DELAY:
                sleep_time = self.RATE_LIMIT_DELAY - elapsed
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def check_ip(self, ip_address: str) -> Dict:
        """
        Check IP reputation on VirusTotal
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Dict with reputation data:
            {
                'malicious': int,
                'suspicious': int,
                'harmless': int,
                'undetected': int,
                'reputation': int,
                'country': str,
                'as_owner': str
            }
        """
        if not self.enabled:
            return {'error': 'VirusTotal not configured'}
        
        try:
            self._wait_for_rate_limit()
            
            url = f"{self.BASE_URL}/ip_addresses/{ip_address}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            
            # Extract analysis stats
            stats = attributes.get('last_analysis_stats', {})
            
            return {
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'harmless': stats.get('harmless', 0),
                'undetected': stats.get('undetected', 0),
                'reputation': attributes.get('reputation', 0),
                'country': attributes.get('country', 'Unknown'),
                'as_owner': attributes.get('as_owner', 'Unknown'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal API error for IP {ip_address}: {e}")
            return {'error': str(e)}
    
    def check_domain(self, domain: str) -> Dict:
        """
        Check domain reputation on VirusTotal
        
        Args:
            domain: Domain name to check
            
        Returns:
            Dict with reputation data
        """
        if not self.enabled:
            return {'error': 'VirusTotal not configured'}
        
        try:
            self._wait_for_rate_limit()
            
            url = f"{self.BASE_URL}/domains/{domain}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            
            # Extract analysis stats
            stats = attributes.get('last_analysis_stats', {})
            
            return {
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'harmless': stats.get('harmless', 0),
                'undetected': stats.get('undetected', 0),
                'reputation': attributes.get('reputation', 0),
                'categories': attributes.get('categories', {}),
                'creation_date': attributes.get('creation_date'),
                'last_update_date': attributes.get('last_update_date'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal API error for domain {domain}: {e}")
            return {'error': str(e)}
    
    def check_url(self, url: str) -> Dict:
        """
        Check URL reputation on VirusTotal
        
        Args:
            url: URL to check
            
        Returns:
            Dict with reputation data
        """
        if not self.enabled:
            return {'error': 'VirusTotal not configured'}
        
        try:
            self._wait_for_rate_limit()
            
            # URL needs to be base64 encoded without padding
            import base64
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip('=')
            
            endpoint = f"{self.BASE_URL}/urls/{url_id}"
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            
            # Extract analysis stats
            stats = attributes.get('last_analysis_stats', {})
            
            return {
                'malicious': stats.get('malicious', 0),
                'suspicious': stats.get('suspicious', 0),
                'harmless': stats.get('harmless', 0),
                'undetected': stats.get('undetected', 0),
                'categories': attributes.get('categories', {}),
                'last_final_url': attributes.get('last_final_url'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"VirusTotal API error for URL {url}: {e}")
            return {'error': str(e)}
    
    def enrich_threat_data(self, threat_type: str, threat_value: str) -> Dict:
        """
        Automatic enrichment based on threat type
        
        Args:
            threat_type: 'ip', 'domain', or 'url'
            threat_value: Value to check
            
        Returns:
            Dict with enriched data
        """
        if threat_type == 'ip':
            return self.check_ip(threat_value)
        elif threat_type == 'domain':
            return self.check_domain(threat_value)
        elif threat_type == 'url':
            return self.check_url(threat_value)
        else:
            return {'error': f'Unsupported threat type: {threat_type}'}


# Global singleton instance
_vt_client = None

def get_virustotal_client() -> VirusTotalClient:
    """Get or create VirusTotal client singleton"""
    global _vt_client
    if _vt_client is None:
        _vt_client = VirusTotalClient()
    return _vt_client
