from pyvirtualdisplay import Display
from selenium import webdriver
import selenium
from config import config
from mysql_wrapper import MySqlWrapper
import logging
import utils

logging.basicConfig(filename='caching.log', level=logging.INFO)

class InvalidUrlError(Exception): pass

def is_internal_url(url, reference):
    '''checks whether the given url is an internal url
    to the reference site'''
    refobj = utils.parse_url(reference)
    urlobj = utils.parse_url(url)
    if not url.startswith('http'):
        raise InvalidUrlError
    return urlobj.origin == refobj.origin

assert(is_internal_url('http://testsite.com', 'http://testsite.com'))
assert(is_internal_url('http://testsite.com/home', 'http://testsite.com'))
assert(not is_internal_url('http://someothersite.com', 'http://testsite.com'))
assert(not is_internal_url('http://testsite.org', 'http://testsite.com'))

def absolute_to_relative(url, reference):
    '''converts absolute urls to relative urls based on the
    reference url'''
    if not url.startswith('http'):
        raise InvalidUrlError
    refobj = utils.parse_url(reference)
    urlobj = utils.parse_url(url)
    if urlobj.origin == refobj.origin:
        return urlobj.path

assert(absolute_to_relative('http://testsite.com/home', 'http://testsite.com') == '/home')
assert(absolute_to_relative('http://testsite.com/', 'http://testsite.com') == '/')
assert(absolute_to_relative('http://testsite.com', 'http://testsite.com') == '/')
assert(absolute_to_relative('http://testsite.com/some?thing=very#!weird', 'http://testsite.com')
        == '/some?thing=very#!weird')

datastore = MySqlWrapper()

def create_browser():
    if config['browser'] == 'firefox':
        profile = webdriver.FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)
        browser = webdriver.Firefox(profile)
    elif config['browser'] == 'chrome':
        browser = webdriver.Chrome()
    elif config['browser'] == 'ie':
        browser = webdriver.Ie()
    elif config['browser'] == 'opera':
        browser = webdriver.Opera()
    elif config['browser'] == 'phantomjs':
        browser = webdriver.PhantomJS()
    else:
        raise Exception('Incorrect browser in config')
    browser.set_page_load_timeout(config['timeout'])
    browser.set_script_timeout(config['timeout'])
    return browser

browser = create_browser()
url = 'http://localhost'

def process_page(browser, url):
    logging.info('Caching %s', url)
    browser.get(url)

    links = browser.find_elements_by_tag_name('a')
    links = [link.get_attribute('href') for link in links]
    # get only internal links and converts absolute links to relative
    links = [absolute_to_relative(link, url) for link in links if is_internal_url(link, url)]

    return links, browser.page_source

while url:
    site, path = utils.parse_url(url)
    try:
        links, source = process_page(browser, url)
    except selenium.common.exceptions.UnexpectedAlertPresentException, e:
        browser.close()
        browser = create_browser()
        continue
    except selenium.common.exceptions.TimeoutException:
        logger.info('Timeout on page %s', url)
        continue

    datastore.add_paths(site, links)
    logging.info('Adding paths %s', links)

    soup = BeautifulSoup(source)
    if config['remove_scripts']:
        [s.extract() for s in soup('script')]
    # this will convert page source to utf-8 irrespective of
    # its character set. the charset meta tag will also be changed
    source = soup.prettify()

    datastore.save_page(url, source)

    url = datastore.next_url(site)
browser.close()
