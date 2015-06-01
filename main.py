#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
import hashlib
import config
import mysqldbhelper
from urlparse import urlparse

db = mysqldbhelper.DatabaseConnection(config.hostname,
                    user=config.user,
                    passwd=config.passwd,
                    db=config.db)

def remove_script_tags(content):
    #TODO
    return content

class PageHandler(tornado.web.RequestHandler):
    def get(self, path):
        url = urlparse(path)
        print url.path
        content = db.get_one('''
        select page_content from page
        where page_url = %s
        ''', (path,))
        self.write(content)

    def put(self, path):
        try:
            content = self.get_argument('content')
            content = remove_script_tags(content)
            hsh = hashlib.sha1(content).hexdigest()

            oldhash = db.get_one('''
            select page_sha1 from page
            where page_url = %s''', (path,))

            if hsh == oldhash:
                print 'page not changed'
            else:
                db.put('''
                insert into page
                (page_url, page_content, page_sha1) values
                (%s, %s, %s)
                ''', (path, content, hsh))
        except Exception, e:
            self.set_status(500)
            self.write(str(e))

    def delete(self, path):
        db.put('''
        delete from page
        where page_url = %s''', (path,))

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
    port = config.port
    if config.ssl:
        server = HTTPServer(application, ssl_options = {
            'certfile': os.path.join(config.certfile),
            'keyfile': os.path.join(config.keyfile),
            })
        server.listen(config.port)
    else:
        application.listen(config.port)
    print 'JsSeo running on port: ' + str(port)
    tornado.ioloop.IOLoop.instance().start()
