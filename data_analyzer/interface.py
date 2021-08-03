import sys

from queries import Queries

query = Queries()


def main():
    while True:
        print('\nWelcome to the ConferenceView! Please choose from the following options:\n'
              '1. Look up an author and the papers they published\n'
              '2. Look up an author and the conferences they served as TPC\n'
              '3. See various statistics of a conference\n'
              '4. Get a report of all available data of the conferences\n'
              '0. Exit')
        selection = int(input('Your selection: '))

        if selection == 1:
            author_papers()
        elif selection == 2:
            author_tpc()
        elif selection == 3:
            conf_stats()
        elif selection == 4:
            conference_report()
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

    result = calc_conference_stats(conf_name, conf_year)
    if result is None:
        print(f'{conf_name} {conf_year} is not found in the database. Please check your input')

    print(f'Among all papers accepted on {result["conf_name"]}, there are {"{:.1f}".format(result["published_pct"])}% '
          f'({result["published_count"]}/{result["total_papers"]}) papers that have at least one author who published'
          f' on this conference before')
    print(f'In addition, {"{:.1f}".format(result["tpc_pct"])}% ({result["tpc_count"]}/{result["total_papers"]}) of '
          f'the papers have at least one author who serves in the TPC as well ')
    print(f'{"{:.1f}".format(result["both_pct"])} ({result["both_count"]}/{result["total_papers"]}) papers satisfy '
          f'both criteria above')


# Obtain a report on the conference data
def conference_report():
    print('\nGenerating report, please wait')
    with open('conference_report.csv', 'w+') as output:
        output.write('conf_name,total_papers,published_count,tpc_count,both_count\n')
        for conf_name in ['SIGCOMM', 'INFOCOM', 'MOBICOM']:
            for conf_year in range(1985, 2022):
                sys.stdout.write(f'\rNow processing {conf_name} {conf_year}')
                sys.stdout.flush()
                result = calc_conference_stats(conf_name, conf_year)
                # Data may be missing for some years, skip them
                if result is None:
                    output.write(f'Data for {conf_name} {conf_year} is missing')
                else:
                    output.write(f'{result["conf_name"]},{result["total_papers"]},{result["published_count"]},'
                                 f'{result["tpc_count"]},{result["both_count"]}\n')
    print('\nReport saved as conference_report.csv')


def calc_conference_stats(conf_name, conf_year):
    # Check if the conference exists in the DB
    conf_id = query.lookup_conference_id(conf_name, conf_year)
    if conf_id == -1:
        return None
    orig_conf_name = query.lookup_conference_name_by_id(conf_id)
    orig_conf_id = conf_id

    # The first statistic is to see how many (or what percentage) of papers are written by authors that have never
    # published in this conference before. Note that as long as one of the authors of a paper has published before, the
    # paper is considered as written by someone who published before. Since each author entity is unique (given their
    # ACM/IEEE ID is unique),  we can safely assume that the author's ID is also unique and can be used for this purpose

    # Get the ids of all authors that have published in the past
    past_authors_id = set()

    cy = conf_year
    while cy > 1985:
        # Iterate until the end year (1985) is reached
        cy -= 1

        conf_id = query.lookup_conference_id(conf_name, cy)

        if conf_id == -1:
            continue

        # Add the list of author ids in the current year to the set
        past_authors_id.update(list(zip(*query.lookup_accepted_authors(conf_id)))[0])

    # Get the list of people that served in the tpc
    tpc_names = set([name.lower() for name in query.lookup_tpc_on_conference(orig_conf_id)])

    # Get the list of papers in the conference
    papers_id = query.lookup_papers_in_conference(orig_conf_id)

    paper_author = []
    # Combine author data with the paper id
    for paper in papers_id:
        # Results are in [(author.id, author.name), (...)] format, need to unpack them first (id and names saved as
        # lists to facilitate comparison)
        authors = list(zip(*query.lookup_paper_authors(paper)))
        authors_id = set(authors[0])
        # Convert the name to lowercase for comparison
        authors_name = set([name.lower() for name in authors[1]])
        # Save the data as a dictionary and initialize both published and tpc to False
        # 'published' key indicates whether the paper is written by someone who published before, 'tpc' key indicates
        # whether it's written by someone who serves in the TPC
        paper_author.append({'id': paper,
                             'authors_id': authors_id,
                             'authors_name': authors_name,
                             'published': False,
                             'tpc': False})

    # Technically only a counter is needed, the T/F indication here is meant for future uses (e.g. GUI expansion)
    published_count = 0
    tpc_count = 0
    both_count = 0
    for paper in paper_author:
        # Check whether the paper contains AN author that published before
        if not paper['authors_id'].isdisjoint(past_authors_id):
            paper['published'] = True
            published_count += 1
        # Check whether the paper contains AN author that served in the TPC
        if not paper['authors_name'].isdisjoint(tpc_names):
            paper['tpc'] = True
            tpc_count += 1
        if paper['published'] and paper['tpc']:
            both_count += 1

    # Crunch some numbers - calculate the percentage of the papers that are published by someone who published before
    # and by someone who serves in the tpc
    published_pct = published_count / len(papers_id)
    tpc_pct = tpc_count / len(papers_id)
    both_pct = both_count / len(papers_id)

    return {'conf_name': orig_conf_name,
            'conf_year': conf_year,
            'total_papers': len(papers_id),
            'published_pct': published_pct,
            'published_count': published_count,
            'tpc_pct': tpc_pct,
            'tpc_count': tpc_count,
            'both_pct': both_pct,
            'both_count': both_count}


if __name__ == '__main__':
    main()
