import scrapy

from tpc_crawler.items import *


class SigCommTpcSpider(scrapy.Spider):
    name = 'sigcomm_tpc_spider'

    start_urls = [
        # New SIGCOMM
        'https://conferences.sigcomm.org/sigcomm/2021/tpc.html',
        'https://conferences.sigcomm.org/sigcomm/2020/tpc.html',
        'https://conferences.sigcomm.org/sigcomm/2019/tpc.html',
        'https://conferences.sigcomm.org/sigcomm/2018/tpc.html',
        'https://conferences.sigcomm.org/sigcomm/2017/tpc.html',
        'https://conferences.sigcomm.org/sigcomm/2016/pc.php',
        'https://conferences.sigcomm.org/sigcomm/2015/pc.php',
        'https://conferences.sigcomm.org/sigcomm/2014/pc.php',
        'https://conferences.sigcomm.org/sigcomm/2013/pclist.php'
        'https://conferences.sigcomm.org/sigcomm/2012/pclist.php'
        # Old SIGCOMM
        'https://conferences.sigcomm.org/sigcomm/2011/organization.php',
        'https://conferences.sigcomm.org/sigcomm/2010/organization.php',
        'https://conferences.sigcomm.org/sigcomm/2009/organization.php',
        'https://conferences.sigcomm.org/sigcomm/2008/organization.php',
        'https://conferences.sigcomm.org/sigcomm/2007/committee.html',
        # SIGCOMM 2006: using Archived page as the original is broken
        'https://web.archive.org/web/20151023052717/http://conferences.sigcomm.org/sigcomm/2006/?committees'
    ]

    def parse(self, response, **kwargs):
        # Get the year of conference
        conf_year = int(response.css('title::text').re(r'\d+')[0])

        if conf_year >= 2012:
            tpc = self.parse_new(response)
        elif conf_year >= 2007 or conf_year == 2005:
            tpc = self.parse_old(response)
        elif conf_year == 2006:
            tpc = self.parse_2006(response)
        elif conf_year == 2004:
            tpc = self.get_2004()
        else:
            tpc = self.parse_legacy(response)

        yield TpcItem(ConferenceType.SIGCOMM, int(conf_year), tpc)

    def parse_new(self, response):
        # Get the tpc list
        tpc = response.css('div.ui-block-a p::text').getall()
        # Clean the extra whitespace and newline around the pc names
        tpc = [name.strip() for name in tpc]
        return tpc

    def parse_old(self, response):
        # Get the table that tpc list resides in by selecting the table under the TPC/PC header
        tpc_table = response.xpath('//table[./preceding-sibling::h2[1]="Technical Program Committee"]')
        if not tpc_table:
            tpc_table = response.xpath('//table[./preceding-sibling::h2[1]="Program Committee"]')

        # Obtain the names by following the first column
        tpc = tpc_table.xpath('./tr/td[1]/text()').getall()
        # Special rule for 2005
        tpc_additional = tpc_table.xpath('./tr/td[3]/text()').getall()
        if tpc_additional:
            tpc.extend(tpc_additional)
        return tpc

    def parse_2006(self, response):
        # Get the table that tpc list resides in by selecting the third table
        tpc = response.xpath('//table[@class="committee"][3]//tr/td[1]/text()').getall()
        return tpc

    def get_2004(self):
        # Very weird HTML markup... in fact it's so cryptic it's easier to manually extract them
        return ['Mostafa Ammar',
                'Tom Anderson',
                'Paul Barford',
                'Bobby Bhattacharjee',
                'John Byers',
                'Ken Calvert',
                'Constantinos Dovrolis',
                'Anja Feldmann',
                'Lixin Gao',
                'Ramesh Govindan',
                'Eddie Kohler',
                'Jorg Liebeherr',
                'Jay Lepreau',
                'Steven Low',
                'Steve McCanne',
                'Michael Mitzenmacher',
                'Robert Morris',
                'Venkat Padmanabhan',
                'Christos Papadopoulos',
                'Craig Partridge',
                'Vern Paxson',
                'Jim Roberts',
                'Antony Rowstron',
                'Dan Rubenstein',
                'Srini Seshan',
                'Alex Snoeren',
                'R. Srikant',
                'Ion Stoica',
                'Nina Taft',
                'Jon Turner',
                'Yin Zhang',
                'Zhi-li Zhang',]

    def parse_(self, response):
        # Obtain the list of TPC members
        tpc_list = response.xpath('//td/p[2]/text()').getall()
        # Remove the affiliation info from the author
        tpc = [member.split(',')[0].strip() for member in tpc_list]
        # Remove the empty strings resulting from newline characters
        tpc = [member for member in tpc if member]

        return tpc

