#!/usr/bin/env python

'''
Jsseo caches your javascript heavy web pages in a mysql database so that
you can serve it to web spiders. It uses selenium alongwith a regular browser
like chrome or firefox to generates snapshots of pages.
'''

import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from config import config
from mysql_wrapper import MySqlWrapper
import logging
from logging.handlers import RotatingFileHandler
from utils import JsSeoHandler
import utils
from sitemap import sitemap

'''The botfacing server faces the internet.
It only allows getting requested pages.'''

if config['installed']:
    db = utils.connect_to_database()

# setup logging
# errors are written to stderr, upstart script writes them to /var/www/logs/
logger = logging.getLogger('Jsseo')
logger.setLevel(logging.DEBUG) # to console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO) # to stderr and log through upstart

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

datastore = MySqlWrapper()

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
                logging.error(message)
                self.write(message)
                self.write(str(traceback.format_exc()))

class SitemapHandler(JsSeoHandler):
    def get(self, url):
        try:
            self.set_header('content-type', 'application/xml; charset="utf-8"')
            self.write(sitemap(datastore.get_paths(url)))
        except Exception, e:
            logging.error('Error generating sitemap', exc_info=True)

class PageHandler(JsSeoHandler):
    def get(self, url):
        '''deliver pages to bots'''
        try:
            logging.info('Serving %s to %s', url, self.request.headers['User-Agent'])
            self.set_header('content-type', 'text/html')
            if not utils.is_valid_url(url):
                self.send_error(400)
                return

            content = datastore.get_page(utils.to_pretty_url(url))

            if content is None:
                self.send_error(502)
            else:
                self.write(content)
        except Exception, e:
            logging.error('Error getting page for crawler', exc_info=True)

settings = {
    'default_handler_args': dict(status_code=404),
    'compress_response': True,
    'debug' : config['debug'],
    'xsrf_cookies': False
}

application = tornado.web.Application([
    (r"/install", InstallHandler),
    (r"/sitemap/(.*)", SitemapHandler),
    (r"/(.*)", PageHandler),
    ], **settings)

if __name__ == "__main__":
    port = config['port']
    application.listen(port)
    message = 'JsSeo running on port: %s' % str(port)
    print message
    logging.info(message)
    tornado.ioloop.IOLoop.instance().start()
