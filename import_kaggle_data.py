"""
Kaggle Data Import Script
===========================

Imports downloaded Kaggle datasets into the project database.

Steps:
1. Read CSV files from dataset/ directory
2. Clean and validate data
3. Insert into PostgreSQL via SQLAlchemy ORM
4. Generate import report
5. Verify data quality

Supports:
- Phishing websites (URL classification)
- Email spam classification
- Malicious URL detection
- Web attack logs
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.connection import DatabaseConnection
from src.database.models import (
    Email, WebLog, Threat, ThreatCorrelation, User
)

# Configuration
CONFIG = {
    "dataset_path": "dataset",
    "batch_size": 500,
    "duplicate_check": True,
    "validate_data": True,
}


class KaggleDataImporter:
    """Import Kaggle datasets into database"""
    
    def __init__(self):
        """Initialize importer with database connection"""
        self.db = DatabaseConnection()
        self.session = self.db.get_session()
        self.import_stats = {
            "emails_imported": 0,
            "emails_duplicates": 0,
            "web_logs_imported": 0,
            "web_logs_duplicates": 0,
            "errors": 0,
            "timestamp": str(datetime.now())
        }
    
    def import_email_datasets(self) -> int:
        """
        Import email datasets into Email table
        
        Returns:
            Number of emails imported
        """
        logger.info("📧 Importing email datasets...")
        
        dataset_path = Path(CONFIG["dataset_path"])
        email_sources = [
            dataset_path / "email_spam" / "*.csv",
            dataset_path / "email_spam_advanced" / "*.csv",
            dataset_path / "phishing_websites" / "*.csv",
        ]
        
        imported = 0
        
        for pattern in email_sources:
            csv_files = list(Path(".").glob(str(pattern)))
            
            for csv_file in csv_files:
                try:
                    logger.info(f"  Reading {csv_file.name}...")
                    df = pd.read_csv(csv_file, nrows=10000)  # Limit rows
                    
                    # Identify columns
                    email_col = self._find_column(df, ['email', 'text', 'message', 'body', 'content'])
                    label_col = self._find_column(df, ['label', 'spam', 'phishing', 'class', 'category'])
                    
                    if not email_col:
                        logger.warning(f"    Could not find email column in {csv_file.name}")
                        continue
                    
                    # Process emails
                    for idx, row in df.iterrows():
                        try:
                            email_text = str(row[email_col]).strip()
                            
                            if not email_text or len(email_text) < 10:
                                continue
                            
                            # Determine if phishing
                            is_phishing = False
                            if label_col:
                                label = str(row[label_col]).lower()
                                is_phishing = label in ['1', 'phishing', 'spam', 'malicious', 'true']
                            
                            # Check duplicate
                            if CONFIG["duplicate_check"]:
                                exists = self.session.query(Email).filter_by(
                                    body_hash=self._hash_text(email_text)
                                ).first()
                                
                                if exists:
                                    self.import_stats["emails_duplicates"] += 1
                                    continue
                            
                            # Create email record
                            email = Email(
                                sender="kaggle-import@dataset.local",
                                subject=email_text[:100],
                                body=email_text,
                                is_phishing=is_phishing,
                                confidence=0.0,  # Will be filled by detector
                                source="kaggle_import",
                                created_at=datetime.now()
                            )
                            
                            self.session.add(email)
                            imported += 1
                            
                            # Batch commit
                            if imported % CONFIG["batch_size"] == 0:
                                self.session.commit()
                                logger.info(f"    Committed {imported} emails...")
                        
                        except Exception as e:
                            logger.error(f"    Error processing row {idx}: {e}")
                            self.import_stats["errors"] += 1
                            continue
                    
                    self.session.commit()
                    logger.info(f"  ✅ {csv_file.name}: {imported} emails")
                
                except Exception as e:
                    logger.error(f"  ❌ Error reading {csv_file.name}: {e}")
                    self.import_stats["errors"] += 1
        
        self.import_stats["emails_imported"] = imported
        return imported
    
    def import_web_log_datasets(self) -> int:
        """
        Import web log datasets into WebLog table
        
        Returns:
            Number of logs imported
        """
        logger.info("🌐 Importing web log datasets...")
        
        dataset_path = Path(CONFIG["dataset_path"])
        log_sources = [
            dataset_path / "http_logs" / "*.csv",
            dataset_path / "malicious_urls" / "*.csv",
        ]
        
        imported = 0
        
        for pattern in log_sources:
            csv_files = list(Path(".").glob(str(pattern)))
            
            for csv_file in csv_files:
                try:
                    logger.info(f"  Reading {csv_file.name}...")
                    df = pd.read_csv(csv_file, nrows=5000)  # Limit rows
                    
                    # Identify columns
                    url_col = self._find_column(df, ['url', 'uri', 'path', 'domain', 'website'])
                    method_col = self._find_column(df, ['method', 'request_method', 'http_method'])
                    status_col = self._find_column(df, ['status', 'status_code', 'response_code'])
                    
                    if not url_col:
                        logger.warning(f"    Could not find URL column in {csv_file.name}")
                        continue
                    
                    # Process logs
                    for idx, row in df.iterrows():
                        try:
                            url = str(row[url_col]).strip()
                            
                            if not url or len(url) < 5:
                                continue
                            
                            # Extract components
                            method = str(row[method_col]).upper() if method_col else "GET"
                            status_code = int(row[status_col]) if status_col else 200
                            
                            # Check duplicate
                            if CONFIG["duplicate_check"]:
                                exists = self.session.query(WebLog).filter_by(
                                    request_hash=self._hash_text(url + method)
                                ).first()
                                
                                if exists:
                                    self.import_stats["web_logs_duplicates"] += 1
                                    continue
                            
                            # Create web log record
                            web_log = WebLog(
                                source_ip="0.0.0.0",  # Not in Kaggle datasets
                                destination_url=url,
                                http_method=method,
                                status_code=status_code,
                                threat_detected=status_code >= 400,  # Simple heuristic
                                threat_type="unknown",
                                severity="medium",
                                source="kaggle_import",
                                timestamp=datetime.now()
                            )
                            
                            self.session.add(web_log)
                            imported += 1
                            
                            # Batch commit
                            if imported % CONFIG["batch_size"] == 0:
                                self.session.commit()
                                logger.info(f"    Committed {imported} logs...")
                        
                        except Exception as e:
                            logger.error(f"    Error processing row {idx}: {e}")
                            self.import_stats["errors"] += 1
                            continue
                    
                    self.session.commit()
                    logger.info(f"  ✅ {csv_file.name}: {imported} logs")
                
                except Exception as e:
                    logger.error(f"  ❌ Error reading {csv_file.name}: {e}")
                    self.import_stats["errors"] += 1
        
        self.import_stats["web_logs_imported"] = imported
        return imported
    
    def verify_imports(self) -> Dict:
        """Verify imported data quality"""
        logger.info("🔍 Verifying imported data...")
        
        verification = {
            "total_emails": self.session.query(Email).count(),
            "phishing_emails": self.session.query(Email).filter_by(is_phishing=True).count(),
            "legitimate_emails": self.session.query(Email).filter_by(is_phishing=False).count(),
            "total_web_logs": self.session.query(WebLog).count(),
            "threat_detected_logs": self.session.query(WebLog).filter_by(threat_detected=True).count(),
            "safe_logs": self.session.query(WebLog).filter_by(threat_detected=False).count(),
        }
        
        logger.info("  Email Statistics:")
        logger.info(f"    Total: {verification['total_emails']}")
        logger.info(f"    Phishing: {verification['phishing_emails']}")
        logger.info(f"    Legitimate: {verification['legitimate_emails']}")
        
        logger.info("  Web Log Statistics:")
        logger.info(f"    Total: {verification['total_web_logs']}")
        logger.info(f"    Threat Detected: {verification['threat_detected_logs']}")
        logger.info(f"    Safe: {verification['safe_logs']}")
        
        return verification
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find column by possible names"""
        cols_lower = {col.lower(): col for col in df.columns}
        for name in possible_names:
            if name.lower() in cols_lower:
                return cols_lower[name.lower()]
        return None
    
    def _hash_text(self, text: str) -> str:
        """Hash text for duplicate detection"""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()
    
    def generate_report(self, verification: Dict):
        """Generate import report"""
        report = {
            "import_date": str(datetime.now()),
            "import_stats": self.import_stats,
            "verification": verification,
            "database": "PostgreSQL",
            "status": "completed"
        }
        
        report_path = Path("reports/kaggle_import_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved to {report_path}")
        return report


def main():
    """Main import function"""
    logger.info("="*60)
    logger.info("KAGGLE DATA IMPORT TO DATABASE")
    logger.info("="*60)
    
    importer = KaggleDataImporter()
    
    try:
        # Import data
        email_count = importer.import_email_datasets()
        log_count = importer.import_web_log_datasets()
        
        logger.info(f"\n✅ Import Summary:")
        logger.info(f"   Emails: {email_count}")
        logger.info(f"   Web Logs: {log_count}")
        
        # Verify
        verification = importer.verify_imports()
        
        # Generate report
        importer.generate_report(verification)
        
        logger.info("\n" + "="*60)
        logger.info("✅ KAGGLE DATA IMPORT COMPLETED!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)
    
    finally:
        importer.session.close()


if __name__ == "__main__":
    main()
