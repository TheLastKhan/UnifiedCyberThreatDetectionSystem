"""
Email Phishing Detection Module
Unified Threat Detection Platform
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import lime
import lime.lime_text
from lime.lime_tabular import LimeTabularExplainer
import re
import pickle
import os
from typing import Dict, List, Tuple, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailPhishingDetector:
    """
    Email phishing detection using machine learning and explainable AI.
    
    This class provides functionality to detect phishing emails using TF-IDF
    vectorization, Random Forest classification, and LIME explainability.
    
    Attributes:
        config (dict): Configuration parameters for the detector
        vectorizer: TF-IDF vectorizer for text feature extraction
        model: Random Forest classifier for predictions
        feature_names (list): Names of all features used in the model
        lime_explainer: LIME explainer for model interpretability
        is_trained (bool): Whether the model has been trained
    """
    
    def __init__(self, config=None):
        """
        Initialize the EmailPhishingDetector.
        
        Args:
            config (dict, optional): Configuration dictionary with keys:
                - max_features (int): Maximum features for TF-IDF (default: 5000)
                - n_estimators (int): Number of trees in Random Forest (default: 100)
                - random_state (int): Random seed for reproducibility (default: 42)
        """
        self.config = config or {}
        self.vectorizer = TfidfVectorizer(
            max_features=self.config.get('max_features', 5000),
            stop_words='english'
        )
        self.model = RandomForestClassifier(
            n_estimators=self.config.get('n_estimators', 100),
            random_state=self.config.get('random_state', 42)
        )
        self.feature_names = []
        self.lime_explainer = None
        self.is_trained = False
    
    def extract_email_features(self, email_text: str, sender: str = "", subject: str = "") -> Dict[str, Any]:
        """
        Extract features from email text.
        
        Extracts both statistical and semantic features from email content
        to identify phishing indicators.
        
        Args:
            email_text (str): The body of the email
            sender (str, optional): Sender's email address
            subject (str, optional): Email subject line
            
        Returns:
            dict: Dictionary containing extracted features with keys:
                - email_length, word_count, sentence_count
                - capital_ratio, exclamation_count, question_count
                - urgent_words, financial_words, personal_info_words
                - url_count, suspicious_urls, ip_in_url
                - sender_suspicious, free_email_provider
        """
        full_text = f"{subject} {email_text}"
        
        features = {
            # Basic text features
            'email_length': len(full_text),
            'word_count': len(full_text.split()),
            'sentence_count': len([s for s in full_text.split('.') if s.strip()]),
            'capital_ratio': sum(1 for c in full_text if c.isupper()) / max(len(full_text), 1),
            
            # Punctuation features
            'exclamation_count': full_text.count('!'),
            'question_count': full_text.count('?'),
            'dollar_count': full_text.count('$'),
            
            # Suspicious word patterns
            'urgent_words': self._count_patterns(full_text, [
                'urgent', 'immediate', 'asap', 'expire', 'limited time', 'act now'
            ]),
            'financial_words': self._count_patterns(full_text, [
                'money', 'bank', 'account', 'credit', 'payment', 'transfer', 'prize'
            ]),
            'personal_info_words': self._count_patterns(full_text, [
                'password', 'username', 'ssn', 'social security', 'verify account'
            ]),
            
            # URL analysis
            'url_count': len(re.findall(r'http[s]?://\S+', full_text)),
            'suspicious_urls': self._check_suspicious_urls(full_text),
            'ip_in_url': 1 if re.search(r'http[s]?://\d+\.\d+\.\d+\.\d+', full_text) else 0,
            
            # Sender analysis
            'sender_suspicious': self._analyze_sender(sender),
            'free_email_provider': 1 if any(provider in sender.lower() 
                                           for provider in ['gmail', 'yahoo', 'hotmail']) else 0,
        }
        
        return features
    
    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        """Belirli pattern'leri sayar"""
        return sum(text.lower().count(pattern) for pattern in patterns)
    
    def _check_suspicious_urls(self, text: str) -> int:
        """Şüpheli URL pattern'leri kontrol eder"""
        suspicious_patterns = [
            r'bit\.ly', r'tinyurl', r'\.tk', r'\.ml',
            r'[0-9]+-[a-z]+\.com', r'[a-z]+-[0-9]+\.org'
        ]
        return sum(1 for pattern in suspicious_patterns 
                  if re.search(pattern, text.lower()))
    
    def _analyze_sender(self, sender: str) -> int:
        """Sender'ın şüphe skorunu hesaplar"""
        if not sender:
            return 1
        
        suspicious_score = 0
        
        # Çok kısa veya çok uzun username
        username = sender.split('@')[0] if '@' in sender else sender
        if len(username) < 3 or len(username) > 20:
            suspicious_score += 1
        
        # Sayılar çok fazla
        if sum(c.isdigit() for c in username) > len(username) / 2:
            suspicious_score += 1
        
        # Çok fazla nokta
        if sender.count('.') > 3:
            suspicious_score += 1
            
        return suspicious_score
    
    def train(self, emails_df: pd.DataFrame, labels: List[int]) -> np.ndarray:
        """
        Train the email phishing detector model.
        
        Extracts features from emails, vectorizes text using TF-IDF,
        trains a Random Forest classifier, and initializes LIME explainer.
        
        Args:
            emails_df (pd.DataFrame): DataFrame with columns 'body', 'sender', 'subject'
            labels (list or array): List of binary labels (0: safe, 1: phishing)
            
        Returns:
            np.ndarray: Combined feature matrix used for training
            
        Raises:
            ValueError: If required columns are missing from emails_df
        """
        try:
            print("📧 Email Phishing Detector training started...")
            
            # Validate input
            if not isinstance(emails_df, pd.DataFrame):
                raise TypeError("emails_df must be a pandas DataFrame")
            
            if len(emails_df) != len(labels):
                raise ValueError("Number of emails and labels must match")
            
            # Feature extraction
            features_list = []
            for idx, row in emails_df.iterrows():
                try:
                    email_features = self.extract_email_features(
                        row.get('body', ''),
                        row.get('sender', ''),
                        row.get('subject', '')
                    )
                    features_list.append(email_features)
                except Exception as e:
                    print(f"⚠️ Warning: Error processing row {idx}: {e}")
                    continue
            
            features_df = pd.DataFrame(features_list)
            
            # Text vectorization
            email_texts = (emails_df['subject'].fillna('') + ' ' + 
                          emails_df['body'].fillna(''))
            text_features = self.vectorizer.fit_transform(email_texts)
            
            # Combine features
            combined_features = np.hstack([
                features_df.values,
                text_features.toarray()
            ])
            
            self.feature_names = (list(features_df.columns) + 
                                 [f'word_{i}' for i in range(text_features.shape[1])])
            
            # Train model
            self.model.fit(combined_features, labels)
            
            # Setup LIME explainer
            self.lime_explainer = LimeTabularExplainer(
                combined_features,
                feature_names=self.feature_names,
                class_names=['Safe', 'Phishing'],
                mode='classification'
            )
            
            self.is_trained = True
            print("✅ Email detector training completed!")
            
            return combined_features
            
        except Exception as e:
            print(f"❌ Error during training: {e}")
            raise
    
    def predict_with_explanation(self, email_text: str, sender: str = "", subject: str = "") -> Dict[str, Any]:
        """
        Predict phishing probability with LIME explanation.
        
        Makes a prediction on whether an email is phishing and provides
        LIME-based explanation for the prediction.
        
        Args:
            email_text (str): The body of the email to analyze
            sender (str, optional): Sender's email address
            subject (str, optional): Email subject line
            
        Returns:
            dict: Prediction results containing:
                - prediction (str): 'Safe' or 'Phishing'
                - confidence (float): Prediction confidence (0-100)
                - phishing_probability (float): Phishing probability (0-100)
                - safe_probability (float): Safe probability (0-100)
                - lime_explanation (list): Feature importance explanations
                - risk_factors (list): Identified risk factors in the email
                
        Raises:
            ValueError: If model is not trained yet
        """
        try:
            if not self.is_trained:
                raise ValueError("Model is not trained yet! Call train() first.")
            
            # Feature extraction
            email_features = self.extract_email_features(email_text, sender, subject)
            features_df = pd.DataFrame([email_features])
            
            # Text features
            full_text = f"{subject} {email_text}"
            text_features = self.vectorizer.transform([full_text])
            
            # Combine features
            combined_features = np.hstack([
                features_df.values,
                text_features.toarray()
            ])
            
            # Prediction
            prediction = self.model.predict(combined_features)[0]
            probabilities = self.model.predict_proba(combined_features)[0]
            
            # LIME explanation
            lime_explanation = self.lime_explainer.explain_instance(
                combined_features[0],
                self.model.predict_proba,
                num_features=10
            )
            
            return {
                'prediction': 'Phishing' if prediction == 1 else 'Safe',
                'confidence': max(probabilities) * 100,
                'phishing_probability': probabilities[1] * 100,
                'safe_probability': probabilities[0] * 100,
                'lime_explanation': lime_explanation.as_list(),
                'risk_factors': self._identify_risk_factors(email_features, email_text)
            }
            
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
            raise
    
    def _identify_risk_factors(self, features: Dict[str, Any], email_text: str) -> List[str]:
        """Risk faktörlerini belirler"""
        risks = []
        
        if features['capital_ratio'] > 0.3:
            risks.append(f"Excessive capital letters ({features['capital_ratio']:.1%})")
        
        if features['urgent_words'] > 0:
            risks.append(f"Urgency keywords ({features['urgent_words']} found)")
        
        if features['financial_words'] > 0:
            risks.append(f"Financial terms detected ({features['financial_words']})")
        
        if features['personal_info_words'] > 0:
            risks.append("Personal information requested")
        
        if features['suspicious_urls'] > 0:
            risks.append("Suspicious URL patterns detected")
        
        if features['ip_in_url'] > 0:
            risks.append("IP address used in URL")
        
        if features['sender_suspicious'] > 1:
            risks.append("Suspicious sender profile")
        
        return risks
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model to disk.
        
        Serializes the vectorizer, model, and configuration for later use.
        
        Args:
            filepath (str): Path where the model should be saved
            
        Raises:
            IOError: If file cannot be written to the specified path
        """
        try:
            if not self.is_trained:
                raise ValueError("Model is not trained yet!")
                
            model_data = {
                'vectorizer': self.vectorizer,
                'model': self.model,
                'feature_names': self.feature_names,
                'config': self.config
            }
            
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"✅ Model saved to {filepath}")
            
        except Exception as e:
            print(f"❌ Error saving model: {e}")
            raise
    
    def load_model(self, filepath: str) -> None:
        """
        Load a previously trained model from disk.
        
        Args:
            filepath (str): Path to the saved model file
            
        Raises:
            FileNotFoundError: If the model file does not exist
            ValueError: If the file is not a valid model
        """
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Model file not found: {filepath}")
                
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.config = model_data.get('config', {})
            self.is_trained = True
            
            print(f"✅ Model loaded from {filepath}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
