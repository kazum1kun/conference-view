from scrapy.crawler import CrawlerProcess

from conference_crawler.spiders.acm_spider import ACMSpider
from conference_crawler.spiders.ieee_spider import IeeeSpider
from tpc_crawler.spiders.sigcomm_tpc_spider import SigCommTpcSpider
from tpc_crawler.spiders.infocom_tpc_spider import InfocomTpcSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "infocom_tpc.json": {"format": "json"},
        },
    })

    process.crawl(InfocomTpcSpider)
    process.start()


if __name__ == '__main__':
    main()
