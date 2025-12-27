"""
Data Loading Utilities
"""

import pandas as pd
import os
from typing import Tuple, List
import numpy as np


class DataLoader:
    """Data loader for email datasets"""
    
    def __init__(self):
        self.dataset_dir = "dataset"
    
    def load_all_emails(self) -> Tuple[List[str], List[int]]:
        """
        Load all email datasets and return texts and labels
        
        Returns:
            Tuple of (texts, labels) where labels are 0=legitimate, 1=phishing
        """
        all_texts = []
        all_labels = []
        
        # Try to load from dataset directory
        datasets = [
            ("Enron.csv", "Email", "Spam/Ham"),
            ("phishing_email.csv", "EmailText", "Label"),
            ("CEAS_08.csv", "body", "label")
        ]
        
        for filename, text_col, label_col in datasets:
            filepath = os.path.join(self.dataset_dir, filename)
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath, encoding='utf-8', on_bad_lines='skip')
                    
                    # Check if columns exist
                    if text_col in df.columns and label_col in df.columns:
                        texts = df[text_col].astype(str).tolist()
                        
                        # Convert labels to binary (0/1)
                        labels = df[label_col].values
                        if labels.dtype == object or labels.dtype == str:
                            # Handle string labels
                            labels = [1 if str(l).lower() in ['spam', 'phishing', '1', 'true'] else 0 
                                     for l in labels]
                        else:
                            labels = [int(l) for l in labels]
                        
                        all_texts.extend(texts)
                        all_labels.extend(labels)
                        
                        print(f"✅ Loaded {len(texts)} emails from {filename}")
                except Exception as e:
                    print(f"⚠️ Error loading {filename}: {e}")
                    continue
        
        # If no data loaded, create synthetic data
        if not all_texts:
            print("⚠️ No datasets found, creating synthetic data...")
            all_texts, all_labels = self._create_synthetic_data()
        
        return all_texts, all_labels
    
    def _create_synthetic_data(self) -> Tuple[List[str], List[int]]:
        """Create synthetic email data for training"""
        
        legitimate = [
            "Hi team, reminder that our meeting is at 3 PM today.",
            "Please find attached the quarterly report for your review.",
            "Your order has been shipped and will arrive in 3-5 business days.",
            "Thank you for your payment. Receipt is attached.",
            "The project deadline has been extended to next Friday.",
            "Please review the attached document at your convenience.",
            "Your account statement for this month is now available.",
            "Meeting notes from yesterday's discussion are attached.",
            "Your subscription has been renewed successfully.",
            "Welcome to our service. Here are your account details.",
        ] * 50  # 500 legitimate emails
        
        phishing = [
            "URGENT: Your account will be suspended! Click here immediately!!!",
            "Verify your PayPal account NOW or lose access forever!!!",
            "You won $10,000! Click to claim your prize immediately!",
            "Your bank account is locked. Verify your identity at this link!",
            "SECURITY ALERT: Unusual activity detected. Confirm password now!",
            "Congratulations! You've been selected for a cash prize. Act now!",
            "Your credit card will be charged unless you cancel at this link!",
            "URGENT: Social Security number verification required immediately!",
            "Click here to update your expired password or lose account access!",
            "Your package cannot be delivered. Pay customs fee at this link!",
        ] * 50  # 500 phishing emails
        
        texts = legitimate + phishing
        labels = [0] * len(legitimate) + [1] * len(phishing)
        
        # Shuffle
        indices = list(range(len(texts)))
        np.random.shuffle(indices)
        texts = [texts[i] for i in indices]
        labels = [labels[i] for i in indices]
        
        print(f"✅ Created {len(texts)} synthetic emails")
        return texts, labels


def load_dataset(filepath, file_type='csv'):
    """Genel veri yükleme fonksiyonu"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    
    try:
        if file_type == 'csv':
            df = pd.read_csv(filepath)
        elif file_type == 'json':
            df = pd.read_json(filepath)
        elif file_type == 'excel':
            df = pd.read_excel(filepath)
        else:
            print(f"❌ Unsupported file type: {file_type}")
            return None
        
        print(f"✅ Loaded {len(df)} records from {filepath}")
        return df
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def create_sample_email_data():
    """Demo email verisi oluşturur"""
    emails = [
        {
            'subject': 'URGENT: Account Suspended!',
            'body': 'Your PayPal account will be suspended. Click here to verify...',
            'sender': 'security@payp4l-fake.com',
            'label': 1
        },
        {
            'subject': 'Team Meeting Tomorrow',
            'body': 'Hi team, we have a meeting tomorrow at 10 AM.',
            'sender': 'manager@company.com',
            'label': 0
        },
        {
            'subject': 'You Won $1,000,000!!!',
            'body': 'CONGRATULATIONS! You won our lottery! Claim now...',
            'sender': 'lottery@scam.org',
            'label': 1
        },
        {
            'subject': 'Project Update',
            'body': 'Please find attached the latest project update document.',
            'sender': 'colleague@company.com',
            'label': 0
        }
    ]
    
    return pd.DataFrame(emails)
