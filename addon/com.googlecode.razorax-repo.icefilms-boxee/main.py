import traceback
# main entry point for the icefilms-boxee app
#
# TODO:
#  - Pagination (more than the first 12 items)
#  - Search
#  - More sorting options than Popular +(Rating, Release, Added)
#  - Download to SMB drive (file-manager)
#  - Queued downloads (download-manager)
#  - Subtitle support (subscene.com? opensubtitles.org)
import re
from time import *

import icerss
import icefilms
import mc
import megaupload
from lib.razutils import *
import settings
import lib.waitdialog as waitdialog
import lib.playerwatchdog as playerwatchdog

# Lists
MAIN_LIST_ID = 100
GENRE_LIST_ID = 200
MOVIES_LIST_ID = 300
POPUP_GROUP_ID = 1000
SOURCES_LIST_ID = 990
PROGRESS_ID = 777
PROGRESS_LABEL_ID = 778

# Title
TITLE_LBL_ID = 10
TITLE_IMG_ID = 11
__windows = {
    'Main' : {'id': MAIN_LIST_ID, 'img': ''},
    'Movies' : {'id' : GENRE_LIST_ID, 'custom' : {'category' : 'movies'}},
    'TV Shows' : {'id' : GENRE_LIST_ID, 'custom' : {'category' : 'tv'}},
    'Music' : {'id' : GENRE_LIST_ID, 'custom' : {'category' : 'music'}},
    'Settings' : {'id' : settings.SETTING_LIST_ID},
    '_Genres_' : {'id' : MOVIES_LIST_ID}, # Just so we "clean" them
    '_Popup_' : {'id' : POPUP_GROUP_ID},
    }
__menu = {
    MAIN_LIST_ID : {
        GENRE_LIST_ID : {
            MOVIES_LIST_ID : {
                POPUP_GROUP_ID : { SOURCES_LIST_ID : None }
                }
            },
        settings.SETTING_LIST_ID : {}
    }
}

__icefilms = None
def __get_icefilms():
    global __icefilms
    # TODO: Handle changes to the settings.
    if not __icefilms:
        iceurl = mc.GetApp().GetLocalConfig().GetValue('icerss.url')
        if not iceurl:
            mc.ShowDialogNotification('Invalid IceURL supplied, check Settings menu')
        else:
            ice = icerss.IceRSS(iceurl)
            __icefilms = icefilms.IceFilms(ice)
    return __icefilms

def focus(control):
    ''' Tries a bit harder to set focus than the normal focus function. '''
    #print "focus(%s)" % control
    control.SetFocus()
    t = time()
    now = t
    while not control.HasFocus() and now - t < 0.7:
        control.SetVisible(True)
        control.SetFocus()
        if not control.HasFocus():
            sleep(0.1)
        now = time()
    if now - t > 0.7:
        print "ERROR: Bailed out trying to set focus to %s" % control
    # If control is a list... we better check the state of the current item...
    try:
        focusIndex = control.GetFocusedItem()
        focusItem = control.GetItem(focusIndex)
        if focusItem.GetProperty('state') == 'showing':
            print "FIXING: Focused control should already have had focus..."
            focusItem.SetProperty('state', '')
    except:
        pass # It wasn't a list
    return control.HasFocus()

def dump(item):
    print "item: %s" % item
    print " - label : %s" % item.GetLabel()
    print " - state : %s" % item.GetProperty('state')
    print " - category : %s" % item.GetProperty('category')
    print " - path : %s" % item.GetPath()
    
__titles = []
__last_img = None
def __set_title(item=None):
    #print "__set_title(%s)" % item
    global __titles, __last_img
    window = mc.GetActiveWindow()
    label = window.GetLabel(TITLE_LBL_ID).GetLabel()
    img = __last_img
    if type(item) == str:
        label = item
        img = '-'
        __titles = []
    elif item == None and len(__titles) > 0:
        label, img = __titles.pop()
    elif item != None:
        __titles.append((label, img))
        if label != 'Main':
            label += ' // ' + item.GetLabel()
        else:
            label = item.GetLabel()
        img = item.GetThumbnail()

    # Actually set the new title
    window.GetLabel(TITLE_LBL_ID).SetLabel(label)
    window.GetImage(TITLE_IMG_ID).SetTexture(img)
    # Image control doesn't support GetTexture(), so we must keep track separately
    __last_img = img
    
def __show(label, item):
    item.SetProperty('state', 'showing')
    wnd = __windows[label]
    if wnd.has_key('custom'):
        for k, v in wnd['custom'].items():
            item.SetProperty(k, v)
        item.Dump()
    __set_title(item)
    list = mc.GetActiveWindow().GetControl(wnd['id'])
    focus(list)

def ask_exit():
    response = mc.ShowDialogConfirm("Exit", "Do you want to exit?", "No", "Yes")
    if response:
        window = mc.GetActiveWindow()
        window.ClearStateStack(False)
        mc.ActivateWindow(10482) # Apps

__last_search = ''
def search():
    term = mc.ShowDialogKeyboard('Search:', __last_search)
    if term:
        mc.ShowDialogNotification("Not yet implemented")
        
