import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

# Load environment variables from .env file (if it exists)
load_dotenv()

def get_database_url():
    """
    Get database URL based on environment.
    
    Priority:
    1. Explicit MYSQL_DATABASE_URL (overrides everything)
    2. Individual components (DB_HOST, DB_USER, etc.)
    3. Environment-based defaults
    """
    # If explicit DATABASE_URL is provided, use it
    explicit_url = os.getenv("MYSQL_DATABASE_URL")
    if explicit_url and explicit_url != "mysql+pymysql://wildeditor_user:YOUR_PASSWORD@localhost:3306/luminari_muddev":
        logger.info("Database connection configured from MYSQL_DATABASE_URL")
        return explicit_url
    
    # Get individual components with environment-based defaults
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    # Database host logic
    if environment == "production":
        # Production: assume database is on same server
        db_host = os.getenv("DB_HOST", "localhost")
        logger.info("Production database connection configured")
    else:
        # Development: use remote database
        db_host = os.getenv("DB_HOST", "your-remote-db-server.com")
        logger.info("Development database connection configured")
    
    # Other database parameters
    db_user = os.getenv("DB_USER", "wildeditor_user")
    db_password = os.getenv("DB_PASSWORD", "")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "luminari_muddev")
    
    if not db_password:
        logger.warning("DB_PASSWORD is not configured")
    
    # Construct URL
    database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return database_url

DATABASE_URL = get_database_url()

if not DATABASE_URL:
    # For testing and CI environments, provide a default test database URL
    if os.getenv("TESTING") or "pytest" in os.environ.get("_", ""):
        DATABASE_URL = "mysql+pymysql://test:test@localhost:3306/test_db"
        logger.info("Using the test database configuration")
    else:
        raise RuntimeError("Unable to determine database URL. Please configure DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME environment variables.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
