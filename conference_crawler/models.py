from scrapy.utils.project import get_project_settings
from sqlalchemy import (
    Integer, String)
from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def db_connect():
    print(get_project_settings().get('CONNECTION_STRING'))
    return create_engine(get_project_settings().get('CONNECTION_STRING'))


def create_table(engine):
    Base.metadata.create_all(engine)


class Conference(Base):
    __tablename__ = 'conference'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Integer)
    papers = relationship("Paper", backref="conference")
    tpc = relationship('Tpc', backref="conference")


paper_author_table = Table('paper_author', Base.metadata,
                           Column('paper_id', Integer, ForeignKey('paper.id')),
                           Column('author_id', Integer, ForeignKey('author.id'))
                           )


class Paper(Base):
    __tablename__ = 'paper'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    authors = relationship(
        "Author",
        secondary=paper_author_table,
        backref="papers"
    )
    conference_id = Column(Integer, ForeignKey('conference.id'))


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    acm_id = Column(Integer)
    ieee_id = Column(Integer)
    dblp_id = Column(String)
    institutions = relationship("AuthorInstitution")


class AuthorInstitution(Base):
    __tablename__ = 'author_institution'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    author_id = Column(Integer, ForeignKey('author.id'))


class Tpc(Base):
    __tablename__ = 'tpc'
    id = Column(Integer, primary_key=True)
    conference_id = Column(Integer, ForeignKey('conference.id'))
    name = Column(String)
