from collections import namedtuple
import tornado.web
import mysqldbhelper
from urlparse import urlparse
from config import config
import re

def get_links(html, hostname):
    '''returns a list of urls in a hrefs. if a hostname is specified
    it also returns internal absolute paths converting them to relative'''
    pass

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

    urlobj = urlparse(url)
    origin = urlobj.scheme + '://' + urlobj.netloc
    path = url[len(origin):]
    if path == '':
        path = '/'

    Url = namedtuple('Url', ['origin', 'path'])
    return Url(origin=origin, path=path)

assert(parse_url('http://testsite.com').path == '/')
assert(parse_url('http://testsite.com/').path == '/')
assert(parse_url('http://testsite.com?key=value').path == '?key=value')
assert(parse_url('http://testsite.com/').path == '/')
assert(parse_url('http://testsite.com/home').path == '/home')
assert(parse_url('http://testsite.com/home/').path == '/home/')

class JsSeoHandler(tornado.web.RequestHandler):
    def missing_argument_error(self, message):
        self.set_header('content-type', 'application/json')
        self.set_status(400)
        self.write(json_output({
            'status': 400,
            'message': message
            }))

def connect_to_database():
    db = mysqldbhelper.DatabaseConnection(config['hostname'],
                        user=config['username'],
                        passwd=config['password'],
                        db=config['database'])
    return db
