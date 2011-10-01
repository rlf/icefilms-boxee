import traceback
# Module for scraping the megaupload links from icefilms.info
# Primarily extracted from default.py of the icefilms-xbmc addon
#
# TODO
#   - support doing HEADs to get file-sizes? (perhaps do this in a worker?)
#   - support RECAPTCHA (see default.py in icefilms-xbmc)
#   - support filtering on quality (i.e. Only HD)
#
# NOTES
#   - doesn't scrape for DVDScr (who would want to see it anyway?)
#   - doesn't support 2shared
#
import copy
import random
import re
import urllib

from lib.razutils import *
import lib.razutils as razutils

import lib.jobmanager as jobmanager

ICEFILMS_URL = 'http://www.icefilms.info/'
ICEFILMS_AJAX = ICEFILMS_URL + 'membersonly/components/com_iceplayer/video.phpAjaxResp.php'
ICEFILMS_REFERRER = 'http://www.icefilms.info'
HD_720P = 'HD 720p'
DVDRIP = 'DVDRip'
DVDR5 = 'DVD R5/R6'
QUALITY_VALUES = { HD_720P : 0, DVDRIP : 1, DVDR5 : 2}

def _IceFilms__cmp_sources(x, y):
    ''' compares sources, highest quality has lowest value '''
    return QUALITY_VALUES[x[0]] - QUALITY_VALUES[y[0]]

def _IceFilms__cmp_parts(x, y):
    ''' compares parts, lowest source comes first, then lowest part '''
    return cmp(x[1], y[1])

def get_url(url, data=None, cookie=None, headers={}):
    ''' modifies headers etc. for use with icefilms.info '''
    headers['Referer'] = ICEFILMS_REFERRER
    return razutils.get_url(url, data, cookie, headers)

