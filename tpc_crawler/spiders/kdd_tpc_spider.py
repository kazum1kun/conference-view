import re

import scrapy

from tpc_crawler.items import *


class KddTpcSpider(scrapy.Spider):
    name = 'kdd_tpc_spider'

    start_urls = [
        # Directly obtain author name - no processing needed
        # New KDD website using div p selectors (two webpages per year)
        'https://www.kdd.org/kdd2020/organizers/research-track-program-committee',
        'https://www.kdd.org/kdd2020/organizers/ads-track-program-committee',
        # Information for KDD 2019 is gone, 404 on the official website and Internet Archive only has broken ones
        'https://www.kdd.org/kdd2018/about/research-track-program-committee',
        'https://www.kdd.org/kdd2018/about/applied-data-science-program-committee',
        'https://www.kdd.org/kdd2017/organizers/program-committees/research-track-program-committee-members',
        'https://www.kdd.org/kdd2017/organizers/program-committees/applied-data-science-program-track-committee-members',
        # No information can be found on KDD 2016 committee members after a through search of the website
        # Picture format section p selection
        'https://www.kdd.org/kdd2014/organizers.html',
        # Table format
        'https://www.kdd.org/kdd2013/senior-program-committee',
        'https://www.kdd.org/kdd2013/program-committee',
        'https://www.kdd.org/kdd2013/industrial-government-committee',
        # Older webpages
        'https://web.archive.org/web/20040218104422/http://www.acm.org/sigs/sigkdd/kdd2002/pc.html',
        'https://web.archive.org/web/20040218165309/http://www.acm.org/sigs/sigkdd/kdd2000/KDD2000-PC.htm',

        # Author (Institution) format
        'https://www.kdd.org/kdd2015/organizers.html',
        'http://kdd2012.sigkdd.org/pc_research.shtml',
        'http://kdd2012.sigkdd.org/pc_industry.shtml',
        'http://www.kdd2008.com/rpc.html',
        'http://www.kdd2008.com/ipc.html',
        'https://web.archive.org/web/20071116143232/http://www.kdd2007.com/organizers.html',

        # Author, Institution format
        'https://www.kdd.org/kdd2011/pc_research.shtml',
        'https://www.kdd.org/kdd2011/pc_industry.shtml',
        'http://www.kdd2006.com/organizers.html',
        'https://web.archive.org/web/20040124113432/http://www.acm.org/sigkdd/kdd2003/pc.html',
        'https://web.archive.org/web/20040404092720/http://www.acm.org/sigkdd/kdd2003/it-gov-pc.html',
        'https://web.archive.org/web/20031230205239/http://www.acm.org/sigkdd/kdd2001/pc.html',

        # Table (require postprocessing)
        'https://web.archive.org/web/20110115030359/http://www.kdd.org/kdd2010/organizers_research.shtml',
        'https://web.archive.org/web/20110115030345/http://www.kdd.org/kdd2010/organizers_industrial.shtml'
        'https://web.archive.org/web/20110817130757fw_/http://www.kdd.org/kdd/2009/rpc.html',
        'https://web.archive.org/web/20110817130802fw_/http://www.kdd.org/kdd/2009/ipc.html',

        # Last, First - Institution format
        'https://web.archive.org/web/20060619100428/http://www.acm.org/sigs/sigkdd/kdd2005/organizers.html',
        'https://web.archive.org/web/20061022100555/http://www.acm.org/sigs/sigkdd/kdd2004/organizers.html',
    ]

    def parse(self, response, **kwargs):
        # Get the year of conference from url
        year_expr = re.compile(r'kdd/*(\d+)')
        conf_year = int(year_expr.findall(response.url)[0])

        if conf_year >= 2017 or conf_year == 2014 or conf_year == 2013 or conf_year == 2002 or conf_year == 2000:
            tpc = self.parse_normal(response, conf_year)
        elif conf_year == 2015 or conf_year == 2012 or conf_year == 2008 or conf_year == 2007:
            tpc = self.parse_parenthesis(response, conf_year)
        elif conf_year == 2011 or conf_year == 2006 or conf_year == 2003 or conf_year == 2001:
            tpc = self.parse_comma(response, conf_year)
        elif conf_year == 2010 or conf_year == 2009:
            tpc = self.parse_table(response, conf_year)
        elif conf_year == 2005 or conf_year == 2004:
            tpc = self.parse_comma_reverse(response, conf_year)
        else:
            tpc = []

        # Final cleanup (remove the nickname and whitespaces)
        tpc = [re.sub(r' \(.*\)', '', name).strip() for name in tpc]
        tpc = [name for name in tpc if name]

        yield TpcItem(ConferenceType.KDD, conf_year, tpc)

    def parse_normal(self, response, year):
        if year >= 2018:
            tpc = response.css('div.container p strong::text').getall()
        elif year == 2017:
            tpc = response.css('div.entry-content p b::text').getall()
        elif year == 2014:
            tpc = response.xpath('//div[@role="main"]/section[position()>1]//p/strong/text()').getall()
        elif year == 2013:
            tpc = response.css('td.name_block a::text').getall()
        elif year == 2002:
            tpc = response.xpath('//table//table[1]//tr/td[1]/text()').getall()
        elif year == 2000:
            tpc = response.css('p.MsoNormal b span::text').getall()
        else:
            tpc = []
        return tpc

    def parse_parenthesis(self, response, year):
        # Get the list of TPC members
        if year == 2015:
            # The TPC members are in the 2nd-5th sections
            tpc = response.xpath('//div[@role="main"]/section[position()>1]//p/text()').getall()
            # Website contains an error, easier to just replace here
            tpc[4] = 'Arno Siebes'
        elif year == 2012:
            tpc = response.css('div.introText ul li::text').getall()
        elif year == 2008:
            tpc = response.css('table.content li::text').getall()
        elif year == 2007:
            tpc = response.css('td.pcCommittee li::text').getall()
        else:
            tpc = []

        tpc = [name.split('(')[0].strip() for name in tpc]

        return tpc

    def parse_comma(self, response, year):
        if year == 2011:
            tpc = response.css('div.introText ul li::text').getall()
            if not tpc:
                # The other webpage uses a slightly different layout
                tpc = response.css('div.content ul li::text').getall()
        elif year == 2006:
            # Filter Awards committee out
            tpc = response.css('td.pcName li::text').getall()[8:]
        elif year == 2003:
            tpc = response.css('body::text').getall()
        elif year == 2001:
            tpc = response.xpath('//body/table/tr/td[3]/font/text()').getall()
        else:
            tpc = []

        tpc = [name.split(',')[0].strip() for name in tpc]
        return tpc

    def parse_table(self, response, year):
        if year == 2010:
            tpc = response.xpath('//div[@class="introText"]//tr/td[1]/text()').getall()
        elif year == 2009:
            tpc = response.xpath('//table[@class="content"]//table//tr/td[1]/text()').getall()
        else:
            tpc = []

        # Replace the \xa0 character
        tpc = [name.replace('\xa0', ' ') for name in tpc]
        return tpc

    def parse_comma_reverse(self, response, year):
        name_expr = re.compile('(.+)-.+$')
        if year == 2005:
            tpc = response.xpath('//tr[@class="contents"]/td/table[position()>2]//li/text()').getall()
            tpc = [name_expr.findall(name)[0] for name in tpc if '-' in name]
        elif year == 2004:
            tpc = response.xpath('//td[@class="content"]/ul/li/text()').getall()
            tpc = [name_expr.findall(name.strip())[0] for name in tpc if '-' in name]
        else:
            tpc = []
        # Get rid of the affiliation info first (note that some names contain dash so we want to make sure it doesn't
        # get accidentally removed, thus we want to use a regex for that

        # All names are Last, First and some has missing/extra whitespaces, hence needing to clean the names first
        # Oddly in 2004 some are mixed up with normal ordering, so a detection is added in such a case
        tpc = [' '.join(name.strip().replace(' ', '').split(',')[::-1]) if ',' in name else name for name in tpc]
        return tpc
