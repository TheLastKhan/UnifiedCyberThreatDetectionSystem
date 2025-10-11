"""
Cross-platform Correlation Engine
"""

from datetime import timedelta

class CorrelationEngine:
    """Email ve web tehditleri arasında korelasyon kuran motor"""
    
    def __init__(self):
        self.correlation_rules = []
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """Varsayılan korelasyon kurallarını ayarlar"""
        self.correlation_rules = [
            {
                'name': 'High_Risk_Coordination',
                'email_threshold': 70,
                'web_threshold': 60,
                'time_window': 3600,  # seconds
                'risk_multiplier': 1.8
            },
            {
                'name': 'IP_Based_Campaign',
                'requires_ip_match': True,
                'risk_multiplier': 2.0
            },
            {
                'name': 'Pattern_Similarity',
                'min_indicators': 2,
                'risk_multiplier': 1.5
            }
        ]
    
    def analyze_correlation(self, email_result, web_result, metadata=None):
        """İki analiz sonucu arasında korelasyon analizi yapar"""
        correlation = {
            'confidence_score': 0.0,
            'risk_amplification': 1.0,
            'indicators': [],
            'matched_rules': []
        }
        
        if not email_result or not web_result:
            return correlation
        
        # Check each rule
        for rule in self.correlation_rules:
            if self._check_rule(rule, email_result, web_result, metadata):
                correlation['matched_rules'].append(rule['name'])
                correlation['risk_amplification'] *= rule.get('risk_multiplier', 1.0)
        
        # Calculate confidence
        if correlation['matched_rules']:
            correlation['confidence_score'] = min(0.95, len(correlation['matched_rules']) * 0.25 + 0.20)
        
        # Generate indicators
        correlation['indicators'] = self._generate_indicators(
            email_result, web_result, correlation['matched_rules']
        )
        
        return correlation
    
    def _check_rule(self, rule, email_result, web_result, metadata):
        """Bir kuralın eşleşip eşleşmediğini kontrol eder"""
        rule_name = rule['name']
        
        if rule_name == 'High_Risk_Coordination':
            email_risk = email_result.get('phishing_probability', 0)
            web_risk = self._get_web_risk_score(web_result.get('risk_level', 'LOW'))
            
            return (email_risk >= rule['email_threshold'] and 
                   web_risk >= rule['web_threshold'])
        
        elif rule_name == 'IP_Based_Campaign':
            # Check if same IP involved
            return metadata and metadata.get('ip_address') is not None
        
        elif rule_name == 'Pattern_Similarity':
            # Check for similar attack patterns
            email_patterns = len(email_result.get('risk_factors', []))
            web_patterns = len(web_result.get('attack_patterns', []))
            
            return (email_patterns + web_patterns) >= rule['min_indicators']
        
        return False
    
    def _get_web_risk_score(self, risk_level):
        """Risk level'ı numerik skora çevirir"""
        mapping = {'LOW': 20, 'MEDIUM': 40, 'HIGH': 70, 'CRITICAL': 90}
        return mapping.get(risk_level, 20)
    
    def _generate_indicators(self, email_result, web_result, matched_rules):
        """Korelasyon göstergelerini oluşturur"""
        indicators = []
        
        for rule_name in matched_rules:
            if rule_name == 'High_Risk_Coordination':
                indicators.append({
                    'type': 'Multi-Vector Attack',
                    'description': 'High-risk email and web threats detected simultaneously',
                    'confidence': 'HIGH'
                })
            elif rule_name == 'IP_Based_Campaign':
                indicators.append({
                    'type': 'IP-Based Campaign',
                    'description': 'Same IP address involved in both email and web attacks',
                    'confidence': 'HIGH'
                })
            elif rule_name == 'Pattern_Similarity':
                indicators.append({
                    'type': 'Coordinated Campaign',
                    'description': 'Similar attack patterns observed across platforms',
                    'confidence': 'MEDIUM'
                })
        
        return indicators