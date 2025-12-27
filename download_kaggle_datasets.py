"""
Kaggle Datasets Download Script
================================

Downloads multiple phishing and malware datasets from Kaggle.

Datasets:
1. Phishing Website Detection - URL/Domain features
2. Email Spam Classification - Spam/Phishing emails
3. Malicious URL Detection - Malware URLs
4. Web Attack Logs - HTTP requests with attack indicators

Setup:
1. Create Kaggle account: https://www.kaggle.com/
2. Install kaggle: pip install kaggle
3. Download API token from: https://www.kaggle.com/settings/account
4. Place at: ~/.kaggle/kaggle.json (Linux/Mac) or C:\\Users\\YourUsername\\.kaggle\\kaggle.json (Windows)
5. Run this script
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dataset configurations
DATASETS = [
    {
        "name": "Phishing Website Detection",
        "kaggle_id": "eswarchandt/phishing-website-detection",
        "local_path": "dataset/phishing_websites",
        "description": "URL and domain-based features for phishing detection"
    },
    {
        "name": "Email Spam Classification",
        "kaggle_id": "uciml/sms-spam-collection-dataset",
        "local_path": "dataset/email_spam",
        "description": "SMS/Email spam classification dataset"
    },
    {
        "name": "Malicious URL Detection",
        "kaggle_id": "sjbell53/malicious-urls",
        "local_path": "dataset/malicious_urls",
        "description": "Malicious URL detection dataset"
    },
    {
        "name": "Spam Email Dataset",
        "kaggle_id": "balaka18/email-spam-classification-dataset-csv",
        "local_path": "dataset/email_spam_advanced",
        "description": "Advanced email spam classification"
    },
]

OPTIONAL_DATASETS = [
    {
        "name": "HTTP Request/Response Dataset",
        "kaggle_id": "devendra416/http-requestresponse-dataset",
        "local_path": "dataset/http_logs",
        "description": "Web server logs with attack indicators"
    },
    {
        "name": "MNIST - Digits (for testing)",
        "kaggle_id": "oddrationale/mnist-digits-dataset",
        "local_path": "dataset/mnist",
        "description": "For general ML testing"
    },
]


def check_kaggle_setup() -> bool:
    """Check if Kaggle API is configured"""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    
    if not kaggle_json.exists():
        logger.error("❌ Kaggle API not configured!")
        logger.info("Setup instructions:")
        logger.info("1. Go to: https://www.kaggle.com/settings/account")
        logger.info("2. Click 'Create New API Token'")
        logger.info("3. This downloads kaggle.json")
        logger.info(f"4. Place it at: {kaggle_json}")
        logger.info("5. Run: chmod 600 ~/.kaggle/kaggle.json (on Linux/Mac)")
        return False
    
    logger.info("✅ Kaggle API configured")
    return True


def install_kaggle():
    """Install kaggle package if not present"""
    try:
        import kaggle
        logger.info("✅ kaggle package already installed")
    except ImportError:
        logger.info("Installing kaggle package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kaggle", "-q"])
        logger.info("✅ kaggle installed")


def download_dataset(kaggle_id: str, local_path: str, dataset_name: str) -> bool:
    """
    Download dataset from Kaggle using Python SDK
    
    Args:
        kaggle_id: Kaggle dataset identifier (username/dataset-name)
        local_path: Local directory to save dataset
        dataset_name: Human-readable name
    
    Returns:
        True if successful
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        import zipfile
        
        local_path = Path(local_path)
        local_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📥 Downloading {dataset_name}...")
        logger.info(f"   Dataset ID: {kaggle_id}")
        logger.info(f"   Local path: {local_path}")
        
        # Initialize Kaggle API
        api = KaggleApi()
        api.authenticate()
        
        # Download using Python SDK
        api.dataset_download_files(kaggle_id, path=str(local_path), unzip=True)
        
        logger.info(f"✅ {dataset_name} downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing {dataset_name}: {e}")
        return False


def download_all_datasets():
    """Download all required datasets"""
    logger.info("="*60)
    logger.info("KAGGLE DATASETS DOWNLOAD")
    logger.info("="*60)
    
    # Check setup
    if not check_kaggle_setup():
        logger.warning("⚠️ Kaggle API not configured. Skipping download.")
        logger.info("You can configure it later and run this script again.")
        return False
    
    # Install kaggle
    install_kaggle()
    
    # Create dataset directory
    Path("dataset").mkdir(exist_ok=True)
    
    # Download datasets
    results = {}
    
    logger.info("\n📦 REQUIRED DATASETS:")
    for dataset_config in DATASETS:
        success = download_dataset(
            dataset_config["kaggle_id"],
            dataset_config["local_path"],
            dataset_config["name"]
        )
        results[dataset_config["name"]] = {
            "success": success,
            "path": dataset_config["local_path"],
            "description": dataset_config["description"]
        }
    
    logger.info("\n📦 OPTIONAL DATASETS:")
    logger.info("(These are optional and can be downloaded if needed)\n")
    for dataset_config in OPTIONAL_DATASETS:
        logger.info(f"  - {dataset_config['name']}")
        logger.info(f"    ID: {dataset_config['kaggle_id']}")
        logger.info(f"    Description: {dataset_config['description']}\n")
    
    # Summary
    logger.info("="*60)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("="*60)
    
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    logger.info(f"Downloaded: {successful}/{total} datasets\n")
    
    for name, result in results.items():
        status = "✅" if result["success"] else "❌"
        logger.info(f"{status} {name}")
        logger.info(f"   Path: {result['path']}")
        logger.info(f"   {result['description']}\n")
    
    # List downloaded files
    logger.info("📂 Dataset directory structure:")
    dataset_dir = Path("dataset")
    for item in sorted(dataset_dir.iterdir()):
        if item.is_dir():
            files = list(item.glob("*.*"))
            logger.info(f"  {item.name}/ ({len(files)} files)")
            for f in files[:3]:
                logger.info(f"    - {f.name}")
            if len(files) > 3:
                logger.info(f"    ... and {len(files)-3} more")
    
    logger.info("\n" + "="*60)
    if successful == total:
        logger.info("✅ ALL DATASETS DOWNLOADED!")
    else:
        logger.info("⚠️ Some datasets failed. Check configuration and try again.")
    logger.info("="*60)
    
    return successful == total


def manual_download_instructions():
    """Print instructions for manual download"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║         MANUAL KAGGLE DATASET DOWNLOAD INSTRUCTIONS            ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║ If automatic download fails, follow these steps:              ║
║                                                                ║
║ 1. Visit Kaggle datasets:                                      ║
║    • https://www.kaggle.com/datasets                          ║
║                                                                ║
║ 2. Search for and download:                                    ║
║    • eswarchandt/phishing-website-detection                   ║
║    • uciml/sms-spam-collection-dataset                        ║
║    • sjbell53/malicious-urls                                  ║
║    • balaka18/email-spam-classification-dataset-csv           ║
║                                                                ║
║ 3. Extract ZIP files to dataset/ folder:                       ║
║    dataset/phishing_websites/                                 ║
║    dataset/email_spam/                                        ║
║    dataset/malicious_urls/                                    ║
║    dataset/email_spam_advanced/                               ║
║                                                                ║
║ 4. Run data import script:                                     ║
║    python import_kaggle_data.py                               ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    try:
        success = download_all_datasets()
        
        if not success:
            logger.warning("\n⚠️ Some downloads may have failed.")
            logger.info("See manual download instructions below:\n")
            manual_download_instructions()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Download cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
