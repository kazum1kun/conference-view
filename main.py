from shutil import which
from scrapy.crawler import CrawlerProcess
from conference_crawler import MobicomSpider, OldMobicomSpider


def main():

    process = CrawlerProcess(settings={
        "FEEDS": {
            "new.json": {"format": "json"},
        },
    })

    process.crawl(MobicomSpider)
    process.start()


if __name__ == '__main__':
    main()
