"""
Test fixtures and utilities for unit and integration tests
"""

import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.email_detector.detector import EmailPhishingDetector
from src.web_analyzer.analyzer import WebLogAnalyzer
from src.unified_platform.platform import UnifiedThreatPlatform


@pytest.fixture(scope="module")
def sample_emails():
    """Create sample email data for testing."""
    return pd.DataFrame([
        {
            'subject': 'URGENT: Account Suspended!',
            'body': 'Your account will be suspended in 24 hours. Click here to verify immediately.',
            'sender': 'security@payp4l-fake.com',
            'label': 1
        },
        {
            'subject': 'Team Meeting Tomorrow',
            'body': 'Hi team, we have our weekly meeting tomorrow at 10 AM in Conference Room B.',
            'sender': 'manager@company.com',
            'label': 0
        },
        {
            'subject': 'You Won $1,000,000!!!',
            'body': 'CONGRATULATIONS! You won our lottery! Claim now at our secure portal.',
            'sender': 'lottery@fake.org',
            'label': 1
        },
        {
            'subject': 'Project Update',
            'body': 'Please find attached the latest project update document. Review and provide feedback.',
            'sender': 'colleague@company.com',
            'label': 0
        },
        {
            'subject': 'Verify Your Identity',
            'body': 'Please provide your SSN and credit card info to verify your account.',
            'sender': 'support@scam.net',
            'label': 1
        }
    ])


@pytest.fixture(scope="module")
def sample_web_logs():
    """Create sample web logs for testing."""
    return pd.DataFrame([
        {
            'ip': '192.168.1.100',
            'timestamp': '20/Sep/2025:14:00:00 +0200',
            'method': 'GET',
            'path': '/',
            'status': '200',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referer': '-',
            'size': '1234',
            'protocol': 'HTTP/1.1'
        },
        {
            'ip': '203.0.113.45',
            'timestamp': '20/Sep/2025:14:01:01 +0200',
            'method': 'POST',
            'path': '/admin/login',
            'status': '401',
            'user_agent': 'Python-urllib/3.6',
            'referer': '-',
            'size': '567',
            'protocol': 'HTTP/1.1'
        },
        {
            'ip': '192.168.1.200',
            'timestamp': '20/Sep/2025:14:02:00 +0200',
            'method': 'GET',
            'path': '/dashboard',
            'status': '200',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referer': '-',
            'size': '2345',
            'protocol': 'HTTP/1.1'
        },
        {
            'ip': '192.168.1.100',
            'timestamp': '20/Sep/2025:14:03:00 +0200',
            'method': 'GET',
            'path': '/home',
            'status': '200',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'referer': '-',
            'size': '1500',
            'protocol': 'HTTP/1.1'
        },
    ])


@pytest.fixture(scope="module")
def trained_email_detector(sample_emails):
    """Create a trained email detector."""
    detector = EmailPhishingDetector()
    labels = sample_emails['label'].tolist()
    detector.train(sample_emails, labels)
    return detector


@pytest.fixture(scope="module")
def trained_web_analyzer(sample_web_logs):
    """Create a trained web analyzer."""
    analyzer = WebLogAnalyzer()
    analyzer.train_anomaly_detector(sample_web_logs)
    return analyzer


@pytest.fixture(scope="module")
def trained_platform(sample_emails, sample_web_logs):
    """Create a trained unified platform."""
    platform = UnifiedThreatPlatform()
    labels = sample_emails['label'].tolist()
    platform.initialize(
        email_data=(sample_emails, labels),
        web_logs=sample_web_logs
    )
    return platform


@pytest.fixture
def suspicious_email():
    """Create a suspicious email for testing."""
    return {
        'subject': 'URGENT: Verify Account NOW!',
        'body': 'Your account will be suspended! Click here immediately to verify.',
        'sender': 'fake@scam.com'
    }


@pytest.fixture
def safe_email():
    """Create a safe email for testing."""
    return {
        'subject': 'Meeting Reminder',
        'body': 'Just a reminder about our team meeting tomorrow at 10 AM.',
        'sender': 'manager@company.com'
    }


@pytest.fixture
def suspicious_logs():
    """Create suspicious web logs for testing."""
    return [
        {
            'ip': '203.0.113.45',
            'timestamp': '20/Sep/2025:14:00:00 +0200',
            'method': 'POST',
            'path': '/admin/login',
            'status': '401',
            'user_agent': 'sqlmap',
            'referer': '-',
            'size': '100',
            'protocol': 'HTTP/1.1'
        },
        {
            'ip': '203.0.113.45',
            'timestamp': '20/Sep/2025:14:01:00 +0200',
            'method': 'POST',
            'path': '/admin/login',
            'status': '401',
            'user_agent': 'sqlmap',
            'referer': '-',
            'size': '100',
            'protocol': 'HTTP/1.1'
        },
    ]


@pytest.fixture
def normal_logs():
    """Create normal web logs for testing."""
    return [
        {
            'ip': '192.168.1.100',
            'timestamp': '20/Sep/2025:14:00:00 +0200',
            'method': 'GET',
            'path': '/',
            'status': '200',
            'user_agent': 'Mozilla/5.0',
            'referer': '-',
            'size': '1234',
            'protocol': 'HTTP/1.1'
        },
        {
            'ip': '192.168.1.100',
            'timestamp': '20/Sep/2025:14:01:00 +0200',
            'method': 'GET',
            'path': '/about',
            'status': '200',
            'user_agent': 'Mozilla/5.0',
            'referer': '-',
            'size': '1500',
            'protocol': 'HTTP/1.1'
        },
    ]
