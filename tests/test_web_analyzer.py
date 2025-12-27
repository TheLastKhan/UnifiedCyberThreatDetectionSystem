"""
Web Analyzer Unit Tests
"""

import sys
sys.path.append('../src')

from src.web_analyzer.analyzer import WebLogAnalyzer
import pandas as pd

def test_log_parsing():
    """Log parse fonksiyonunu test eder"""
    analyzer = WebLogAnalyzer()
    
    log_line = '203.0.113.45 - - [10/Oct/2023:14:01:01 +0200] "POST /admin/login HTTP/1.1" 401 1234 "-" "Python-urllib/3.6"'
    
    parsed = analyzer.parse_log_line(log_line)
    
    assert parsed is not None
    assert parsed['ip'] == '203.0.113.45'
    assert parsed['method'] == 'POST'
    print("✅ Log parsing test passed")

def test_attack_pattern_detection():
    """Saldırı pattern tespitini test eder"""
    analyzer = WebLogAnalyzer()
    
    # SQL Injection pattern
    logs = [
        {'ip': '198.51.100.22', 'path': "/search?q=' UNION SELECT * FROM users--", 
         'method': 'GET', 'status': '500', 'timestamp': '10/Oct/2023:14:05:10 +0200',
         'user_agent': 'sqlmap/1.6.2'}
    ]
    
    attacks = analyzer.detect_attack_patterns(logs)
    
    assert 'SQL Injection Attempt' in attacks
    print("✅ Attack pattern detection test passed")

if __name__ == "__main__":
    test_log_parsing()
    test_attack_pattern_detection()
    print("\n🎉 All web analyzer tests passed!")
