# Inspired by the icefilms-xbmc (and the port to boxee) on
# https://github.com/rlf/icefilms-addon
# TODO:
#  - support link caching (so we know how long time is left for a link)
import re
import time
from lib.razutils import *

MEGAUPLOAD_URL = 'http://www.megaupload.com/'
WAIT_TIMES = { 'none' : 45, 'free' : 25, 'premium' : 0}
CACHE_TTL = 2*60 # 2 mins... is that "ok"?

_MegaUpload__static_cache = {}
class MegaUpload:
    def __init__(self, username, password, cookie=None):
        self.username = username
        self.password = password
        self.cookie = cookie
        if not cookie and username and password:
            self.__login()
        global __static_cache
        if username in __static_cache.keys():
            self.cache = __static_cache[username]
        else:
            self.cache = LinkCache()
            __static_cache[username] = self.cache

    # PUBLIC ------------------------------------------------------------------

    def get_cookie(self):
        if self.cookie:
            return self.cookie
        return ''

    def resolve(self, url):
        ''' returns (link, name, wait_time, cookie);
            link -- is direct-download link
            name -- is the filename
            wait_time -- is the number of seconds to wait before the link activates
            cookie -- a cookie to be used when requesting the content
        '''
        cache = self.cache.resolve(url)
        if cache:
            return cache
        account_type = 'none'
        filelink = None
        filename = None

        source, cookies = get_url(url, cookie=self.get_cookie())
        cookie = None # Cookie required when accessing the URL after the wait
        if cookies:
            cookie = cookies[0]

        if source.startswith('http://'): # premium redirect
            account_type = 'premium'
            filelink = source
        else:
            account_type = self.__scrape_account_type(source)
            filelink = self.__scrape_filelink(source)

        filename = self.__scrape_filename(filelink)
        wait_time = WAIT_TIMES[account_type]
        self.cache.put(url, filelink, filename, wait_time, cookie)
        return filelink, filename, wait_time, cookie

    # PRIVATE -----------------------------------------------------------------
    
    def __login(self):
        data = {
            'username' : self.username,
            'password' : self.password,
            'login' : 1,
            'redir' : 1
            }
        url = MEGAUPLOAD_URL + '?c=login'
        response, cookies = get_url(url, data)
        self.__process_cookies(cookies)

    def __set_cookie(self, cookie):
        self.cookie = cookie

    def __process_cookies(self, cookies):
        for cookie in cookies:
            if cookie.name == 'user':# or cookie.name == 'mcpop':
                self.__set_cookie('%s=%s' % (cookie.name, cookie.value))

    def __scrape_filename(self, url):
        parts = re.split('\/+', url)
        return parts[-1]

    def __scrape_account_type(self, source):
        login = re.search('<b>Welcome</b>', source)
        premium = re.search('flashvars.status = "premium";', source)

        if login != None:
            if premium is not None:
                return 'premium'
            elif premium is None:
                return 'free'
        return 'none'

    def __scrape_filelink(self, source):
        '''try getting the premium link. if it returns none, use free link scraper.'''
        match = re.compile('<a href="(.+?)" class="down_ad_butt1">').findall(source)
        if len(match) == 0:
            match = re.compile('id="downloadlink"><a href="(.+?)" class=').findall(source)
            if len(match) > 0:
                return match[0]
            return None # give up
        return match[0]

class LinkCache:
    def __init__(self):
        self.urls = {}

    def put(self, url, link, name, wait_time, cookie):
        self.urls[url] = CacheItem(link, name, wait_time, cookie)
        
    def resolve(self, url):
        if url in self.urls.keys():
            t = time.time()
            cache_item = self.urls[url]
            if cache_item.timestamp < t - CACHE_TTL:
                print "CACHE: timeout for content %s" % url
                return None
            wait_time = cache_item.wait_time - (t - cache_item.timestamp)
            print "CACHE: HIT for content %s, wait_time = %f" % (cache_item, wait_time)
            if wait_time < 0:
                wait_time = 0
            return cache_item.link, cache_item.name, wait_time, cache_item.cookie
        return None

class CacheItem:
    def __init__(self, link, name, wait_time, cookie, timestamp=time.time()):
        self.link = link
        self.name = name
        self.wait_time = wait_time
        self.timestamp = timestamp
        self.cookie = cookie

    def __repr__(self):
        return "<%s: %s, %d, %f, %s>" % (self.name, self.link, self.wait_time, self.timestamp, self.cookie)