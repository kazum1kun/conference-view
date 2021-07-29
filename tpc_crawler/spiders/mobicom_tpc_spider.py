import re

import scrapy

from tpc_crawler.items import *


class MobiComTpcSpider(scrapy.Spider):
    name = 'mobicom_tpc_spider'

    start_urls = [
        # Mobicom with two-column table layout
        'https://sigmobile.org/mobicom/2021/committee.html',
        'https://sigmobile.org/mobicom/2020/committee.php',
        'https://sigmobile.org/mobicom/2019/committee.php',
        'https://sigmobile.org/mobicom/2018/committees.php',
        'https://sigmobile.org/mobicom/2017/committees.php',
        'https://sigmobile.org/mobicom/2016/committees.php',
        'https://sigmobile.org/mobicom/2015/committees.html',
        'https://sigmobile.org/mobicom/2014/committees.html',
        'https://sigmobile.org/mobicom/2013/committees.html',
        'https://sigmobile.org/mobicom/2012/committees.html',
        'https://sigmobile.org/mobicom/2011/committees.html',
        'https://sigmobile.org/mobicom/2010/committees.html',
        'https://sigmobile.org/mobicom/2008/committees.html',
        'https://sigmobile.org/mobicom/2007/committees.html',
        'https://sigmobile.org/mobicom/2006/committees.html',
        'https://sigmobile.org/mobicom/2005/committees.html',
        'https://sigmobile.org/mobicom/2004/committees.html',
        'https://sigmobile.org/mobicom/2003/committees.html',
        'https://sigmobile.org/mobicom/2000/committee.htm',
        # Mobicom 2009
        'https://sigmobile.org/mobicom/2009/committees.html',
        # Comma-separated values in older mobicom
        'https://sigmobile.org/mobicom/2002/procom/',
        'https://sigmobile.org/mobicom/2001/program.html',
        'https://sigmobile.org/mobicom/1998/committee.html',
        'https://sigmobile.org/mobicom/1997/committee.html',
        'https://sigmobile.org/mobicom/1996/mobicom96-prog.html',
        'https://sigmobile.org/mobicom/1995/program/committee.html',
    ]

    def parse(self, response, **kwargs):
        # Get the year of conference from url
        year_expr = re.compile(r'mobicom/(\d+)')
        conf_year = int(year_expr.findall(response.url)[0])

        if conf_year >= 2010 or 2008 >= conf_year >= 2003 or conf_year == 2000:
            tpc = self.parse_table(response, conf_year)
        elif conf_year == 2009 or conf_year == 1999:
            tpc = self.parse_parenthesis(response, conf_year)
        else:
            tpc = self.parse_comma(response, conf_year)

        # Remove the empty strings resulting from newline characters
        tpc = [member for member in tpc if member]
        yield TpcItem(ConferenceType.MOBICOM, conf_year, tpc)

    def parse_table(self, response, year):
        # Get the tpc list
        if year == 2021:
            tpc = response.css('table.tpct td a::text').getall()
        elif year == 2020 or year == 2019:
            tpc = response.xpath('//main/table[2]//a/text()').getall()
        elif 2018 >= year >= 2014:
            tpc = response.xpath('//center//center/table[5]//a/text()').getall()
            if year == 2016:
                tpc = [name.replace('\t', ' ') for name in tpc]
        elif year >= 2010:
            tpc = response.xpath('//center//center/table[5]//tr/td[1]/text()').getall()
            if year == 2011:
                tpc = [' '.join(name.split()) for name in tpc]
        elif year == 2008 or year == 2007:
            tpc = response.xpath('//center//center/table[3]//tr/td[1]/text()').getall()
        elif year == 2006:
            tpc = response.css('div#comm2 td p::text').getall()
        elif year == 2005:
            tpc = response.xpath('(//td[@class="plaintext"])[2]/table//tr/td[2]//text()').getall()
        elif year == 2004:
            tpc = response.xpath('//div[@class="text"]/table[4]//tr/td[1]/text()').getall()
            # The first name is not read in because of weird table formatting, add it manually
            tpc[0] = 'Arup Acharya'
        elif year == 2003:
            tpc = response.xpath('//div[@class="text"]/table[4]//tr/td[1]/text()').getall()
            tpc[0] = 'Prathima Agrawal'
        elif year == 2000:
            tpc = response.xpath('//table//table/tr/td[1]//text()').getall()
        else:
            tpc = []

        # Remove nicknames from the name list and clean extra whitespace
        tpc = [re.sub(r' \(.*\)', '', name.replace('&nbsp', '')).strip() for name in tpc]
        return tpc

    def parse_parenthesis(self, response, year):
        if year == 2009:
            tpc = response.xpath('(//tr[@valign="top"])[last()]//text()').getall()
        else:
            tpc = response.xpath('//center//table//tr/td[1 or 2]//text()').getall()
        tpc = [name.split('(')[0].strip() for name in tpc]
        return tpc

    def parse_comma(self, response, year):
        # Again weird structure... every entry is nested inside the other?
        if year == 2002:
            tpc = response.xpath('//font/text()').getall()[9:]
        elif year == 2001:
            tpc = response.xpath('//tr/td[2]/p/text()').getall()
        elif year == 1998:
            # Select 3rd and 5th columns in the TPC table
            tpc = response.xpath('//center/table[3]/tr[2]/td[3 or 5]/text()').getall()
        elif year == 1997:
            tpc = response.xpath('//tr[last()]/td[2 or 4]//text()').getall()
        elif year == 1996:
            tpc = response.xpath('//p/text()').getall()
        # Easier to do it manually
        elif year == 1995:
            tpc = [
                'Baruch Awerbuch',
                'B.R.Badrinath',
                'Ramon Caceres',
                'Steve Deering',
                'Dan Duchamp',
                'David Johnson',
                'Randy Katz',
                'Leonard Kleinrock',
                'Paul Leach',
                'Jean - Francois Mergen',
                'James O\'Toole',
                'Christos Papadimitriou',
                'Rafi Rom',
                'Nachum Shacham',
                'Jeff Vitter',
                'John Zahorjan',
            ]
        else:
            tpc = []

        # Remove author affiliation info from the names
        tpc = [name.split(',')[0].strip() for name in tpc]
        return tpc

