"""
Database module for Unified Cyber Threat Detection System.

Exports:
- Models: Email, WebLog, ThreatCorrelation, ThreatReport, AuditLog
- Database engine and session management
- Configuration and initialization functions
"""

from .models import (
    Base,
    Email,
    WebLog,
    ThreatCorrelation,
    ThreatReport,
    AuditLog,
)

from .connection import (
    DatabaseConfig,
    DatabaseEngine,
    get_db_engine,
    get_db_session,
    db_session_context,
    init_db,
    test_db_connection,
)

__all__ = [
    # Models
    'Base',
    'Email',
    'WebLog',
    'ThreatCorrelation',
    'ThreatReport',
    'AuditLog',
    # Connection
    'DatabaseConfig',
    'DatabaseEngine',
    'get_db_engine',
    'get_db_session',
    'db_session_context',
    'init_db',
    'test_db_connection',
]
