from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.exc import NoResultFound

from conference_crawler.models import *

class Queries:
    # Init db connection and sessionmaker
    def __init__(self):
        engine = db_connect()
        self.session: Session = sessionmaker(bind=engine)()

    def __del__(self):
        self.session.close()

    # Look up author by name and return their published papers
    def lookup_author_by_name(self, author_name):
        authors = self.session.query(Author).filter(Author.name.contains(author_name))

        return authors.all()

    # Lookup conference id by year and name
    def lookup_conference_id(self, name, year):
        conf_id = self.session.query(Conference.id).filter(Conference.name.contains(name), Conference.year == year).first()

        if conf_id is not None:
            return conf_id[0]
        else:
            return -1

    # Look up author's published papers given their ID
    def lookup_papers_by_author_id(self, author_id):
        papers = self.session.query(Paper).filter(Paper.authors.any(Author.id == author_id)).all()

        return papers

    # Look up author's services in TPC
    def lookup_author_tpc_services(self, author_name):
        # Lookup author's TPC service
        conferences = self.session.query(Conference).join(Tpc).filter(Tpc.name.contains(author_name)).all()

        return conferences

    # Look up where a paper is published given its id
    def lookup_paper_publish(self, paper_id):
        # Should have only one result, returning the first is fine
        conference = self.session.query(Conference).filter(Conference.papers.any(Paper.id == paper_id)).first()

        return conference

    # Get the list of authors whose papers are accepted in a conference
    def lookup_accepted_author_name(self, conf_id):
        # Get the list of papers that are accepted in a conference
        papers = self.session.query(Paper.id).filter_by(conference_id=conf_id).all()
        # Convert the result to a list (originally list of tuples)
        papers = [paper for paper, in papers]

        # Get the list of authors
        authors = self.session.query(Author.name).filter(Author.papers.any(Paper.id.in_(papers))).all()

        return [author for author, in authors]
