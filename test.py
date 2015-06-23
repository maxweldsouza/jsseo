from mysql_wrapper import MySqlWrapper
import unittest

class TestDatastore(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.datastore = MySqlWrapper()

    def test_non_existent(self):
        self.assertEqual(self.datastore.get_page('http://example.com'), None)

    def test_save_page(self):
        self.datastore.save_page('http://example.com', '<html></html>')
        self.assertEqual(self.datastore.get_page('http://example.com'), '<html></html>')
        self.datastore.delete_page('http://example.com')
        self.assertEqual(self.datastore.get_page('http://example.com'), None)

    def test_unicode_page(self):
        #TODO
        pass

    def test_unicode_url(self):
        #TODO
        pass

    def test_paths(self):
        self.assertEqual(self.datastore.next_url('http://example.com'), None)
        self.datastore.add_paths('http://example.com', ['/home'])
        self.assertEqual(self.datastore.next_url('http://example.com'), 'http://example.com/home')
        self.datastore.delete_page('http://example.com/home')
        self.assertEqual(self.datastore.next_url('http://example.com'), None)


if __name__ == '__main__':
    unittest.main()
