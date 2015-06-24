#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from config import config
from mysql_wrapper import MySqlWrapper
import logging
from logging.handlers import RotatingFileHandler
from utils import JsSeoHandler
import utils

'''The botfacing server faces the internet.
It only allows getting requested pages.'''

if config['installed']:
    db = utils.connect_to_database()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='jsSeo.log', level=logging.INFO)

datastore = MySqlWrapper()

class InstallHandler(tornado.web.RequestHandler):
    def get(self):
        if not config['installed']:
            self.render('install.html')
        else:
            self.send_error(400)

    def post(self):
        #TODO copy sample_config.json to config.json
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

class PageHandler(JsSeoHandler):
    def get(self, url):
        '''deliver pages to bots'''
        try:
            logging.info('Serving %s to %s', url, self.request.headers['User-Agent'])
            self.set_header('content-type', 'text/html')
            if not utils.is_valid_url(url):
                self.send_error(400)
                return

            content = datastore.get_page(url)

            if content is None:
                self.set_error(502)
            else:
                self.write(content)
        except Exception, e:
            logging.error('Error getting page for crawler', exc_info=True)

settings = {
    #'default_handler_class': ErrorHandler,
    'default_handler_args': dict(status_code=404),
    'compress_response': True,
    'debug' : True,
    'cookie_secret' : 'TODO add some secret string here',
    'xsrf_cookies': False
}

application = tornado.web.Application([
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
    logging.info('JsSeo bot facing server running on port: %s', str(port))
