"""
Database migration script to fully reset teachers table to match model.
Drops and recreates the table with the correct schema.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from config import engine, logger


def migrate_reset_teachers_table():
    """Drop and recreate teachers table with correct schema."""
    
    with engine.connect() as conn:
        # Check if table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'teachers'
            )
        """))
        table_exists = result.fetchone()[0]
        
        if not table_exists:
            print("Teachers table doesn't exist - nothing to reset")
            return
            
        # Backup data if needed (optional - we can skip this for now)
        print("Dropping teachers table...")
        conn.execute(text("DROP TABLE IF EXISTS teachers CASCADE"))
        conn.commit()
        print("Teachers table dropped")
        
        # Recreate table with correct schema
        print("Recreating teachers table...")
        conn.execute(text("""
            CREATE TABLE teachers (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(120) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'TEACHER' NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        print("Teachers table recreated with correct schema")
        
        # Verify
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'teachers'
        """))
        columns = [row[0] for row in result.fetchall()]
        print(f"New teachers table columns: {columns}")


if __name__ == "__main__":
    try:
        migrate_reset_teachers_table()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
