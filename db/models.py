from sqlalchemy import Column, Integer, String, Float
from db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    surname = Column(String)
    home_latitude = Column(Float)
    home_longitude = Column(Float)