from scrapy.crawler import CrawlerProcess

from conference_crawler.spiders.acm_spider import ACMSpider
from conference_crawler.spiders.ieee_spider import IeeeSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        # "FEEDS": {
        #     "new.json": {"format": "json"},
        # },
    })

    process.crawl(IeeeSpider)
    process.start()


if __name__ == '__main__':
    main()
