"""
Database migration script to fix teachers table schema.
Run this script once to fix the missing/renamed columns issue.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config import engine, logger


def migrate_fix_teachers_table():
    """Fix teachers table schema - rename password to password_hash if needed."""
    
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'teachers'
        """))
        
        columns = [row[0] for row in result.fetchall()]
        logger.info(f"Current teachers table columns: {columns}")
        
        # Check if password column exists (old schema)
        if 'password' in columns and 'password_hash' not in columns:
            # Rename password to password_hash
            conn.execute(text("""
                ALTER TABLE teachers 
                RENAME COLUMN password TO password_hash
            """))
            conn.commit()
            logger.info("Successfully renamed password column to password_hash in teachers table")
            print("Migration completed: Renamed password column to password_hash in teachers table")
        elif 'password_hash' in columns:
            logger.info("password_hash column already exists in teachers table")
            print("Migration skipped: password_hash column already exists")
        else:
            # Add the column if neither exists
            conn.execute(text("""
                ALTER TABLE teachers 
                ADD COLUMN password_hash VARCHAR(255) NOT NULL
            """))
            conn.commit()
            logger.info("Successfully added password_hash column to teachers table")
            print("Migration completed: Added password_hash column to teachers table")


if __name__ == "__main__":
    try:
        migrate_fix_teachers_table()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
