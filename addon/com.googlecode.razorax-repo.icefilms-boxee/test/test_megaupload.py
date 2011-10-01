import megaupload
import unittest
import re
import time

# TODO: Do NOT commit with my personal account!!
USERNAME='IcefilmsBoxee'
PASSWORD='ic3f1lms'
COOKIE = 'user=OOU6SSFN0YY8SRNUVDAHIKX5KIUHBEZN'
LINKS = (
    ('http://www.megaupload.com/?d=HNSZKQU9', 'crudos.720p.1.avi'), # The Hangover, Source #1 Part 1
    ('http://www.megaupload.com/?d=HMUN3QTR', 'The.Hangover.2009.UNRATED.BDRip.XviD-NoGRP.avi'), # The Hangover, Source #3
    ('http://www.megaupload.com/?d=MAW13HIS', 'Incptn-aXXo.avi'), # Inception Source # 2
    ('http://www.megaupload.com/?d=UXSOQ2IX', 'Inception (2010).avi'), # Inception Source # 3
    ('http://www.megaupload.com/?d=NDBVRJ4W', 'The.Hangover.2009.UNRATED.BDRip.XviD.avi'), # The Hangover, Source #2
    ('http://www.megaupload.com/?d=IMZRWQEY', 'crudos.720p.2.avi'), # The Hangover, Source #1 Part 2
)

class TestMegaUpload(unittest.TestCase):

    def test_no_account(self):
        # Arrange
        self.mu = megaupload.MegaUpload('', '')
        wait_time = 46
        link, filename = LINKS[0]

        # Act
        l = self.mu.resolve(link)

        # Assert
        self.assert_link(l, filename, wait_time)

    def test_free_account_login(self):
        # Arrange
        self.mu = megaupload.MegaUpload(USERNAME, PASSWORD)
        wait_time = 26
        link, filename = LINKS[1]

        # Act
        l = self.mu.resolve(link)

        # Assert
        self.assert_link(l, filename, wait_time)

    def test_free_account_cookie(self):
        # Arrange
        self.mu = megaupload.MegaUpload('USERNAME', 'PASSWORD', COOKIE)
        wait_time = 26
        link, filename = LINKS[2]

        # Act
        l = self.mu.resolve(link)

        # Assert
        self.assert_link(l, filename, wait_time)

    def test_cache_same_obj(self):
        # Arrange
        self.mu = megaupload.MegaUpload('', '')
        wait_time = 46
        link, filename = LINKS[3]

        # Act
        l1 = self.mu.resolve(link)
        time.sleep(4)
        l2 = self.mu.resolve(link)

        # Assert
        self.assert_link(l1, filename, wait_time)
        self.assert_link(l2, filename, wait_time-4, True)

    def test_cache_multiple_obj(self):
        # Arrange
        user = 'user1'
        self.mu = megaupload.MegaUpload(user, '')
        wait_time = 46
        link, filename = LINKS[4]

        # Act
        l1 = self.mu.resolve(link)
        time.sleep(4)
        self.mu = megaupload.MegaUpload(user, '')
        l2 = self.mu.resolve(link)

        # Assert
        self.assert_link(l1, filename, wait_time)
        self.assert_link(l2, filename, wait_time-4, True)

    def test_cache_multiple_users(self):
        # Arrange
        self.mu = megaupload.MegaUpload('user2', '')
        wait_time = 46
        link, filename = LINKS[5]

        # Act
        l1 = self.mu.resolve(link)
        time.sleep(4)
        self.mu = megaupload.MegaUpload('user3', '')
        l2 = self.mu.resolve(link)

        # Assert
        self.assert_link(l1, filename, wait_time)
        self.assert_link(l2, filename, wait_time)

    def assert_link(self, l, filename, wait_time, cache_test = False):
        self.assertTrue(re.match('http://[^.]*.megaupload.com/files/[^/]*/' + re.escape(filename), l[0]), "link: %s" % l[0])
        self.assertEqual(l[1], filename, "filename: %s" % l[1])
        if cache_test:
            #self.assertTrue(l[2] < wait_time, "wait_time %s < %s" % (wait_time, l[2]))
            # TODO: Somehow this is running "too fast"... 
            self.assertAlmostEqual(l[2], wait_time, 0, "wait_time %s < %s" % (wait_time, l[2]))
        else:
            self.assertEqual(l[2], wait_time, "wait_time: %s" % l[2])
        #self.assertTrue(l[3])
        #self.assertEqual(l[3].name, 'mcpop', 'cookie value')
        
if __name__ == '__main__':
    unittest.main()
