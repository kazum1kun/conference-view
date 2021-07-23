from scrapy.crawler import CrawlerProcess

from conference_crawler.spiders.mobicom_acm_spider import MobicomACMSpider
from conference_crawler.spiders.infocom_ieee_spider import InfocomIeeeSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        # "FEEDS": {
        #     "new.json": {"format": "json"},
        # },
    })

    process.crawl(InfocomIeeeSpider)
    process.start()


if __name__ == '__main__':
    main()
