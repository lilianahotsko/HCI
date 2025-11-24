#!/usr/bin/env python3
"""
Test database connection script
Run this to verify your database connection works
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

database_url = os.getenv('DATABASE_URL', 'sqlite:///hci_experiment.db')

# Convert postgres:// to postgresql:// if needed
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Testing database connection...")
print(f"URL: {database_url.split('@')[0]}@****")  # Hide password

try:
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={'connect_timeout': 10}
    )
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✓ Connection successful!")
        print(f"✓ Database version: {version}")
        
        # Test if we can create a table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        print("✓ Can create tables")
        
        # Clean up
        conn.execute(text("DROP TABLE IF EXISTS test_connection;"))
        print("✓ Test table cleaned up")
        
except Exception as e:
    print(f"✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✅ Database connection test passed!")

