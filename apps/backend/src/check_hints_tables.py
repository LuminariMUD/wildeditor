#!/usr/bin/env python3
"""
Script to check if region hints tables exist in the database.
Run this to verify the database is properly set up.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_tables():
    """Check if region hints tables exist in the database."""
    
    # Get database URL from environment
    database_url = os.getenv("MYSQL_DATABASE_URL")
    if not database_url:
        print("ERROR: MYSQL_DATABASE_URL not set in environment")
        return False
    
    print(f"Connecting to database...")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Check each table
        tables_to_check = ['region_hints', 'region_profiles', 'hint_usage_log']
        
        with engine.connect() as conn:
            for table in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = :table_name
                """), {"table_name": table})
                
                exists = result.fetchone()[0] > 0
                status = "✓ EXISTS" if exists else "✗ MISSING"
                print(f"{table}: {status}")
                
                if exists:
                    # Get row count
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.fetchone()[0]
                    print(f"  - Contains {count} rows")
        
        print("\nDatabase check complete!")
        return True
        
    except Exception as e:
        print(f"ERROR checking database: {e}")
        return False

if __name__ == "__main__":
    success = check_tables()
    sys.exit(0 if success else 1)