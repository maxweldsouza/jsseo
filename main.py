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

class ApiHandler(tornado.web.RequestHandler):
    def get(self, path):
        action = self.get_argument('action')
        hostname = self.get_argument('hostname')
        if action == 'list-urls':
            limit = self.get_argument('limit', 20)
            offset = self.get_argument('offset', 0)
            #TODO
            if limit > 100 or limit <= 0:
                self.write('limit is out of range')
            if offset < 0:
                self.write('offset is out of range')
            urls = db.get_all('''
            select url_path
            from url
            where site_hostname = %s''', (hostname))
            result = {
                    'hostname': hostname,
                    'urls': [x[0] for x in urls]
                    }
            self.write(mysqldbhelper.json_output(result))

    def post(self, path):
        action = self.get_argument('action')
        hostname = self.get_argument('hostname')
        path = self.get_argument('path')
        if action == 'create-url':
            db.put('''
            insert into url
            (url_path, site_hostname) values
            (%s, %s)''', (path, hostname))

        elif action == 'delete-url':
            db.put('''
            delete from url
            where url_path = %s and
            site_hostname = %s''', (path, hostname))

class PageHandler(tornado.web.RequestHandler):
    def get(self, path):
        url = urlparse(path)
        content = db.get_one('''
        select page_content from page
        where page_url = %s
        ''', (path,))
        self.write(content)

    def post(self, path):
        try:
            content = self.get_argument('content')
            content = remove_script_tags(content)
            content = content.encode('utf-8')
            hsh = hashlib.sha1(content).hexdigest()

            urlobj = urlparse(path)
            print urlobj
            hostname = urlobj.netloc
            scheme = urlobj.scheme
            self.set_header('Access-Control-Allow-Origin', scheme + '://' + hostname)

            oldhash = db.get_one('''
            select page_sha1 from page
            where page_url = %s''', (path,))

            if not oldhash:
                db.put('''
                insert into page
                (page_hostname, page_url, page_content, page_sha1) values
                (%s, %s, %s, %s)
                ''', (hostname, path, content, hsh))
            if hsh == oldhash:
                self.write('page not changed')
            else:
                db.put('''
                update page
                set
                page_hostname = %s, page_content = %s, page_sha1 = %s
                where
                page_url = %s
                ''', (hostname, content, hsh, path))

        except Exception, e:
            self.set_status(500)
            print str(e)
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
    (r"/api/v1(.*)", ApiHandler),
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
