from sqlalchemy import Column, Integer, String, Boolean
from backend.db.db_connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="shopper", nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
