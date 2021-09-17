from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from main import config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Table

engine_sql_lite= create_engine("sqlite:///database.db", connect_args={
                       "check_same_thread": False})
Session = sessionmaker(bind=engine_sql_lite)
Base = declarative_base(bind=engine_sql_lite)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close() 


class Doc(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    text = Column(String(1024))
    date = Column(Date)
    tags = relationship("Rubric", lazy='joined')


class Rubric(Base):
    __tablename__ = "rubrics"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))