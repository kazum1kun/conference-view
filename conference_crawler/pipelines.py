# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from conference_crawler.items import *
from conference_crawler.models import *


class ConferenceCrawlerPipeline:
    # Init db connection and sessionmaker, and create tables
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    # Save the information
    def process_item(self, item: ConferenceItem, spider):
        session = self.Session()
        session.begin()

        conference_db = Conference()
        conference_db.name = item.name
        conference_db.year = item.year

        for paper in item.papers:
            paper_db = Paper()
            paper_db.title = paper.title

            for author in paper.authors:
                # If the author is already existing, add the paper to the existing entry
                try:
                    if author.acm_id is not None:
                        author_db = session.query(Author).filter_by(acm_id=author.acm_id).one()
                    elif author.ieee_id is not None:
                        author_db = session.query(Author).filter_by(ieee_id=author.ieee_id).one()
                    else:
                        author_db = session.query(Author).filter(Author.acm_id.is_(None), Author.ieee_id.is_(None)).one()

                except MultipleResultsFound as e:
                    # Impossible given the situation
                    author_db = None
                except NoResultFound as e:
                    author_db = self.create_author(author)
                    session.add(author_db)

                paper_db.authors.append(author_db)

            session.add(paper_db)
            conference_db.papers.append(paper_db)

        session.add(conference_db)
        session.commit()
        session.close()

        return item

    def create_author(self, author):
        author_db = Author()
        author_db.name = author.name
        author_db.acm_id = author.acm_id
        author_db.ieee_id = author.ieee_id
        return author_db
