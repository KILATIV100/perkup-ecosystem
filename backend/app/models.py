from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), unique=True, nullable=True)
    photo_url = Column(Text)
    
    # Loyalty
    points = Column(Integer, default=0)
    experience = Column(Integer, default=0)
    level = Column(Integer, default=1)
    total_checkins = Column(Integer, default=0)
    total_games_played = Column(Integer, default=0)
    best_game_score = Column(Integer, default=0)
    
    # Metadata
    language_code = Column(String(10), default='uk')
    timezone = Column(String(50), default='Europe/Kiev')
    last_active_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), default="Бровари")
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Integer, default=100)
    
    description = Column(Text)
    phone = Column(String(20))
    
    is_active = Column(Boolean, default=True)
    total_checkins = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Checkin(Base):
    __tablename__ = "checkins"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    location_id = Column(Integer, nullable=False, index=True)
    
    user_latitude = Column(Float)
    user_longitude = Column(Float)
    distance_meters = Column(Integer)
    
    points_earned = Column(Integer, default=1)
    experience_earned = Column(Integer, default=10)
    
    verification_method = Column(String(20), default='gps')
    is_verified = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())