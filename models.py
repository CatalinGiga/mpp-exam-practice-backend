from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=False)
    health = Column(Integer, default=100)
    armor = Column(Integer, default=0)
    mana = Column(Integer, default=0)
    kills = Column(Integer, default=0)

class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, unique=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

class Enemy(Base):
    __tablename__ = "enemies"
    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    health = Column(Integer, default=100) 