class IceFilms:
    ''' Scrapes links from icefilms.info, and propagates meta-information
        requests to the IceRSS object.
    '''

    def __init__(self, icerss):
        self.icerss = icerss
        self.jobmanager = jobmanager.BoxeeJobManager(1)
        self.jobmanager.daemon = True
        self.jobmanager.setDaemon(True)
        self.jobmanager.start() # No jobs to begin with...
        self.job = None
        self.jobcount = 0
        
    # PUBLIC ------------------------------------------------------------------

    def abort(self):
        ''' Aborts any on-going jobs (i.e. get_list). '''
        if self.job:
            self.jobmanager.remove_job(self.job)
            self.job.abort()
            self.job = None

    def get_list(self, movie_list, type, genre, callback):
        self.abort()
        self.jobcount += 1
        movie_list.SetItems(mc.ListItems())
        self.job = FetchJob(self.jobcount, self, callback, movie_list, (type, genre))
        self.jobmanager.add_job(self.job)
        return True

    def get_sources(self, uri):
        ''' returns all sources for the supplied link in a sorted list of tuples.
            first item is the key (quality/type) and second is a list of parts.
            the suppied link should be an ip.php?v=<vidid> type of link
        '''
        url = ICEFILMS_URL + uri
        self.url = url
        try:
            source, cookies = get_url(url)

            mirrorurl = self.__scrape_mirrorurl(source)
            mirrorsource, cookies = get_url(mirrorurl)
            cookie = None
            if cookies:
                cookie = '%s=%s' % (cookies[0].name, cookies[0].value)
            sources = self.__scrape_sources(mirrorsource, cookie)
            return sorted(sources.items(), __cmp_sources)
        except:
            traceback.print_exc(20)
            return None # Robust = Icefilms down, or changed design

    def get_seasons(self, uri):
        ''' return all the seasons. '''
        return self.icerss.get_seasons(uri)
        
    def is_tvshow(self, uri):
        ''' returns true if uri is a tv-show (and get_seasons) should be called.
        '''
        return re.match('tv/series/.*', uri);

    # PRIVATE -----------------------------------------------------------------

    def __scrape_mirrorurl(self, source):
        ''' return a link to the mirrors '''
        match = re.compile('/membersonly/components/com_iceplayer/(.+?)" width=').findall(source)
        if len(match) > 0:
            m = match[0]
            m = re.sub('%29', ')', m)
            m = re.sub('%28', '(', m)
            return ICEFILMS_URL + 'membersonly/components/com_iceplayer/' + m
        raise "No ice_player found in content from %s" % self.url

    def __scrape_sources(self, source, cookie):
        ''' return a dict of the sources. '''
        sources = {}
        # extract the ingredients used to generate the XHR request
        #
        # set here:
        #
        #     iqs: not used?
        #     url: not used?
        #     cap: form field for recaptcha? - always set to empty in the JS
        #     sec: secret identifier: hardwired in the JS
        #     t:   token: hardwired in the JS
        #
        # set in GetSource:
        #
        #     m:   starts at 0, decremented each time a mousemove event is fired e.g. -123
        #     s:   seconds since page loaded (> 5, < 250)
        #     id:  source ID in the link's onclick attribute (extracted in PART)
        args = {
            'iqs': '',
            'url': '',
            'cap': ''
        }

        sec = re.search("f\.lastChild\.value=\"([^']+)\",a", source).group(1)
        t   = re.search('"&t=([^"]+)",', source).group(1)

        args['sec'] = sec
        args['t'] = t

        # Scrape number of sources...
        dvdrips = re.compile('<div class=ripdiv><b>DVDRip / Standard Def</b>(.+?)</div>').findall(source)
        for scrape in dvdrips:
            sources[DVDRIP] = self.__scrape_parts(source, scrape, args, cookie)
        hds = re.compile('<div class=ripdiv><b>HD 720p</b>(.+?)</div>').findall(source)
        for scrape in hds:
            sources[HD_720P] = self.__scrape_parts(source, scrape, args, cookie)
        dvdr5 = re.compile('<div class=ripdiv><b>R5/R6 DVDRip</b>(.+?)</div>').findall(source)
        for scrape in dvdr5:
            sources[DVDR5] = self.__scrape_parts(source, scrape, args, cookie)
        return sources

    def __scrape_parts(self, source, scrape, args, cookie):
        ''' scrapes the part-links out of the source; return a list of links '''
        # Since we have no clue, as to what ordering the sources come in...
        # (we could beutifulsoupt it... but... let's just copy-paste)
        parts = []
        for i in range(1, 21):
            part = self.__scrape_part(source, i, scrape, args, cookie)
            if part:
                # append the two lists
                parts += part
        return sorted(parts, __cmp_parts)

    def __scrape_part(self, source, sourcenum, scrape, args, cookie):
        ''' scrapes the parts out for the specified source; return a list of
            tuples containing (url, name)
        '''
        #check if source exists
        sourcenumber = str(sourcenum)
        sourcestring = 'Source #%d' % sourcenum
        if not re.search(sourcestring, scrape):
            return False # Bail-out
        
        multi_part = re.search('<p>Source #' + sourcenumber + ':', scrape)

        parts = []
        if multi_part:
            #print sourcestring+' has multiple parts'
            #get all text under source if it has multiple parts
            multi_part_source = re.compile('<p>Source #' + sourcenumber + ': (.+?)PART 1(.+?)</i><p>').findall(scrape)

            #put scrape back together
            for sourcescrape1, sourcescrape2 in multi_part_source:
                scrape = sourcescrape1 + 'PART 1' + sourcescrape2
                pair = re.compile("onclick='go\((\d+)\)'>PART\s+(\d+)").findall(scrape)
                for id, partnum in pair:
                    url = self.__get_source(id, args, cookie)
                    # check if source is megaupload or 2shared, and add all parts as links
                    ismega = re.search('\.megaupload\.com/', url)

                    if ismega:
                        partname = 'Part %s/%s' % (partnum, len(pair))
                        fullname = '#%d | %s' % (sourcenum, partname)
                        parts.append((url, fullname))

        # if source does not have multiple parts...
        else:
            # print sourcestring+' is single part'
            # find corresponding '<a rel=?' entry and add as a one-link source
            source5 = re.compile('<a\s+rel=' + sourcenumber + '.+?onclick=\'go\((\d+)\)\'>Source\s+#' + sourcenumber + ':').findall(scrape)
            # print source5
            for id in source5:
                url = self.__get_source(id, args, cookie)
                ismega = re.search('\.megaupload\.com/', url)
                if ismega:
                    # print 'Source #'+sourcenumber+' is hosted by megaupload'
                    fullname = '#%d | Full' % (sourcenum)
                    parts.append((url, fullname))
        return parts

    def __get_source(self, id, args, cookie):
        m = random.randrange(100, 300) * -1
        s = random.randrange(5, 50)
        params = copy.copy(args)
        params['id'] = id
        params['m'] = m
        params['s'] = s
        body, cookies = get_url(ICEFILMS_AJAX, data = params, cookie = cookie)
        match = re.search('url=(http[^&]+)', body)
        if match:
            source = match.group(1)
            url = urllib.unquote(source)
        return url
    
    def _create_movie_item(self, movie):
        print "create_movie_item: %s" % movie
        item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_FEATURE_FILM)
        poster = None
        if u'id' in movie:
            item.SetLabel(u2s(movie[u'title']))
            poster = u2s(movie[u'poster'])
            item.SetThumbnail(poster)
            # TODO: Support more than english
            item.SetProperty('plot', u2s(movie[u'plot'][u'en']))
            rating = movie[u'rating'] # 0-5
            rating = round(rating * 2)*10/2 # 0,5,10...,50
            item.SetProperty('stars', u2s(rating))
        else:
            print "No meta-info for %s" % movie
            item.SetLabel(u2s(movie[u'name']))
        if poster == 'N/A' or poster == 'N\\/A' or not poster:
            item.SetProperty('noposter', 'true')
        item.SetPath(u2s(movie[u'url']))
        return item

class FetchJob(jobmanager.BoxeeJob):
    ''' A thread used for fetching movies "behind the scenes" '''
    def __init__(self, jobid, icefilm, callback, movie_list, args):
        jobmanager.BoxeeJob.__init__(self, 'FetchJob-%i' % jobid, 1)
        self.icefilm = icefilm
        self.movie_list = movie_list
        self.args = args
        self.kwargs = {'type' : args[0], 'genre' : args[1]}
        self.count = 12
        self.offset = 0
        self.aborted = False
        self.callback = callback

    def abort(self):
        self.aborted = True
        
    def process(self):
        try:
            list = self.movie_list
            if list.IsVisible() and self.offset < self.count:
                # fetch next batch
                self.kwargs['offset'] = self.offset
                movies = self.icefilm.icerss.get_list(**self.kwargs)
                if movies and not self.aborted:
                    self.count = movies['count']
                    self.callback(self.offset, self.count)
                    items = list.GetItems()
                    for m in movies['movies']:
                        item = self.icefilm._create_movie_item(m)
                        items.append(item)
                    mc.ShowDialogWait()
                    focus = list.GetFocusedItem()
                    list.SetItems(items)
                    list.SetFocusedItem(focus)
                    mc.HideDialogWait()
                self.offset += 12
                self.callback(self.offset, self.count)
            else:
                print '%s: Completed [%d]' % (self.name, self.count)
                self.icefilm.jobmanager.remove_job(self)
                self.callback(not self.aborted)
        except Exception, e:
            traceback.print_exc(10)
            raise e