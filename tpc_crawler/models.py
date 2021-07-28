from scrapy.utils.project import get_project_settings
from sqlalchemy import (
    Integer, String)
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def db_connect():
    return create_engine(get_project_settings().get('CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)


class Tpc(Base):
    __tablename__ = 'tpc'
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer, ForeignKey('conference.id'))
    name = Column(String)
