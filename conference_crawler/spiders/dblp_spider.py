import re

import scrapy

from conference_crawler.items import *


class DblpSpider(scrapy.Spider):
    name = 'dblpspider'

    start_urls = [
        'https://dblp.org/db/conf/nips/neurips2020.html',
        'https://dblp.org/db/conf/nips/nips2019.html',
        'https://dblp.org/db/conf/nips/nips2018.html',
        'https://dblp.org/db/conf/nips/nips2017.html',
        'https://dblp.org/db/conf/nips/nips2016.html',
        'https://dblp.org/db/conf/nips/nips2015.html',
        'https://dblp.org/db/conf/nips/nips2014.html',
        'https://dblp.org/db/conf/nips/nips2013.html',
        'https://dblp.org/db/conf/nips/nips2012.html',
        'https://dblp.org/db/conf/nips/nips2011.html',
        'https://dblp.org/db/conf/nips/nips2010.html',
        'https://dblp.org/db/conf/nips/nips2009.html',
        'https://dblp.org/db/conf/nips/nips2008.html',
        'https://dblp.org/db/conf/nips/nips2007.html',
        'https://dblp.org/db/conf/nips/nips2006.html',
        'https://dblp.org/db/conf/nips/nips2005.html',
        'https://dblp.org/db/conf/nips/nips2004.html',
        'https://dblp.org/db/conf/nips/nips2003.html',
        'https://dblp.org/db/conf/nips/nips2002.html',
        'https://dblp.org/db/conf/nips/nips2001.html',
        'https://dblp.org/db/conf/nips/nips2000.html',
        'https://dblp.org/db/conf/nips/nips1999.html',
        'https://dblp.org/db/conf/nips/nips1998.html',
        'https://dblp.org/db/conf/nips/nips1997.html',
        'https://dblp.org/db/conf/nips/nips1996.html',
        'https://dblp.org/db/conf/nips/nips1995.html',
        'https://dblp.org/db/conf/nips/nips1994.html',
        'https://dblp.org/db/conf/nips/nips1993.html',
        'https://dblp.org/db/conf/nips/nips1992.html',
        'https://dblp.org/db/conf/nips/nips1991.html',
        'https://dblp.org/db/conf/nips/nips1990.html',
        'https://dblp.org/db/conf/nips/nips1989.html',
        'https://dblp.org/db/conf/nips/nips1988.html',
        'https://dblp.org/db/conf/nips/nips1987.html',
    ]

    def parse(self, response, **kwargs):
        # Obtain year of the conference
        year_expr = re.compile(r'\d+')
        conf_year = int(year_expr.findall(response.url)[0])
        # Conference name changed in 2017 from NIPS to NeurIPS
        if conf_year >= 2017:
            conf_name = f'NeurIPS {conf_year}'
        else:
            conf_name = f'NIPS {conf_year}'

        # Get all conference paper entries
        entries = response.xpath('//ul[@class="publ-list"]/li[@class="entry inproceedings"]')
        # dblp stores author in https://dblp.org/pid/xxx/xxxx.html format (numbers or letters, variable length),
        # so we need the middle xxx/xxxx part
        author_id_expr = re.compile(r'pid/(.+)\.html')

        paper_items = []
        for entry in entries:
            # Get the title and remove the period at the end
            title = entry.xpath('./cite/span[@class="title"]/text()').get()
            if title[-1] == '.':
                title = title[:-1]
            author_items = []

            authors = entry.xpath('./cite/span[@itemprop="author"]')

            for author in authors:
                author_name = author.xpath('./a/span/text()').get()
                # Some in some rare cases the author does not have a link, use a different strategy
                if author_name is None:
                    author_name = author.xpath('./span/text()').get()
                    author_id = None
                else:
                    author_id = author_id_expr.findall(author.xpath('./a/@href').get())[0]

                author_item = AuthorItem(author_name, None, None, author_id, None)
                author_items.append(author_item)

            paper_item = PaperItem(title, author_items)
            paper_items.append(paper_item)

        conf_item = ConferenceItem(conf_name, conf_year, paper_items)

        yield conf_item
