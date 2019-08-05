import collections
import json
import pickle
from importlib import resources
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.common import exceptions

from instruments.data.gibson import json as json_dir, html as html_dir
from instruments.webscrape.utils import ScraperABC


class FenderScraper(ScraperABC):
    def __init__(
            self,
            browser='Firefox',
            headless=True,
            json_file='fender_data.json',
        ):
        super().__init__(browser, headless, json_file, brand='fender')
    

    def _get_guitar_raw(self):
        shopping_url = urljoin(self._root_url, 'en-US/start')
        self._driver.get(shopping_url)

        main_menu = self._driver.find_element_by_id('main-menu-nav')
        anchors = main_menu.find_elements_by_tag_name('a')
        for category_href in [anchor.get_attribute('href') for anchor in anchors]:
            self._driver.get(category_href)

            #: load all listings
            while True:
                try:
                    button = (
                        self._driver
                            .find_element_by_id('show-more')
                            .find_element_by_tag_name('button')
                    )
                except exceptions.NoSuchElementException:
                    break
                else:
                    button.click()
            
            product_anchors = (
                self._driver
                    .find_element_by_class('product-grid')
                    .find_elements_by_class('link')
            )

            for href in [anchor.get_attribute('href') for anchor in anchors]:
                self._driver.get(href)
                html = self._driver.page_source
                yield (href, html)

            
    def _merge_parsed_data(self, url):
        pass