"""
Boxee Function Library
A Python collection of functions and classes o releive some work for boxee devs.

written by /bartsidee, 12 Sept 2011

Requres:
Python 2.4
Boxee

License:
GPLv2 - http://www.gnu.org/licenses/gpl-2.0.txt
"""

import os
import mc
import re

import unicodedata
import time
import stat
import traceback
import binascii
import bz2

from operator import itemgetter, attrgetter

try:    from hashlib import md5
except: from md5 import md5

try:    import cPickle as pickle
except: import pickle

def urlopen(url, **kwargs):
    """
    Action a http request
    # url - reqest url
    # params - dict,    extra http parameters (optional)
    #        xhr       - boolean,  make a xhr ajax request
    #        post      - dict,     parameters to POST if empty a GET request is executed
    #        cookie    - string,   send cookie data with request
    #        useragent - string,   send custom useragent with request
    # cache - instance, possible to feed a cache instance
    # age   - int,      maximum age in seconds of cached item
    """

    http = mc.Http()
    http.SetUserAgent("Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")
    http.SetHttpHeader('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')

    if kwargs.get('cache', False):
        cache = kwargs['cache']
        if kwargs.get('age', False):
            data = cache.get(url, kwargs['age'])
        else:
            data = cache.get(url)
        if data:
            return data

    params = {}
    if kwargs.get('params', False):
        params = kwargs['params']

    if params.get('xhr', False):
        http.SetHttpHeader('X-Requested-With', 'XMLHttpRequest')
    if params.get('cookie', False):
        http.SetHttpHeader('Cookie', params['cookie'])
    if params.get('useragent', False):
        http.SetUserAgent(params['useragent'])

    if params.get('post', False):
        data = http.Post(url, params['post'])
    else:
        data = http.Get(url)

    if kwargs.get('cache', False):
        cache.set(url, data)

    return data

def encode_ASCII(string):
    """
    Convert a string to ASCII and ignore non ASCII characters
    # string - string to check
    """

    return unicodedata.normalize('NFKD', string.decode('utf-8')).encode('ascii','ignore')

def encode_UTF8(string):
    """
    Convert a string to UTF-8
    # string - string to check
    """

    try:
        return string.encode('utf-8', 'ignore')
    except UnicodeDecodeError:
        return string

def select_sublist(list_of_dicts, **kwargs):
    """
    Get sublist from list of dicts based on keys in dict
    # list_of_dicts  - list, big list containing unique dictonaries
    # arguments      - key/arg, set keyword + argument to match those in the dict
    """

    return [dict(d) for d in list_of_dicts
            if all(d.get(k)==kwargs[k] for k in kwargs)]

def sort_dict(list, key, reverse=False):
    """
    Sort list of dicts based on key
    # list           - list,    big list containing unique dictonaries
    # key            - strin,   key in dict to sort the list on
    # reverse        - boolean, reverse order                            (optional)
    """

    return sorted(list, key=itemgetter(key), reverse=reverse)

def sort_instance(list, key, reverse=False):
    """
    Sort list of instances based on attribute
    # list           - list,    big list containing unique instances
    # key            - string,  key in dict to sort the list on
    # reverse        - boolean, reverse order                            (optional)
    """

    return sorted(list, key=attrgetter(key), reverse=reverse)

def getFileExtension(path):
    """
    Try to find the filextension of an url
    # path - string,  path/url to extract the extension from
    """

    dict = {'http://www.youtube.com':'avi', 'flyupload.com':'mp4'}

    ext = [dict[source] for source in dict.keys() if source in path]
    if len(ext) > 0:
        ext = ext[0][:3]
    else:
        url_stripped = re.sub('\?.*$', '', path) # strip GET-method args
        re_ext = re.compile('(\.\w+)$')          # find extension
        match = re_ext.search(url_stripped)
        if match is None:
            ext_pos = path.rfind('.')            #find last '.' in the string
            if ext_pos != -1:
                ext_pos2 = path.rfind('?', ext_pos) #find last '.' in the string
                if ext_pos2 != -1:
                    ext = path[ext_pos+1:ext_pos2][:3]
                else:
                    ext = path[ext_pos+1:][:3]
            else:
                ext = ''
            if ext != '':
                ext = '.' + ext[:3]
            else:
                ext = None
        else:
            ext = match.group(1)
    return ext


