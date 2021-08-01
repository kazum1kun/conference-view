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
    print('Please enter the name of the conference, currently INFOCOM, MOBICOM, and SIGCOMM are supported')
    conf_name = input('Conference name: ')
    print('Please enter the year of the conference, between 1985 and 2021')
    conf_year = int(input('Conference year: '))
    # Check if the conference exists in the DB
    conf_id = query.lookup_conference_id(conf_name, conf_year)
    if conf_id == -1:
        print(f'{conf_name} {conf_year} is not found in the database. Please check your input')
        return
    orig_conf_name = query.lookup_conference_name_by_id(conf_id)
    orig_conf_id = conf_id

    # The first statistic is to see how many (or what percentage) of authors have never published in this conference
    # before. Since each author entity is unique (given their ACM/IEEE ID is unique), we can safely assume that the
    # author's ID is also unique and can be used for this purpose
    past_authors_id = set()

    # Results are in [(authod.id, author.name), (...)] format, need to unpack them first
    authors = list(zip(*query.lookup_accepted_author(conf_id)))
    current_authors_id = set(authors[0])
    current_authors_name = set(authors[1])

    cy = conf_year
    while cy > 1985:
        # Iterate until the end year (1985) is reached
        cy -= 1

        conf_id = query.lookup_conference_id(conf_name, cy)

        if conf_id == -1:
            continue

        # Add the list of author ids in the current year to the set
        past_authors_id.update(list(zip(*query.lookup_accepted_author(conf_id)))[0])

    # Compare the set of past authors and current authors: find the intersection between the two (i.e. the authors that
    # has published in the past) and divide it by the number of current authors to obtain the ratio
    current_published = past_authors_id & current_authors_id
    new_author_count = len(current_authors_id) - len(current_published)
    new_author_pct = new_author_count / len(current_authors_id) * 100

    # Another stat one might be interested in is how many accepted authors serve in the TPC. Since we only have the
    # names of the TPC members, comparing names vs accepted authors should give us a close approximation

    # Convert the name lists to lower case
    current_authors_names = set([name.lower() for name in current_authors_name])
    tpc_names = set([name.lower() for name in query.lookup_tpc_on_conference(orig_conf_id)])

    # Calculate the intersect anf derive the stats
    tpc_publish = current_authors_names & tpc_names
    tpc_publish_pct = len(tpc_publish) / len(current_authors_names) * 100

    # Calculate how many in the tpc have their paper accepted
    tpc_accepted_pct = len(tpc_publish) / len(tpc_names) * 100

    print(f'Among all papers accepted on {orig_conf_name}, there are {"{:.1f}".format(new_author_pct)}% '
          f'({new_author_count}/{len(current_authors_id)}) authors that have never published on this conference before')
    print(f'In addition, {"{:.1f}".format(tpc_publish_pct)}% ({len(tpc_publish)}/{len(current_authors_name)}) '
          f'of all authors who are accepted also work in the TPC, which is {"{:.1f}".format(tpc_accepted_pct)} '
          f'({len(tpc_publish)}/{len(tpc_names)})% of the TPC members')


if __name__ == '__main__':
    main()
