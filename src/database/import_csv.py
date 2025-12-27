"""
CSV Data Import Script

Imports email threat data from CSV files into PostgreSQL database.
Handles phishing, legitimate, and training datasets.
"""

import os
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from tqdm import tqdm
from .models import Email
from .connection import DatabaseEngine

logger = logging.getLogger(__name__)


class CSVImporter:
    """
    Imports threat data from CSV files into the database.
    
    Supports:
    - Human-generated emails (phishing and legitimate)
    - Dataset samples (Enron, Nigerian, Ling, etc.)
    - Automatic data format detection
    """
    
    # CSV file patterns and their handlers
    PHISHING_FILES = [
        'human-phishing.csv',
        'llm-phishing.csv',
        'phishing_email.csv',
    ]
    
    LEGITIMATE_FILES = [
        'human-legit.csv',
        'llm-legit.csv',
    ]
    
    DATASET_FILES = [
        'Enron.csv',
        'Enron_vectorized_data.csv',
        'Nigerian_Fraud.csv',
        'Nigerian_5.csv',
        'Nigerian-5_vectorized_data.csv',
        'Ling.csv',
        'CEAS_08.csv',
        'SpamAssasin.csv',
        'Nazario.csv',
        'Nazario_5.csv',
        'Nazario-5_vectorized_data.csv',
        'email_text.csv',
    ]
    
    def __init__(self, dataset_dir: str = 'dataset'):
        """
        Initialize importer.
        
        Args:
            dataset_dir: Path to dataset directory
        """
        self.dataset_dir = Path(dataset_dir)
        self.db_engine = DatabaseEngine()
        self.stats = {
            'total_imported': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'by_file': {}
        }
    
    def import_all(self, skip_existing: bool = True) -> Dict[str, Any]:
        """
        Import all CSV files from dataset directory.
        
        Args:
            skip_existing: Skip files that have already been imported
        
        Returns:
            Dictionary with import statistics
        """
        if not self.dataset_dir.exists():
            logger.error(f"Dataset directory not found: {self.dataset_dir}")
            return self.stats
        
        # Get all CSV files
        csv_files = list(self.dataset_dir.glob('*.csv'))
        logger.info(f"Found {len(csv_files)} CSV files in {self.dataset_dir}")
        
        for csv_file in csv_files:
            self._import_file(csv_file, skip_existing)
        
        logger.info(f"Import complete. Stats: {self.stats}")
        return self.stats
    
    def _import_file(self, csv_path: Path, skip_existing: bool = True):
        """
        Import a single CSV file.
        
        Args:
            csv_path: Path to CSV file
            skip_existing: Skip if already imported
        """
        filename = csv_path.name
        logger.info(f"Processing {filename}...")
        
        try:
            # Determine email classification
            if filename in self.PHISHING_FILES:
                classification = 1  # Phishing
            elif filename in self.LEGITIMATE_FILES:
                classification = 0  # Legitimate
            else:
                classification = None  # Unknown
            
            # Detect CSV format and import
            rows_imported = self._import_csv_content(csv_path, classification)
            
            self.stats['by_file'][filename] = {
                'imported': rows_imported,
                'classification': classification,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.stats['total_imported'] += rows_imported
            
            logger.info(f"✓ {filename}: {rows_imported} emails imported")
            
        except Exception as e:
            logger.error(f"✗ {filename}: {e}")
            self.stats['total_errors'] += 1
    
    def _import_csv_content(self, csv_path: Path, classification: Optional[int]) -> int:
        """
        Import CSV content with automatic format detection.
        
        Args:
            csv_path: Path to CSV file
            classification: 0=legitimate, 1=phishing, None=unknown
        
        Returns:
            Number of rows imported
        """
        rows_imported = 0
        
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Detect dialect
            sample = f.read(4096)
            f.seek(0)
            
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = 'excel'
            
            reader = csv.DictReader(f, dialect=dialect)
            
            if reader.fieldnames is None:
                logger.warning(f"Could not detect headers in {csv_path.name}")
                return 0
            
            # Map field names (case-insensitive)
            field_map = self._create_field_map(reader.fieldnames)
            
            # Import rows
            with self.db_engine.session_context() as session:
                for row in tqdm(reader, desc=csv_path.name, unit='emails'):
                    try:
                        email = self._parse_row(row, field_map, classification)
                        if email:
                            session.add(email)
                            rows_imported += 1
                            
                            # Batch commit every 100 rows
                            if rows_imported % 100 == 0:
                                session.flush()
                    
                    except Exception as e:
                        logger.debug(f"Skipped row in {csv_path.name}: {e}")
                        self.stats['total_skipped'] += 1
                        continue
        
        return rows_imported
    
    def _create_field_map(self, fieldnames: List[str]) -> Dict[str, Optional[str]]:
        """
        Create mapping from CSV headers to model fields.
        
        Args:
            fieldnames: List of CSV field names
        
        Returns:
            Dictionary mapping standard fields to CSV columns
        """
        lower_fields = [f.lower().strip() for f in fieldnames]
        
        field_map = {
            'email_text': self._find_field(['text', 'body', 'email', 'content', 'message'], lower_fields),
            'sender': self._find_field(['sender', 'from', 'email_from', 'source'], lower_fields),
            'receiver': self._find_field(['receiver', 'to', 'email_to', 'recipient'], lower_fields),
            'subject': self._find_field(['subject', 'title'], lower_fields),
            'date': self._find_field(['date', 'timestamp', 'time'], lower_fields),
        }
        
        return field_map
    
    def _find_field(self, candidates: List[str], available_fields: List[str]) -> Optional[str]:
        """Find matching field name from candidates."""
        for candidate in candidates:
            for field in available_fields:
                if candidate in field:
                    return field
        return None
    
    def _parse_row(
        self,
        row: Dict[str, str],
        field_map: Dict[str, Optional[str]],
        classification: Optional[int]
    ) -> Optional[Email]:
        """
        Parse CSV row into Email model.
        
        Args:
            row: CSV row as dictionary
            field_map: Mapping of field names
            classification: Email classification (0=legitimate, 1=phishing)
        
        Returns:
            Email object or None if invalid
        """
        # Extract text (required)
        email_text = None
        if field_map['email_text']:
            email_text = row.get(field_map['email_text'], '').strip()
        
        if not email_text:
            return None  # Skip rows without email text
        
        # Extract other fields
        sender = None
        if field_map['sender']:
            sender = row.get(field_map['sender'], '').strip() or None
        
        receiver = None
        if field_map['receiver']:
            receiver = row.get(field_map['receiver'], '').strip() or None
        
        subject = None
        if field_map['subject']:
            subject = row.get(field_map['subject'], '').strip() or None
        
        date = None
        if field_map['date']:
            date_str = row.get(field_map['date'], '').strip()
            if date_str:
                try:
                    date = datetime.fromisoformat(date_str)
                except (ValueError, TypeError):
                    date = None
        
        # Create Email object with default values
        email = Email(
            email_text=email_text,
            sender=sender,
            receiver=receiver,
            subject=subject,
            date=date,
            prediction=classification if classification is not None else 0,
            confidence=0.0,  # Will be set by detector
            risk_score=0.0,  # Will be set by detector
            risk_level='low',  # Default
            risk_factors=None,
            urls=None,
        )
        
        return email


def import_emails_from_csv(dataset_dir: str = 'dataset') -> Dict[str, Any]:
    """
    Import all emails from CSV files into database.
    
    Args:
        dataset_dir: Path to dataset directory
    
    Returns:
        Import statistics
    
    Example:
        stats = import_emails_from_csv('dataset')
        print(f"Imported {stats['total_imported']} emails")
    """
    importer = CSVImporter(dataset_dir)
    return importer.import_all()


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Import emails
    stats = import_emails_from_csv()
    print(f"\n{'='*50}")
    print(f"Import Summary:")
    print(f"  Total Imported: {stats['total_imported']}")
    print(f"  Total Skipped: {stats['total_skipped']}")
    print(f"  Total Errors: {stats['total_errors']}")
    print(f"{'='*50}")
