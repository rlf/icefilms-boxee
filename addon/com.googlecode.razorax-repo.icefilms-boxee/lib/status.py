# status.py - status methods
import mc, xbmc, math

DIALOG_ID = 14020
STATUS_ID = 100
PROGRESS_ID = 600

_msg, _ratio  = '', 0
def error(msg):
    print "%s" % msg
    mc.ShowDialogNotification("%s" % msg)

def status(msg, progress=0, max=0):
    global _ratio, _msg
    ratio = 0
    if max > 0:
        ratio = math.ceil(progress*10/max)/2 # number between 0-5 with increments of .5
    if _msg == msg and _ratio == ratio:
        # no need to update - no additional information
        return
    mc.ActivateWindow(DIALOG_ID)
    window = mc.GetWindow(DIALOG_ID)
    label = window.GetLabel(STATUS_ID)
    image = window.GetImage(PROGRESS_ID)
    label.SetLabel(msg)
    if max:
        texture = 'stars_%02i.png' % (ratio * 10)
        image.SetTexture(texture)
        image.SetVisible(True)
    else:
        image.SetVisible(False)
    _msg = msg
    _ratio = ratio

def info(msg):
    mc.ShowDialogNotification(msg)

def error(msg):
    mc.ShowDialogOk("Error", msg)

def hideWaitDialog():
    xbmc.executebuiltin('Dialog.Close(%i)' % DIALOG_ID)
    xbmc.executebuiltin('Dialog.Close(%i)' % 14001) # ProgressDialog
    mc.HideDialogWait()
