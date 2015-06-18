#!/usr/bin/env python
import traceback
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
import hashlib
import mysqldbhelper
from urlparse import urlparse
import datetime
import json
import re
from bs4 import BeautifulSoup
import logging
from logging.handlers import RotatingFileHandler

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jsSeo')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler('jsSeo.log', maxBytes=10*1000*1000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)


with open('config.json') as f:
    config_text = f.read()
config = json.loads(config_text)

def connect_to_database():
    db = mysqldbhelper.DatabaseConnection(config['hostname'],
                        user=config['username'],
                        passwd=config['password'],
                        db=config['database'])
    return db

if config['installed']:
    db = connect_to_database()

json_output = mysqldbhelper.json_output

default_expiry_time = 86400

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

class JsSeoHandler(tornado.web.RequestHandler):
    def missing_argument_error(self, message):
        self.set_header('content-type', 'application/json')
        self.set_status(400)
        self.write(json_output({
            'status': 400,
            'message': message
            }))

class InstallHandler(tornado.web.RequestHandler):
    def get(self):
        if not config['installed']:
            self.render('install.html')
        else:
            self.send_error(400)

    def post(self):
        if not config['installed']:
            config['database'] = self.get_argument('database')
            config['username'] = self.get_argument('username')
            config['password'] = self.get_argument('password')
            config['hostname'] = self.get_argument('hostname')
            try:
                db = connect_to_database()
                check = db.get_one('SELECT 1', ())
                if not check:
                    raise Exception('Test query did not run')

                f = open('config.json', 'w')
                f.write(json.dumps(config, indent=4, sort_keys=True))
                self.write('Installation complete')

                config['installed'] = True

            except Exception, e:
                message = ('Could not connect to database. '
                    'Check your settings and try again.')
                logger.error(message)
                self.write(message)
                self.write(str(traceback.format_exc()))

class ApiHandler(JsSeoHandler):
    def get(self, path):
        try:
            self.set_header('access-control-allow-origin', '*')
            self.set_header('content-type', 'application/json')
            action = self.get_argument('action')
            hostname = self.get_argument('hostname')
            if action == 'next-page':
                # send the next page to be crawled
                url = db.get_one('''
                select page_path
                from page
                where site_hostname = %s
                and (page_expires < current_timestamp()
                or page_content is null)''', (hostname,))
                if url == None:
                    result = dict(hostname=hostname, message='all pages done')
                else:
                    result = {
                            'hostname': hostname,
                            'next-page': url
                            }
                self.write(json_output(result))
        except tornado.web.MissingArgumentError, e:
            self.missing_argument_error(str(e))
        except Exception, e:
            logger.error('Api error', hostname, exc_info=True)

    def post(self, path):
        try:
            self.set_header('access-control-allow-origin', '*')
            self.set_header('content-type', 'application/json')
            action = self.get_argument('action')
            hostname = self.get_argument('hostname')
            self.write(json_output(dict(message='recieved request')))
            if action == 'submit-paths':
                # list of links
                paths = self.get_argument('paths')
                paths = paths.split('\n')
                paths = [x for x in paths if is_valid_path(x)]
                for path in paths:
                    try:
                        db.start()
                        exists = db.get_one('''
                        select page_path from page
                        where site_hostname = %s and
                        page_path = %s''', (hostname, path))
                        if not exists:
                            db.put('''
                            insert into page
                            (page_path, site_hostname, page_expiresevery, page_expires) values
                            (%s, %s, %s, %s)''',
                            (path, hostname, default_expiry_time, datetime.datetime.now()))
                        db.save()
                    except Exception, e:
                        logger.error('Could not add paths', exc_info=True)
                        db.rollback()

        except tornado.web.MissingArgumentError, e:
            self.missing_argument_error(str(e))
        except Exception, e:
            logger.error('Api error', exc_info=True)

class PageHandler(JsSeoHandler):
    def get(self, url):
        try:
            self.set_header('content-type', 'text/html')
            if not is_valid_url(url):
                self.send_error(400)
                return

            url = parse_url(url)
            content = db.get_one('''
            select page_content from page
            where
            page_path = %s and
            site_hostname = %s
            ''', (url.path, url.origin))
            if content is None:
                self.set_error(502)
            else:
                self.write(content)
        except Exception, e:
            logger.error('Error getting page for crawler', exc_info=True)

    def post(self, url):
        try:
            print 'Caching:', url
            self.set_header('content-type', 'application/json')

            content = self.get_argument('content')
            if config['remove_scripts']:
                content = remove_script_tags(content)
            content = content.encode('utf-8')
            hsh = hashlib.sha1(content).hexdigest()

            urlobj = parse_url(url)
            self.set_header('access-control-allow-origin', urlobj.origin)

            current = db.get_one('''
            select page_id, page_sha1 from page
            where
            site_hostname = %s and
            page_path = %s''', (urlobj.origin, urlobj.path))

            expires = datetime.datetime.now() + datetime.timedelta(0, default_expiry_time) #secs

            if not current:
                # TODO paths should always be present beforehand
                db.put('''
                insert into page
                (site_hostname, page_path, page_content, page_sha1,
                page_expires, page_expiresevery) values
                (%s, %s, %s, %s, %s, %s)
                ''', (urlobj.origin, urlobj.path, content, hsh, expires, default_expiry_time))
                self.write(json_output({
                    'message': 'successfully created'
                    }))

            else:
                pageid = current[0]
                db.put('''
                update page
                set
                site_hostname = %s, page_content = %s, page_sha1 = %s,
                page_expires = %s, page_expiresevery = %s
                where
                page_id = %s
                ''', (urlobj.origin, content, hsh, expires, default_expiry_time, pageid))
                self.write(json_output({
                    'message': 'successfully updated'
                    }))

        except tornado.web.MissingArgumentError, e:
            self.missing_argument_error(str(e))

        except Exception, e:
            logger.error('Error caching page', exc_info=True)
            self.write(json_output({
                'message': str(e)
                }))

    def delete(self, url):
        try:
            self.set_header('content-type', 'application/json')
            urlobj = parse_url(url)
            self.set_header('access-control-allow-origin', urlobj.origin)
            db.put('''
            delete from page
            where page_path = %s
            and
            site_hostname = %s''', (urlobj.path, urlobj.origin))
            self.write(json_output({
                'message': 'successfully deleted'
                }))
        except Exception, e:
            logger.error('Error deleting page', exc_info=True)
            self.write(json_output({
                'message': str(e)
                }))

settings = {
    #'default_handler_class': ErrorHandler,
    'default_handler_args': dict(status_code=404),
    'compress_response': True,
    'debug' : True,
    'cookie_secret' : 'TODO add some secret string here',
    'xsrf_cookies': False
}

application = tornado.web.Application([
    (r"/api/v1(.*)", ApiHandler),
    (r"/install", InstallHandler),
    (r"/(.*)", PageHandler),
    ], **settings)

if __name__ == "__main__":
    port = config['port']
    if config['ssl']:
        server = HTTPServer(application, ssl_options = {
            'certfile': os.path.join(config.certfile),
            'keyfile': os.path.join(config.keyfile),
            })
        server.listen(port)
    else:
        application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
    logger.info('JsSeo running on port: %s', str(port))
