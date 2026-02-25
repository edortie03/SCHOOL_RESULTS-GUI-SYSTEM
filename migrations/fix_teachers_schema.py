"""
Database migration script to fix teachers table schema completely.
Renames fullname to full_name and handles password column properly.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config import engine, logger


def migrate_fix_teachers_schema():
    """Fix teachers table schema - rename columns to match the model."""
    
    with engine.connect() as conn:
        # Check existing columns
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'teachers'
        """))
        
        columns = [row[0] for row in result.fetchall()]
        logger.info(f"Current teachers table columns: {columns}")
        print(f"Current teachers table columns: {columns}")
        
        # Fix fullname -> full_name
        if 'fullname' in columns:
            conn.execute(text("""
                ALTER TABLE teachers 
                RENAME COLUMN fullname TO full_name
            """))
            conn.commit()
            logger.info("Renamed fullname to full_name")
            print("Renamed fullname to full_name")
        
        # Fix password -> password_hash (if password exists and password_hash doesn't)
        if 'password' in columns and 'password_hash' not in columns:
            conn.execute(text("""
                ALTER TABLE teachers 
                RENAME COLUMN password TO password_hash
            """))
            conn.commit()
            logger.info("Renamed password to password_hash")
            print("Renamed password to password_hash")
        elif 'password' in columns and 'password_hash' in columns:
            # Drop the old password column if both exist
            conn.execute(text("""
                ALTER TABLE teachers 
                DROP COLUMN password
            """))
            conn.commit()
            logger.info("Dropped old password column")
            print("Dropped old password column")
        
        # Verify final schema
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'teachers'
        """))
        
        final_columns = [row[0] for row in result.fetchall()]
        logger.info(f"Final teachers table columns: {final_columns}")
        print(f"Final teachers table columns: {final_columns}")


if __name__ == "__main__":
    try:
        migrate_fix_teachers_schema()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
