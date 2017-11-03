#!/usr/bin/env python3

from PyQt5 import QtWidgets
from AssayLib.PlateGUIModulePrototype import PlateGUIModulePrototype


################################################################################
class PlateGUIUntreatedSelect(PlateGUIModulePrototype):
	def __init__(self, parent):
		super(PlateGUIUntreatedSelect, self).__init__(parent, _mid = 2,
												geometry = (5, 680, 660, 34))
		self._setup_widgets()

	def _setup_widgets(self):
		self.add_fc_prev_button()
		self.add_fc_next_button(is_finish = True)
		self.add_fc_cancel_button()

		self.text_hint = QtWidgets.QLabel("Untreated sample:", parent = self)
		self.text_hint.setGeometry(6, 5, 130, 24)

		self.combo_box = QtWidgets.QComboBox(parent = self)
		self.combo_box.setGeometry(140, 5, 150, 24)
		self.combo_box.setEditable(False)
		self.combo_box.setMaxVisibleItems(7)

	############################################################################
	# add items into the combobox
	# existing ones will be all cleared
	def combo_box_add_items(self):
		self.combo_box.clear()
		samples_list = self.parentWidget().get_sample_mapping()
		for i, s in enumerate(samples_list):
			self.combo_box.addItem("Sample %d" % (i + 1))

@PlateGUIUntreatedSelect.onEnable
def onEnable(self):
	self.parentWidget().setFixedSize(670, 719)
	self.combo_box_add_items()

@PlateGUIUntreatedSelect.checkOnFinishClick
def onFinish(self):
	self.parentWidget().set_untreated_sample(self.combo_box.currentIndex())


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
