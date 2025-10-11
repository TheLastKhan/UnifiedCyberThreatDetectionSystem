"""
Unified Threat Detection Platform
Main Integration Module
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json

from ..email_detector.detector import EmailPhishingDetector
from ..web_analyzer.analyzer import WebLogAnalyzer

class UnifiedThreatPlatform:
    def __init__(self, email_config=None, web_config=None):
        self.email_detector = EmailPhishingDetector(email_config)
        self.web_analyzer = WebLogAnalyzer(web_config)
        self.correlation_engine = CorrelationEngine()
        self.threat_intelligence = ThreatIntelligence()
        
    def initialize(self, email_data=None, web_logs=None):
        """Platform'u başlatır ve modelleri eğitir"""
        print("🚀 Initializing Unified Threat Detection Platform...")
        
        # Train email detector
        if email_data is not None:
            emails_df, labels = email_data
            self.email_detector.train(emails_df, labels)
        
        # Train web analyzer  
        if web_logs is not None and not web_logs.empty:
            self.web_analyzer.train_anomaly_detector(web_logs)
        
        print("✅ Platform initialization completed!")
    
    def analyze_unified_threat(self, email_data=None, web_logs=None, ip_address=None):
        """Birleşik tehdit analizi yapar"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'email_analysis': None,
            'web_analysis': None,
            'correlation_analysis': None,
            'unified_risk_score': 0,
            'threat_level': 'LOW',
            'recommendations': []
        }
        
        # Email analysis
        if email_data:
            if isinstance(email_data, dict):
                results['email_analysis'] = self.email_detector.predict_with_explanation(
                    email_data.get('body', ''),
                    email_data.get('sender', ''),
                    email_data.get('subject', '')
                )
            else:
                results['email_analysis'] = self.email_detector.predict_with_explanation(email_data)
        
        # Web analysis
        if web_logs and ip_address:
            results['web_analysis'] = self.web_analyzer.analyze_ip_with_explanation(
                web_logs, ip_address
            )
        
        # Correlation analysis
        if results['email_analysis'] and results['web_analysis']:
            results['correlation_analysis'] = self.correlation_engine.analyze_correlation(
                results['email_analysis'],
                results['web_analysis'],
                ip_address
            )
        
        # Calculate unified risk
        results['unified_risk_score'] = self._calculate_unified_risk(results)
        results['threat_level'] = self._determine_threat_level(results['unified_risk_score'])
        
        # Generate recommendations
        results['recommendations'] = self._generate_unified_recommendations(results)
        
        return results
    
    def _calculate_unified_risk(self, results):
        """Birleşik risk skorunu hesaplar"""
        email_risk = 0
        web_risk = 0
        correlation_bonus = 0
        
        # Email risk (0-40 points)
        if results['email_analysis']:
            email_risk = min(40, results['email_analysis']['phishing_probability'] * 0.4)
        
        # Web risk (0-40 points)
        if results['web_analysis']:
            risk_mapping = {'LOW': 5, 'MEDIUM': 15, 'HIGH': 30, 'CRITICAL': 40}
            web_risk = risk_mapping.get(results['web_analysis']['risk_level'], 5)
        
        # Correlation bonus (0-20 points)
        if results['correlation_analysis']:
            correlation_bonus = len(results['correlation_analysis'].get('indicators', [])) * 10
        
        total_risk = min(100, email_risk + web_risk + correlation_bonus)
        return round(total_risk, 1)
    
    def _determine_threat_level(self, risk_score):
        """Risk skoruna göre tehdit seviyesi belirler"""
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_unified_recommendations(self, results):
        """Birleşik öneriler oluşturur"""
        recommendations = {
            'immediate': [],
            'short_term': [],
            'long_term': []
        }
        
        # Email-based recommendations
        if (results['email_analysis'] and 
            results['email_analysis']['prediction'] == 'Phishing'):
            recommendations['immediate'].extend([
                '📧 Block sender immediately',
                '🚨 Alert security team'
            ])
        
        # Web-based recommendations
        if (results['web_analysis'] and 
            results['web_analysis']['risk_level'] in ['HIGH', 'CRITICAL']):
            recommendations['immediate'].extend([
                '🛡️ Block suspicious IP',
                '📊 Enhanced monitoring'
            ])
        
        # Correlation-based recommendations
        if results['correlation_analysis']:
            recommendations['short_term'].extend([
                '🔗 Implement correlation rules',
                '📈 Cross-platform monitoring'
            ])
        
        return recommendations

class CorrelationEngine:
    """Korelasyon analizi motoru"""
    
    def analyze_correlation(self, email_result, web_result, ip_address):
        """Email ve web sonuçları arasında korelasyon analizi"""
        correlation = {
            'indicators': [],
            'confidence_score': 0.0,
            'risk_amplification': 1.0
        }
        
        # IP-based correlation
        if (email_result['phishing_probability'] > 50 and 
            web_result['is_anomaly']):
            correlation['indicators'].append({
                'type': 'Multi-Vector Attack',
                'description': 'Phishing email + web anomaly from same source',
                'confidence': 'HIGH'
            })
            correlation['risk_amplification'] *= 1.5
        
        # Timing correlation (simulated)
        if (email_result['phishing_probability'] > 40 and 
            len(web_result['attack_patterns']) > 0):
            correlation['indicators'].append({
                'type': 'Coordinated Campaign',
                'description': 'Email phishing followed by web attacks',
                'confidence': 'MEDIUM'
            })
            correlation['risk_amplification'] *= 1.3
        
        # Calculate confidence
        if correlation['indicators']:
            correlation['confidence_score'] = min(0.95, len(correlation['indicators']) * 0.3)
        
        return correlation

class ThreatIntelligence:
    """Tehdit istihbaratı modülü"""
    
    def generate_intelligence_report(self, analysis_results):
        """Tehdit istihbaratı raporu oluşturur"""
        intelligence = {
            'attack_techniques': [],
            'iocs': [],  # Indicators of Compromise
            'attribution': 'UNKNOWN',
            'campaign_indicators': []
        }
        
        # Email-based techniques
        if (analysis_results.get('email_analysis') and 
            analysis_results['email_analysis']['prediction'] == 'Phishing'):
            intelligence['attack_techniques'].extend([
                'Social Engineering',
                'Email Phishing',
                'Credential Harvesting'
            ])
        
        # Web-based techniques
        if analysis_results.get('web_analysis'):
            for pattern in analysis_results['web_analysis'].get('attack_patterns', []):
                if pattern == 'Brute Force Attack':
                    intelligence['attack_techniques'].append('Credential Brute Force')
                elif pattern == 'SQL Injection Attempt':
                    intelligence['attack_techniques'].append('SQL Injection')
        
        return intelligence
