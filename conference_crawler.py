import scrapy as sp


class ConferenceSpider(sp.Spider):
    name = 'mobiconspider'
    start_urls = [
        'https://sigmobile.org/mobicom/2021/accepted.html',
        'https://sigmobile.org/mobicom/2020/accepted.php',
        'https://sigmobile.org/mobicom/2019/accepted.php',
    ]

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