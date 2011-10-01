import icerss
import unittest

ICE_RSS = 'http://lockfuglsang.dk/boxee/icerss'

class TestIceRSS(unittest.TestCase):

    def setUp(self):
        self.ice = icerss.IceRSS(ICE_RSS)

    def test_get_sources(self):
        # Arrange
        expected = [{u'plot': {u'en': u'Lifelong platonic friends Zack and Miri look to solve their respective cash-flow problems by making an adult film together. As the cameras roll, however, the duo begin to sense that they may have more feelings for each other than they previously thought.'}, u'genres': [u'Comedy', u'Drama', u'Romance'], u'rating': 3.5, u'name': u'Zack and Miri Make a Porno (2008)</a>', u'title': u'Zack and Miri Make a Porno', u'url': u'ip.php?v=1255&', u'poster': u'http://ia.media-imdb.com/images/M/MV5BMTMwNzM5MTIxNl5BMl5BanBnXkFtZTcwNzkwNzM5MQ@@._V1._SX320.jpg', u'director': u'Kevin Smith', u'writers': [u'Kevin Smith'], u'actors': [u'Seth Rogen', u'Elizabeth Banks', u'Craig Robinson', u'Gerry Bednob'], u'year': u'2008', u'runtime': u'1 hr 41 mins', u'id': u'tt1007028'}]
        offset = 1
        count = 1
        type = 'movies'
        genre = 'Z'
        sorting = 'a-z'

        # Act
        list = self.ice.get_list(offset, count, type, genre, sorting)
        #print list

        # Assert
        self.assertEqual(list, expected, 'sources')

if __name__ == '__main__':
    unittest.main()