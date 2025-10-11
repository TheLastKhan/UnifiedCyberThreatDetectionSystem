"""
Data Loading Utilities
"""

import pandas as pd
import os

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
