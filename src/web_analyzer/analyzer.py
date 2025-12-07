"""
Web Log Analysis Module
Unified Threat Detection Platform
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import ipaddress
import logging
from typing import Dict, List, Tuple, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebLogAnalyzer:
    """
    Web log analysis using machine learning and behavioral analysis.
    
    This class analyzes web server logs to detect anomalies and attacks
    using Isolation Forest anomaly detection and pattern matching.
    
    Attributes:
        config (dict): Configuration parameters for the analyzer
        scaler: StandardScaler for feature normalization
        anomaly_detector: IsolationForest model for anomaly detection
        feature_names (list): Names of all features used in the model
        is_trained (bool): Whether the model has been trained
        attack_patterns (dict): Definitions of known attack patterns
    """
    
    def __init__(self, config=None):
        """
        Initialize the WebLogAnalyzer.
        
        Args:
            config (dict, optional): Configuration dictionary with keys:
                - contamination (float): Expected proportion of anomalies (default: 0.1)
                - random_state (int): Random seed for reproducibility (default: 42)
        """
        self.config = config or {}
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(
            contamination=self.config.get('contamination', 0.1),
            random_state=self.config.get('random_state', 42)
        )
        self.feature_names = []
        self.is_trained = False
        self.attack_patterns = {}
        
    def parse_log_line(self, log_line: str) -> Optional[Dict[str, str]]:
        """
        Parse Apache/Nginx combined log format.
        
        Args:
            log_line (str): A single line from web server log
            
        Returns:
            dict: Parsed log components or None if parsing fails
                - ip, timestamp, method, path, protocol
                - status, size, referer, user_agent
                
        Example:
            >>> log = '192.168.1.1 - - [01/Jan/2025:12:00:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
            >>> parser.parse_log_line(log)
        """
        try:
            # Combined Log Format pattern
            pattern = (r'(?P<ip>\d+\.\d+\.\d+\.\d+) '
                      r'- - \[(?P<timestamp>[^\]]+)\] '
                      r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" '
                      r'(?P<status>\d+) (?P<size>\S+) '
                      r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"')
            
            match = re.match(pattern, log_line)
            if not match:
                logger.warning(f"Failed to parse log line: {log_line[:50]}...")
                return None
            
            return match.groupdict()
            
        except Exception as e:
            logger.error(f"Error parsing log line: {e}")
            return None
    
    def extract_behavioral_features(self, ip_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """IP'nin davranışsal özelliklerini çıkarır"""
        if not ip_logs:
            return {}
        
        # Basic metrics
        request_count = len(ip_logs)
        
        # Time analysis
        timestamps = []
        for log in ip_logs:
            try:
                ts = datetime.strptime(log['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
                timestamps.append(ts)
            except:
                continue
        
        if len(timestamps) < 2:
            time_variance = 0
            requests_per_minute = 0
            min_interval = 0
        else:
            timestamps.sort()
            intervals = [(timestamps[i] - timestamps[i-1]).seconds 
                        for i in range(1, len(timestamps))]
            time_variance = np.var(intervals) if len(intervals) > 1 else 0
            
            total_time = (max(timestamps) - min(timestamps)).seconds / 60  # minutes
            requests_per_minute = request_count / max(total_time, 1)
            min_interval = min(intervals) if intervals else 0
        
        # Path analysis
        paths = [log.get('path', '/') for log in ip_logs]
        unique_paths = len(set(paths))
        path_diversity = unique_paths / request_count if request_count > 0 else 0
        
        # Status code analysis
        status_codes = [int(log.get('status', 200)) for log in ip_logs]
        error_rate = sum(1 for code in status_codes if code >= 400) / request_count
        client_errors = sum(1 for code in status_codes if 400 <= code < 500)
        server_errors = sum(1 for code in status_codes if code >= 500)
        
        # Method analysis
        methods = [log.get('method', 'GET') for log in ip_logs]
        unique_methods = len(set(methods))
        post_ratio = methods.count('POST') / request_count if request_count > 0 else 0
        
        # User agent analysis
        user_agents = [log.get('user_agent', '') for log in ip_logs]
        unique_user_agents = len(set(user_agents))
        bot_patterns = ['bot', 'crawler', 'spider', 'scan']
        bot_requests = sum(1 for ua in user_agents 
                          if any(pattern in ua.lower() for pattern in bot_patterns))
        
        # Attack pattern detection
        admin_paths = sum(1 for path in paths 
                         if any(admin in path.lower() 
                               for admin in ['/admin', '/wp-admin', '/phpmyadmin']))
        
        sql_injection = sum(1 for path in paths 
                           if any(sql in path.lower() 
                                 for sql in ['union', 'select', 'drop', 'insert', 'or 1=1']))
        
        directory_traversal = sum(1 for path in paths if '../' in path)
        
        suspicious_extensions = sum(1 for path in paths 
                                   if any(ext in path.lower() 
                                         for ext in ['.php', '.asp', '.jsp', '.cgi']))
        
        features = {
            # Volume metrics
            'request_count': request_count,
            'requests_per_minute': requests_per_minute,
            'unique_paths': unique_paths,
            'path_diversity': path_diversity,
            
            # Timing metrics
            'time_variance': time_variance,
            'min_interval': min_interval,
            
            # Error metrics
            'error_rate': error_rate,
            'client_errors': client_errors,
            'server_errors': server_errors,
            
            # Method metrics
            'unique_methods': unique_methods,
            'post_ratio': post_ratio,
            
            # User agent metrics
            'unique_user_agents': unique_user_agents,
            'bot_requests': bot_requests,
            'bot_ratio': bot_requests / request_count if request_count > 0 else 0,
            
            # Attack patterns
            'admin_path_attempts': admin_paths,
            'sql_injection_attempts': sql_injection,
            'directory_traversal_attempts': directory_traversal,
            'suspicious_extensions': suspicious_extensions,
            
            # Reputation (simplified)
            'geographic_risk': self._calculate_geo_risk(ip_logs[0].get('ip', '')),
            'is_private_ip': self._is_private_ip(ip_logs[0].get('ip', ''))
        }
        
        return features
    
    def _calculate_geo_risk(self, ip: str) -> float:
        """IP'nin coğrafi risk skorunu hesaplar (basit)"""
        high_risk_prefixes = ['1.1.1', '8.8.8', '208.67']
        for prefix in high_risk_prefixes:
            if ip.startswith(prefix):
                return 0.8
        return 0.2
    
    def _is_private_ip(self, ip: str) -> bool:
        """IP'nin private olup olmadığını kontrol eder"""
        try:
            return ipaddress.ip_address(ip).is_private
        except:
            return False
    
    def detect_attack_patterns(self, ip_logs: List[Dict[str, Any]]) -> List[str]:
        """Saldırı pattern'lerini tespit eder"""
        attacks = []
        
        features = self.extract_behavioral_features(ip_logs)
        
        # Brute force detection
        if (features.get('error_rate', 0) > 0.8 and 
            features.get('request_count', 0) > 10):
            attacks.append('Brute Force Attack')
        
        # DDoS detection
        if features.get('requests_per_minute', 0) > 20:
            attacks.append('DDoS/High Volume Attack')
        
        # SQL Injection
        if features.get('sql_injection_attempts', 0) > 0:
            attacks.append('SQL Injection Attempt')
        
        # Directory Traversal
        if features.get('directory_traversal_attempts', 0) > 0:
            attacks.append('Directory Traversal')
        
        # Admin access attempts
        if features.get('admin_path_attempts', 0) > 5:
            attacks.append('Admin Access Attempts')
        
        # Bot/Scanner activity
        if (features.get('bot_ratio', 0) > 0.8 and 
            features.get('path_diversity', 0) > 0.5):
            attacks.append('Automated Scanning')
        
        return attacks
    
    def train_anomaly_detector(self, logs_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Train the anomaly detection model on web logs.
        
        Extracts behavioral features from logs grouped by IP, normalizes them,
        and trains an Isolation Forest model.
        
        Args:
            logs_df (pd.DataFrame): DataFrame with columns: ip, timestamp, method,
                                   path, status, user_agent, protocol, referer, size
                                   
        Returns:
            tuple: (features_df, ip_list) - Extracted features and corresponding IPs
            
        Raises:
            ValueError: If no valid features can be extracted from logs
            TypeError: If logs_df is not a pandas DataFrame
        """
        try:
            print("🌐 Web Log Analyzer training started...")
            
            if not isinstance(logs_df, pd.DataFrame):
                raise TypeError("logs_df must be a pandas DataFrame")
            
            # Group logs by IP
            ip_groups = logs_df.groupby('ip')
            features_list = []
            ip_list = []
            
            for ip, ip_logs in ip_groups:
                try:
                    ip_data = ip_logs.to_dict('records')
                    features = self.extract_behavioral_features(ip_data)
                    
                    if features:  # Only add if features extracted successfully
                        features_list.append(features)
                        ip_list.append(ip)
                except Exception as e:
                    logger.warning(f"Failed to extract features for IP {ip}: {e}")
                    continue
            
            if not features_list:
                raise ValueError("No features could be extracted from log data!")
            
            # Convert to DataFrame
            features_df = pd.DataFrame(features_list)
            features_df = features_df.fillna(0)
            
            self.feature_names = features_df.columns.tolist()
            
            # Normalize features
            features_normalized = self.scaler.fit_transform(features_df)
            
            # Train anomaly detector
            self.anomaly_detector.fit(features_normalized)
            
            self.is_trained = True
            print(f"✅ Web log analyzer training completed! Trained on {len(ip_list)} IPs")
            
            return features_df, ip_list
            
        except Exception as e:
            print(f"❌ Error during training: {e}")
            raise
    
    def analyze_ip_with_explanation(self, ip_logs: List[Dict[str, Any]], ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Analyze IP behavior with anomaly detection and explanations.
        
        Extracts behavioral features, detects anomalies, identifies attack
        patterns, and provides recommendations.
        
        Args:
            ip_logs (list): List of log records for a specific IP
            ip_address (str): The IP address being analyzed
            
        Returns:
            dict: Analysis results containing:
                - ip_address: The analyzed IP
                - anomaly_score: Anomaly detection score
                - is_anomaly: Whether IP is flagged as anomalous
                - risk_level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'
                - attack_patterns: List of detected attack patterns
                - behavioral_insights: Behavioral observations
                - recommendations: Security recommendations
                
        Raises:
            ValueError: If model is not trained yet
        """
        try:
            if not self.is_trained:
                raise ValueError("Model is not trained yet! Call train_anomaly_detector() first.")
            
            # Extract features
            features = self.extract_behavioral_features(ip_logs)
            
            if not features:
                logger.warning(f"No features extracted for IP {ip_address}")
                return None
            
            # Convert to array
            features_df = pd.DataFrame([features])
            features_df = features_df.reindex(columns=self.feature_names, fill_value=0)
            features_normalized = self.scaler.transform(features_df)
            
            # Anomaly detection
            anomaly_score = self.anomaly_detector.decision_function(features_normalized)[0]
            is_anomaly = self.anomaly_detector.predict(features_normalized)[0] == -1
            
            # Attack patterns
            attack_patterns = self.detect_attack_patterns(ip_logs)
            
            # Risk level calculation
            risk_level = self._calculate_risk_level(anomaly_score, attack_patterns, features)
            
            return {
                'ip_address': ip_address,
                'anomaly_score': float(anomaly_score),
                'is_anomaly': bool(is_anomaly),
                'risk_level': risk_level,
                'attack_patterns': attack_patterns,
                'behavioral_insights': self._generate_insights(features),
                'recommendations': self._generate_recommendations(attack_patterns, features)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing IP {ip_address}: {e}")
            raise
    
    def _calculate_risk_level(self, anomaly_score: float, attack_patterns: List[str], features: Dict[str, Any]) -> str:
        """Risk seviyesini hesaplar"""
        base_risk = 0
        
        # Anomaly score contribution
        if anomaly_score < -0.5:
            base_risk += 40
        elif anomaly_score < 0:
            base_risk += 20
        
        # Attack patterns contribution
        base_risk += len(attack_patterns) * 25
        
        # Feature-based risk
        if features.get('error_rate', 0) > 0.5:
            base_risk += 15
        if features.get('requests_per_minute', 0) > 10:
            base_risk += 10
        
        # Risk levels
        if base_risk >= 70:
            return 'CRITICAL'
        elif base_risk >= 50:
            return 'HIGH'
        elif base_risk >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_insights(self, features: Dict[str, Any]) -> List[str]:
        """Davranışsal insights oluşturur"""
        insights = []
        
        if features.get('request_count', 0) > 100:
            insights.append(f"High volume: {features['request_count']} requests")
        
        if features.get('error_rate', 0) > 0.3:
            insights.append(f"High error rate: {features['error_rate']:.1%}")
        
        if features.get('path_diversity', 0) < 0.1:
            insights.append("Low path diversity - bot-like behavior")
        
        if features.get('time_variance', 0) < 1:
            insights.append("Regular timing pattern - automated behavior")
        
        return insights
    
    def _generate_recommendations(self, attack_patterns: List[str], features: Dict[str, Any]) -> List[str]:
        """Güvenlik önerileri oluşturur"""
        recommendations = []
        
        if 'Brute Force Attack' in attack_patterns:
            recommendations.extend([
                "🔒 Block IP address immediately",
                "📧 Send brute force alert"
            ])
        
        if 'SQL Injection Attempt' in attack_patterns:
            recommendations.extend([
                "⚡ Conduct urgent security analysis", 
                "🗃️ Check database logs"
            ])
        
        if 'DDoS/High Volume Attack' in attack_patterns:
            recommendations.extend([
                "🛡️ Apply rate limiting",
                "☁️ Activate DDoS protection"
            ])
        
        if not recommendations:
            recommendations.append("👀 Continue monitoring")
        
        return recommendations
