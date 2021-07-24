import scrapy
import logging
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

        logging.basicConfig(filename='ignored_articles.log', level=logging.DEBUG)
        super().__init__(**kwargs)

    start_urls = [
        'https://ieeexplore.ieee.org/xpl/conhome/1000359/all-proceedings'
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
    # def parse(self, response, **kwargs):
        self.driver.get(response.url)
        base_url = response.url

        # Wait until the page fully loads
        response = self.wait_for_page_load()

        # Conference year is hard to locate due to changing formats, but the "Publication Year" in the page should
        # be consistent with the year the conference is held
        conf_year = self.driver.find_element_by_css_selector('div.description div span').text.split(':')[1].strip()
        # For consistency we will just going to use "IEEE INFOCOM XXXX" as conference title
        conf_title = 'IEEE INFOCOM ' + conf_year
        conf_item = ConferenceItem(conf_title, int(conf_year), [])

        # Pass the fully loaded webpage back and resume normal processing
        self.parse_page(response, conf_item)

        # Some proceedings are broken into several "volumes" which also needs to be clicked through
        volumes = self.driver.find_elements_by_css_selector('div.volume-container div select option')
        if volumes:
            volume_nums = [volume.get_attribute('value') for volume in volumes]
            # Skip the first volume as this is already being parsed
            for vol_num in volume_nums[1:]:
                self.driver.get(f'{base_url}&isnumber={vol_num}')
                self.navigate_pages(conf_item, True)
        else:
            self.navigate_pages(conf_item, False)

        yield conf_item

    # Navigate down the pages, if there are any
    # If volume_mode is true, the current page will be parsed before it looks for the next page
    def navigate_pages(self, conf_item, volume_mode):
        if volume_mode:
            response = self.wait_for_page_load()
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
            response = self.wait_for_page_load()
            self.parse_page(response, conf_item)

    # The actual parsing is done in the Scrapy engine
    def parse_page(self, response: Selector, conf_item: ConferenceItem):
        papers = response.css('div.List-results-items')

        for paper in papers:
            # Extract paper information
            paper_title = paper.css('div.result-item div h2 a::text').get()
            # Check whether the entry is a valid paper (some can be committee list or forewords)
            # From observation, it seems that the entries with open access are not real papers, so safe to skip them
            # Some non-papers also don't have author information, which can be ignored
            if paper.css('span.icon-access-ephemera') or not paper.css('p.author'):
                self.logger.info(f'An article named {paper_title} was ignored')
                continue

            paper_item = PaperItem(paper_title, [])

            # Obtain the information of author(s) - note additional css selector necessary to prevent duplication
            for author in paper.css('div.result-item-align xpl-authors-name-list p.author span a'):
                author_name = author.css('a span::text').get()
                if author_name is None:
                    continue
                # In some cases the author might not have an IEEE id - in this case just leave it to None
                author_ieee_id = None
                if author.css('a').xpath('@href').re(r'\d+'):
                    # Extract author's IEEE ID (i.e. the number part in their profile link)
                    author_ieee_id = author.css('a').xpath('@href').re(r'\d+')[0]

                author_item = AuthorItem(author_name, None, author_ieee_id, None)
                paper_item.authors.append(author_item)
            conf_item.papers.append(paper_item)

    # An auxiliary function specific to IEEE websites that wait for items to load and return the resulting page
    # as Scrapy selector
    def wait_for_page_load(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'List-results-items'))
        )
        return scrapy.Selector(text=self.driver.page_source)
