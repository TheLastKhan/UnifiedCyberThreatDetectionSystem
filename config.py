import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

# Data paths
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "samples"

# Model configurations
EMAIL_MODEL_CONFIG = {
    'max_features': 5000,
    'n_estimators': 100,
    'random_state': 42
}

WEB_MODEL_CONFIG = {
    'contamination': 0.1,
    'random_state': 42
}

# XAI configurations
LIME_CONFIG = {
    'num_features': 10,
    'num_samples': 5000
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}