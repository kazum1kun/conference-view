from scrapy.crawler import CrawlerProcess

from tpc_crawler.spiders.infocom_tpc_spider import InfocomTpcSpider
from conference_crawler.spiders.dblp_spider import DblpSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "dblp.json": {"format": "json"},
        },
    })

    process.crawl(DblpSpider)
    process.start()


if __name__ == '__main__':
    main()
