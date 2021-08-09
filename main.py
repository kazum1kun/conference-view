from scrapy.crawler import CrawlerProcess

from conference_crawler.spiders.acm_spider import ACMSpider
from tpc_crawler.spiders.kdd_tpc_spider import KddTpcSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "kdd_tpc.json": {"format": "json"},
        },
    })

    process.crawl(KddTpcSpider)
    process.start()


if __name__ == '__main__':
    main()
