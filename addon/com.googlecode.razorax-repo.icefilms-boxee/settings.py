# python file for the UI settings.
import mc

SETTING_LIST_ID=600

def load():
    print "settings.load"
    global __configurations, __values, __conf, __keys, __questions
    # Config
    __conf = mc.GetApp().GetLocalConfig()
    __keys = ['megaupload.username', 'megaupload.password', 'icerss.url']
    __values = dict([(k,__conf.GetValue(k)) for k in __keys])
    __questions = {
        'megaupload.username' : 'Enter MU username',
        'megaupload.password' : 'Enter MU password',
        'icerss.url' : 'URL for icerss scraper'
    }
    __configurations = {
        'megaupload.username' : ['Megaupload account', 'megaupload_icon.png', 'Configures the username and password to be used when downloading from megaupload.com', __conf_megaupload],
        'icerss.url' : ['IceRSS JSON URL', 'url_icon.png', 'Configures the url for the JSON feed (see http://github.com/rlf/icefilms-addon for details)', __conf_icerss],
        }
    # Initialize UI
    #window = mc.GetActiveWindow()
    window = mc.GetWindow(14000)
    list = window.GetList(SETTING_LIST_ID)
    items = mc.ListItems()
    for key, values in __configurations.items():
        item = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        item.SetLabel(values[0])
        item.SetThumbnail(values[1])
        item.SetProperty('description', values[2])
        item.SetProperty('value', __values[key])
        item.SetPath(key)
        items.append(item)
        values.append(item)
        print "adding %s" % item.GetLabel()
    list.SetItems(items)
    print "done settings.load"

def set(k, v):
    __values[k] = v
    __conf.SetValue(k, v)
    if k in __configurations.keys():
        item = __configurations[k][4]
        print "found item %s for %s" % (item, k)
        item.Dump()
        item.SetProperty('value', v)

def get(key):
    if key in __values.keys():
        return __values[key]
    return None

def __get(key, ask=True):
    if ask:
        return mc.ShowDialogKeyboard(__questions[key], __values[key], key[-8:] == 'password')
    else:
        return __values[key]
    
def __conf_megaupload(item, ask=True):
    username = __get('megaupload.username', ask)
    if username:
        password = __get('megaupload.password', ask)
        if password:
            set('megaupload.username', username)
            set('megaupload.password', password)
            set('megaupload.cookie', '')

def __conf_icerss(item):
    url = __get('icerss.url')
    if url:
        set('icerss.url', url)
    
def select_setting():
    window = mc.GetActiveWindow()
    list = window.GetList(SETTING_LIST_ID)
    focused_index = list.GetFocusedItem()
    item = list.GetItem(focused_index)
    key = item.GetPath()
    if key in __configurations.keys():
        __configurations[key][4] = item
        __configurations[key][3](item)


