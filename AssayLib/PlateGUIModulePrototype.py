#!/usr/bin/env python3

from PyQt5 import QtWidgets


################################################################################
class PlateGUIModulePrototype(QtWidgets.QFrame):
	def __init__(self, parent, _mid, geometry):
		super(PlateGUIModulePrototype, self).__init__(parent = parent)
		self.parent = parent
		self._mid = _mid
		self.setGeometry(*geometry)
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

	@classmethod
	def onEnable(cls, callbacks):
		def wrap(self):
			callbacks(self)
			self.show()
			self.setEnabled(True)
			self._show_fc_buttons()
		cls.enable = wrap
		return wrap

	@classmethod
	def onDisable(cls, callbacks):
		def wrap(self, hide = False):
			callbacks(self)
			self.setDisabled(True)
			if hide:
				self.hide()
			self._hide_fc_buttons()
		cls.disable = wrap
		return wrap

	############################################################################
	# validation check for all parameters input
	# check callbacks is provided by modules themselves
	# each callbacks should return 0 or null to indicate success
	# otherwise the process is halted
	#
	# the check callbacks will be set to null function (returns nothing)
	# as default
	@classmethod
	def checkOnPrevClick(cls, callbacks):
		def wrap(self):
			if callbacks(self):
				return		
			self.disable(hide  = True)
			self.parentWidget().call_prev_module(self._mid)
		cls.prev = wrap
		return wrap

	@classmethod
	def checkOnNextClick(cls, callbacks):
		def wrap(self):
			if callbacks(self):
				return		
			self.disable()
			self.parentWidget().call_next_module(self._mid)
		cls.next = wrap
		return wrap

	############################################################################
	# finish is a special case of next
	# it shares the same entry 'self.next()' with next button
	@classmethod
	def checkOnFinishClick(cls, callbacks):
		def wrap(self):
			if callbacks(self):
				return
			self.parentWidget().call_finish()
		cls.next = wrap
		return wrap

	@classmethod
	def onCancel(cls, callbacks):
		def wrap(self):
			callbacks(self)
			self.parentWidget().call_cancel()
		cls.cancel = wrap
		return wrap

# set null to all default methods
def NullFunction(self):
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
