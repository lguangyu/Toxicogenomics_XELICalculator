#!/usr/bin/env python3
################################################################################
# File: AssayLib/PlateGUI.py
#   Author: Guangyu Li, Northeastern University, C&E Engineering
#   E-mail: li.gua@husky.neu.edu
################################################################################
# SYNOPSIS
#   The main window for configuring plate setting through GUI. Many methods are
#   called by children config modules for communicating (to avoid intermodular
#   calls)
#
# DEFINES
#   PlateGUI
#     methods:
#       sample_types
#       sample_class
#       num_modules
#       call_prev_module
#       call_next_module
#       _window_expand
#       call_cancel
#       call_finish
#       fire_msg
#       set_basic_config
#       get_basic_config
#       set_sample_mapping
#       get_sample_mapping
#       set_untreated_sample
#       get_untreated_sample
#       launch
#       exception_capture
#       run
################################################################################
from PyQt5 import QtWidgets
from AssayLib.Exceptions import AsRuntimeError
from AssayLib.PlateGUIBasicSetup import PlateGUIBasicSetup
from AssayLib.PlateGUISampleMapper import PlateGUISampleMapper
from AssayLib.PlateGUIUntreatedSelect import PlateGUIUntreatedSelect
from AssayLib.Layout import Layout
from AssayLib.AssayPlate import AssayPlate
# samples
from AssayLib.EColiSample import EColiSample
# from AssayLib.YeastSample import YeastSample
# from AssayLib.HumanQPcrSample import HumanQPcrSample
################################################################################
class PlateGUI(QtWidgets.QDialog):
	def __init__(self, parent = None, **kw):
		super(PlateGUI, self).__init__()
		self.setModal(True)
		self._setup_widgets()
		self._create_msg_box()
		self.modules = []
		self._setup_modules()
		########################################################################
		# manually add all available samples types here
		# this is used for calculations after
		self._sample_types_dict = {
			"E-Coli": EColiSample,
			"Yeast (place holder)": EColiSample,
			"Human qPCR (place holder)": EColiSample,
		}

	def _setup_widgets(self):
		self.setStyleSheet("QDialog{background-color:#FFFFFF;};QRadioButton{background-color:#F0F0F0;};")
		self.setWindowTitle("Configure Assay Plate")
		self.setFixedSize(670, 5)

	############################################################################
	# module manage
	def sample_types(self):
		return self._sample_types_dict

	def sample_class(self, type_name):
		return self._sample_types_dict[type_name]

	############################################################################
	# module manage
	def _append_module(self, module):
		self.modules.append(module)
		return self

	def _setup_modules(self):
		self.modules = []
		self._append_module(PlateGUIBasicSetup(parent = self))
		self._append_module(PlateGUISampleMapper(parent = self))
		self._append_module(PlateGUIUntreatedSelect(parent = self))

	def num_modules(self):
		return len(self.modules)

	def _get_module_by_index(self, index):
		if ((index >= self.num_modules()) or index < 0):
			return None
		return self.modules[index]

	def call_prev_module(self, caller_id):
		module = self._get_module_by_index(caller_id - 1)
		if module:
			module.enable()

	def call_next_module(self, caller_id):
		module = self._get_module_by_index(caller_id + 1)
		if module:
			# call next will always reset the next module
			module.enable(reset = True)

	############################################################################
	# called by children modules on show to tell this widget to expand
	# vertically by certain pixels to hold the new module
	def _window_expand(self, expand_w = 0, expand_h = 0):
		w = self.width() + expand_w
		h = self.height() + expand_h
		if ((w > 0) and (h > 0)):
			self.setFixedSize(w, h)

	############################################################################
	# this method is internally called by modules when 'Cancel' button clicked
	def call_cancel(self):
		self.close()

	############################################################################
	# this method is internally called by modules when 'Finish' button clicked
	def call_finish(self):
		self.run()

	############################################################################
	# a built-in message box representing errors
	def _create_msg_box(self):
		self.msg_box = QtWidgets.QMessageBox(parent = self)
		# self.msg_box.setModal(False)
		self.msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)

	def fire_msg(self, text, title = ""):
		self.msg_box.setWindowTitle(title)
		self.msg_box.setText(text)
		self.msg_box.exec_()

	############################################################################
	# inter-module communications
	def set_basic_config(self, **kw):
		self.basic_config = dict(kw)

	def get_basic_config(self, key = None):
		if key:
			return self.basic_config[key]
		else:
			return self.basic_config

	def set_sample_mapping(self, mapped_samples):
		# make a copy of the list
		self.sample_mapping = mapped_samples[:]

	def get_sample_mapping(self):
		return self.sample_mapping

	def set_untreated_sample(self, sample_index):
		self.untreated_sample = sample_index

	def get_untreated_sample(self):
		return self.untreated_sample

	############################################################################
	# launch the widget
	def launch(self):
		self.move(500, 100)
		self.show()
		# default call will force enable the first module
		self.call_next_module(caller_id = -1)

	############################################################################
	# exception handling
	def exception_capture(self, exception):
		self.fire_msg(str(exception), "Error")

	############################################################################
	# gather all the information and call AssayPlate class for analysis
	def run(self):
		# add basic settings
		conf = self.get_basic_config()
		try:
			assay = AssayPlate( name = conf["assay_name"],
								size = conf["plate_type"],
								# overwrite = True,
								out_dir = conf["out_dir"],
								layout = conf["layout_file"],
								data_file = conf["data_file"])

			# add samples
			for i, s_anchor in enumerate(self.get_sample_mapping()):
				name = "C%d" % (i + 1)
				untreated = (i == self.get_untreated_sample())
				assay.add_sample(self.sample_class(conf["sample_type"]),
								name = name,
								offset = s_anchor,
								untreated = untreated)
			assay.analyze()
			self.close()
		except AsRuntimeError as err:
			self.exception_capture(err)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest

# 	app = QtWidgets.QApplication([])

# 	class test(unittest.TestCase):

# 		def test_launch(self):
# 			w = PlateGUI()
# 			w.launch()

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
