import collections
import json
import pickle
from importlib import resources
from urllib.parse import urlparse

from requests.compat import urljoin
from selenium import webdriver

from instruments.data.gibson import json as json_dir, html as html_dir


class GibsonScraper:
    def __init__(
            self,
            webdriver='Firefox',
            headless=True,
            json_file='gibson_data.json',
        ):
        self.webdriver = str(webdriver).title()
        self.headless = bool(headless)
        self.json_file = resources.path(json_dir, str(json_file))
        self._driver = None
        self._root_url = 'https://www.gibson.com/'


    def __enter__(self):
        options = getattr(webdriver, f'{self.webdriver}Options')()
        options.headless = self.headless
        self._driver = getattr(webdriver, self.webdriver)(options=options)


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._driver.close()


    def save_guitar_data(self):
        for url, html in self._get_guitar_raw:
            data = self._merge_parsed_data(url)

            with open(self.json_file, 'a') as fp:
                json.dump(data)
                fp.write('\n')

            html_file = resources.path(html_dir, f'{data['id']}.html')
            with open(html_file, 'w') as fp:
                fp.write(html)
    

    def _get_guitar_raw(self):
        self._driver.get(self._root_url)
        anchors = (
            self._driver
                .find_element_by_class_name('body-types')
                .find_elements_by_tag_name('a')
        )

        for body_type_href in [a.get_attribute('href') for a in anchors]:
            self._driver.get(body_type_href)
            anchors = (
                self._driver
                    .find_element_by_id('body-wrap')
                    .find_elements_by_tag_name('a')
            )
            hrefs = {
                anchor.get_attribute('href') for anchor in anchors
                if not anchor.get_attribute('class') == 'collection-link'
            }

            for href in hrefs:
                self._driver.get(href)
                yield (href, self._driver.page_source)


    def _merge_parsed_data(self, url):
        self._driver.get(url)

        id = urlparse(url).path.split('/')[2]

        image_data = self._parse_image_carousel()
        buying_data = self._parse_buying_options()
        product_data = self._parse_product_overview()
        related_data = self._parse_related_products()
        
        guitar_data = collections.ChainMap(
            dict(id=id, url=url), 
            image_data, 
            buying_data,
            product_data,
            related_data,
        )
        return dict(guitar_data)


    def _parse_image_carousel(self):
        image_urls = []
        carousel = self._driver.find_element_by_class_name('carousel-indicators')
        for item in carousel.find_elements_by_tag_name('li'):
            item.click()
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
        for label in orientation.find_elements_by_tag_name('label'):
            for anchor in finish_selector.find_elements_by_tag_name('a'):
                if 'disabled' in label.get_attribute('class'):
                    continue
                else:
                    label.click()
                    handedness = label.get_attribute('for')

                anchor.click()
                finish = anchor.get_attribute('title')
                price = buying_options.find_element_by_id('localized-price').text
                version = dict(handedness=handedness, finish=finish, price=price)
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
        related = (
            self._driver
                .find_element_by_class_name('related-treasure')
                .find_element_by_class_name('row')
        )

        related_products = []
        for anchor in related.find_elements_by_tag_name('a'):
            product, *_ = anchor.text.split('\n')
            related_products.append(product)
        
        related_data = dict(related_products=related_products)
        return related_data
