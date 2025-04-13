# account_service/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # В реальном проекте используйте хэширование паролей
    high_score = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    games = relationship("GameResult", back_populates="owner")

class GameResult(Base):
    __tablename__ = 'game_results'
    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="games")
