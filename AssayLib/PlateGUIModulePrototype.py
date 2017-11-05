#!/usr/bin/env python3
################################################################################
# File: AssayLib/PlateGUIModulePrototype.py
#   Author: Guangyu Li, Northeastern University, C&E Engineering
#   E-mail: li.gua@husky.neu.edu
################################################################################
# SYNOPSIS
#   Base class for all interactive plate configuring GUI.
#
# DEFINES
#   PlateGUIModulePrototype
#     methods:
#       add_fc_prev_button
#       add_fc_next_button
#       add_fc_cancel_button
#     decorators:
#       @onEnable
#       @onDisable
#       @checkOnPrevClick
#       @checkOnNextClick
#       @checkOnFinishClick
#       @onCancel
################################################################################
from PyQt5 import QtWidgets
################################################################################
# the GUI is made up by several 'modules', controlled by a series of flow-control
# buttons
# this is the base class for all GUI modules, which, defines some critical and
# fundamental behaviors
class PlateGUIModulePrototype(QtWidgets.QFrame):
	def __init__(self, parent, _mid, geometry):
		super(PlateGUIModulePrototype, self).__init__(parent = parent)
		self.parent = parent
		self._mid = _mid
		self.setGeometry(*geometry)
		# expand_h tells the main window to expand howmuch vertically to hold
		# this module.
		# since there is 5-pix gap between all modules, this value will be
		# height + 5
		self._expand_h = geometry[3] + 5
		self.setStyleSheet("QFrame{background-color:#F0F0F0;}")
		self.hide()
		self.flow_control_buttons = []

	def _add_button(self, geometry, text, callbacks, auto_default = False):
		button = QtWidgets.QPushButton(parent = self)
		button.setGeometry(*geometry)
		button.setText(text)
		button.setAutoDefault(auto_default)
		button.released.connect(callbacks)
		return button

	############################################################################
	# add a flow-control button (next, prev, cancel, etc)
	# flow-control buttons are hidden when the current module is disabled
	# they are tracked by self.flow_control_buttons list
	def add_fc_prev_button(self):
		x = self.width() - 330
		y = self.height() - 29
		text = "< Back"
		button = self._add_button((x, y, 100, 24), text,
									callbacks = self.prev)
		self.flow_control_buttons.append(button)

	def add_fc_next_button(self, is_finish = False):
		x = self.width() - 225
		y = self.height() - 29
		text = is_finish and "Run" or "Next >"
		# set auto-default for this button
		button = self._add_button((x, y, 100, 24), text,
									callbacks = self.next,
									auto_default = True)
		self.flow_control_buttons.append(button)

	def add_fc_cancel_button(self):
		x = self.width() - 110
		y = self.height() - 29
		text = "Cancel"
		button = self._add_button((x, y, 100, 24), text,
									callbacks = self.cancel)
		self.flow_control_buttons.append(button)

	def _show_fc_buttons(self):
		for btn in self.flow_control_buttons:
			btn.show()

	def _hide_fc_buttons(self):
		for btn in self.flow_control_buttons:
			btn.hide()

	############################################################################
	# these decorators are for derived class to do locally defined behaviors
	# when certain event is triggered
	# the local function should be passed as 'callback' 
	@classmethod
	def onEnable(cls, callbacks):
		# reset = True is usually called by the call_next_module method
		# since the config changes in previous modules infects current module
		def wrap(self, reset = False):
			callbacks(self, reset)
			self.setEnabled(True)
			self._show_fc_buttons()
			if reset:
				self.parentWidget()._window_expand(expand_h = self._expand_h)
				self.show()
		cls.enable = wrap
		return wrap

	@classmethod
	def onDisable(cls, callbacks):
		def wrap(self, hide = False):
			callbacks(self)
			self.setDisabled(True)
			if hide:
				self.hide()
				self.parentWidget()._window_expand(expand_h = (-self._expand_h))
			self._hide_fc_buttons()
		cls.disable = wrap
		return wrap

	############################################################################
	# these are also decorators, for when Next or Prev button is hit
	# these decorates a 'check_callbacks', which will return a value indicate
	# if every settings in current module is good
	# if returned a null value (including None from implicity retuning):
	#   the check is passed and will move to the next module
	# if returned a non-null value:
	#   the check failed and will stays in the current module until settings are
	#   all satisfied
	#
	# the check callbacks will be set to null function below (returns nothing)
	# as default (always pass the check)
	@classmethod
	def checkOnPrevClick(cls, check_callbacks):
		def wrap(self):
			if check_callbacks(self):
				return		
			self.disable(hide  = True)
			self.parentWidget().call_prev_module(self._mid)
		cls.prev = wrap
		return wrap

	@classmethod
	def checkOnNextClick(cls, check_callbacks):
		def wrap(self):
			if check_callbacks(self):
				return		
			self.disable()
			self.parentWidget().call_next_module(self._mid)
		cls.next = wrap
		return wrap

	############################################################################
	# finish is a special case of next, which is designed to be called when hit
	# the next button of the last module
	#
	# it shares and replaces the same entry 'self.next()' with next button
	@classmethod
	def checkOnFinishClick(cls, check_callbacks):
		def wrap(self):
			if check_callbacks(self):
				return
			self.parentWidget().call_finish()
		cls.next = wrap
		return wrap

	@classmethod
	def onCancel(cls, check_callbacks):
		def wrap(self):
			check_callbacks(self)
			self.parentWidget().call_cancel()
		cls.cancel = wrap
		return wrap

# set null to all default methods
def NullFunction(self, *ka, **kw):
	return None
PlateGUIModulePrototype.onEnable(NullFunction)
PlateGUIModulePrototype.onDisable(NullFunction)
PlateGUIModulePrototype.checkOnPrevClick(NullFunction)
PlateGUIModulePrototype.checkOnNextClick(NullFunction)
PlateGUIModulePrototype.onCancel(NullFunction)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
	# import unittest
# 
	# class test(unittest.TestCase):
		# pass
# 
	# suite = unittest.TestLoader().loadTestsFromTestCase(test)
	# unittest.TextTestRunner(verbosity = 2).run(suite)
