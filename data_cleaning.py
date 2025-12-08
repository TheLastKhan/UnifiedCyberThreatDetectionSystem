"""
Data Cleaning and Preprocessing Script - AŞAMA 4.3
====================================================

1. Remove duplicates
2. Handle missing values
3. Text normalization
4. Validation
5. Save cleaned datasets
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
import json
import hashlib
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Clean and prepare datasets for analysis."""
    
    def __init__(self, dataset_path: str = "dataset", output_path: str = "data/processed"):
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.stats = {
            "timestamp": datetime.now().isoformat(),
            "total_rows_before": 0,
            "total_rows_after": 0,
            "duplicates_removed": 0,
            "files_processed": {},
        }
        
    def clean_all_datasets(self):
        """Clean all CSV files."""
        logger.info("="*60)
        logger.info("DATA CLEANING & PREPROCESSING - AŞAMA 4.3")
        logger.info("="*60)
        
        csv_files = list(self.dataset_path.glob("**/*.csv"))
        logger.info(f"\n📊 Found {len(csv_files)} CSV files to clean\n")
        
        for csv_file in csv_files:
            # Skip already processed files
            if "spam" in csv_file.name.lower() and csv_file.parent.name == "email_spam":
                logger.info(f"📁 Cleaning: {csv_file.relative_to(self.dataset_path)}")
                self._clean_file(csv_file, is_spam=True)
            elif csv_file.parent.name != "processed":
                logger.info(f"📁 Cleaning: {csv_file.relative_to(self.dataset_path)}")
                self._clean_file(csv_file)
        
        self._generate_summary()
    
    def _clean_file(self, filepath: Path, is_spam: bool = False):
        """Clean a single CSV file."""
        try:
            # Read with different encodings
            df = None
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                    break
                except:
                    continue
            
            if df is None:
                logger.error(f"  ❌ Could not read file")
                return
            
            file_key = str(filepath.relative_to(self.dataset_path))
            initial_rows = len(df)
            self.stats["total_rows_before"] += initial_rows
            
            logger.info(f"  Initial rows: {initial_rows:,}")
            
            # Step 1: Remove complete duplicates
            df_before_dup = len(df)
            df = df.drop_duplicates()
            duplicates = df_before_dup - len(df)
            self.stats["duplicates_removed"] += duplicates
            
            if duplicates > 0:
                logger.info(f"  ✅ Removed {duplicates} duplicate rows")
            
            # Step 2: Drop columns that are mostly empty (>95% missing)
            cols_to_drop = []
            for col in df.columns:
                missing_pct = (df[col].isna().sum() / len(df)) * 100
                if missing_pct > 95:
                    cols_to_drop.append(col)
            
            if cols_to_drop:
                df = df.drop(columns=cols_to_drop)
                logger.info(f"  ✅ Dropped {len(cols_to_drop)} mostly-empty columns")
            
            # Step 3: Handle missing values strategically
            for col in df.columns:
                if df[col].isna().sum() > 0:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        # Fill numeric with median
                        df[col].fillna(df[col].median(), inplace=True)
                    else:
                        # Fill text with 'unknown'
                        df[col].fillna('unknown', inplace=True)
            
            # Step 4: Text normalization (for text columns)
            text_columns = df.select_dtypes(include=['object']).columns
            for col in text_columns:
                if col in ['body', 'email_text', 'text', 'subject', 'Message']:
                    # Normalize whitespace
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
                    # Remove rows with very short text
                    df = df[df[col].str.len() > 10]
            
            # Step 5: Remove rows where all values are NaN or empty
            df = df.dropna(how='all')
            
            final_rows = len(df)
            self.stats["total_rows_after"] += final_rows
            
            logger.info(f"  Final rows: {final_rows:,}")
            
            # Save cleaned file
            output_subdir = self.output_path / filepath.parent.name
            output_subdir.mkdir(exist_ok=True)
            output_file = output_subdir / filepath.name
            
            df.to_csv(output_file, index=False)
            logger.info(f"  💾 Saved to: {output_file.relative_to(Path.cwd())}")
            
            self.stats["files_processed"][file_key] = {
                "rows_before": initial_rows,
                "rows_after": final_rows,
                "duplicates_removed": duplicates,
                "columns_dropped": len(cols_to_drop),
                "output_file": str(output_file.relative_to(Path.cwd()))
            }
            
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")
    
    def _generate_summary(self):
        """Generate cleaning summary."""
        logger.info("\n" + "="*60)
        logger.info("CLEANING SUMMARY")
        logger.info("="*60)
        
        rows_removed = self.stats["total_rows_before"] - self.stats["total_rows_after"]
        removal_pct = (rows_removed / self.stats["total_rows_before"] * 100) if self.stats["total_rows_before"] > 0 else 0
        
        logger.info(f"\n📈 Results:")
        logger.info(f"  • Files processed: {len(self.stats['files_processed'])}")
        logger.info(f"  • Total rows BEFORE: {self.stats['total_rows_before']:,}")
        logger.info(f"  • Total rows AFTER: {self.stats['total_rows_after']:,}")
        logger.info(f"  • Rows removed: {rows_removed:,} ({removal_pct:.1f}%)")
        logger.info(f"  • Duplicates removed: {self.stats['duplicates_removed']:,}")
        
        logger.info(f"\n📂 Cleaned data saved to: {self.output_path}")
        
        # Save stats
        stats_file = Path("reports") / f"data_cleaning_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        stats_file.parent.mkdir(exist_ok=True)
        
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2, default=str)
        
        logger.info(f"✅ Stats saved to: {stats_file}")
        logger.info("="*60)


def main():
    """Run data cleaning."""
    cleaner = DataCleaner()
    cleaner.clean_all_datasets()


if __name__ == "__main__":
    main()
