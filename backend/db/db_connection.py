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
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.sid = os.getenv("DB_SID")
        
        # Setup Engine and Session
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def _create_engine(self):
        """Private method to construct the URL and return the engine."""
        engine = None
        if self.username and self.password and self.host and self.port and self.sid:
            encoded_password = urllib.parse.quote_plus(self.password)
            db_url = f"oracle+oracledb://{self.username}:{encoded_password}@{self.host}:{self.port}/{self.sid}"
            try:
                engine = create_engine(db_url)
                # Quick test to see if Oracle is reachable (e.g., behind VPN)
                with engine.connect() as conn:
                    pass
            except Exception as e:
                print(f"Warning: Could not connect to Oracle DB ({e}). Falling back to SQLite.")
                engine = None
                
        if not engine:
            print("Using local SQLite database for development.")
            db_url = "sqlite:///./optishop.db"
            engine = create_engine(db_url, connect_args={"check_same_thread": False})
            
            # Auto-create tables for SQLite to make local testing easy
            from backend.models.user import User
            from backend.models.store import Store
            from backend.models.aisle import Aisle
            from backend.models.grocery_item import GroceryItem
            from backend.models.cart import Cart, CartItem
            Base.metadata.create_all(bind=engine)
            
        return engine

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
