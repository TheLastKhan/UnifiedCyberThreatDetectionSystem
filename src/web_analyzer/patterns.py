"""
Attack Pattern Detection Utilities
"""

import re

class AttackPatternDetector:
    """Saldırı pattern'lerini tespit eden sınıf"""
    
    def __init__(self):
        self.patterns = {
            'sql_injection': [
                r'union.*select',
                r'or\s+1\s*=\s*1',
                r'drop\s+table',
                r'insert\s+into',
                r';\s*--',
                r'\'.*or.*\'.*=.*\''
            ],
            'xss': [
                r'<script',
                r'javascript:',
                r'onerror\s*=',
                r'onload\s*='
            ],
            'directory_traversal': [
                r'\.\./\.\.',
                r'\.\.\\\.\.', 
                r'%2e%2e',
                r'etc/passwd',
                r'windows/system32'
            ],
            'command_injection': [
                r';\s*cat\s+',
                r';\s*ls\s+',
                r'\|\s*whoami',
                r'&&\s*pwd'
            ]
        }
    
    def detect_pattern(self, text, pattern_type):
        """Belirli bir pattern tipini tespit eder"""
        if pattern_type not in self.patterns:
            return False
        
        text_lower = text.lower()
        for pattern in self.patterns[pattern_type]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def detect_all_patterns(self, text):
        """Tüm pattern'leri tespit eder"""
        detected = []
        for pattern_type in self.patterns.keys():
            if self.detect_pattern(text, pattern_type):
                detected.append(pattern_type)
        return detected

class BehavioralAnalyzer:
    """Davranışsal analiz yapan sınıf"""
    
    @staticmethod
    def analyze_request_timing(timestamps):
        """İstek zamanlamasını analiz eder"""
        if len(timestamps) < 2:
            return {'regular': False, 'bot_like': False}
        
        intervals = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(diff)
        
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        
        # Very regular timing = bot
        is_regular = variance < 1.0
        is_bot_like = is_regular and avg_interval < 5
        
        return {
            'regular': is_regular,
            'bot_like': is_bot_like,
            'avg_interval': avg_interval,
            'variance': variance
        }
    
    @staticmethod
    def analyze_user_agent(user_agents):
        """User agent pattern'lerini analiz eder"""
        unique_agents = set(user_agents)
        
        bot_indicators = ['bot', 'crawler', 'spider', 'scan', 'python', 'curl', 'wget']
        
        bot_count = sum(1 for ua in user_agents 
                       if any(indicator in ua.lower() for indicator in bot_indicators))
        
        return {
            'unique_count': len(unique_agents),
            'bot_ratio': bot_count / len(user_agents) if user_agents else 0,
            'is_likely_bot': bot_count / len(user_agents) > 0.5 if user_agents else False
        }