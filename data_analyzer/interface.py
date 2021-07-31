from conference_crawler.models import *
from queries import Queries

query = Queries()


def main():
    while True:
        print('\nWelcome to the ConferenceView! Please choose from the following options:\n'
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
    print('\nAuthor published paper lookup')
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
    print(f'\n{author.name} has published the following papers: ')
    for paper in papers:
        # Obtain the conference the paper is published in
        conference = query.lookup_paper_publish(paper.id)
        print(f'Title: {paper.title}, published on {conference.name}')


def author_tpc():
    print('\nAuthor TPC services lookup')
    author_name = input('Please enter the name of author: ')
    tpc = query.lookup_tpc_names(author_name)
    if len(tpc) == 0:
        print(
            'No service record found for this author. Please check spelling or '
            'consider alternative spellings of that name')
        return
    # Due to technical difficulties, all tpc member lists stores people's name and the conference they serve in only.
    # Duplicate names of the same person are possible because of that, so we want to make sure the dups are removed
    elif len(tpc) > 1:
        # Consolidate duplicate names
        result = []
        # The set is used to prevent duplication (where names are stored in lower-case)
        name_set = set()
        for tpc_member in tpc:
            lower_name = tpc_member.name.lower()
            if lower_name not in name_set:
                name_set.add(lower_name)
                result.append(tpc_member.name)
        # If there are still multiple results found, they are likely different people
        if len(result) > 1:
            print('Multiple TPC names found, please choose from the list:')
            for i in range(1, len(result)):
                tpc_member = result[i - 1]
                print(f'{i}: {tpc_member}')
            selection = int(input('Your selection: '))
            tpc_member = result[selection - 1]
        # No duplicate found, use the first (and the only) name to query
        else:
            tpc_member = result[0]
    else:
        tpc_member = tpc[0].name

    conferences = query.lookup_tpc_services(tpc_member)
    print(f'\n{tpc_member} has served in TPC at the following conferences: ')
    for conf in conferences:
        print(conf.name)


def conf_stats():
    print('\nConference statistics')

    pass


if __name__ == '__main__':
    main()
