import scrapy as sp
from scrapy.crawler import CrawlerProcess

from conference_crawler import MobicomSpider, OldMobicomSpider


def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "mobicom.json": {"format": "json"},
        },
    })

    process.crawl(OldMobicomSpider)
    process.start()


if __name__ == '__main__':
    main()
