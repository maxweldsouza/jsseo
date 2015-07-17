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

    def failed_attempt(self, url):
        '''registers a failed attempt'''
        self.db.put('''
        update page
        set page_attempts = page_attempts + 1''', ())

    def save_page(self, url, html):
        '''saves the dom for the path'''
        try:
            urlobj = utils.parse_url(url)
            hsh = hashlib.sha1(html.encode('utf-8')).hexdigest()

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
                page_expires, page_expiresevery, page_attempts) values
                (%s, %s, %s, %s, %s, %s, %s)
                ''', (urlobj.origin, urlobj.path, html, hsh, expires, default_expiry_time, 0))
            else:
                pageid = current[0]
                self.db.put('''
                update page
                set
                site_hostname = %s, page_content = %s, page_sha1 = %s,
                page_expires = %s, page_expiresevery = %s, page_attempts = %s
                where
                page_id = %s
                ''', (urlobj.origin, html, hsh, expires, default_expiry_time, pageid, 0))
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
        none if there are no pages left to be cached. the preference
        for the order in which paths are returned is:
            paths that are not indexed and with less than 3 failed attempts
            paths with the earliest expiration time with no failed attempts
            paths with the earliest expiration time with one failed attempts
            paths with the earliest expiration time with two failed attempts

            after three failed attempts dont attempt to index the page'''
        try:
            path = self.db.get_one('''
            select page_path
            from page
            where site_hostname = %s
            and page_content is null
            and page_attempts < 3
            ''', (hostname,))

            failed_attempts = 0
            while failed_attempts < 3 and not path:
                path = self.db.get_one('''
                select page_path
                from page
                where site_hostname = %s
                and page_attempts = %s
                order by page_expires
                ''', (hostname, failed_attempts))
                failed_attempts += 1

            if path:
                return hostname + path
            else:
                return None
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

    def get_paths(self, hostname):
        try:
            paths = self.db.get_all('''
            select page_path from page
            where site_hostname = %s''', (hostname,))
            if paths:
                return [hostname + path[0] for path in paths]
            else:
                return None
        except Exception, e:
            logging.error('Could not add paths', exc_info=True)

