import abc
from importlib import resources

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
        self.json_file = resources.path(json_dir, str(json_file))
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
        for url, html in self._get_guitar_raw:
            data = self._merge_parsed_data(url)

            with open(self.json_file, 'a') as fp:
                json.dump(data)
                fp.write('\n')

            html_dir = f'instruments.data.{self.brand}.html'
            html_file = resources.path(html_dir, f'{data['id']}.html')
            with open(html_file, 'w') as fp:
                fp.write(html)


    def save_guitar_data(self):
        for url, html in self._get_guitar_raw:
            data = self._merge_parsed_data(url)

            with open(self.json_file, 'a') as fp:
                json.dump(data)
                fp.write('\n')

            html_file = resources.path(html_dir, f'{data['id']}.html')
            with open(html_file, 'w') as fp:
                fp.write(html)