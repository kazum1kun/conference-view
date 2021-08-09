import re

import scrapy


from tpc_crawler.items import *


class NipsTpcSpider(scrapy.Spider):
    name = 'nips_tpc_spider'

    start_urls = [
        # No postprocessing needed
        'https://nips.cc/Conferences/2020/ProgramCommittee',
        'https://nips.cc/Conferences/2019/Reviewers',
        'https://nips.cc/Conferences/2018/Reviewers',
        'https://nips.cc/Conferences/2017/Reviewers',
        'https://nips.cc/Conferences/2016/Reviewers',
        'https://nips.cc/Conferences/2006/Committees',
        'https://nips.cc/Conferences/2005/Committees',
        'https://web.archive.org/web/20050825055135/http://nips.cc/Conferences/2004/Committees/',
        'https://web.archive.org/web/20040312001920/http://nips.cc/Conferences/2003/Committees/',

        # Author (Institution) format
        'https://nips.cc/Conferences/2015/Committees',
        'https://nips.cc/Conferences/2014/Committees',
        'https://nips.cc/Conferences/2013/Committees',
        'https://nips.cc/Conferences/2012/Committees',
        'https://nips.cc/Conferences/2011/Committees',
        'https://nips.cc/Conferences/2010/Committees',
        'https://nips.cc/Conferences/2009/Committees',
        'https://nips.cc/Conferences/2008/Committees',
        'https://nips.cc/Conferences/2007/Committees',

        # Author, Institution format
        'https://web.archive.org/web/20061129204303/http://nips.cc/Conferences/2002',
        'https://web.archive.org/web/20061210003740/http://nips.cc/Conferences/2001',
        'https://web.archive.org/web/20061129204322/http://www.nips.cc/Conferences/2000/',
    ]

    def parse(self, response, **kwargs):
        # Get the year of conference from url
        year_expr = re.compile(r'Conferences/(\d+)')
        conf_year = int(year_expr.findall(response.url)[0])

        if conf_year >= 2016 or 2006 >= conf_year >= 2003:
            tpc = self.parse_normal(response, conf_year)
        elif 2015 >= conf_year >= 2007:
            tpc = self.pase_parenthesis(response, conf_year)
        elif conf_year >= 2000:
            tpc = self.parse_comma(response, conf_year)
        else:
            tpc = []

        # Final cleanup (remove the nickname and whitespaces)
        tpc = [re.sub(r' \(.*\)', '', name).strip() for name in tpc]
        tpc = [name for name in tpc if name]

        # Account for the name change in 2017
        if conf_year >= 2017:
            conf_type = ConferenceType.NEURIPS
        else:
            conf_type = ConferenceType.NIPS

        yield TpcItem(conf_type, conf_year, tpc)

    def parse_normal(self, response, year):
        if year == 2020:
            # Select all elements under "2020 Reviewers"
            tpc = response.xpath('//div[preceding::h3[.="2020 Reviewers"]]/text()').getall()[:-2]
        elif year == 2019:
            tpc = response.xpath('//div[preceding::div/h2[.="2019 All Reviewers"]]/text()').getall()[:-2]
        elif year == 2018:
            tpc = response.xpath('//div[preceding::div/h3[.="All Reviewers"]]/text()').getall()[:-2]
        elif year == 2017:
            tpc = response.css('div.reviewer-block::text').getall()
        elif year == 2016:
            tpc = response.css('div.col-md-4::text').getall()
        elif year == 2006:
            tpc = response.xpath('//main//p[preceding::p/span]/text()').getall()
            # Python magic...
            # First we select one every 3 elements from the list (since the list has the pattern [name, institution, \n]
            # and we only cares about the name
            # Notation-wise, [start:stop:step] but by default they take the whole length of list, so we only need to
            # specify the start (so the first '\n' is skipped) and step size
            # Then, remove the first name as we don't want to include the PC chair
            tpc = tpc[1::3][1:]
        elif year == 2005:
            tpc = response.xpath('//main//div[preceding::div/h4[.="NIPS 2005 Program Committee"]]/text()').getall()
            tpc = tpc[3::3]
        elif year == 2004:
            tpc = response.xpath('//div[@class="Section1"]/p[preceding::p/b/span[.="Members"]]//text()').getall()
            tpc = tpc[:29:3] + tpc[31::3]
            # Some names contain a new line for no reason
            tpc = [name.replace('\n', ' ') for name in tpc]
        elif year == 2003:
            tpc = response.xpath('//div[@class="Section1"]/p[preceding::h5/span[.="Chair"]]//text()').getall()
            tpc = tpc[3:16:3] + tpc[19::3]
        else:
            tpc = []

        return tpc

    def pase_parenthesis(self, response, year):
        if year == 2015:
            tpc = response.css('div.container div.container div::text').getall()
        elif year >= 2011 or year == 2009:
            tpc = response.xpath('//main//p[last()]/text()').getall()
        elif year == 2010:
            tpc = response.xpath('//main//p[last() - 2]/text()').getall()
        elif year == 2008:
            tpc = response.xpath('//main//p[last()]/text()').getall()[1:]
        elif year == 2007:
            tpc = response.xpath('//main//p[last() - 1]/text()').getall()[1:]
        else:
            tpc = []

        tpc = [name.split('(')[0].strip() for name in tpc]
        return tpc

    def parse_comma(self, response, year):
        if year == 2002:
            # Select the entries between PC header and Webmasters header
            # Note: the website is kinda messed up, these texts have the same color as the background
            tpc = response.xpath('//tr[preceding::tr//b[.="Program Committee"] '
                                 'and following::tr//b[.="Webmasters"]]//text()').getall()[3:]
        elif year == 2001 or year == 2000:
            # Everything is meshed in one big block, need to unpack first
            tpc = response.css('blockquote::text').get()
            tpc = tpc.split(';')[1:]
        else:
            tpc = []

        tpc = [name.split(',')[0] for name in tpc]
        return tpc