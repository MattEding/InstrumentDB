import itertools
import json
import logging
from concurrent import futures
from importlib import resources
from pathlib import Path
from urllib import parse


from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from instruments.transform import clean


#: monkey patching to provide aliases
WebDriver.elem = WebDriver.find_element_by_css_selector
WebDriver.elems = WebDriver.find_elements_by_css_selector

WebElement.attr = WebElement.get_attribute
WebElement.elem = WebElement.find_element_by_css_selector
WebElement.elems = WebElement.find_elements_by_css_selector


ROOT_URL = 'https://www.gibson.com'

LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.INFO)
path = Path(__file__).parent
handler = logging.FileHandler(path / 'scraper.log')
LOGGER.addHandler(handler)


with resources.path('instruments.data.html', '') as HTML_DIR:
    pass

with resources.path('instruments.data.json', '') as JSON_DIR:
    JSON_FILE = JSON_DIR / 'model.json'


def get_driver(browser='Firefox', headless=True):
    """Return driver for given browser.

    Parameters
    ----------
    browser : str (default='Firefox')
    Browswer to use with webdriver.

    headless : bool (default=True)
    Flag to determine whether to use headless browsing.

    Returns
    -------
    driver : WebDriver
    ...
    """

    browser = str(browser).title()
    options = getattr(webdriver, f'{browser}Options')()
    options.headless = bool(headless)
    driver = getattr(webdriver, browser)(options=options)
    return driver


def get_style_urls():
    """Get URLs for guitar styles.

    Yields
    ------
    style_url : str
    URL for a guitar body style (Les Paul, SG, ES, Acoustic, Designer, Basses)
    """

    with get_driver() as driver:
        driver.get(ROOT_URL)
        style_urls = (elem.attr('href') for elem in driver.elems('.body-types a'))
        yield from style_urls


def get_model_urls(style_url):
    """Get URLs of guitar models for a given style.

    Parameters
    ----------
    style_url : str
    URL for a guitar body style.

    Yields
    ------
    model_url : str
    URL for a guitar model.
    """

    with get_driver() as driver:
        driver.get(style_url)
        model_urls = (elem.attr('href') for elem in driver.elems('.model-card h4 a'))
        yield from model_urls


def parse_model(model_url):
    """...

    Parameters
    ----------
    model_url : str
    URL for a guitar model

    Yields
    ------
    id : str
    ...

    html : str
    Raw HTML for guitar model URL excluding WebDriver interactions.

    model : dict
    Extracted data for guitar model including WebDriver interactions.
    """

    #: yield to allow check if URL has already been processed by
    #: looking only at ID to avoid creating resources for web driver
    id = parse.urlparse(model_url).path.split('/')[2]
    yield id

    with get_driver() as driver:
        driver.get(model_url)
        
        html = driver.page_source
        yield html

        header = get_header(driver)
        versions = list(get_versions(driver))
        specs = get_specifications(driver)

        model = dict(
            url=driver.current_url, 
            versions=versions,
            related=[elem.attr('href') for elem in driver.elems('.related-item')],
        )
        model.update(header)
        model.update(specs)
        yield clean.clean(model)


def get_header(driver):
    """Return product name, headline, and description.

    Parameters
    ----------
    driver : WebDriver
    ...

    Returns
    -------
    description : dict
    ...
    """

    marketing = driver.elem('.marketing-copy')
    try:
        #: some models have quality assurance message in description
        message = marketing.elem('p').text
    except exceptions.NoSuchElementException:
        message = ''
    
    description = marketing.text.strip(message).strip().split('\n')[0]
    headline = driver.elem('.marketing-headline').text.split('\n')
    name = headline[0]
    try:
        headline = headline[1]
    except IndexError:
        headline = None

    header = dict(
        name=name,
        headline=headline,
        description=description,
    )
    return header


def get_versions(driver):
    """Yield versons of each left/right handedness and wood finish combo with price and images.

    Parameters
    ----------
    driver : WebDriver
    ...

    Yields
    -------
    version : dict
    ...
    """

    #: bypass pricing messages of the form "We are unfortunately unable to ship this guitar"
    driver.refresh()

    finishes = driver.elems('.finish-selector a')
    handedness = driver.elems('.orientation label')
    for f_elem, h_elem in itertools.product(finishes, handedness):
        if 'disabled' in h_elem.attr('class'):
            continue

        f_elem.click()
        h_elem.click()

        handedness = h_elem.attr('for')
        finish = f_elem.attr('title')
        price = driver.elem('.local-price').text
        images = get_image_urls(driver, finish)

        version = dict(
            handedness=handedness,
            finish=finish,
            price=price,
            images=images,
        )
        yield version


def get_image_urls(driver, finish):
    """...

    Parameters
    ----------
    driver : WebDriver
    ...

    Returns
    -------
    image_urls : list[str]
    ...
    """

    finish = parse.quote(finish)
    image_urls = (img.attr('src') for img in driver.elems('.carousel-indicators li img'))
    image_urls = [url for url in image_urls if url and finish in url]
    return image_urls


def get_specifications(driver):
    """...

    Parameters
    ----------
    driver : WebDriver
    ...

    Returns
    -------
    specs : dict
    ...
    """

    specs = dict()

    sections = driver.elems('.spec-section')
    for section in sections:
        labels = (elem.text for elem in section.elems('.spec-label'))
        values = (elem.text for elem in section.elems('.spec-value'))

        rows = dict(zip(labels, values))
        header = section.elem('h4').text
        specs[header] = rows

    return specs


def save_model(model_url):
    """
    """

    LOGGER.info(f'starting {model_url}')

    try:
        id, html, model = parse_model(model_url)
    except Exception:
        LOGGER.error()

    with open(JSON_FILE, 'a') as fp:
        json.dump(model, fp)
        fp.write('\n')
    
    html_file = HTML_DIR / f'{id}.html'
    with open(html_file, 'w') as fp:
        fp.write(html)
    
    LOGGER.info(f'finished {model_url}')


def get_urls():
    """
    """

    for style_url in get_style_urls():
        yield from get_model_urls(style_url)
    

def main(max_workers=None):
    """
    """

    finished = set(path.stem for path in HTML_DIR.iterdir())
    work = []

    for url in (url for url in get_urls() if url not in finished):
        iterator = parse_model(url)
        id = next(iterator)
        iterator.close()
        if id not in finished:
            work.append(url)
    
    with futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        executor.map(save_model, work)
