from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func

from conference_crawler.models import *


class Queries:
    # Init db connection and sessionmaker
    def __init__(self):
        engine = db_connect()
        self.session: Session = sessionmaker(bind=engine)()

    # Look up author by name and return their published papers
    def lookup_author_by_name(self, author_name):
        # Case-insensitive query
        authors = self.session.query(Author).filter(func.lower(Author.name).contains(func.lower(author_name)))

        return authors.all()

    # Lookup conference id by year and name
    def lookup_conference_id(self, name, year):
        # Case-insensitive query
        conf_id = self.session.query(Conference.id).filter(
            func.lower(Conference.name).contains(func.lower(name)),
            Conference.year == year) \
            .first()

        if conf_id is not None:
            return conf_id[0]
        else:
            return -1

    # Look up author's published papers given their ID
    def lookup_papers_by_author_id(self, author_id):
        papers = self.session.query(Paper).filter(Paper.authors.any(Author.id == author_id)).all()

        return papers

    # Look up the name of tpc members
    def lookup_tpc_names(self, name):
        # Case-insensitive
        names = self.session.query(Tpc).join(Conference).filter(
            func.lower(Tpc.name).contains(func.lower(name))).all()

        return names

    # Look up service history of a tpc member
    def lookup_tpc_services(self, tpc_name):
        # Case-insensitive
        conferences = self.session.query(Conference).join(Tpc).filter(
            func.lower(Tpc.name).contains(func.lower(tpc_name))).all()

        return conferences

    # Look up where a paper is published given its id
    def lookup_paper_publish(self, paper_id):
        # Should have only one result, returning the first is fine
        conference = self.session.query(Conference).filter(Conference.papers.any(Paper.id == paper_id)).first()

        return conference

    # Get the list of authors (name and id) whose papers are accepted in a conference
    def lookup_accepted_author(self, conf_id):
        # Get the list of papers that are accepted in a conference
        papers = self.session.query(Paper.id).filter_by(conference_id=conf_id).all()
        # Convert the result to a list (originally list of tuples)
        papers = [paper for paper, in papers]

        authors = self.session.query(Author.id, Author.name).filter(Author.papers.any(Paper.id.in_(papers))).all()

        return authors

    # Look up conference name by id
    def lookup_conference_name_by_id(self, conf_id):
        conf_name = self.session.query(Conference.name).filter(Conference.id == conf_id).first()

        return conf_name[0]

    # Look up tpc members on a conference
    def lookup_tpc_on_conference(self, conf_id):
        tpc = self.session.query(Tpc.name).filter(Tpc.conference_id == conf_id).all()

        tpc = [name for name, in tpc]

        return tpc
