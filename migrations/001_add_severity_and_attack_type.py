"""
Database Migration: Add Severity and Attack Type Fields

This migration adds:
1. severity field to Email table (phishing, malware, spam, suspicious, legitimate)
2. attack_type field to WebLog table (sql_injection, xss, ddos, brute_force, etc.)

Migration Version: 001
Created: 2025-12-08
Status: Development
"""

from sqlalchemy import (
    Column, String, DateTime, Index, text, MetaData, Table,
    create_engine, inspect, Enum
)
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums for new fields
SEVERITY_ENUM = ['phishing', 'malware', 'spam', 'suspicious', 'legitimate']
ATTACK_TYPE_ENUM = [
    'sql_injection', 'xss', 'ddos', 'brute_force', 'malware_distribution',
    'credential_theft', 'data_exfiltration', 'command_injection', 'path_traversal',
    'file_upload', 'authentication_bypass', 'business_logic', 'unknown'
]


def add_severity_to_emails(connection):
    """Add severity column to emails table"""
    inspector = inspect(connection)
    
    # Check if column already exists
    email_columns = [col['name'] for col in inspector.get_columns('emails')]
    
    if 'severity' not in email_columns:
        logger.info("Adding 'severity' column to emails table...")
        
        # Add the column
        connection.execute(text("""
            ALTER TABLE emails 
            ADD COLUMN severity VARCHAR(20) DEFAULT 'legitimate'
        """))
        
        # Create index
        connection.execute(text("""
            CREATE INDEX idx_email_severity ON emails(severity)
        """))
        
        logger.info("✅ 'severity' column added to emails table")
    else:
        logger.info("'severity' column already exists in emails table")


def add_attack_type_to_web_logs(connection):
    """Add attack_type column to web_logs table"""
    inspector = inspect(connection)
    
    # Check if column already exists
    web_log_columns = [col['name'] for col in inspector.get_columns('web_logs')]
    
    if 'attack_type' not in web_log_columns:
        logger.info("Adding 'attack_type' column to web_logs table...")
        
        # Add the column
        connection.execute(text("""
            ALTER TABLE web_logs 
            ADD COLUMN attack_type VARCHAR(50) DEFAULT 'unknown'
        """))
        
        # Create index
        connection.execute(text("""
            CREATE INDEX idx_web_log_attack_type ON web_logs(attack_type)
        """))
        
        logger.info("✅ 'attack_type' column added to web_logs table")
    else:
        logger.info("'attack_type' column already exists in web_logs table")


def add_detection_method_to_emails(connection):
    """Add detection_method to emails (which model detected it)"""
    inspector = inspect(connection)
    email_columns = [col['name'] for col in inspector.get_columns('emails')]
    
    if 'detection_method' not in email_columns:
        logger.info("Adding 'detection_method' column to emails table...")
        
        connection.execute(text("""
            ALTER TABLE emails 
            ADD COLUMN detection_method VARCHAR(50) DEFAULT 'tfidf'
        """))
        
        connection.execute(text("""
            CREATE INDEX idx_email_detection_method ON emails(detection_method)
        """))
        
        logger.info("✅ 'detection_method' column added to emails table")
    else:
        logger.info("'detection_method' column already exists in emails table")


def add_ml_confidence_to_web_logs(connection):
    """Add ml_confidence field to web_logs"""
    inspector = inspect(connection)
    web_log_columns = [col['name'] for col in inspector.get_columns('web_logs')]
    
    if 'ml_confidence' not in web_log_columns:
        logger.info("Adding 'ml_confidence' column to web_logs table...")
        
        connection.execute(text("""
            ALTER TABLE web_logs 
            ADD COLUMN ml_confidence FLOAT DEFAULT 0.0
        """))
        
        logger.info("✅ 'ml_confidence' column added to web_logs table")
    else:
        logger.info("'ml_confidence' column already exists in web_logs table")


def update_existing_emails(connection):
    """Update existing email records with appropriate severity based on prediction"""
    logger.info("Updating existing email records with severity...")
    
    # Set severity based on existing prediction
    connection.execute(text("""
        UPDATE emails 
        SET severity = CASE 
            WHEN prediction = 1 AND risk_score >= 75 THEN 'phishing'
            WHEN prediction = 1 AND risk_score < 75 THEN 'suspicious'
            WHEN prediction = 0 THEN 'legitimate'
            ELSE 'suspicious'
        END
        WHERE severity = 'legitimate'
    """))
    
    logger.info("✅ Existing email records updated")


