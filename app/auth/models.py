from sqlalchemy import Column, DateTime, Integer, Sequence, String, Text, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('msg_id_seq'), primary_key=True, nullable=False)
    username = Column(String(40), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    coins = Column(Integer, default=0)

sa_users = User.__table__

