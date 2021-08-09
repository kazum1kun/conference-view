from scrapy.crawler import CrawlerProcess

from tpc_crawler.spiders.infocom_tpc_spider import InfocomTpcSpider


# Unused, use scrapy crawl xxx instead


def main():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "infoconm_tpc.json": {"format": "json"},
        },
    })

    process.crawl(InfocomTpcSpider)
    process.start()


if __name__ == '__main__':
    main()
