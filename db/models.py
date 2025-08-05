from sqlalchemy import Column, Integer, String, Float
from db.database import Base
from sqlalchemy import Boolean


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    surname = Column(String)
    home_latitude = Column(Float)
    home_longitude = Column(Float)


class TodayControl(Base):
    __tablename__ = "today_control"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    is_home = Column(Boolean, nullable=False)


class NotHomeDistance(Base):
    __tablename__ = "not_home_distance"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    distance = Column(Float, nullable=False)