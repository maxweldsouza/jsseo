#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from config import config
import logging
from logging.handlers import RotatingFileHandler
from utils import JsSeoHandler
import utils

'''The botfacing server faces the internet.
It only allows getting requested pages.'''

if config['installed']:
    db = utils.connect_to_database()

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jsSeo')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = RotatingFileHandler(config['logfile'], maxBytes=10*1000*1000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)

class PageHandler(JsSeoHandler):
    def get(self, url):
        '''deliver pages to bots'''
        try:
            logger.info('Serving %s to %s', url, self.request.headers['User-Agent'])
            self.set_header('content-type', 'text/html')
            if not utils.is_valid_url(url):
                self.send_error(400)
                return

            url = utils.parse_url(url)
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

settings = {
    #'default_handler_class': ErrorHandler,
    'default_handler_args': dict(status_code=404),
    'compress_response': True,
    'debug' : True,
    'cookie_secret' : 'TODO add some secret string here',
    'xsrf_cookies': False
}

application = tornado.web.Application([
    (r"/(.*)", PageHandler),
    ], **settings)

if __name__ == "__main__":
    port = config['botfacing_port']
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