def select_main():
    mc.ShowDialogWait()
    window = mc.GetActiveWindow()
    list = window.GetList(MAIN_LIST_ID)
    items = list.GetItems()
    lastSelected = list.GetFocusedItem()
    item = items[lastSelected]
    label = item.GetLabel()
    if label in __windows.keys():
        print "showing : %s" % item.GetLabel()
        __show(label, item)
    elif label == 'Search':
        search()
    elif label == 'Exit':
        ask_exit()
    else:
        print "No window defined yet for %s" % label
    #dump(item)
    mc.HideDialogWait()

def __hide(item):
    item.SetProperty('state', '')
    if item.GetLabel() in __windows.keys():
        wnd = __windows[item.GetLabel()]
        if wnd and wnd.has_key('custom'):
            for k in wnd['custom'].keys():
                item.SetProperty(k, '')

def hide_main():
    mc.ShowDialogWait()
    window = mc.GetActiveWindow()
    list = window.GetList(MAIN_LIST_ID)
    items = list.GetItems()
    lastSelected = list.GetFocusedItem()
    item = items[lastSelected]
    if item.GetProperty('state') == 'showing':
        print "hiding : %s" % item.GetLabel()
        __hide(item)
    else:
        print "ERROR: trying to hide main with nothing being shown! [%s]" % item.GetLabel()
    __set_title()
    focus(list)
    list.SetFocusedItem(lastSelected)
    mc.HideDialogWait()

def get_type():
    list = mc.GetActiveWindow().GetList(MAIN_LIST_ID)
    index = list.GetFocusedItem()
    item = list.GetItem(index)
    if item and item.GetLabel() in __windows.keys():
        wnd = __windows[item.GetLabel()]
        if 'custom' in wnd.keys():
            return wnd['custom']['category']
    return None

def get_genre():
    list = mc.GetActiveWindow().GetList(GENRE_LIST_ID)
    index = list.GetFocusedItem()
    item = list.GetItem(index)
    if item and item.GetLabel() == 'All':
        return '1'
    elif item:
        return item.GetLabel().lower()
    return None

def create_part_item(type, part):
    ''' takes a tuple of (url, name) and generates a ListItem '''
    item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_FEATURE_FILM)
    item.SetLabel(part[1])
    item.SetPath(part[0])
    thumb = '%s.png' % re.sub('[^a-zA-Z0-9]+', '_', type)
    item.SetProperty('type', thumb)
    #thumb = 'media/%s.png' % re.sub('[^a-zA-Z0-9]+', '_', type)
    item.SetThumbnail(thumb)
    return item

def __hide_list(list_id):
    mc.ShowDialogWait()
    list = mc.GetActiveWindow().GetList(list_id)
    lastSelected = list.GetFocusedItem()
    item = list.GetItem(lastSelected)
    if item.GetProperty('state') == 'showing':
        print "hiding : %s" % item.GetLabel()
        __hide(item)
    else:
        print "ERROR: trying to hide genres with nothing being shown! [%s]\n%s" % (item.GetLabel(), traceback.format_exc(10))
    __set_title() # go back
    focus(list)
    list.SetFocusedItem(lastSelected)
    mc.HideDialogWait()

def hide_genre():
    __hide_list(GENRE_LIST_ID)

def select_genre():
    print ">> select_genre"
    mc.ShowDialogWait()
    type = get_type()
    genre = get_genre()
    if not (type and genre):
        mc.ShowDialogNotification('Type or genre is invalid')
        return

    icefilms = __get_icefilms()
    # TODO: pagination
    list = mc.GetActiveWindow().GetList(GENRE_LIST_ID)
    index = list.GetFocusedItem()
    item = list.GetItem(index)
    item.SetProperty('state', 'showing')
    movie_list = mc.GetActiveWindow().GetList(MOVIES_LIST_ID)
    focus(movie_list)
    __set_title(item)
    fetch_callback(0, 1)
    if not icefilms.get_list(movie_list, type, genre, fetch_callback):
        mc.ShowDialogNotification('No movies found')
        hide_genre() #??
    mc.HideDialogWait()
    print "<< select_genre"

def select_movie():
    mc.ShowDialogWait()
    # TODO: Progressbar?
    window = mc.GetActiveWindow()
    list = window.GetList(MOVIES_LIST_ID)
    movieitem = list.GetItem(list.GetFocusedItem())

    ice = __get_icefilms()
    url = movieitem.GetPath()
    
    sources = ice.get_sources(movieitem.GetPath())
    if sources:
        # alternating backgrounds
        sourcelist = window.GetList(SOURCES_LIST_ID)
        items = mc.ListItems()
        # TODO: Sorting
        sourcenum = 1
        oldsource = 'initial'
        for quality, parts in sources:
            for part in parts:
                item = create_part_item(quality, part)
                if not part[1].startswith(oldsource):
                    sourcenum += 1
                else:
                    # Same as previous - remove the icon
                    item.SetProperty('type', '')
                item.SetProperty('row', str(sourcenum % 2))
                oldsource = part[1][:3]
                item.Dump()
                items.append(item)
        sourcelist.SetItems(items)
        movieitem.SetProperty('state', 'showing')
        focus(window.GetControl(POPUP_GROUP_ID))
        focus(window.GetControl(SOURCES_LIST_ID))
    else:
        mc.ShowDialogOk('Error Scraping Icefilms.Info', 'Could not find any sources for %s[CR]Either none matched your filters, icefilms changed design, or the site is down.[CR]Please try again later' % movieitem.GetLabel())
    mc.HideDialogWait()

