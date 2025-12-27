"""
Database Connection and Session Management

Handles PostgreSQL connection setup, session management, and connection pooling.
"""

import os
from typing import Optional, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration from environment variables."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', 'postgres')
        self.database = os.getenv('DB_NAME', 'threat_detection')
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '10'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '20'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', '3600'))
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )
    
    def __repr__(self):
        return f"<DatabaseConfig({self.user}@{self.host}:{self.port}/{self.database})>"


class DatabaseEngine:
    """
    Manages SQLAlchemy engine and session factory.
    
    Features:
    - Connection pooling with QueuePool
    - Automatic pool recycle
    - Connection timeout handling
    - Logging of pool events
    """
    
    _instance: Optional['DatabaseEngine'] = None
    _engine = None
    _session_factory = None
    
    def __new__(cls) -> 'DatabaseEngine':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database engine (only once due to singleton)."""
        if self._engine is not None:
            return  # Already initialized
        
        self.config = DatabaseConfig()
        self._create_engine()
    
    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling."""
        try:
            self._engine = create_engine(
                self.config.connection_string,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    'connect_timeout': 10,
                    'options': '-c statement_timeout=30000'  # 30 second statement timeout
                }
            )
            
            # Set up event listeners for pool
            @event.listens_for(self._engine, "connect")
            def receive_connect(dbapi_conn, connection_record):
                """Initialize connection settings and log connections."""
                logger.debug(f"Database connection established from pool")
                # Set search path for PostgreSQL
                cursor = dbapi_conn.cursor()
                cursor.execute("SET search_path TO public")
                cursor.close()
            
            # Create session factory
            self._session_factory = sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
            
            logger.info(f"Database engine created: {self.config}")
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    
    def get_engine(self):
        """Get SQLAlchemy engine."""
        return self._engine
    
    def get_session(self) -> Session:
        """Get a new database session."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        return self._session_factory()
    
    def session_context(self) -> Generator[Session, None, None]:
        """Context manager for session (auto cleanup)."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """Create all tables in the database."""
        from .models import Base
        try:
            Base.metadata.create_all(self._engine)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_all_tables(self):
        """Drop all tables from the database (use with caution!)."""
        from .models import Base
        try:
            Base.metadata.drop_all(self._engine)
            logger.warning("All tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def dispose(self):
        """Close all connections in the pool."""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connections disposed")
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.session_context() as session:
                session.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global functions for convenience
def get_db_engine():
    """Get the global database engine."""
    return DatabaseEngine().get_engine()


def get_db_session() -> Session:
    """Get a new database session."""
    return DatabaseEngine().get_session()


def db_session_context() -> Generator[Session, None, None]:
    """Context manager for database session."""
    return DatabaseEngine().session_context()


def init_db():
    """Initialize database (create tables)."""
    DatabaseEngine().create_all_tables()


def test_db_connection() -> bool:
    """Test database connection."""
    return DatabaseEngine().test_connection()


# Export public API
_db_engine = DatabaseEngine()
DATABASE_URL = _db_engine.config.connection_string
get_engine = _db_engine.get_engine
get_session = _db_engine.get_session
session_context = _db_engine.session_context

