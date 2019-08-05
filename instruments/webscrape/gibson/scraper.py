import collections
import json
import pickle
from importlib import resources
from urllib.parse import urlparse

from selenium import webdriver

# from instruments.data.gibson import json as json_dir, html as html_dir
from instruments.webscrape.utils import ScraperABC


class GibsonScraper(ScraperABC):
    def __init__(
            self,
            browser='Firefox',
            headless=True,
            json_file='gibson_data.json',
        ):
        super().__init__(browser, headless, json_file, brand='gibson')
    

    def _get_guitar_raw(self):
        self._driver.get(self._root_url)
        anchors = (
            self._driver
                .find_element_by_class_name('body-types')
                .find_elements_by_tag_name('a')
        )

        for category_href in [a.get_attribute('href') for a in anchors]:
            self._driver.get(category_href)
            product_anchors = (
                self._driver
                    .find_element_by_id('body-wrap')
                    .find_elements_by_tag_name('a')
            )
            hrefs = {
                anchor.get_attribute('href') for anchor in product_anchors
                if not anchor.get_attribute('class') == 'collection-link'
            }

            for href in hrefs:
                self._driver.get(href)
                html = self._driver.page_source  #TODO move html to _merged_parsed_data? avoid loading page 2x
                yield (href, html)


    def _merge_parsed_data(self, url):
        self._driver.get(url)

        id = urlparse(url).path.split('/')[2]

        buying_data = self._parse_buying_options()
        product_data = self._parse_product_overview()
        related_data = self._parse_related_products()
        
        guitar_data = collections.ChainMap(
            dict(id=id, url=url), 
            buying_data,
            product_data,
            related_data,
        )
        return dict(guitar_data)


    def _parse_image_carousel(self):
        image_urls = []
        carousel = self._driver.find_element_by_class_name('carousel-indicators')
        for image_item in carousel.find_elements_by_tag_name('li'):
            image_item.click()
            image_url = (
                self._driver
                    .find_element_by_class_name('active')
                    .find_element_by_tag_name('img')
                    .get_attribute('src')
            )
            image_urls.append(image_url)
        
        image_data = dict(image_urls=image_urls)
        return image_data


    def _parse_buying_options(self):
        #: refresh to ensure price is loaded
        self._driver.refresh()

        cart_options = self._driver.find_element_by_id('cart-options')
        model_name, headline = cart_options.find_element_by_tag_name('h2').text.split('\n')
        description = cart_options.find_element_by_tag_name('div').text
        
        buying_options = cart_options.find_element_by_id('ecomm-cta')
        orientation = buying_options.find_element_by_class_name('orientation')
        finish_selector = buying_options.find_element_by_class_name('finish-selector')

        versions = []
        for handedness_label in orientation.find_elements_by_tag_name('label'):
            for finish_anchor in finish_selector.find_elements_by_tag_name('a'):
                finish_anchor.click()
                if 'disabled' in handedness_label.get_attribute('class'):
                    continue
                else:
                    handedness_label.click()
                    handedness = handedness_label.get_attribute('for')

                finish = finish_anchor.get_attribute('title')
                price = buying_options.find_element_by_id('localized-price').text
                image_data = self._parse_image_carousel()

                version = dict(handedness=handedness, finish=finish, price=price)
                version.update(image_data)
                versions.append(version)
        
        buying_options_data = dict(
            model_name=model_name,
            headline=headline,
            description=description,
            version=versions,
        )
        return buying_options_data


    def _parse_product_overview(self):
        product_data = dict()
        product_overview = self._driver.find_element_by_id('product-overview')
        
        for section in product_overview.find_elements_by_class_name('spec-section'):
            section_data = dict()
            section_name = section.find_element_by_tag_name('h4').text

            for row in section.find_elements_by_class_name('spec-item'):
                label = row.find_element_by_class_name('spec-label').text
                value = row.find_element_by_class_name('spec-value').text
                section_data[label] = value
                
            product_data[section_name] = section_data

        return product_data


    def _parse_related_products(self):
        driver = self._get_driver()
        related = (driver.find_element_by_class_name('related-treasure')
                         .find_element_by_class_name('row'))
        related_products = []
        for product_anchor in related.find_elements_by_tag_name('a'):
            product, *_ = product_anchor.text.split('\n')
            related_products.append(product)
        
        related_data = dict(related_products=related_products)
        driver.close()
        return related_data


def main():
    gibson_scraper = GibsonScraper()
    with gibson_scraper:
        gibson_scraper.save_guitar_data()
