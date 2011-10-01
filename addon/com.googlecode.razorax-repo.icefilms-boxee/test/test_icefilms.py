import icefilms
import unittest

BASE_URI = 'ip.php?v=62631&'
BASE_URI2 = 'ip.php?v=34333&'

class TestIcefilms(unittest.TestCase):

    def setUp(self):
        self.ice = icefilms.IceFilm()

    def test_get_sources(self):
        # Arrange
        expected = [('HD 720p', [('http://www.megaupload.com/?d=1N57ZSNS', '#1 | Part 1/3'), ('http://www.megaupload.com/?d=JYPPB75Y', '#1 | Part 2/3'), ('http://www.megaupload.com/?d=ZI6EDHIT', '#1 | Part 3/3'), ('http://www.megaupload.com/?d=I45RIQ8W', '#2 | Part 1/3'), ('http://www.megaupload.com/?d=NJCP60CC', '#2 | Part 2/3'), ('http://www.megaupload.com/?d=Y1XZKL6A', '#2 | Part 3/3')]), ('DVDRip', [('http://www.megaupload.com/?d=8BU26EUX', '#3 | Full'), ('http://www.megaupload.com/?d=GS36WM6M', '#4 | Full'), ('http://www.megaupload.com/?d=S3FVQ0B6', '#5 | Full')]), ('DVD R5/R6', [('http://www.megaupload.com/?d=Z674SSVH', '#6 | Full')])]

        # Act
        sources = self.ice.get_sources(BASE_URI)
        #print sources

        # Assert
        self.assertEqual(sources, expected, 'sources')

if __name__ == '__main__':
    unittest.main()