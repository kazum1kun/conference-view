from shutil import which
from scrapy.crawler import CrawlerProcess
from conference_crawler.spiders.conference_spider import MobicomACMSpider

# Unused, use scrapy crawl xxx instead

def main():

    process = CrawlerProcess(settings={
        # "FEEDS": {
        #     "new.json": {"format": "json"},
        # },
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy_selenium.SeleniumMiddleware': 800
        }
    })

    process.crawl(MobicomACMSpider)
    process.start()


if __name__ == '__main__':
    main()
