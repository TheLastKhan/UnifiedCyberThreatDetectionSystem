#!/usr/bin/env python
"""
Database Migration Runner

Executes database migrations in order.

Usage:
    python run_migrations.py              # Run all pending migrations
    python run_migrations.py rollback     # Rollback last migration
    python run_migrations.py status       # Show migration status
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.connection import DATABASE_URL, get_engine, get_session
from migrations import run_migration, rollback_migration, SEVERITY_ENUM, ATTACK_TYPE_ENUM

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_migration_status():
    """Get current migration status"""
    engine = get_engine()
    inspector = __import__('sqlalchemy').inspect(engine)
    
    # Check if migrations table exists
    tables = inspector.get_table_names()
    
    if 'migrations' not in tables:
        return "No migrations table found"
    
    # Get migration status
    session = get_session()
    try:
        migrations = session.query(
            __import__('sqlalchemy').text('SELECT * FROM migrations ORDER BY applied_at DESC')
        ).fetchall()
        
        if not migrations:
            return "No migrations applied"
        
        result = "Applied Migrations:\n"
        for migration in migrations:
            result += f"  • {migration[1]}: {migration[2]} ({migration[3]}) - {migration[4]}\n"
        return result
        
    finally:
        session.close()


def verify_database_connection():
    """Verify database connection"""
    logger.info("Verifying database connection...")
    try:
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(
                __import__('sqlalchemy').text("SELECT 1")
            )
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def check_prerequisites():
    """Check if database prerequisites are met"""
    logger.info("Checking prerequisites...")
    
    if not verify_database_connection():
        return False
    
    # Check if base tables exist
    engine = get_engine()
    inspector = __import__('sqlalchemy').inspect(engine)
    required_tables = ['emails', 'web_logs']
    existing_tables = inspector.get_table_names()
    
    for table in required_tables:
        if table not in existing_tables:
            logger.error(f"❌ Required table '{table}' not found")
            logger.info("Please run 'python setup.py' first to create base tables")
            return False
    
    logger.info("✅ All prerequisites met")
    return True


def run_all_migrations():
    """Run all pending migrations"""
    logger.info("="*70)
    logger.info("STARTING DATABASE MIGRATIONS")
    logger.info("="*70)
    
    if not check_prerequisites():
        logger.error("Prerequisites not met. Aborting migration.")
        return False
    
    try:
        logger.info("\n📋 Migration 001: Add Severity and Attack Type")
        logger.info("-"*70)
        run_migration(DATABASE_URL)
        logger.info("✅ Migration 001 completed\n")
        
        logger.info("="*70)
        logger.info("✅ ALL MIGRATIONS COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        logger.error("Please fix the issue and run migrations again")
        return False


def rollback_all_migrations():
    """Rollback all migrations"""
    logger.info("="*70)
    logger.info("STARTING DATABASE ROLLBACK")
    logger.info("="*70)
    
    if not check_prerequisites():
        logger.error("Prerequisites not met. Aborting rollback.")
        return False
    
    try:
        logger.info("\n📋 Rollback Migration 001")
        logger.info("-"*70)
        rollback_migration(DATABASE_URL)
        logger.info("✅ Rollback 001 completed\n")
        
        logger.info("="*70)
        logger.info("✅ ROLLBACK COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        return True
        
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        return False


def show_migration_summary():
    """Show migration summary"""
    logger.info("="*70)
    logger.info("DATABASE MIGRATION SUMMARY")
    logger.info("="*70)
    
    logger.info(f"\nDatabase URL: {DATABASE_URL}")
    logger.info(f"\nEnums Used:")
    logger.info(f"  • Severity: {SEVERITY_ENUM}")
    logger.info(f"  • Attack Types: {ATTACK_TYPE_ENUM}")
    
    logger.info(f"\nMigrations Available:")
    logger.info(f"  • 001: Add severity to emails and attack_type to web_logs")
    
    logger.info(f"\nNew Fields Added:")
    logger.info(f"  • Email.severity (VARCHAR(20))")
    logger.info(f"  • Email.detection_method (VARCHAR(50))")
    logger.info(f"  • WebLog.attack_type (VARCHAR(50))")
    logger.info(f"  • WebLog.ml_confidence (FLOAT)")
    
    logger.info(f"\nNew Indexes Created:")
    logger.info(f"  • idx_email_severity")
    logger.info(f"  • idx_web_log_attack_type")
    logger.info(f"  • idx_email_detection_method")
    
    logger.info("="*70)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'rollback':
            rollback_all_migrations()
        elif command == 'status':
            show_migration_summary()
        elif command == 'help':
            print(__doc__)
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
    else:
        # Default: run migrations
        success = run_all_migrations()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
