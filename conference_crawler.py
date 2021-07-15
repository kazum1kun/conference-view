import os
import scrapy
from scrapy_selenium import SeleniumRequest

# For "modern" Mobicom website (2019+) with separated accepted paper page
class MobicomSpider(scrapy.Spider):
    name = 'mobiconspider'

    def start_requests(self):
        start_urls = [
            'https://sigmobile.org/mobicom/2021/accepted.html',
            'https://sigmobile.org/mobicom/2020/accepted.php',
            'https://sigmobile.org/mobicom/2019/accepted.php',
        ]

        for url in start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        # Get the year of the conference
        year = response.css('title::text').re(r'\d{4}')[0]

        # Obtain individual papers
        for paper in response.css('div.acceptedpapers ul li'):
            # Get the paper title and authors info
            yield {
                'year': year,
                'title': paper.css('b::text').get(),
                'authors': paper.css('div::text').get()
            }


# For "old" Mobicom the information is more readily accessed in the ACM page on the conference proceedings
class OldMobicomSpider(scrapy.Spider):
    name = 'oldmobiconspider'
    cwd = os.getcwd()
    start_urls = [
        'file:///C:/Users/kilve/PycharmProjects/ConferenceView/res/mobicom_acm/Proceedings of the 24th Annual International Conference on Mobile Computing and Networking _ ACM Conferences.html',
    ]

    def parse(self, response, **kwargs):
        # Get the year of the conference
        year = response.css('div.coverDate::text').get()

        # Obtain divs of individual papers
        for paper in response.css('div.issue-item'):
            # Check if the div contains the type of paper we wanted
            paper_type = paper.css('div.issue-item__citation div.issue-heading::text').get()
            if paper_type != 'article' and paper_type != 'research-article':
                continue

            authors = []
            # Obtain the information of author(s)
            for author in paper.css('div div').xpath('./ul[@aria-label="authors"]').css('li'):
                author_info = {
                    'name': author.css('a span::text').get(),
                    'profile_id': author.css('a').xpath('@href').re(r'\d+')[0],
                }
                authors.append(author_info)

            # Get the paper title and authors info
            yield {
                'year': year,
                'title': paper.css('div div h5 a::text').get(),
                'authors': authors
            }
