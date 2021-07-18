# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy.orm import sessionmaker
from conference_crawler.models import *
from conference_crawler.items import *


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
                author_db = Author()
                author_db.name = author.name
                author_db.acm_id = author.acm_id

                for institution in author.affiliations:
                    author_inst_db = AuthorInstitution()
                    author_inst_db.name = institution
                    author_db.institutions.append(author_inst_db)
                    session.add(author_inst_db)
                session.add(author_db)
                paper_db.authors.append(author_db)
            session.add(paper_db)
            conference_db.papers.append(paper_db)
        session.add(conference_db)
        session.commit()
        session.close()

        return item
