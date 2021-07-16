from sqlalchemy import create_engine, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Integer, SmallInteger, String, Date, DateTime, Float, Boolean, Text, LargeBinary)
from scrapy.utils.project import get_project_settings

DeclarativeBase = declarative_base()


def db_connect():
    return create_engine(get_project_settings().get('CONNECTION_STRING'))


def create_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Conference(DeclarativeBase):
    __tablename__ = 'conference'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    year = Column(Integer)
    papers = relationship("Paper")


paper_author_table = Table('association', DeclarativeBase.metadata,
                           Column('paper_id', Integer, ForeignKey('paper.id')),
                           Column('author_id', Integer, ForeignKey('author.id'))
                           )


class Paper(DeclarativeBase):
    __tablename__ = 'paper'
    id = Column(Integer, primary_key=True)
    title: Column(String)
    authors = relationship(
        "Author",
        secondary=paper_author_table,
        back_populates="papers"
    )
    conference_id = Column(Integer, ForeignKey('conference.id'))


class Author(DeclarativeBase):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    acm_id = Column(Integer)
    papers = relationship(
        "Paper",
        secondary=paper_author_table,
        back_populates="authors"
    )
    institutions = relationship("AuthorInstitution")


class AuthorInstitution(DeclarativeBase):
    __tablename__ = 'author_institution'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('author.id'))
