"""
Data Quality Analysis for AŞAMA 4.3
====================================

Comprehensive data quality assessment:
1. Dataset inventory
2. Missing values analysis
3. Duplicate detection
4. Data validation
5. Quality report generation
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataQualityAnalyzer:
    """Comprehensive data quality analysis."""
    
    def __init__(self, dataset_path: str = "dataset"):
        self.dataset_path = Path(dataset_path)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "dataset_summary": {},
            "file_analysis": {},
            "quality_metrics": {}
        }
        
    def analyze_all_datasets(self):
        """Analyze all CSV files in dataset directory."""
        logger.info("="*60)
        logger.info("DATA QUALITY ANALYSIS - AŞAMA 4.3")
        logger.info("="*60)
        
        csv_files = list(self.dataset_path.glob("**/*.csv"))
        logger.info(f"\n📊 Found {len(csv_files)} CSV files\n")
        
        for csv_file in csv_files:
            logger.info(f"📁 Analyzing: {csv_file.relative_to(self.dataset_path)}")
            self._analyze_file(csv_file)
        
        self._generate_report()
        
    def _analyze_file(self, filepath: Path):
        """Analyze a single CSV file."""
        try:
            # Try different encodings
            df = None
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, low_memory=False)
                    break
                except:
                    continue
            
            if df is None:
                logger.error(f"  ❌ Could not read file with any encoding")
                return
            
            file_key = str(filepath.relative_to(self.dataset_path))
            
            # Basic stats
            stats = {
                "rows": len(df),
                "columns": len(df.columns),
                "size_mb": filepath.stat().st_size / (1024 * 1024),
                "memory_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
            }
            
            logger.info(f"  ✅ Loaded: {stats['rows']} rows × {stats['columns']} columns")
            logger.info(f"     File size: {stats['size_mb']:.2f} MB")
            
            # Column analysis
            column_analysis = {}
            for col in df.columns:
                col_stats = {
                    "dtype": str(df[col].dtype),
                    "non_null": int(df[col].notna().sum()),
                    "null_count": int(df[col].isna().sum()),
                    "null_percent": float(round(df[col].isna().sum() / len(df) * 100, 2)),
                    "unique": int(df[col].nunique()),
                }
                
                # Additional stats for numeric columns
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_stats["min"] = float(df[col].min()) if df[col].notna().any() else None
                    col_stats["max"] = float(df[col].max()) if df[col].notna().any() else None
                    col_stats["mean"] = float(df[col].mean()) if df[col].notna().any() else None
                    col_stats["std"] = float(df[col].std()) if df[col].notna().any() else None
                
                # Additional stats for string columns
                elif pd.api.types.is_object_dtype(df[col]):
                    col_stats["sample_values"] = df[col].dropna().unique()[:3].tolist()
                    col_stats["max_length"] = int(df[col].astype(str).str.len().max())
                    col_stats["empty_strings"] = int((df[col] == "").sum())
                
                column_analysis[col] = col_stats
            
            stats["columns_analysis"] = column_analysis
            
            # Duplicates
            duplicate_rows = len(df) - len(df.drop_duplicates())
            stats["duplicate_rows"] = duplicate_rows
            stats["duplicate_percent"] = float(round(duplicate_rows / len(df) * 100, 2)) if len(df) > 0 else 0
            
            if duplicate_rows > 0:
                logger.info(f"  ⚠️ Duplicates: {duplicate_rows} rows ({stats['duplicate_percent']:.2f}%)")
            
            # Missing data summary
            missing_cols = df.columns[df.isna().any()].tolist()
            if missing_cols:
                logger.info(f"  ⚠️ Missing values in {len(missing_cols)} columns:")
                for col in missing_cols[:5]:
                    pct = (df[col].isna().sum() / len(df) * 100)
                    logger.info(f"     - {col}: {df[col].isna().sum()} ({pct:.1f}%)")
                if len(missing_cols) > 5:
                    logger.info(f"     ... and {len(missing_cols) - 5} more")
            
            self.results["file_analysis"][file_key] = stats
            
        except Exception as e:
            logger.error(f"  ❌ Error analyzing file: {e}")
    
    def _generate_report(self):
        """Generate quality report."""
        logger.info("\n" + "="*60)
        logger.info("QUALITY METRICS SUMMARY")
        logger.info("="*60)
        
        total_files = len(self.results["file_analysis"])
        total_rows = sum(stats["rows"] for stats in self.results["file_analysis"].values())
        total_size = sum(stats["size_mb"] for stats in self.results["file_analysis"].values())
        
        logger.info(f"\n📈 Overall Statistics:")
        logger.info(f"  • Total files: {total_files}")
        logger.info(f"  • Total rows: {total_rows:,}")
        logger.info(f"  • Total size: {total_size:.2f} MB")
        
        # Quality recommendations
        logger.info(f"\n🔍 Quality Findings:")
        
        total_duplicates = sum(
            stats.get("duplicate_rows", 0) 
            for stats in self.results["file_analysis"].values()
        )
        if total_duplicates > 0:
            logger.info(f"  ⚠️ Total duplicate rows across all files: {total_duplicates:,}")
        
        # Files with significant missing data
        files_with_missing = {}
        for file, stats in self.results["file_analysis"].items():
            if "columns_analysis" in stats:
                missing = [
                    (col, c_stats["null_percent"]) 
                    for col, c_stats in stats["columns_analysis"].items()
                    if c_stats["null_percent"] > 10
                ]
                if missing:
                    files_with_missing[file] = missing
        
        if files_with_missing:
            logger.info(f"  ⚠️ Files with columns > 10% missing:")
            for file, cols in files_with_missing.items():
                logger.info(f"     {file}:")
                for col, pct in cols:
                    logger.info(f"       - {col}: {pct:.1f}%")
        
        # Save JSON report
        report_file = Path("reports") / f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"\n✅ Report saved to: {report_file}")
        logger.info("="*60)


def main():
    """Run data quality analysis."""
    analyzer = DataQualityAnalyzer()
    analyzer.analyze_all_datasets()


if __name__ == "__main__":
    main()
