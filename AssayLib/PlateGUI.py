#!/usr/bin/env python3

from PyQt5 import QtWidgets

from AssayLib.Exceptions import AsRuntimeError
from AssayLib.PlateGUIBasicSetup import PlateGUIBasicSetup
from AssayLib.PlateGUISampleMapper import PlateGUISampleMapper
from AssayLib.PlateGUIUntreatedSelect import PlateGUIUntreatedSelect
from AssayLib.Layout import Layout
from AssayLib.AssayPlate import AssayPlate

from AssayLib.EColiSample import EColiSample


################################################################################
class PlateGUI(QtWidgets.QDialog):
	def __init__(self, parent = None, **kw):
		super(PlateGUI, self).__init__()
		self.setModal(True)
		self._setup_widgets()
		self._create_msg_box()

	def _setup_widgets(self):
		self.setStyleSheet("QRadioButton{background-color:#F0F0F0}")
		self.setWindowTitle("Configure Assay Plate")
		self.setStyleSheet("QDialog{background-color:#FFFFFF;}")
		self.modules = [PlateGUIBasicSetup(parent = self),
						PlateGUISampleMapper(parent = self),
						PlateGUIUntreatedSelect(parent = self)]

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
	# this method is internally called by modules when 'Cancel' button clicked
	def call_cancel(self):
		self.close()

	############################################################################
	# this method is internally called by modules when 'Finish' button clicked
	def call_finish(self):
		self.run()

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
	# module calls
	def _get_module_by_index(self, module_id):
		try:
			return self.modules[module_id]
		except IndexError:
			return None

	def call_prev_module(self, module_id):
		module = self._get_module_by_index(module_id - 1)
		if module:
			module.enable()

	def call_next_module(self, module_id):
		module = self._get_module_by_index(module_id + 1)
		if module:
			module.enable()

	############################################################################
	# launch the widget
	def launch(self):
		self.modules[0].enable()
		self.move(500, 100)
		self.show()

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
				assay.add_sample(EColiSample,
								name = name,
								offset = s_anchor,
								untreated = untreated)
			assay.analyze()
		except AsRuntimeError as err:
			self.exception_capture(err)
		self.close()





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
