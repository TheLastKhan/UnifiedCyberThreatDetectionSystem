"""
Unified Threat Detection Platform
Main Integration Module for Email & Web Security Analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json
import logging
from typing import Dict, List, Tuple, Optional, Any, Union

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..email_detector.detector import EmailPhishingDetector
from ..web_analyzer.analyzer import WebLogAnalyzer

class UnifiedThreatPlatform:
    """
    Unified platform for detecting threats across email and web domains.
    
    Integrates email phishing detection, web log analysis, and cross-platform
    correlation to provide comprehensive threat intelligence.
    
    Attributes:
        email_detector: EmailPhishingDetector instance
        web_analyzer: WebLogAnalyzer instance
        correlation_engine: CorrelationEngine for cross-platform analysis
        threat_intelligence: ThreatIntelligence module
    """
    
    def __init__(self, email_config: Optional[Dict[str, Any]] = None, web_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Unified Threat Detection Platform.
        
        Args:
            email_config (dict, optional): Configuration for email detector
            web_config (dict, optional): Configuration for web analyzer
        """
        self.email_detector = EmailPhishingDetector(email_config)
        self.web_analyzer = WebLogAnalyzer(web_config)
        self.correlation_engine = CorrelationEngine()
        self.threat_intelligence = ThreatIntelligence()
        
    def initialize(self, email_data: Optional[Tuple[pd.DataFrame, List[int]]] = None, web_logs: Optional[pd.DataFrame] = None) -> None:
        """
        Initialize platform and train models.
        
        Trains email phishing detector and web log anomaly detector
        on provided datasets.
        
        Args:
            email_data (tuple, optional): (emails_df, labels) for training email detector
            web_logs (pd.DataFrame, optional): Web logs for training web analyzer
            
        Raises:
            ValueError: If provided data is invalid
        """
        try:
            print("🚀 Initializing Unified Threat Detection Platform...")
            
            # Train email detector
            if email_data is not None:
                try:
                    emails_df, labels = email_data
                    self.email_detector.train(emails_df, labels)
                except Exception as e:
                    logger.error(f"Error training email detector: {e}")
                    raise
            
            # Train web analyzer  
            if web_logs is not None and not web_logs.empty:
                try:
                    self.web_analyzer.train_anomaly_detector(web_logs)
                except Exception as e:
                    logger.error(f"Error training web analyzer: {e}")
                    raise
            
            print("✅ Platform initialization completed!")
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise
    
    def analyze_unified_threat(self, email_data: Optional[Union[Dict[str, str], str]] = None, 
                              web_logs: Optional[List[Dict[str, Any]]] = None, 
                              ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform unified threat analysis across email and web platforms.
        
        Analyzes potential threats from both email and web perspectives,
        correlates findings, and calculates unified risk scores.
        
        Args:
            email_data (dict or str, optional): Email content as dict or text
            web_logs (list or pd.DataFrame, optional): Web logs to analyze
            ip_address (str, optional): IP address for correlation
            
        Returns:
            dict: Comprehensive threat analysis containing:
                - timestamp: Analysis timestamp
                - email_analysis: Email detection results
                - web_analysis: Web analysis results
                - correlation_analysis: Cross-platform findings
                - unified_risk_score: Overall risk (0-100)
                - threat_level: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
                - recommendations: Security recommendations
        """
        try:
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
                try:
                    if isinstance(email_data, dict):
                        results['email_analysis'] = self.email_detector.predict_with_explanation(
                            email_data.get('body', ''),
                            email_data.get('sender', ''),
                            email_data.get('subject', '')
                        )
                    else:
                        results['email_analysis'] = self.email_detector.predict_with_explanation(email_data)
                except Exception as e:
                    logger.error(f"Error analyzing email: {e}")
            
            # Web analysis
            if web_logs and ip_address:
                try:
                    results['web_analysis'] = self.web_analyzer.analyze_ip_with_explanation(
                        web_logs, ip_address
                    )
                except Exception as e:
                    logger.error(f"Error analyzing web logs: {e}")
            
            # Correlation analysis
            if results['email_analysis'] and results['web_analysis']:
                try:
                    results['correlation_analysis'] = self.correlation_engine.analyze_correlation(
                        results['email_analysis'],
                        results['web_analysis'],
                        ip_address
                    )
                except Exception as e:
                    logger.error(f"Error in correlation analysis: {e}")
            
            # Calculate unified risk
            results['unified_risk_score'] = self._calculate_unified_risk(results)
            results['threat_level'] = self._determine_threat_level(results['unified_risk_score'])
            
            # Generate recommendations
            results['recommendations'] = self._generate_unified_recommendations(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in unified threat analysis: {e}")
            raise
    
    def _calculate_unified_risk(self, results: Dict[str, Any]) -> float:
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
    
    def _determine_threat_level(self, risk_score: float) -> str:
        """Risk skoruna göre tehdit seviyesi belirler"""
        if risk_score >= 80:
            return 'CRITICAL'
        elif risk_score >= 60:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_unified_recommendations(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
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

