"""
Web Analyzer Utility Functions
"""

import pandas as pd
from datetime import datetime

def load_web_logs(filepath):
    """Web log dosyasını yükler"""
    try:
        with open(filepath, 'r') as f:
            logs = f.readlines()
        print(f"✅ Loaded {len(logs)} log entries from {filepath}")
        return logs
    except Exception as e:
        print(f"❌ Error loading logs: {e}")
        return []

def parse_log_timestamp(timestamp_str):
    """Log timestamp'ini parse eder"""
    try:
        # Format: 10/Oct/2023:13:55:36 +0200
        return datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
    except:
        return None

def aggregate_logs_by_ip(logs_df):
    """Logları IP'ye göre gruplar"""
    if 'ip' not in logs_df.columns:
        print("❌ Error: 'ip' column not found")
        return None
    
    ip_stats = logs_df.groupby('ip').agg({
        'path': 'count',
        'status': lambda x: (x >= '400').sum(),
        'method': lambda x: x.value_counts().to_dict()
    }).rename(columns={'path': 'request_count', 'status': 'error_count'})
    
    print(f"📊 Aggregated logs for {len(ip_stats)} unique IPs")
    return ip_stats