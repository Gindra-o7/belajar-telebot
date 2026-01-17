from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="watchlist")
    
    # Constraint: user tidak bisa tambah symbol yang sama 2x
    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='unique_user_symbol'),
    )

class StockQuery(Base):
    """Log query untuk analytics"""
    __tablename__ = "stock_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    query_type = Column(String, nullable=False)  # price, info, watchlist
    created_at = Column(DateTime(timezone=True), server_default=func.now())