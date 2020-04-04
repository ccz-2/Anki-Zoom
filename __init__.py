# Anki Zoom
# v1.1.4 4/3/2020
# Copyright (c) 2020 Quip13 (random.emailforcrap@gmail.com)
# Based in part on code by Damien Elmes <anki@ichi2.net>, Roland Sieker <ospalh@gmail.com> and github.com/krassowski
# Big thanks to u/Glutanimate and u/yumenogotoshi for code suggestions
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from aqt import *
from aqt import mw
from aqt.webview import AnkiWebView, QWebEngineView
from aqt.qt import QEvent, Qt
from anki.hooks import addHook, runHook, wrap
from anki.hooks import *
from anki.lang import _
from .toolbar import *
from aqt.utils import closeTooltip, tooltip, _tooltipLabel, _tooltipTimer

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
	showZoomLvl()

def change_zoom_by(interval):
	currZoom = QWebEngineView.zoomFactor(mw.web) #use non-overridden method
	change_zoom(currZoom * interval)
	showZoomLvl()

def showZoomLvl(duration = 1000):
	def getZoom():
		currZoom = QWebEngineView.zoomFactor(mw.web)
		return str(round(currZoom*100))
	def newToolTip():
		tooltip(f'Zoom: {getZoom()}%',duration)
	# Tries to replace string in existing tooltip to prevent flickering when recreating
	def replaceTooltipTxt(label):
		txt = label.text()
		if "Zoom: " in txt:
			sI = txt.rfind("Zoom: ") + 6
			eI = txt.rfind("%")
			txt = txt[:sI] + getZoom() + txt[eI:]
			label.setText(txt)
			aqt.utils._tooltipTimer.start(duration)
			return True
		else:
			newToolTip()
		return False

	if zoomLvlToggle.isChecked():
		if not aqt.utils._tooltipLabel:
			newToolTip()
		else:
			replaceTooltipTxt(aqt.utils._tooltipLabel)


def change_zoom(zoom_lvl):
	mw.web.setZoomFactor(zoom_lvl)

def set_save_zoom(new_state, old_state, *args):
	if old_state == new_state: #skips if reset
		return

	config = mw.addonManager.getConfig(__name__)
	#Saves state zoom
	old_state_zoom = QWebEngineView.zoomFactor(mw.web)
	if old_state == 'deckBrowser':
		config[ 'deckBrowser_zoom' ] = old_state_zoom
	elif old_state == 'overview':
		config[ 'overview_zoom' ] = old_state_zoom
	elif old_state == 'review':
		config[ 'review_zoom' ] = old_state_zoom
	mw.addonManager.writeConfig(__name__, config)


	mw.setUpdatesEnabled(False) #prevents flickering

	#Applies state zoom
	if new_state == 'deckBrowser':
		change_zoom( config[ 'deckBrowser_zoom' ] )
	elif new_state == 'overview':
		change_zoom( config[ 'overview_zoom' ] )
	elif new_state == 'review':
		change_zoom( config[ 'review_zoom' ] )

	def unpause():
		mw.setUpdatesEnabled(True)
	QTimer.singleShot(150, unpause) #prevents flickering

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

def userAction():
	config = mw.addonManager.getConfig(__name__)
	config['zoom_lvl_tooltip_enabled'] = zoomLvlToggle.isChecked()
	mw.addonManager.writeConfig(__name__, config)

def setupConfig(*args):
	global scrl_threshold
	global zoom_step
	global config
	config = mw.addonManager.getConfig(__name__)
	scrl_threshold = config[ 'scroll_sensitivity' ]
	zoom_step = config[ 'zoom_step' ]
	zoomLvlToggle.setChecked(config['zoom_lvl_tooltip_enabled'])

def setup_menu():
	global zoomLvlToggle
	mw.addon_view_menu = getMenu(mw, "&View")
	mw.form.menubar.insertMenu(
		mw.form.menuTools.menuAction(),
		mw.addon_view_menu
	)

	mw.zoom_submenu = QMenu(_('&Zoom'), mw)
	mw.addon_view_menu.addMenu(mw.zoom_submenu)

	add_action(mw.zoom_submenu, 'Zoom &In', zoom_in, ['Ctrl++','Ctrl+='])
	add_action(mw.zoom_submenu, 'Zoom &Out', zoom_out, ['Ctrl+-'])
	add_action(mw.zoom_submenu, '&Reset', reset_zoom, ['Ctrl+0'])
	mw.zoom_submenu.addSeparator()
	zoomLvlToggle = add_action(mw.zoom_submenu, 'Show Zoom Level', userAction , [''])
	zoomLvlToggle.setCheckable(True)
	setupConfig()

def onClose():
	set_save_zoom(None,mw.state)

addHook("afterStateChange", set_save_zoom)
addHook("unloadProfile", onClose)
mw.addonManager.setConfigUpdatedAction(__name__, setupConfig)
setup_menu()
