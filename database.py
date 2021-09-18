import typing
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, ForeignKey
import requests
import os

engine_sql_lite= create_engine(os.environ.get('sql_db'), connect_args={
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
    __tablename__ = "doc"
    id = Column(Integer, primary_key=True)
    text = Column(String(1024))
    date = Column(Date)     
    rubrics = relationship("Rubric", lazy='joined')


class Rubric(Base):
    __tablename__ = "rubric"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    doc_id = Column(Integer, ForeignKey('doc.id'))  


class Elastic():
    _index = 'docs'
    _host = os.environ.get('host_elastic')

    @staticmethod
    def create(id: int, query_params: typing.Optional[dict] = None, body_params: typing.Optional[dict] = None) -> None:
        return requests.post(url=Elastic._host + f"/{Elastic._index}/_doc/{id}", params=query_params, json=body_params).json()
    
    @staticmethod
    def search(query_params: typing.Optional[dict] = None, body_params: typing.Optional[dict] = None):
        return requests.get(url=Elastic._host + f"/{Elastic._index}/_search/", params=query_params, json=body_params).json()
    
    @staticmethod
    def delete(id: int) -> None:
        requests.delete(url=Elastic._host + f"/{Elastic._index}/_doc/{id}")
    
# Создаём таблицы.
Base.metadata.create_all(engine_sql_lite)