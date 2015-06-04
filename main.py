#!/usr/bin/env python
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
import hashlib
import config
import mysqldbhelper
from urlparse import urlparse
import datetime
import json

db = mysqldbhelper.DatabaseConnection(config.hostname,
                    user=config.user,
                    passwd=config.passwd,
                    db=config.db)

json_output = mysqldbhelper.json_output

default_expiry_time = 86400

def remove_script_tags(content):
    #TODO
    return content

def parse_url(url):
    class UrlObj():
        pass
    result = UrlObj()
    urlobj = urlparse(url)
    origin = urlobj.scheme + '://' + urlobj.netloc
    path = url[len(origin):]
    result.origin = origin
    result.path = path
    return result

class ApiHandler(tornado.web.RequestHandler):
    def get(self, path):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json')
        action = self.get_argument('action')
        hostname = self.get_argument('hostname')
        if action == 'next-page':
            # send the next page to be crawled
            url = db.get_one('''
            select page_path
            from page
            where site_hostname = %s
            and page_expires < current_timestamp()''', (hostname,))
            if url == None:
                result = dict(hostname=hostname, message='all pages done')
            else:
                result = {
                        'hostname': hostname,
                        'next-page': url
                        }
            self.write(json_output(result))

    def post(self, path):
        self.set_header('Access-Control-Allow-Origin', '*')
        action = self.get_argument('action')
        hostname = self.get_argument('hostname')
        self.write(json_output(dict(message='recieved request')))
        if action == 'submit-paths':
            # list of links
            # TODO get paths from body and not argument
            paths = self.get_argument('paths')
            data = json.loads(paths)
            for path in data['paths']:
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
                    db.rollback()
                    raise

class PageHandler(tornado.web.RequestHandler):
    def get(self, url):
        self.set_header('Content-Type', 'text/html')
        url = parse_url(url)
        content = db.get_one('''
        select page_content from page
        where page_path = %s and
        site_hostname = %s
        ''', (url.path, url.origin))
        self.write(content)

    def post(self, url):
        try:
            self.set_header('Content-Type', 'application/json')

            content = self.get_argument('content')
            content = remove_script_tags(content)
            content = content.encode('utf-8')
            hsh = hashlib.sha1(content).hexdigest()

            urlobj = parse_url(url)
            self.set_header('Access-Control-Allow-Origin', urlobj.origin)

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

        except Exception, e:
            self.set_status(500)
            print str(e)
            self.write(json_output({
                'message': str(e)
                }))

    def delete(self, url):
        urlobj = parse_url(url)
        db.put('''
        delete from page
        where page_path = %s
        and
        site_hostname = %s''', (urlobj.path, urlobj.origin))
        self.write(json_output({
            'message': 'successfully deleted'
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
