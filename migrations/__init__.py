"""
Migrations package

Provides access to migration modules
"""

# Import migration functions from 001_add_severity_and_attack_type
import importlib.util
from pathlib import Path

# Get the path to the migration file
migration_path = Path(__file__).parent / "001_add_severity_and_attack_type.py"

# Load the module dynamically
spec = importlib.util.spec_from_file_location(
    "migrations.add_severity_and_attack_type",
    migration_path
)
migration_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_module)

# Re-export the functions and constants
run_migration = migration_module.run_migration
rollback_migration = migration_module.rollback_migration
SEVERITY_ENUM = migration_module.SEVERITY_ENUM
ATTACK_TYPE_ENUM = migration_module.ATTACK_TYPE_ENUM

__all__ = [
    'run_migration',
    'rollback_migration',
    'SEVERITY_ENUM',
    'ATTACK_TYPE_ENUM',
]
