# Anki Zoom
# v1.2 3/10/2020
# Copyright (c) 2020 Quip13 (random.emailforcrap@gmail.com)
# Based in part on code by Damien Elmes <anki@ichi2.net>, Roland Sieker <ospalh@gmail.com> and github.com/krassowski
# Big thanks to u/Glutanimate and u/yumenogotoshi for code suggestions
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt import *
from aqt import mw
from aqt.reviewer import Reviewer
from aqt.webview import AnkiWebView, QWebEngineView
from aqt.qt import QEvent, Qt
from anki.hooks import addHook, runHook, wrap
from anki.hooks import *
from anki.lang import _

xzoom = open(os.path.join(os.path.dirname(__file__), 'panzoom_az.js')).read()
imgZoom = open(os.path.join(os.path.dirname(__file__), 'img_zoom.js')).read()

def reviewer_initWeb_wrapper(func):
	def _initWeb(*args):
		func()
		mw.reviewer.web.eval(xzoom)
		mw.reviewer.web.eval(imgZoom)
		setImgZoom()
	return _initWeb

mw.reviewer._initWeb = reviewer_initWeb_wrapper(mw.reviewer._initWeb)

def toggle_img_zoom():
	setImgZoom()
	config = mw.addonManager.getConfig(__name__)
	config[ 'img_zoom_enabled' ] = img_zoom.isChecked()
	mw.addonManager.writeConfig(__name__, config)

def setImgZoom():
	if mw.state == 'review':
		if img_zoom.isChecked():
			mw.reviewer.web.eval("enableImgZoom();") #must wait until reviewer initialized before enabling
		else:
			mw.reviewer.web.eval("disableImgZoom();")

def configUpdated(*args):
	global scrl_threshold
	global zoom_step
	global config
	config = mw.addonManager.getConfig(__name__) #can be moved out of func for performance but config will not update automatically
	scrl_threshold = config[ 'scroll_sensitivity' ]
	zoom_step = config[ 'zoom_step' ]

configUpdated()
mw.addonManager.setConfigUpdatedAction(__name__, configUpdated)

def zoom_in(step=None):
	if not step:
		step = zoom_step
	change_zoom_by(step)

def zoom_out(step=None):
	if not step:
		step = zoom_step
	change_zoom_by(1 / step)

def reset_zoom(state=None, *args):
	if not state:
		state = mw.state
	if state == 'deckBrowser':
		change_zoom( config[ 'deckBrowser_zoom_default' ] )
	if state == 'overview':
		change_zoom( config[ 'overview_zoom_default' ] )
	elif state == 'review':
		change_zoom( config[ 'review_zoom_default' ] )
		mw.reviewer.web.eval("applyZoom()")

def change_zoom_by(interval):
	currZoom = QWebEngineView.zoomFactor(mw.web) #use non-overridden method
	change_zoom(currZoom * interval)

def change_zoom(zoom_lvl):
	mw.web.setZoomFactor(zoom_lvl)

last_state = mw.state #reported states through hook can have erroneous values - tracked manually
def set_save_zoom(new_state, old_state, *args):
	global last_state
	if last_state == mw.state: #skips if reset
		return

	#Saves state zoom
	old_state_zoom = QWebEngineView.zoomFactor(mw.web)
	if last_state == 'deckBrowser':
		config[ 'deckBrowser_zoom' ] = old_state_zoom
	elif last_state == 'overview':
		config[ 'overview_zoom' ] = old_state_zoom
	elif last_state == 'review':
		config[ 'review_zoom' ] = old_state_zoom
	mw.addonManager.writeConfig(__name__, config)

	mw.setUpdatesEnabled(False) #prevents flickering

	#Applies state zoom
	if mw.state == 'deckBrowser':
		change_zoom( config[ 'deckBrowser_zoom' ] )
	elif mw.state == 'overview':
		change_zoom( config[ 'overview_zoom' ] )
	elif mw.state == 'review':
		change_zoom( config[ 'review_zoom' ] )

	def unpause():
		mw.setUpdatesEnabled(True)
	QTimer.singleShot(150, unpause) #prevents flickering

	last_state = mw.state

numDeg = 0
def AnkiWebView_eventFilter_wrapper(self, obj, event):
	global numDeg
	if (mw.app.keyboardModifiers() == Qt.ControlModifier and
			event.type() == QEvent.Wheel):
		numDeg = numDeg + event.angleDelta().y()
		if numDeg >= scrl_threshold:
			zoom_in()
			numDeg = 0
		elif numDeg <= -scrl_threshold :
			zoom_out()
			numDeg = 0

AnkiWebView.eventFilter = wrap(AnkiWebView.eventFilter, AnkiWebView_eventFilter_wrapper, 'before')

def add_action(submenu, label, callback, shortcut=None):
	action = QAction(_(label), mw)
	action.triggered.connect(callback)
	if shortcut:
		shortcutList= []
		for i in shortcut:
			shortcutList.append(QKeySequence(i))
		action.setShortcuts(shortcutList)
	submenu.addAction(action)
	return action


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
mw.zoom_submenu.addSeparator()

img_zoom = QAction('Enable Image Zoom', mw)
img_zoom.setCheckable(True)
mw.zoom_submenu.addAction(img_zoom)
img_zoom.triggered.connect(toggle_img_zoom)

config = mw.addonManager.getConfig(__name__)
img_zoom.setChecked(config[ 'img_zoom_enabled' ])


def onClose():
	set_save_zoom(None,mw.state)

addHook("afterStateChange", set_save_zoom)
addHook("unloadProfile", onClose)
