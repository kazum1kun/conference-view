from conference_crawler.models import *
from queries import Queries

query = Queries()


def main():
    while True:
        print('Welcome to the ConferenceView! Please choose from the following options:\n'
              '1. Look up an author and the papers they published\n'
              '2. Look up an author and the conferences they served as TPC\n'
              '3. See various statistics of a conference\n'
              '0. Exit')
        selection = int(input('Your selection: '))

        if selection == 1:
            author_papers()
        elif selection == 2:
            author_tpc()
        elif selection == 3:
            conf_stats()
        else:
            break


def author_papers():
    author_name = input('Please enter the name of author: ')
    authors = query.lookup_author_by_name(author_name)

    if len(authors) == 0:
        print('No author found, please check your spelling')
        return
    elif len(authors) > 1:
        print('Multiple authors found, please choose from the list:')
        for i in range(1, len(authors)):
            author = authors[i - 1]
            print(f'{i}: {author.name}, ACM ID {author.acm_id}, IEEE ID {author.ieee_id}')
        selection = int(input('Your selection: '))
        author = authors[selection - 1]
    else:
        author = authors[0]

    papers = query.lookup_papers_by_author_id(author.id)

    for paper in papers:
        # Obtain the conference the paper is published in
        conference = query.lookup_paper_publish(paper.id)
        print(f'Title: {paper.title}, published on {conference.name}')


def author_tpc():
    author_name = input('Please enter the name of author: ')
    tpc = query.lookup_author_tpc_services(author_name)
    if len(tpc) == 0:
        print(
            'No service record found for this author. Please check spelling or consider alternative spellings of that name')
    else:
        for conf in tpc:
            print(conf.name)


def conf_stats():
    pass


if __name__ == '__main__':
    main()
