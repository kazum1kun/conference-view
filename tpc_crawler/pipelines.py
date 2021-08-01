# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from conference_crawler.models import *
from tpc_crawler.items import *


class TpcCrawlerPipeline:
    # Init db connection and sessionmaker, and create tables
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    # Save the information
    def process_item(self, item: TpcItem, spider):
        session = self.Session()
        session.begin()

        # Look up the corresponding conference
        try:
            conference_db = session.query(Conference).filter(Conference.name.contains(item.conference_type.value),
                                                             Conference.year == item.conference_year).one()

            for member in item.tpc:
                member_db = Tpc()
                member_db.name = member
                conference_db.tpc.append(member_db)
                session.add(member_db)

        except NoResultFound as e:
            print('Error, conference not found!')

        session.commit()
        session.close()
