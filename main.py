from scrapy.crawler import CrawlerProcess

from conference_crawler.spiders.sigcomm_acm_spider import ACMSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        # "FEEDS": {
        #     "new.json": {"format": "json"},
        # },
    })

    process.crawl(ACMSpider)
    process.start()


if __name__ == '__main__':
    main()
