import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Base stays outside the class so your model files can easily import it
Base = declarative_base()

class DatabaseManager:
    """
    An Object-Oriented manager for handling the Oracle 19c database connection.
    """
    def __init__(self):
        self.env_path = Path(__file__).resolve().parents[2] / ".env"
        load_dotenv(dotenv_path=self.env_path)
        
        # Load credentials
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        
        # Connection Details
        self.host = "10.110.10.90"
        self.port = "1521"
        self.sid = "oracle"
        
        # Setup Engine and Session
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _create_engine(self):
        """Private method to construct the URL and return the engine."""
        if not self.username or not self.password:
            return None
            
        encoded_password = urllib.parse.quote_plus(self.password)
        db_url = f"oracle+oracledb://{self.username}:{encoded_password}@{self.host}:{self.port}/{self.sid}"
        return create_engine(db_url)

    def get_db(self):
        """Yields a database session. Used for FastAPI dependency injection."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def test_connection(self):
        """Tests the connection to the ISU Oracle database."""
        print("Attempting to connect to the Oracle database...")
        
        if not self.engine:
            print("Error: Could not load USERNAME or PASSWORD. Check your .env file path!")
            return

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 'Connection Successful!' FROM DUAL"))
                for row in result:
                    print(f"Success: {row[0]}")
        except Exception as e:
            print("\n--- Connection Failed ---")
            print(f"Error details: {e}")

# Create a single instance of the manager to be imported by FastAPI app(singleton)
db_manager = DatabaseManager()

# --- Connection Test ---
if __name__ == "__main__":
    # Now you just call the method on your object!
    db_manager.test_connection()
