import scrapy
from scrapy import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conference_crawler.items import *


class InfocomIeeeSpider(scrapy.Spider):
    name = 'infocomieeespider'

    def __init__(self, **kwargs):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        # Window size necessary to make sure additional authors don't get hidden
        chrome_options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        super().__init__(**kwargs)

    start_urls = [
        # 'https://ieeexplore.ieee.org/xpl/conhome/1000359/all-proceedings'
        'https://ieeexplore.ieee.org/xpl/conhome/7172813/proceeding?rowsPerPage=100'
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # First, proceeding pages from each year and parse them individually
    def parse(self, response, **kwargs):
        # Extract
        self.driver.get(response.url)
        # Wait to make sure the page fully loads
        links_a = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div ul.conference-records li a'))
        )
        links = [link.get_attribute('href') for link in links_a]

        for link in links:
            # Increase the rows displayed per page to 100, which reduces the pages we need to follow
            yield scrapy.Request(url=link + '?rowsPerPage=100', callback=self.parse_conference)

    # Then, use Selenium to load the proceeding page and handle pagination
    def parse_conference(self, response, **kwargs):
        self.driver.get(response.url)

        # Wait until the page fully loads
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'List-results-items'))
        )

        # Conference year is hard to locate due to changing formats, but the "Publication Year" in the page should
        # be consistent with the year the conference is held
        conf_year = self.driver.find_element_by_css_selector('div.description div span').text.split(':')[1].strip()
        # For consistency we will just going to use "IEEE INFOCOM XXXX" as conference title
        conf_title = 'IEEE INFOCOM ' + conf_year
        conf_item = ConferenceItem(conf_title, int(conf_year), [])

        # Pass the fully loaded webpage back and resume normal processing
        response = scrapy.Selector(text=self.driver.page_source)
        self.parse_page(response, conf_item)

        # Follow the pagination to obtain all papers, until the "next page" arrow no longer exists, which indicates
        # we have reached the last page
        while True:
            try:
                next_btn = self.driver.find_element_by_css_selector('li.next-btn a')
            except NoSuchElementException as e:
                break
            # Emulate a click on the next button
            self.driver.execute_script('arguments[0].click()', next_btn)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'List-results-items'))
            )

            response = scrapy.Selector(text=self.driver.page_source)
            self.parse_page(response, conf_item)

        yield conf_item

    # The actual parsing is done in the Scrapy engine
    def parse_page(self, response: Selector, conf_item: ConferenceItem):
        papers = response.css('div.List-results-items')

        for paper in papers:
            # Check whether the entry is a valid paper (some can be committee list or forewords)
            if not paper.css('p.author'):
                continue

            # Extract paper information
            paper_title = paper.css('div.result-item div h2 a::text').get()
            paper_item = PaperItem(paper_title, [])

            # Obtain the information of author(s)
            for author in paper.css('div.result-item-align xpl-authors-name-list p.author span a'):
                author_name = author.css('a span::text').get()
                if author_name is None:
                    continue
                author_ieee_id = author.css('a').xpath('@href').re(r'\d+')[0]

                author_item = AuthorItem(author_name, None, author_ieee_id, None)
                paper_item.authors.append(author_item)
            conf_item.papers.append(paper_item)
