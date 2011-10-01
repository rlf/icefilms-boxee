import unittest
from lib.razutils import *

class TestRazUtil(unittest.TestCase):

    def test_get_url_basic(self):
        data, cookies = get_url('http://docs.python.org/library/unittest.html')
        self.assertFalse(cookies, 'no cookies expected')
        self.assertNotEqual('http', data[:4], 'no redirect expected')

    def test_get_url_redirect(self):
        data, cookies = get_url('http://www.google.com')
        #print cookies
        self.assertTrue(cookies)
        self.assertEqual('http://', data[:7]) # Google redirects to localized pages

if __name__ == '__main__':
    unittest.main()