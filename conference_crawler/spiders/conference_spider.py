import time

import scrapy
from selenium import webdriver

from conference_crawler.items import *


# For Mobicom the information is more readily accessed in the ACM page on the conference proceedings
class MobicomACMSpider(scrapy.Spider):
    name = 'mobicomacmspider'

    def __init__(self, **kwargs):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        # Window size necessary to make sure additional authors don't get hidden
        chrome_options.add_argument('--window-size=1920,1080')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        super().__init__(**kwargs)

    start_urls = [
        'https://dl.acm.org/doi/proceedings/10.1145/215530',  # '95
        'https://dl.acm.org/doi/proceedings/10.1145/236387',
        'https://dl.acm.org/doi/proceedings/10.1145/262116',
        'https://dl.acm.org/doi/proceedings/10.1145/288235',
        'https://dl.acm.org/doi/proceedings/10.1145/313451',
        'https://dl.acm.org/doi/proceedings/10.1145/345910',  # '00
        'https://dl.acm.org/doi/proceedings/10.1145/381677',
        'https://dl.acm.org/doi/proceedings/10.1145/570645',
        'https://dl.acm.org/doi/proceedings/10.1145/938985',
        'https://dl.acm.org/doi/proceedings/10.1145/1023720',
        'https://dl.acm.org/doi/proceedings/10.1145/1080829',  # '05
        'https://dl.acm.org/doi/proceedings/10.1145/1161089',
        'https://dl.acm.org/doi/proceedings/10.1145/1287853',
        'https://dl.acm.org/doi/proceedings/10.1145/1409944',
        'https://dl.acm.org/doi/proceedings/10.1145/1614320',
        'https://dl.acm.org/doi/proceedings/10.1145/1859995',  # '10
        'https://dl.acm.org/doi/proceedings/10.1145/2030613',
        'https://dl.acm.org/doi/proceedings/10.1145/2348543',
        'https://dl.acm.org/doi/proceedings/10.1145/2500423',
        'https://dl.acm.org/doi/proceedings/10.1145/2639108',
        'https://dl.acm.org/doi/proceedings/10.1145/2789168',  # '15
        'https://dl.acm.org/doi/proceedings/10.1145/2973750',
        'https://dl.acm.org/doi/proceedings/10.1145/3117811',
        'https://dl.acm.org/doi/proceedings/10.1145/3241539',
        'https://dl.acm.org/doi/proceedings/10.1145/3300061',
        'https://dl.acm.org/doi/proceedings/10.1145/3372224',  # '20
        'https://dl.acm.org/doi/proceedings/10.1145/3447993',
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

        # Obtain divs of individual papers
        for paper in response.css('div.issue-item'):
            # Check if the div contains the types of paper we wanted
            paper_type = paper.css('div.issue-item__citation div.issue-heading::text').get().lower()
            if paper_type != 'article' and paper_type != 'research-article':
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
