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
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class AlternativeLocation(Base):
    __tablename__ = "alternative_locations"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    comment = Column(String, nullable=False)


class Questionnaire(Base):
    __tablename__ = "questionnaire"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    surname = Column(String)
    will_feed = Column(Boolean, nullable=False)
