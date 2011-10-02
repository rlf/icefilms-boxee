import traceback
from time import *

import jobmanager
import mc
import xbmc

DIALOG_ID = 14010
TITLE_ID = 100
DESCRIPTION_ID = 101
ETC_ID = 102
CLOCK_ID = 20

instance = None

def load():
    ''' does nothing, for now '''

def cancel():
    ''' A feeble effort to allow the WaitDialog object to be a singleton '''
    print "cancelling wait..."
    if instance:
        instance.cancel()
    else:
        print "!! no outstanding wait !!"

class WaitDialog:
    def __init__(self, title, description):
        self.title = title
        self.description = description
        global instance
        instance = self

    # PUBLIC ------------------------------------------------------------------
    def wait(self, secs_to_wait, callback, token=None, interval=0.1):
        ''' Returns True if the wait completed, False if it was cancelled. '''
        if secs_to_wait <= 0:
            callback(True, token)
            return
        self.callback = callback
        self.token = token
        self.secs = secs_to_wait
        self.is_cancelled = False
        self.start = time()
        self.last_update = 0
        self.dialog = mc.GetWindow(DIALOG_ID)
        self.__setup_static()
        self.update(0)
        self.jobmanager = jobmanager.BoxeeJobManager(interval)
        job = WaitJob(self, interval)
        self.jobmanager.add_job(job)
        self.jobmanager.start()

    def cancel(self):
        self.is_cancelled = True
        self.__stop()
        mc.ShowDialogNotification('Wait cancelled by user')
        self.callback(False, self.token)

    def done(self):
        self.__stop()
        self.callback(True, self.token)

    def update(self, wait_time):
        #print "__update(%s)" % wait_time
        if self.is_cancelled:
            return
        if wait_time >= self.secs:
            self.done()
            return
        if round(wait_time) != self.last_update:
            self.last_update = round(wait_time)
            # Labels are cleared if (some idiot) dismisses the wait-dialog
            # with the back-button
            self.__setup_static()
            # update dynamic
            self.dialog = mc.GetWindow(DIALOG_ID)
            diff = ((self.secs - self.last_update) % 60)
            self.dialog.GetImage(CLOCK_ID).SetTexture('clock3/clock2_%i.png' % diff)
            self.dialog.GetLabel(ETC_ID).SetLabel('%i seconds remaining' % (self.secs - self.last_update))
            #print "have been waiting for %d of %d seconds" % (self.last_update, self.secs)
            
    # PRIVATE -----------------------------------------------------------------
    def __setup_static(self):
        ''' Initializes static UI components
            This is called periodically, because we cannot control the BACK key
        '''
        mc.ActivateWindow(DIALOG_ID)
        self.dialog.GetLabel(TITLE_ID).SetLabel(self.title)
        self.dialog.GetLabel(DESCRIPTION_ID).SetLabel(self.description)
        
    def __stop(self):
        if self.jobmanager:
            self.jobmanager.stop()
            self.jobmanager = None
        xbmc.executebuiltin('Dialog.Close(%d)' % DIALOG_ID)

class WaitJob(jobmanager.BoxeeJob):
    def __init__(self, dialog, interval):
        self.start = time()
        self.dialog = dialog
        jobmanager.BoxeeJob.__init__(self, 'WaitDialog', interval)
        self.error_count = 0
        self.max_error_count = 10

    def process(self):
        tdiff = time() - self.start
        try:
            self.dialog.update(tdiff)
        except Exception,e:
            # We change the UI state from another thread than the UI thread
            # ... so we must expect some exceptions
            self.error_count += 1
            self.error("ERROR: %s, ignoring it %d/%d\n%s" % (e, self.error_count, self.max_error_count, traceback.format_exc(10)))
            if self.error_count >= self.max_error_count:
                raise e

    