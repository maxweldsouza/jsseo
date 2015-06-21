from pyvirtualdisplay import Display
from selenium import webdriver
from config import config
from mysql_wrapper import MySqlWrapper
import utils

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

if config['browser'] == 'firefox':
    browser = webdriver.Firefox()
elif config['browser'] == 'google-chrome':
    browser = webdriver.Firefox()

while True:
    url = 'http://localhost:8000/test.html'
    browser.get(url)
    links = browser.find_elements_by_tag_name('a')
    links = [link.get_attribute('href') for link in links]
    # get only internal links and converts absolute links to relative
    links = [absolute_to_relative(link, url) for link in links if is_internal_url(link, url)]
    print links
    break
    datastore.save_page(browser.page_source)
    datastore.add_paths(paths)

browser.close()
