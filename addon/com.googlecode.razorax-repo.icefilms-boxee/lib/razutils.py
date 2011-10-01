import urllib
import urllib2
import re

try: import mc
except: mc = False

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

def u2s(s):
    if type(s) == unicode:
        return s.encode('ascii', 'ignore')
    elif type(s) == str:
        return s
    elif s is None:
        return ''
    else:
        return "%s" % s # handles ints, floats etc.

def get_content_size_url(url, cookie=None, headers=None):
    ''' Sends a HTTP HEAD to the url to determine the size of the content. '''
    
def get_url(url, data=None, cookie=None, headers=None):
    ''' retrieves the content from the supplied url;return (response, cookies)
        If the url leads to a redirect, the redirect-url is returned instead of
        the content.
    '''
    print "URL: %s" % url
    value = None
    if mc and False:
        value = __get_url_mc(url, data, cookie, headers)
    else:
        value = __get_url_urllib(url, data, cookie, headers)
    print " - cookies [%s]: %s" % (len(value[1]), value[1])
    return value

def __get_cookies(cookiestring):
    ''' extracts a cookie from the cookiestring
        it seems we only get one header from mc.Http() :-(
    '''
    if cookiestring:
        return [RazCookie(cookiestring)]
    return []

def __get_url_mc(url, data=None, cookie=None, headers=None):
    ''' retrieves the content from the supplied url;return (response, cookies)
        If the url leads to a redirect, the redirect-url is returned instead of
        the content.
    '''
    http = mc.Http()
    http.SetUserAgent(USER_AGENT)
    if headers:
        for k,v in headers.items():
            http.SetHttpHeader(k, v)

    if cookie:
        http.SetHttpHeader('Cookie', cookie)

    if data:
        data = urllib.urlencode(data)
        response = http.Post(url, data)
    else:
        response = http.Get(url)

    location = http.GetHttpHeader('location')
    cookies = __get_cookies(http.GetHttpHeader('Set-Cookie'))
    #print "cookies: %s" % cookies
    if location and location != url:
        print "redirect: %s" % location
        return location, cookies
    return response, cookies

def __get_url_urllib(url, data=None, cookie=None, headers=None):
    ''' retrieves the content from the supplied url;return (response, cookies) 
        If the url leads to a redirect, the redirect-url is returned instead of
        the content.

        Uses the urllib - so you can execute get_url() without the mc module
        (i.e. for running unit tests).
    '''

    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    if headers:
        for k,v in headers.items():
            req.add_header(k, v)
    if cookie:
        # Ideally we would just use the CookieJar for this...
        # But it's broken 
        req.add_header('Cookie', cookie)
    if data:
        data = urllib.urlencode(data)
    processor = urllib2.HTTPCookieProcessor()
    response = urllib2.build_opener(processor).open(req, data)
    cookies = []
    for cookie in processor.cookiejar:
        cookies.append(cookie)
    #print "cookies: %s" % cookies
    # check for redirect (megaupload premium users)
    response_url = response.geturl()
    if response_url == url:
        content = response.read()
    else:
        content = response_url
    response.close()

    return content, cookies

class RazCookie:
    ''' Just simple name, value pairs '''
    def __init__(self, cookiestring):
        split = re.split(';', cookiestring)
        self.name = None
        self.value = None
        if split:
            self.name, self.value = re.split('=', split[0])

    def __repr__(self):
        return "%s=%s" % (self.name, self.value)
    
    def __getattr__(self, name):
        if name.lower() in ('expires', 'path', 'comment', 'domain', 'max-age', 'secure', 'version', 'httponly'):
            return None
        else:
            raise AttributeError
        