from scrapy.crawler import CrawlerProcess

from conference_crawler.spiders.sigcomm_acm_spider import SigcommACMSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        # "FEEDS": {
        #     "new.json": {"format": "json"},
        # },
    })

    process.crawl(SigcommACMSpider)
    process.start()


if __name__ == '__main__':
    main()
