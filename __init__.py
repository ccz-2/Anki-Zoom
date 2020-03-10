# Anki Zoom
# v1.0 3/1/2020
# Copyright © 2020 Quip13 (random.emailforcrap@gmail.com)
# Based in part on code by Damien Elmes <anki@ichi2.net>, Roland Sieker <ospalh@gmail.com>
# Forked from https://github.com/krassowski/Anki-Zoom
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt import *
from aqt import mw
from aqt.webview import AnkiWebView, QWebEngineView
from anki.hooks import addHook, runHook, wrap
from anki.hooks import *
from anki.lang import _

zoom_step = 1.1

# After changing states, the reported mw.zoomFactor() is inaccurate
# When changing states, the zoom value (Z) is applied twice, essential applying a Z^2 zoom
# This value tracks the correct zoom displayed
zoomActual = 1

# Reflects the desired actual zoom level (what the user expects to see).
# Will deviate from zoomActual during state changes, and used to apply zoom correction
userZoomActual = 1

def zoom_in(step=None):
    if not step:
        step = zoom_step
    change_zoom(zoomActual * step)

def zoom_out(step=None):
    if not step:
        step = zoom_step
    change_zoom(zoomActual / step)

def reset_zoom(state=None, *args):
    config = mw.addonManager.getConfig(__name__)
    if not state:
        state = mw.state
    if state == 'deckBrowser':
        change_zoom( config[ 'deckBrowser_zoom_default' ] )
    if state == 'overview':
        change_zoom( config[ 'overview_zoom_default' ] )
    elif state == 'review':
        change_zoom( config[ 'review_zoom_default' ] )

def change_zoom(desired_zoomActual, fromHook=False):
    global zoomActual
    global userZoomActual
    pZoom = mw.web.zoomFactor()
    i = desired_zoomActual/zoomActual
    zoomFactor = pZoom*i
    if zoomFactor < 0.2: #documented qt bug where zoomFactor cannot exceed 5 or 1/5
        zoomFactor = 0.2
    elif zoomFactor > 5:
        zoomFactor = 5
    mw.web.setZoomFactor(zoomFactor)
    zoomActual = zoomActual * (mw.web.zoomFactor()/pZoom)
    if not fromHook:
        userZoomActual = zoomActual
    debugPrint('change_zoom, ' + str(fromHook))

def set_save_zoom(new_state, old_state, *args):
    if old_state == new_state: #skips if reset
        return
    config = mw.addonManager.getConfig(__name__)

    if old_state == 'deckBrowser':
        config[ 'deckBrowser_zoom' ] = userZoomActual
    elif old_state == 'overview':
        config[ 'overview_zoom' ] = userZoomActual
    elif old_state == 'review':
        config[ 'review_zoom' ] = userZoomActual
    mw.addonManager.writeConfig(__name__, config)

    config = mw.addonManager.getConfig(__name__)
    if new_state == 'deckBrowser':
        change_zoom( config[ 'deckBrowser_zoom' ] )
    elif new_state == 'overview':
        change_zoom( config[ 'overview_zoom' ] )
    elif new_state == 'review':
        change_zoom( config[ 'review_zoom' ] )

resetSentByZoom = False
def zoomStateChange(new_state, old_state, *args):
    global resetSentByZoom
    global zoomActual
    global userZoomActual

    def unpause():
        mw.setUpdatesEnabled(True)

    if old_state == 'startup':
        return

    if resetSentByZoom:
        resetSentByZoom = False
        QTimer.singleShot(150, unpause) #prevents flickering
        return
    elif abs(userZoomActual-zoomActual)>0.001: #does not refresh if close enough
        mw.setUpdatesEnabled(False)
        mw.web.setZoomFactor(userZoomActual**0.5)
        resetSentByZoom = True
        mw.reset() #recursion

prevZoom = mw.web.zoomFactor()
def calcActualZoom(new_state, old_state, *args):
    global zoomActual
    global prevZoom
    global currZoom
    if old_state == 'startup':
        return
    currZoom = mw.web.zoomFactor() 
    if currZoom != prevZoom:
        zoomActual = currZoom**2
    prevZoom = currZoom
    debugPrint('After Statechange')

def debugPrint(debug=""):
    #print(debug + ': ZoomValue: ' + f'{mw.web.zoomFactor():.3f}' + ' Actual: ' + f'{zoomActual:.3f}' + ' UserActual: ' + f'{userZoomActual:.3f}')
    return

# Uses QtEventListener to track wheel
class wheelListener(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.ctrl_Pushed = False
        self.numDeg = 0
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel and self.ctrl_Pushed:
            self.numDeg = self.numDeg + event.angleDelta().y()
            if self.numDeg > 110:
                zoom_in()
                self.numDeg = 0
            elif self.numDeg < -110:
                zoom_out()
                self.numDeg = 0
        elif event.type() == QEvent.KeyPress and event.key() == Qt.Key_Control:
            self.ctrl_Pushed = True
        elif event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Control:
            self.ctrl_Pushed = False
        return False
wheelListener = wheelListener()

#enables scrolling regardless of what has focus (listener installed on bottom, toolbar and main screen)
def setup_event_filters(new_state, old_state, *args): #if called before startup will throw error on linux machines
    if old_state == 'startup':
        reviewer_QWidget = mw.reviewer.web.findChildren(QWidget)[0] #undocumented method to get underlying event-handling widget of QWebView *may break in future Qt releases
        reviewer_QWidget.installEventFilter(wheelListener)

        bottom_QWidget = mw.reviewer.bottom.web.findChildren(QWidget)[0] #undocumented method to get underlying event-handling widget of QWebView *may break in future Qt releases
        bottom_QWidget.installEventFilter(wheelListener)

        toolbar_QWidget = mw.toolbar.web.findChildren(QWidget)[0] #undocumented method to get underlying event-handling widget of QWebView *may break in future Qt releases
        toolbar_QWidget.installEventFilter(wheelListener)

def add_action(submenu, label, callback, shortcut=None):
    """Add action to menu"""
    action = QAction(_(label), mw)
    action.triggered.connect(callback)
    if shortcut:
        shortcutList= []
        for i in shortcut:
            shortcutList.append(QKeySequence(i))
        action.setShortcuts(shortcutList)
    submenu.addAction(action)
    return action

def setup_menu():
    """Set up the zoom menu."""
    try:
        mw.addon_view_menu
    except AttributeError:
        mw.addon_view_menu = QMenu(_('&View'), mw)
        mw.form.menubar.insertMenu(
            mw.form.menuTools.menuAction(),
            mw.addon_view_menu
        )

    mw.zoom_submenu = QMenu(_('&Zoom'), mw)
    mw.addon_view_menu.addMenu(mw.zoom_submenu)

    add_action(mw.zoom_submenu, 'Zoom &In', zoom_in, ['Ctrl++','Ctrl+='])
    add_action(mw.zoom_submenu, 'Zoom &Out', zoom_out, ['Ctrl+-'])
    mw.zoom_submenu.addSeparator()

    add_action(mw.zoom_submenu, '&Reset', reset_zoom, ['Ctrl+0'])

def real_zoom_factor(self):
    """Use the default zoomFactor.

    Overwrites Anki's effort to support hiDPI screens.
    """
    return QWebEngineView.zoomFactor(self)

AnkiWebView.zoomFactor = real_zoom_factor

addHook("afterStateChange", calcActualZoom)
addHook("afterStateChange", zoomStateChange)
addHook("afterStateChange", set_save_zoom)
addHook("afterStateChange", setup_event_filters)

setup_menu()
