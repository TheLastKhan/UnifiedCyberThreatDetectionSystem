"""
Visualization Utilities
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_risk_distribution(risk_scores, labels):
    """Risk skorlarının dağılımını çizer"""
    plt.figure(figsize=(10, 6))
    
    safe_scores = [score for score, label in zip(risk_scores, labels) if label == 0]
    phishing_scores = [score for score, label in zip(risk_scores, labels) if label == 1]
    
    plt.hist([safe_scores, phishing_scores], bins=20, label=['Safe', 'Phishing'], alpha=0.7)
    plt.xlabel('Risk Score')
    plt.ylabel('Frequency')
    plt.title('Risk Score Distribution')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    return plt.gcf()

def plot_confusion_matrix(cm, class_names):
    """Confusion matrix görselleştirir"""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    return plt.gcf()

def plot_feature_importance(feature_names, importances, top_n=15):
    """Feature importance'ları çizer"""
    # Sort by importance
    indices = np.argsort(importances)[-top_n:]
    
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(indices)), importances[indices])
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel('Importance')
    plt.title(f'Top {top_n} Most Important Features')
    plt.tight_layout()
    
    return plt.gcf()