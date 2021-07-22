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
                    author_db = session.query(Author).filter_by(name=author.name).one()
                    # Update author's acm id or ieee id
                    if author.acm_id and not author_db.acm_id:
                        author_db.acm_id = author.acm_id
                    if author.ieee_id and not author_db.ieee_id:
                        author_db.ieee_id = author.ieee_id
                except MultipleResultsFound as e:
                    # TODO: better handle authors with the identical names
                    print(f'Error: Multiple authors named {author.name} found')
                    author_db = None
                except NoResultFound as e:
                    author_db = Author()
                    author_db.name = author.name
                    author_db.acm_id = author.acm_id
                    author_db.ieee_id = author.ieee_id
                    session.add(author_db)

                paper_db.authors.append(author_db)

            session.add(paper_db)
            conference_db.papers.append(paper_db)

        session.add(conference_db)
        session.commit()
        session.close()

        return item
