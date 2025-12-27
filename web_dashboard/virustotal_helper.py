"""
VirusTotal Integration for IP and Domain Reputation Checking
"""

import requests
import os
from datetime import datetime, timedelta

# VirusTotal API Key (set in environment)
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', '')

# Cache for VirusTotal results (to avoid rate limits)
_vt_cache = {}
_cache_ttl = timedelta(hours=24)


def check_ip_reputation(ip_address):
    """
    Check IP reputation using VirusTotal API
    
    Returns:
        dict: {
            'malicious': int,
            'suspicious': int,
            'harmless': int,
            'undetected': int,
            'reputation': str,
            'country': str,
            'asn': str,
            'last_analysis_date': str
        }
    """
    if not VIRUSTOTAL_API_KEY:
        return {
            'error': 'VirusTotal API key not configured',
            'malicious': 0,
            'suspicious': 0,
            'harmless': 0,
            'undetected': 0,
            'reputation': 'Unknown',
            'country': 'Unknown',
            'asn': 'Unknown'
        }
    
    # Check cache
    cache_key = f"ip_{ip_address}"
    if cache_key in _vt_cache:
        cached_data, cached_time = _vt_cache[cache_key]
        if datetime.now() - cached_time < _cache_ttl:
            return cached_data
    
    try:
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip_address}"
        headers = {
            "x-apikey": VIRUSTOTAL_API_KEY
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            harmless = stats.get('harmless', 0)
            undetected = stats.get('undetected', 0)
            
            # Determine reputation
            if malicious > 0:
                reputation = 'Malicious'
            elif suspicious > 0:
                reputation = 'Suspicious'
            elif harmless > 0:
                reputation = 'Clean'
            else:
                reputation = 'Unknown'
            
            result = {
                'malicious': malicious,
                'suspicious': suspicious,
                'harmless': harmless,
                'undetected': undetected,
                'reputation': reputation,
                'country': attributes.get('country', 'Unknown'),
                'asn': str(attributes.get('asn', 'Unknown')),
                'last_analysis_date': attributes.get('last_analysis_date', '')
            }
            
            # Cache result
            _vt_cache[cache_key] = (result, datetime.now())
            
            return result
        
        elif response.status_code == 404:
            return {
                'error': 'IP not found in VirusTotal database',
                'malicious': 0,
                'suspicious': 0,
                'harmless': 0,
                'undetected': 0,
                'reputation': 'Unknown',
                'country': 'Unknown',
                'asn': 'Unknown'
            }
        
        else:
            return {
                'error': f'VirusTotal API error: {response.status_code}',
                'malicious': 0,
                'suspicious': 0,
                'harmless': 0,
                'undetected': 0,
                'reputation': 'Unknown',
                'country': 'Unknown',
                'asn': 'Unknown'
            }
    
    except Exception as e:
        print(f"[ERROR] VirusTotal IP check error: {e}")
        return {
            'error': str(e),
            'malicious': 0,
            'suspicious': 0,
            'harmless': 0,
            'undetected': 0,
            'reputation': 'Unknown',
            'country': 'Unknown',
            'asn': 'Unknown'
        }


def check_domain_reputation(domain):
    """
    Check domain reputation using VirusTotal API
    
    Returns:
        dict: {
            'malicious': int,
            'suspicious': int,
            'harmless': int,
            'undetected': int,
            'reputation': str,
            'categories': dict,
            'last_analysis_date': str
        }
    """
    if not VIRUSTOTAL_API_KEY:
        return {
            'error': 'VirusTotal API key not configured',
            'malicious': 0,
            'suspicious': 0,
            'harmless': 0,
            'undetected': 0,
            'reputation': 'Unknown',
            'categories': {}
        }
    
    # Check cache
    cache_key = f"domain_{domain}"
    if cache_key in _vt_cache:
        cached_data, cached_time = _vt_cache[cache_key]
        if datetime.now() - cached_time < _cache_ttl:
            return cached_data
    
    try:
        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {
            "x-apikey": VIRUSTOTAL_API_KEY
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            attributes = data.get('data', {}).get('attributes', {})
            stats = attributes.get('last_analysis_stats', {})
            
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            harmless = stats.get('harmless', 0)
            undetected = stats.get('undetected', 0)
            
            # Determine reputation
            if malicious > 0:
                reputation = 'Malicious'
            elif suspicious > 0:
                reputation = 'Suspicious'
            elif harmless > 0:
                reputation = 'Clean'
            else:
                reputation = 'Unknown'
            
            result = {
                'malicious': malicious,
                'suspicious': suspicious,
                'harmless': harmless,
                'undetected': undetected,
                'reputation': reputation,
                'categories': attributes.get('categories', {}),
                'last_analysis_date': attributes.get('last_analysis_date', '')
            }
            
            # Cache result
            _vt_cache[cache_key] = (result, datetime.now())
            
            return result
        
        elif response.status_code == 404:
            return {
                'error': 'Domain not found in VirusTotal database',
                'malicious': 0,
                'suspicious': 0,
                'harmless': 0,
                'undetected': 0,
                'reputation': 'Unknown',
                'categories': {}
            }
        
        else:
            return {
                'error': f'VirusTotal API error: {response.status_code}',
                'malicious': 0,
                'suspicious': 0,
                'harmless': 0,
                'undetected': 0,
                'reputation': 'Unknown',
                'categories': {}
            }
    
    except Exception as e:
        print(f"[ERROR] VirusTotal domain check error: {e}")
        return {
            'error': str(e),
            'malicious': 0,
            'suspicious': 0,
            'harmless': 0,
            'undetected': 0,
            'reputation': 'Unknown',
            'categories': {}
        }


def extract_domain_from_email(email_address):
    """Extract domain from email address"""
    if '@' in email_address:
        return email_address.split('@')[1]
    return email_address
