from scrapy.crawler import CrawlerProcess

from tpc_crawler.spiders.infocom_tpc_spider import InfocomTpcSpider
from tpc_crawler.spiders.mobicom_tpc_spider import MobiComTpcSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "mobicom_tpc.json": {"format": "json"},
        },
    })

    process.crawl(MobiComTpcSpider)
    process.start()


if __name__ == '__main__':
    main()
