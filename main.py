from scrapy.crawler import CrawlerProcess

from conference_crawler.spiders.acm_spider import ACMSpider
from conference_crawler.spiders.ieee_spider import IeeeSpider
from tpc_crawler.spiders.sigcomm_tpc_spider import SigCommTpcSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "sigcomm_tpc.json": {"format": "json"},
        },
    })

    process.crawl(SigCommTpcSpider)
    process.start()


if __name__ == '__main__':
    main()