def hide_popup():
    window = mc.GetActiveWindow()
    list = window.GetList(MOVIES_LIST_ID)
    movieitem = list.GetItem(list.GetFocusedItem())
    movieitem.SetProperty('state', '')
    # Somehow... this isn't enough - it's "reshown" once the player emerges
    window.GetControl(POPUP_GROUP_ID).SetVisible(False)
    focus(list)

def player_callback(success, token):
    print "PLAYER CALLBACK: just for fun: %s" % mc.Http().GetHttpResponseCode()
    if not success:
        mc.ShowDialogOk('Limit Reached', 'The player could not play the source[CR]This usually indicate that you have reached your download-limit at MegaUpload.[CR]Please try again later')
        
def waitdialog_callback(success, token):
    print "WAIT CALLBACK: done waiting - %s, %s" % (success, token)
    mc.HideDialogWait()
    if success:
        movieitem = mc.ListItem(mc.ListItem.MEDIA_VIDEO_FEATURE_FILM)
        movieitem.SetPath(token[0])
        movieitem.SetTitle(token[1])
        player = mc.Player(True)
        playerwatchdog.PlayerWatchDog(player, player_callback, movieitem)
        # TODO: Figure out how to get the cookie from the token into the player...
        mc.GetActiveWindow().PushState() # A feeble attempt at getting (back) from the player to work...
        player.Play(movieitem)

def fetch_callback(*vargs):
    if len(vargs) == 1: # Boolean
        print "Fetch returned: %s" % vargs[0]
        #mc.GetActiveWindow().GetImage(PROGRESS_ID).SetTexture('progress/100.png')
        mc.GetActiveWindow().GetImage(PROGRESS_ID).SetVisible(False)
    elif len(vargs) == 2: # offset, count
        mc.GetActiveWindow().GetLabel(PROGRESS_LABEL_ID).SetLabel('%i of %i' % (vargs[0], vargs[1]))
        ratio = round(vargs[0]*10.0 / vargs[1])
        ratio *= 10
        print "Progress %i of %i (%s)" % (vargs[0], vargs[1], ratio)
        mc.GetActiveWindow().GetImage(PROGRESS_ID).SetVisible(True)
        mc.GetActiveWindow().GetImage(PROGRESS_ID).SetTexture('progress/%i.png' % ratio)
        
def select_source():
    mc.ShowDialogWait()
    window = mc.GetActiveWindow()
    list = window.GetList(SOURCES_LIST_ID)
    sourceitem = list.GetItem(list.GetFocusedItem())
    username = settings.get('megaupload.username')
    password = settings.get('megaupload.password')
    cookie = settings.get('megaupload.cookie')
    print "MU: %s, %s, %s" % (username, password, cookie)
    mu = megaupload.MegaUpload(username, password, cookie)
    settings.set('megaupload.cookie', mu.get_cookie())
    link, name, wait, cookie = mu.resolve(sourceitem.GetPath())
    hide_popup()
    wd = waitdialog.WaitDialog('Megaupload', 'Waiting for link to activate')
    wd.wait(wait, waitdialog_callback, (link, name, cookie))

def __get_list(window, id):
    try:
        return window.GetList(id)
    except:
        return None
    
def __restore_menu(window, menu, is_showing=False):
    focus_cmp = None
    for id, children in menu.items():
        list = __get_list(window, id)
        is_showing = False
        if list:
            list.SetVisible(False) # Hide to begin with...
            items = list.GetItems()
            if items:
                for item in items:
                    if item.GetProperty('state') == 'showing':
                        focus_cmp = list
                        is_showing = True
                        break
        else:
            list = window.GetControl(id)
            list.SetVisible(False)
        if children:
            child_focus = __restore_menu(window, children, is_showing)
            if child_focus:
                focus_cmp = child_focus
            elif is_showing:
                focus_cmp = window.GetControl(children.values()[0])
    return focus_cmp

__initialized = False
def load():
    print "main.load"
    global __initialized
    if __initialized:
        print "skipping load (we already are initialized)"
        return
    settings.load()
    window = mc.GetActiveWindow()
    window.GetControl(1).SetVisible(False)
    focus_control = __restore_menu(window, __menu)
    if focus_control:
        print "SETTING focus in LOAD"
        focus(focus_control)
    else:
        __set_title('Main')
        window.GetList(MAIN_LIST_ID).SetVisible(True)
    window.GetControl(1).SetVisible(True)
    __initialized = True

if __name__ == '__main__':
    mc.ActivateWindow(14000)
