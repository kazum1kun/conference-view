from shutil import which
from scrapy.crawler import CrawlerProcess
from conference_crawler.spiders.conference_spider import OldMobicomSpider


def main():

    process = CrawlerProcess(settings={
        # "FEEDS": {
        #     "new.json": {"format": "json"},
        # },
    })

    process.crawl(OldMobicomSpider)
    process.start()


if __name__ == '__main__':
    main()
