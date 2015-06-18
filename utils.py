from bs4 import BeautifulSoup
from urlparse import urlparse
import re

def remove_script_tags(html):
    soup = BeautifulSoup(html)
    [s.extract() for s in soup('script')]
    return soup.prettify()

def is_valid_url(url):
    return re.match(r'^(?:http|https)://', url)

assert(is_valid_url('http://www.google.com'))
assert(is_valid_url('https://www.google.com'))
assert(not is_valid_url('ftp://www.google.com'))
assert(not is_valid_url('www.google.com'))

def is_valid_path(path):
    if path == '#':
        return False
    return True

def parse_url(url):
    """ Parse urls and return an object with an origin and a path.
    Add trailing slash only to the root url. Root urls are stored
    in the database with path "/" 
    http://googlewebmastercentral.blogspot.in/2010/04/to-slash-or-not-to-slash.html """

    class UrlObj():
        def __str__(self):
            return 'Origin: {0} \n Path: {1}'.format(self.origin, self.path)

    result = UrlObj()
    urlobj = urlparse(url)
    origin = urlobj.scheme + '://' + urlobj.netloc
    path = url[len(origin):]
    if path == '':
        path = '/'

    result.origin = origin
    result.path = path
    return result

assert(parse_url('http://testsite.com').path == '/')
assert(parse_url('http://testsite.com/').path == '/')
assert(parse_url('http://testsite.com?key=value').path == '?key=value')
assert(parse_url('http://testsite.com/').path == '/')
assert(parse_url('http://testsite.com/home').path == '/home')
assert(parse_url('http://testsite.com/home/').path == '/home/')

