"""
config.py - Application configuration and database setup
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("school_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
encoded_password = quote_plus(DB_PASSWORD)

DATABASE_URL = (
    f"postgresql://{DB_USER}:{encoded_password}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Application constants
APP_TITLE = "School Examination Results Management System"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1280x780"

# Grade scale
GRADE_SCALE = [
    (80, 100, "A", 4.0, "Distinction"),
    (70, 79,  "B", 3.0, "Credit"),
    (60, 69,  "C", 2.0, "Merit"),
    (50, 59,  "D", 1.0, "Pass"),
    (0,  49,  "F", 0.0, "Fail"),
]

# Theme colours
COLORS = {
    "primary":     "#1a237e",
    "primary_light": "#3949ab",
    "secondary":   "#0277bd",
    "accent":      "#00acc1",
    "success":     "#2e7d32",
    "warning":     "#f57f17",
    "danger":      "#c62828",
    "bg_dark":     "#0d1117",
    "bg_medium":   "#161b22",
    "bg_light":    "#21262d",
    "sidebar":     "#0d1117",
    "card":        "#21262d",
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "border":      "#30363d",
    "hover":       "#2d333b",
    "white":       "#ffffff",
    "table_odd":   "#1c2128",
    "table_even":  "#21262d",
    "table_header":"#1a237e",
}

FONTS = {
    "heading":  ("Segoe UI", 18, "bold"),
    "subheading": ("Segoe UI", 13, "bold"),
    "body":     ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "small":    ("Segoe UI", 9),
    "mono":     ("Courier New", 10),
}


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database — create all tables."""
    try:
        # Clear any cached metadata to ensure fresh table inspection
        Base.metadata.clear()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
