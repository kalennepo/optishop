import os
import urllib.parse # encode password
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
# Connection Information
# Replace with the actual credentials provided by your professor
USERNAME = os.getenv("DB_USERNAME")  # e.g., your student ID
PASSWORD = os.getenv("DB_PASSWORD")

ENCODED_PASSWORD = urllib.parse.quote_plus(PASSWORD)

# University Oracle 19c Server Details
HOST = "10.110.10.90" 
PORT = "1521"         
SID = "oracle"        

# Construct the database URL for SQLAlchemy using the oracledb driver
# Format: oracle+oracledb://user:pass@host:port/?sid=sid
SQLALCHEMY_DATABASE_URL = f"oracle+oracledb://{USERNAME}:{ENCODED_PASSWORD}@{HOST}:{PORT}/{SID}"

# SQLAlchemy Setup

# The engine is the core interface to the database. 
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal will be used to create independent database sessions for each web request.
# autocommit=False and autoflush=False are standard safe practices for SQLAlchemy.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all Object-Oriented database models.
Base = declarative_base()

# --- Connection Test ---
# This block only runs if you execute this specific script directly from the terminal
if __name__ == "__main__":
    from sqlalchemy import text
    print("Attempting to connect to the Oracle database...")
    
    # Check if env variables loaded
    if not USERNAME or not PASSWORD:
        print("Error: Could not load USERNAME or PASSWORD. Check your .env file path!")
    else:
        try:
            # Try to open a connection and run a simple test query
            with engine.connect() as connection:
                # DUAL is a dummy table built into Oracle databases specifically for testing
                result = connection.execute(text("SELECT 'Connection Successful!' FROM DUAL"))
                for row in result:
                    print(f"Success: {row[0]}")
        except Exception as e:
            print("\n--- Connection Failed ---")
            print(f"Error details: {e}")
