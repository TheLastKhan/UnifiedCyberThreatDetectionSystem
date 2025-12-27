"""
Email Feature Extraction Utilities
"""

import re
from collections import Counter

class EmailFeatureExtractor:
    """Email'lerden feature çıkaran yardımcı sınıf"""
    
    def __init__(self):
        self.suspicious_keywords = {
            'urgent': ['urgent', 'immediate', 'asap', 'expire', 'limited time', 'act now'],
            'financial': ['money', 'bank', 'account', 'credit', 'payment', 'transfer', 'prize', 'winner'],
            'personal': ['password', 'username', 'ssn', 'social security', 'verify account', 'confirm identity']
        }
    
    def extract_url_features(self, text):
        """URL özelliklerini çıkarır"""
        features = {}
        
        # Find all URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        features['url_count'] = len(urls)
        features['has_ip_url'] = any(re.match(r'http[s]?://\d+\.\d+\.\d+\.\d+', url) for url in urls)
        features['has_suspicious_tld'] = any(url.endswith(('.tk', '.ml', '.ga', '.cf')) for url in urls)
        features['has_shortener'] = any(('bit.ly' in url or 'tinyurl' in url) for url in urls)
        
        return features
    
    def extract_text_features(self, text):
        """Metin özelliklerini çıkarır"""
        features = {}
        
        features['length'] = len(text)
        features['word_count'] = len(text.split())
        features['sentence_count'] = len([s for s in text.split('.') if s.strip()])
        
        # Character analysis
        features['capital_ratio'] = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        features['digit_ratio'] = sum(1 for c in text if c.isdigit()) / max(len(text), 1)
        features['special_char_ratio'] = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1)
        
        # Punctuation
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['dollar_count'] = text.count('$')
        
        return features
    
    def extract_keyword_features(self, text):
        """Anahtar kelime özelliklerini çıkarır"""
        text_lower = text.lower()
        features = {}
        
        for category, keywords in self.suspicious_keywords.items():
            count = sum(text_lower.count(keyword) for keyword in keywords)
            features[f'{category}_keywords'] = count
        
        return features
