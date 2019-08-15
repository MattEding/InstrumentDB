import abc
import json
from importlib import resources

from selenium import webdriver


class ScraperABC(abc.ABC):
    def __init__(
            self,
            browser='Firefox',
            headless=True,
            json_file='',
            brand=''
        ):
        if isinstance(browser, webdriver.Remote):
            browser = browser.name
        self.browser = str(browser).title()
        self.headless = bool(headless)
        self.brand = str(brand).lower()
        json_dir = f'instruments.data.{self.brand}.json'
        with resources.path(json_dir, '') as json_dir:
            self.json_file = json_dir / str(json_file)
        self._driver = None
        self._root_url = f'https://www.{self.brand}.com/'
        
    
    def __enter__(self):
        options = getattr(webdriver, f'{self.browser}Options')()
        options.headless = self.headless
        self._driver = getattr(webdriver, self.browser)(options=options)


    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._driver.quit()


    @abc.abstractmethod
    def _get_guitar_raw(self):
        pass


    @abc.abstractmethod
    def _merge_parsed_data(self, url):
        pass


    def save_guitar_data(self):
        for url, html in self._get_guitar_raw():
            html_dir = f'instruments.data.{self.brand}.html'
            with resources.path(html_dir, '') as html_dir:
                id = urlparse(url).path.split('/')[2]
                html_file = html_dir / f'{id}.html'

                if html_file in html_dir.iterdir():
                    continue

                with open(html_file, 'w') as fp:
                    fp.write(html)

            data = self._merge_parsed_data(url)
            with open(self.json_file, 'a') as fp:
                json.dump(data, fp)
                fp.write('\n')
