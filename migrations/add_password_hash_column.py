"""
Database migration script to add password_hash column to students table.
Run this script once to fix the missing column issue.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config import engine, logger


def migrate_add_password_hash_column():
    """Add password_hash column to students table if it doesn't exist."""
    
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'students' AND column_name = 'password_hash'
        """))
        
        if result.fetchone() is None:
            # Add the column
            conn.execute(text("""
                ALTER TABLE students 
                ADD COLUMN password_hash VARCHAR(255)
            """))
            conn.commit()
            logger.info("Successfully added password_hash column to students table")
            print("Migration completed: Added password_hash column to students table")
        else:
            logger.info("password_hash column already exists in students table")
            print("Migration skipped: password_hash column already exists")


if __name__ == "__main__":
    try:
        migrate_add_password_hash_column()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
