import time

import scrapy
from selenium import webdriver

from conference_crawler.items import *


# For Mobicom the information is more readily accessed in the ACM page on the conference proceedings
class MobicomACMSpider(scrapy.Spider):
    name = 'sigcommacmspider'

    def __init__(self, **kwargs):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        # Window size necessary to make sure additional authors don't get hidden
        chrome_options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        super().__init__(**kwargs)

    start_urls = [
        'https://dl.acm.org/doi/proceedings/10.1145/319056',  # '85
        'https://dl.acm.org/doi/proceedings/10.1145/18172',
        'https://dl.acm.org/doi/proceedings/10.1145/55482',
        'https://dl.acm.org/doi/proceedings/10.1145/52324',
        'https://dl.acm.org/doi/proceedings/10.1145/75246',
        'https://dl.acm.org/doi/proceedings/10.1145/99508',  # '90
        'https://dl.acm.org/doi/proceedings/10.1145/115992',
        'https://dl.acm.org/doi/proceedings/10.1145/144179',
        'https://dl.acm.org/doi/proceedings/10.1145/166237',
        'https://dl.acm.org/doi/proceedings/10.1145/190314',
        'https://dl.acm.org/doi/proceedings/10.1145/217382',  # '95
        'https://dl.acm.org/doi/proceedings/10.1145/248156',
        'https://dl.acm.org/doi/proceedings/10.1145/263105',
        'https://dl.acm.org/doi/proceedings/10.1145/285237',
        'https://dl.acm.org/doi/proceedings/10.1145/316188',
        'https://dl.acm.org/doi/proceedings/10.1145/347059',  # '00
        'https://dl.acm.org/doi/proceedings/10.1145/383059',
        'https://dl.acm.org/doi/proceedings/10.1145/633025',
        'https://dl.acm.org/doi/proceedings/10.1145/1015467',
        'https://dl.acm.org/doi/proceedings/10.1145/1080091',  # '05
        'https://dl.acm.org/doi/proceedings/10.1145/1159913',
        'https://dl.acm.org/doi/proceedings/10.1145/1282380',
        'https://dl.acm.org/doi/proceedings/10.1145/1402958',
        'https://dl.acm.org/doi/proceedings/10.1145/1592568',
        'https://dl.acm.org/doi/proceedings/10.1145/1851182',  # '10
        'https://dl.acm.org/doi/proceedings/10.1145/2018436',
        'https://dl.acm.org/doi/proceedings/10.1145/2342356',
        'https://dl.acm.org/doi/proceedings/10.1145/2486001',
        'https://dl.acm.org/doi/proceedings/10.1145/2619239',
        'https://dl.acm.org/doi/proceedings/10.1145/2785956',  # '15
        'https://dl.acm.org/doi/proceedings/10.1145/2934872',
        'https://dl.acm.org/doi/proceedings/10.1145/3098822',
        'https://dl.acm.org/doi/proceedings/10.1145/3230543',
        'https://dl.acm.org/doi/proceedings/10.1145/3341302',
        'https://dl.acm.org/doi/proceedings/10.1145/3387514',
    ]

    def parse(self, response, **kwargs):
        # Use selenium driver to further interact with the page
        self.driver.get(response.url)

        # Obtain the session headers and click on them as these are lazy-loaded
        session_headers = self.driver.find_elements_by_css_selector('div.table-of-content div div.accordion div '
                                                                    'div.toc__section a.section__title')
        # No need to click the first header - always loaded on page load
        session_headers = session_headers[1:]

        # Workaround for a known bug (https://github.com/clemfromspace/scrapy-selenium/issues/22) where meta driver url
        # is not in sync with the response url due to the single threaded nature of the selenium driver
        if session_headers:
            for header in session_headers:
                # We have to use js to emulate a click because click() function doesn't work properly
                self.driver.execute_script('arguments[0].click();', header)

        # Some pages have a "Show All" button that must be clicked to show the entire proceeding page
        show_all = self.driver.find_elements_by_css_selector('button.showAllProceedings')
        if show_all:
            see_more_count = len(self.driver.find_elements_by_css_selector('div.see_more'))
            list_bottom = self.driver.find_elements_by_css_selector('ol.organizational-chart')
            show_all[0].click()
            while True:
                # Some docs requires multiple loads - when additional "see_more" div is present
                self.driver.execute_script('arguments[0].scrollIntoView(true)', list_bottom[0])
                new_see_more_count = len(self.driver.find_elements_by_css_selector('div.see_more'))
                # Scroll to bottom of the list to make sure the list fully loads
                if new_see_more_count <= see_more_count:
                    break
                see_more_count = new_see_more_count

        # Wait for 3 secs to make sure lazy-loaded contents are rendered fully
        time.sleep(3)
        # Pass the updated webpage back and resume normal processing
        response = scrapy.Selector(text=self.driver.page_source)

        # Get the title and the year year of the conference
        # Example title: MobiCom '18: Proceedings of the 24th Annual..., where the first part is used
        conf_title = response.css('div.left-bordered-title span::text').get().split(':')[0]
        conf_year = response.css('div.coverDate::text').get()
        conf_item = ConferenceItem(conf_title, int(conf_year), [])

        # Special rule for SIGCOMM 19: opening words are labeled as "article" and the actual is "research-article"
        # Scan ~10 items to check if it's the case and proceed to special treatment if so
        papers = response.css('div.issue-item')
        special = False
        for paper in papers[:10]:
            article = False
            research_article = False
            paper_type = paper.css('div.issue-item__citation div.issue-heading::text').get().lower()
            if paper_type == 'article':
                article = True
            elif paper_type == 'research-article':
                research_article = True
            if article and research_article:
                special = True

        # Obtain divs of individual papers
        for paper in papers:
            # Check if the div contains the types of paper we wanted
            paper_type = paper.css('div.issue-item__citation div.issue-heading::text').get().lower()

            if paper_type != 'research-article' and (paper_type != 'article' or special):
                continue

            # Remove whitespaces and newline in the title
            paper_title = ' '.join(paper.css('div div h5 a::text').get().split())
            paper_item = PaperItem(paper_title, [])

            # Obtain the information of author(s)
            for author in paper.css('div div').xpath('./ul[@aria-label="authors"]').css('li'):
                author_name = author.css('a span::text').get()
                if author_name is None:
                    continue
                author_acm_id = author.css('a').xpath('@href').re(r'\d+')[0]

                author_item = AuthorItem(author_name, author_acm_id, None, None)
                paper_item.authors.append(author_item)
            conf_item.papers.append(paper_item)

        yield conf_item

    # def parse_author_affiliations(self, response):
    #     partial_author = response.meta['partial_author']
    #     institutions = response.css('ul.list-of-institutions li a::text').getall()
    #     partial_author.affiliations = institutions
    #     yield partial_author
