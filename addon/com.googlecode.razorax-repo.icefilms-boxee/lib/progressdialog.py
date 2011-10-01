#
# Progress Dialog for Boxee, emulating the ProgressDialog in XBMC.
#
# Setup & Syntax:
# TODO

import xbmc, mc

DIALOG_ID=14001
TITLE_ID=100
DESCRIPTION_ID=101
CANCEL_ID=102
# TODO: Progress?

class ProgressDialog:
    def create(self, title):
        self.title = title
        mc.ActivateWindow(DIALOG_ID)

    def update(self, percent, text, description):
        # do nothing ... for now
        self.progress = percent
        self.text = text
        self.description = description
        window = mc.GetWindow(DIALOG_ID)
        window.GetLabel(TITLE_ID).SetLabel(text)
        window.GetLabel(DESCRIPTION_ID).SetLabel(description)

    ''' Close the dialog
    '''
    def close(self):
        xbmc.executebuiltin("Dialog.Close(%s)" % DIALOG_ID)

    def iscanceled(self):
        # Wheter or not the pb has been cancelled
        # Not supported in v0.1 - ?
        return False
