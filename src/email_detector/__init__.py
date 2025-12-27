"""Email Phishing Detection Module"""

from .detector import EmailPhishingDetector
try:
    from .bert_detector import BertEmailDetector
    __all__ = ['EmailPhishingDetector', 'BertEmailDetector']
except ImportError:
    # If transformers not installed, BERT detector won't be available
    __all__ = ['EmailPhishingDetector']