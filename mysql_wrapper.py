import datetime
import hashlib
from config import config
import logging
import utils

# TODO shouldnt be here
default_expiry_time = 86400

class MySqlWrapper():
    def __init__(self):
        if config['installed']:
            self.db = utils.connect_to_database()

    def get_page(self, url):
        '''gets the dom for the path'''
        try:
            url = utils.parse_url(url)
            content = self.db.get_one('''
            select page_content from page
            where
            page_path = %s and
            site_hostname = %s
            ''', (url.path, url.origin))
            return content
        except Exception, e:
            logging.error('Could not get page', exc_info=True)

    def save_page(self, url, html):
        '''saves the dom for the path'''
        try:
            urlobj = utils.parse_url(url)
            hsh = hashlib.sha1(html).hexdigest()

            current = self.db.get_one('''
            select page_id, page_sha1 from page
            where
            site_hostname = %s and
            page_path = %s''', (urlobj.origin, urlobj.path))

            expires = datetime.datetime.now() + datetime.timedelta(0, default_expiry_time) #secs

            logging.info('Saving page: %s', url)
            if not current:
                # TODO paths should always be present beforehand
                self.db.put('''
                insert into page
                (site_hostname, page_path, page_content, page_sha1,
                page_expires, page_expiresevery) values
                (%s, %s, %s, %s, %s, %s)
                ''', (urlobj.origin, urlobj.path, html, hsh, expires, default_expiry_time))
            else:
                pageid = current[0]
                self.db.put('''
                update page
                set
                site_hostname = %s, page_content = %s, page_sha1 = %s,
                page_expires = %s, page_expiresevery = %s
                where
                page_id = %s
                ''', (urlobj.origin, html, hsh, expires, default_expiry_time, pageid))
        except Exception, e:
            logging.error('Could not save page', exc_info=True)

    def delete_page(self, url):
        try:
            urlobj = utils.parse_url(url)
            self.db.put('''
            delete from page
            where page_path = %s
            and
            site_hostname = %s''', (urlobj.path, urlobj.origin))
        except Exception, e:
            logging.error('Could not delete page', exc_info=True)

    def next_url(self, hostname):
        '''gets the url of the next page to be cached. returns
        none if there are no pages left to be cached'''
        try:
            url = self.db.get_one('''
            select page_path
            from page
            where site_hostname = %s
            and (page_expires < current_timestamp()
            or page_content is null)''', (hostname,))
            return url
        except Exception, e:
            logging.error('Could not get next url', exc_info=True)

    def add_paths(self, hostname, urls):
        '''adds paths to the database'''
        for path in urls:
            try:
                self.db.start()
                exists = self.db.get_one('''
                select page_path from page
                where site_hostname = %s and
                page_path = %s''', (hostname, path))
                if not exists:
                    self.db.put('''
                    insert into page
                    (page_path, site_hostname, page_expiresevery, page_expires) values
                    (%s, %s, %s, %s)''',
                    (path, hostname, default_expiry_time, datetime.datetime.now()))
                self.db.save()
            except Exception, e:
                logging.error('Could not add paths', exc_info=True)
                self.db.rollback()
