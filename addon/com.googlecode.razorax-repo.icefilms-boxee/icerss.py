import lib.jobmanager as jobmanager
# Integration with the icerss feeds
import urllib
try: import json
except: import simplejson as json

from lib.razutils import *

class IceRSS:
    def __init__(self, iceurl):
        self.iceurl = iceurl

    def get_list(self, type='movies', genre='1', sorting='popular', offset=0, count=12):
        url = '%s/%s/%s' % (type, sorting, genre)

        args = {'url' : url, 'offset' : offset, 'count' : count}
        listurl = "%s/icefilms.php?%s" % (self.iceurl, urllib.urlencode(args))
        jsondata, _ = get_url(listurl)
        data = json.loads(jsondata)
        if data and data.has_key('success') and data['success']:
            return data['data']
        return {}

    def get_seasons(self, uri):
        args = {'url' : url}
        listurl = "%s/icefilms.php?%s" % (self.iceurl, urllib.urlencode(args))
        jsondata, _ = get_url(listurl)
        data = json.loads(jsondata)
        if data and data.has_key('success') and data['success']:
            # TODO: What about the meta-data?
            return data['data']['seasons']
        return []

class IceJob(jobmanager.BoxeeJob):
    ''' A job that allows us to fetch the movies + metadata "behind the scenes"
    '''
    def __init__(self, icerss, callback):
        jobmanager.BoxeeJob.__init__(self, 'IceJob', 5)
        self.icerss = icerss

    def process(self):
        pass