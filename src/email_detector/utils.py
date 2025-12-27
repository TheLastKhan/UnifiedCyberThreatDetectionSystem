"""
Email Detector Utility Functions
"""

import pandas as pd
import numpy as np
from datetime import datetime

def load_email_dataset(filepath):
    """Email dataset'i yükler"""
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(df)} emails from {filepath}")
        return df
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None

def split_email_data(df, test_size=0.2):
    """Email verisini train/test olarak böler"""
    from sklearn.model_selection import train_test_split
    
    if 'label' not in df.columns:
        print("❌ Error: 'label' column not found")
        return None, None
    
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=42, stratify=df['label'])
    
    print(f"📊 Train set: {len(train_df)} emails")
    print(f"📊 Test set: {len(test_df)} emails")
    
    return train_df, test_df

def evaluate_email_model(y_true, y_pred):
    """Model performansını değerlendirir"""
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
    
    accuracy = accuracy_score(y_true, y_pred)
    print(f"\n📊 Accuracy: {accuracy:.3f}")
    print("\n📋 Classification Report:")
    print(classification_report(y_true, y_pred, target_names=['Safe', 'Phishing']))
    print("\n🔢 Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    return accuracy