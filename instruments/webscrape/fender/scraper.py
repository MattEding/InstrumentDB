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


    def _parse_image_carousel(self):
        image_urls = []
        thumbnails = (
            self._driver
                .find_element_by_class('thumbs')
                .find_elements_by_tag_name('li')    
        )
        for thumb in thumbnails:
            thumb.click()
            image = (
                self._driver
                    .find_element_by_class('mz-figure')
                    .find_element_by_tag_name('img')
                    .get_attribute('src')
            )

        # ul class:thumb
        # for li in ul -> click

        # img to dl tag:figure class:mz-figure
        # then to child img (first or second are the same)


    def _parse_price(self:
        # https://shop.fender.com/en-US/accessories/cables/original-series-instrument-cables/0990510058.html
        #   color & cable length

        # https://shop.fender.com/en-US/electric-guitars/telecaster/vintera-50s-telecaster/0149852340.html
        #   colorm & fingerboard material
        for ... in ...:
            image_urls = self._parse_image_carousel()
            price = (
                self._driver
                    .find_element_by_class('price')
                    .find_element_by_class('value')
                    .text
            )


    def _parse_misc(self):
        product_name = (
            self._driver
                .find_element_by_class('product-name')
                .text
        )
        id = (
            self._driver
                .find_element_by_class('product-id')
                .text
        )
        description = (
            self._driver
                .find_element_by_class('long-description')
                .text
        )
        feature_bullets = (
            self._driver
                .find_element_by_class('feature-bullets')
                .find_elements_by_tag_name('li')
        )
        features = [item.text for item in feature_bullets]


    def _parse_tabs(self):
        # guitars and amps have 
        #   highlights, specs, support
        # cables have
        #   specs, support
        #   dont have recommended
        # pedals have
        #   support
        #   dont have recommended

        highlights_tab, specs_tab, _ = (
            self._driver
                .find_element_by_class('nav-tabs')
                .find_elements_by_tag_name('li')
        )
        
        highlights_tab.click()
        highlights_items = (
            self._driver
                .find_element_by_id('tab-highlights')
                .find_elements_by_class('highlight-item')
        )
        highlights_data = dict()
        for row in highlights_rows:
            header = row.find_element_by_tag_name('h6').text
            image = row.find_element_by_tag_name('img').get_attribute('src')
            content = row.find_element_by_tag_name('p').text
            highlights_data[header] = dict(image=image, content=content)

        specs_tab.click()
        specifcations = (
            self._driver
                .find_element_by_id('tab-specs')
                .find_elements_by_class('specification')
        )
        specifcations_data = dict()
        for spec in specifcations:
            title = spec.find_element_by_class('title')
            attributes = spec.find_elements_by_tag_name('li')
            attributes_data = dict()

            for attr in attributes:
                label = attr.find_element_by_class('label')
                value = attr.find_element_by_class('value')
                attributes_data[label] = value

            specifcations_data[title] = attributes_data

    
    def _parse_recommended_gear(self):
        recommended = set()
        next_button = self._driver.find_element_by_class('slick-next')
        while not 'slick-disabled' in next_button.get_attribute('class'):
            products = (
                self._driver
                    .find_element_by_class('slick-track')
                    .find_elements_by_class('product-recommendation-list')
            )
            for product in products:
                id = (
                    product.find_element_by_tag_name('div')
                           .get_attribute('data-pid')
                )
                recommended.add(id)