def slugify(string):
    """
    Converts string (url) to be used as path name
    # string   - string,  string to be slugified
    """

    string = string.strip().lower()
    return re.sub(r'[\s_-]+', '-', string)[:41]


class storage:
    """
    Saves data to disk or persistant storage
    """
    
    def __init__(self, eol = 86400):
        self.path       = self.construct()
        self.eol        = eol
        self.clean()

    def construct(self):
        """sets cache dir in temp folder"""
        id     = mc.GetApp().GetId()
        prefix = "cache_"
        tmp    = mc.GetTempDir()
        path   = os.path.join(tmp, prefix + id)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def clean(self):
        """removes only data that has been expired (EOL)"""
        expire = time.time() - self.eol
        for item in os.listdir(self.path):
            pointer = os.path.join(self.path, item)
            if os.path.isfile(pointer):
                timestamp = os.path.getmtime(pointer)
                if timestamp <= expire:
                    os.chmod(pointer, stat.S_IWUSR)
                    os.remove(pointer)

    def empty(self, **kwargs):
        """
        removes all data from cache
        # persistent - boolean, if true empties all persistent data (optional)
        """
        for root, dirs, files in os.walk(self.path, topdown=False):
            for name in files:
                filename = os.path.join(root, name)
                os.chmod(filename, stat.S_IWUSR)
                os.remove(filename)
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        if kwargs.get('persistent', False):
            mc.GetApp().GetLocalConfig().ResetAll()


    def md5(self, string):
        """returns md5 hash of string"""
        return md5(string).hexdigest()

    def get(self, id, **kwargs):
        """
        Gets data from storage
        # id         - string, unique string to identify data
        # age        - int,    if set checks if data is not older then age in seconds (optional)
        # persistent - boolean, if true it saves the data persistent                  (optional)
        """
        if kwargs.get('age'):
            age = kwargs['age']
        else:
            age = 0

        if kwargs.get('persistent', False):
            pointer = self.md5(id)
            expire  = time.time() - age

            try:
                raw       = bz2.decompress(binascii.unhexlify(mc.GetApp().GetLocalConfig().GetValue(pointer)))
                timestamp = float(mc.GetApp().GetLocalConfig().GetValue(pointer+"_timestamp"))
                if timestamp >= expire or age == 0:
                    return pickle.loads(raw)
            except:
                print traceback.format_exc()
        else:
            pointer = os.path.join( self.path, self.md5(id) )
            expire  = time.time() - age

            if os.path.isfile(pointer):
                timestamp = os.path.getmtime(pointer)
                if timestamp >= expire or age == 0:
                    try:
                        fp = open( pointer)
                        data = pickle.load(fp)
                        fp.close()
                        return data
                    except:
                        print traceback.format_exc()

        return False

    def set(self, id, data, **kwargs):
        """
        Saves data to storage
        # id   - string,   unique string to identify data
        # data - any type, data to cache (string, int, list, dict)
        # persistent - boolean, if true it saves the data persistent    (optional)
        """

        if kwargs.get('persistent', False):
            pointer = self.md5(id)
            try:
                raw = pickle.dumps(data)
                mc.GetApp().GetLocalConfig().SetValue(pointer, binascii.hexlify(bz2.compress(raw)))
                mc.GetApp().GetLocalConfig().SetValue(pointer+"_timestamp", str(time.time()))
                return True
            except:
                print traceback.format_exc()

        else:
            pointer = os.path.join( self.path, self.md5(id) )
            try:
                fp = open( pointer, "wb" )
                pickle.dump(data, fp)
                fp.close()
                return True
            except:
                print traceback.format_exc()

        return False

### Function to support python < 2.5
def all(iterable):
    for element in iterable:
        if not element:
            return False
    return True