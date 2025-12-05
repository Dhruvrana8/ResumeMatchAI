from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to documents
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(BigInteger)  # Size in bytes
    status = Column(String, default="uploaded")  # uploaded, processing, analyzed, error
    
    # Relationship to user
    owner = relationship("User", back_populates="documents")