def update_existing_web_logs(connection):
    """Update existing web_log records with appropriate attack_type"""
    logger.info("Updating existing web_log records with attack_type...")
    
    # Set attack_type based on existing indicators
    connection.execute(text("""
        UPDATE web_logs 
        SET attack_type = CASE 
            WHEN indicators LIKE '%sql%' OR indicators LIKE '%injection%' THEN 'sql_injection'
            WHEN indicators LIKE '%xss%' THEN 'xss'
            WHEN indicators LIKE '%ddos%' THEN 'ddos'
            WHEN indicators LIKE '%brute%' THEN 'brute_force'
            WHEN is_anomaly = true THEN 'unknown'
            ELSE 'unknown'
        END
        WHERE attack_type = 'unknown'
    """))
    
    logger.info("✅ Existing web_log records updated")


def create_migration_tracking_table(connection):
    """Create migration tracking table if it doesn't exist"""
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    if 'migrations' not in existing_tables:
        logger.info("Creating migration tracking table...")
        
        connection.execute(text("""
            CREATE TABLE migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                status VARCHAR(20) DEFAULT 'completed',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        logger.info("✅ Migration tracking table created")


def record_migration(connection, version, description):
    """Record the migration in tracking table"""
    inspector = inspect(connection)
    existing_tables = inspector.get_table_names()
    
    if 'migrations' in existing_tables:
        connection.execute(text("""
            INSERT INTO migrations (version, description, status)
            VALUES (:version, :description, 'completed')
        """), {"version": version, "description": description})
        
        logger.info(f"✅ Migration {version} recorded")


def run_migration(database_url: str):
    """
    Main migration function
    
    Args:
        database_url: PostgreSQL connection string
        
    Example:
        run_migration("postgresql://user:password@localhost/threat_detection")
    """
    logger.info("="*60)
    logger.info("STARTING MIGRATION: Add Severity & Attack Type")
    logger.info("="*60)
    
    try:
        # Create engine
        engine = create_engine(database_url, echo=False)
        
        # Run migration
        with engine.connect() as connection:
            with connection.begin():
                # 1. Create migration tracking table
                create_migration_tracking_table(connection)
                
                # 2. Add new columns
                add_severity_to_emails(connection)
                add_attack_type_to_web_logs(connection)
                add_detection_method_to_emails(connection)
                add_ml_confidence_to_web_logs(connection)
                
                # 3. Update existing records
                update_existing_emails(connection)
                update_existing_web_logs(connection)
                
                # 4. Record migration
                record_migration(
                    connection,
                    "001",
                    "Add severity to emails and attack_type to web_logs"
                )
        
        logger.info("="*60)
        logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"❌ MIGRATION FAILED: {str(e)}")
        logger.error("Rolling back changes...")
        raise


def rollback_migration(database_url: str):
    """
    Rollback the migration
    
    Args:
        database_url: PostgreSQL connection string
    """
    logger.info("="*60)
    logger.info("STARTING ROLLBACK: Remove Severity & Attack Type")
    logger.info("="*60)
    
    try:
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as connection:
            with connection.begin():
                # Drop columns
                logger.info("Removing 'severity' column from emails...")
                connection.execute(text("""
                    ALTER TABLE emails DROP COLUMN IF EXISTS severity
                """))
                
                logger.info("Removing 'attack_type' column from web_logs...")
                connection.execute(text("""
                    ALTER TABLE web_logs DROP COLUMN IF EXISTS attack_type
                """))
                
                logger.info("Removing 'detection_method' column from emails...")
                connection.execute(text("""
                    ALTER TABLE emails DROP COLUMN IF EXISTS detection_method
                """))
                
                logger.info("Removing 'ml_confidence' column from web_logs...")
                connection.execute(text("""
                    ALTER TABLE web_logs DROP COLUMN IF EXISTS ml_confidence
                """))
        
        logger.info("="*60)
        logger.info("✅ ROLLBACK COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        return True
        
    except Exception as e:
        logger.error(f"❌ ROLLBACK FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    from src.database.connection import DATABASE_URL
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_migration(DATABASE_URL)
    else:
        run_migration(DATABASE_URL)
