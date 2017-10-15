from sqlalchemy import Column, DateTime, Integer, Sequence, String, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'useres'
    id = Column(Integer, Sequence('msg_id_seq'), primary_key=True, nullable=False)
    username = Column(String(40), nullable=False)
    password = Column(String(64), nullable=False)


class Stat(Base):
    __tablename__ = 'stats'


sa_messages = User.__table__
