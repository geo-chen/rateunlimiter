from sqlalchemy import Boolean, Column, DateTime, Integer, \
    String, SmallInteger, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RequestLog(Base):
    __tablename__ = 'request_log'
    request_id = Column(Integer(), primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(), nullable=False)
    url = Column(String(255), nullable=False)
    status = Column(Integer, default=0)
    blocked = Column(Boolean(), nullable=False)
