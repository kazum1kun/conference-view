import scrapy as sp


class ConferenceSpider(sp.Spider):
    name = 'mobiconspider'
    start_urls = [
        'https://sigmobile.org/mobicom/2021/accepted.html'
    ]

    def parse(self, response, **kwargs):
        # Obtain individual papers
        for paper in response.css('div.acceptedpapers ul li'):
            yield {
                'title': paper.css('b::text').get(),
                'authors': paper.css('div::text').get()
            }