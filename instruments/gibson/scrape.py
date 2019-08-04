import requests
from requests.compat import urljoin

from selenium import webdriver
# from selenium.common import exceptions
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options


class GibsonScraper:
    def __init__(self, webdriver='Firefox', headless=True):
        self.driver = None
        self.webdriver = str(webdriver).title()
        self.headless = bool(headless)
        self.root_url = 'https://www.gibson.com/'
        # self.guitars_url = urljoin(self.root_url, 'Guitars')
        # self.guitar_url = urljoin(self.root_url, 'Guitar')
        self.custom_url = urljoin(self.root_url, 'Custom-Shop')

    def __enter__(self):
        options = get_attribute(webdriver, f'{self.webdriver}Options')()
        # options = webdriver.FirefoxOptions()
        options.headless = self.headless
        self.driver = get_attribute(webdriver, self.webdriver)(options=options)
        # self.driver = webdriver.Firefox(options=options)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.close()

    def get_guitar_htmls(self):
        self.driver.get(self.root_url)
        anchors = (
            self.driver
                .find_element_by_class_name('body-types')
                .find_elements_by_tag_name('a')
        )
        body_type_hrefs = [anchor.get_attribute('href') for anchor in anchors]

        for body_type_href in body_type_hrefs:
            self.driver.get(body_type_href)
            anchors = (
                self.driver
                    .find_element_by_id('body-wrap')
                    .find_elements_by_tag_name('a')
            )
            hrefs = {
                anchor.get_attribute('href') for anchor in anchors
                if not anchor.get_attribute('class') == 'collection-link'
            }

            for href in hrefs:
                self.driver.get(href)
                yield (href, self.driver.page_source)

    def parse_guitar_html(self, url):
        self.driver.get(url)

        image_urls = []
        carousel = self.driver.find_element_by_class_name('carousel-indicators')
        for li in carousel.find_elements_by_tag_name('li'):
            li.click()
            image_url = (
                self.driver
                    .find_element_by_class_name('active')
                    .find_element_by_tag_name('img')
                    .get_attribute('src')
            )
            image_urls.append(image_url)

        cart_options = self.driver.find_element_by_id('cart-options')
        model_name, headline = cart_options.find_element_by_tag_name('h2').text.split('\n')
        description = cart_options.find_element_by_tag_name('div').text

        Version = namedtuple('Version', 'handedness finish price')
        versions = []
        buying_options = cart_options.find_element_by_id('ecomm-cta')
        orientation = buying_options.find_element_by_class_name('orientation')
        finish_selector = buying_options.find_element_by_class_name('finish-selector')
        for label in orientation.find_elements_by_tag_name('label')
            for anchor in finish_selector.find_elements_by_tag_name('a')
                if 'disabled' not in label.get_attribute('class'):
                    label.click()
                    handedness = label.get_attribute('for')

                anchor.click()
                finish = anchor.get_attribute('title')
                #: note I had it without a price shown and then refreshed to get it showing once
                #: can check using a try-except NoSuchElementException
                price = buying_options.find_element_by_id('localized-price').text
                version = Version(handedness, finish, price)._asdict()
                versions.append(version)

        product_overview = self.driver.find_element_by_id('product-overview')
