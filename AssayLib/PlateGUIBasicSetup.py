#!/usr/bin/env python3

import os
import re
from PyQt5 import QtWidgets
from AssayLib.PlateGUIModulePrototype import PlateGUIModulePrototype
from AssayLib.Layout import Layout


################################################################################
class PlateGUIBasicSetup(PlateGUIModulePrototype):
	def __init__(self, parent):
		super(PlateGUIBasicSetup, self).__init__(parent, _mid = 0,
												geometry = (5, 5, 660, 173))
		self._setup_widgets()

	def _setup_widgets(self):
		self.add_fc_next_button()
		self.add_fc_cancel_button()

		self.file_selector = QtWidgets.QFileDialog(parent = self)
		self.file_selector.setModal(True)

		x2_open = self.width() - 30
		x2_edit = self.width() - 175

		self.dataf_label = QtWidgets.QLabel("Data file:", parent = self)
		self.dataf_label.setGeometry(8, 5, 140, 24)
		self.dataf_edit = QtWidgets.QLineEdit(parent = self)
		self.dataf_edit.setGeometry(140, 5, x2_edit, 24)
		self.dataf_open = self._add_button(geometry = (x2_open, 5, 24, 24),
			text = "...", callbacks = self.onClick_select_datafile)

		self.layoutf_label = QtWidgets.QLabel("Layout file:", parent = self)
		self.layoutf_label.setGeometry(8, 34, 140, 24)
		self.layoutf_edit = QtWidgets.QLineEdit(parent = self)
		self.layoutf_edit.setGeometry(140, 34, x2_edit, 24)
		self.layoutf_open = self._add_button(geometry = (x2_open, 34, 24, 24),
			text = "...", callbacks = self.onClick_select_layoutfile)

		self.outdir_label = QtWidgets.QLabel("Output directory:", parent = self)
		self.outdir_label.setGeometry(8, 63, 140, 24)
		self.outdir_edit = QtWidgets.QLineEdit(parent = self)
		self.outdir_edit.setGeometry(140, 63, x2_edit, 24)
		self.outdir_edit.setText("./output/")
		self.outdir_open = self._add_button(geometry = (x2_open, 63, 24, 24),
			text = "...", callbacks = self.onClick_select_outdir)

		self.aname_label = QtWidgets.QLabel("Assay name:", parent = self)
		self.aname_label.setGeometry(8, 92, 140, 24)
		self.aname_edit = QtWidgets.QLineEdit(parent = self)
		self.aname_edit.setGeometry(140, 92, 514, 24)

		self.type96 = QtWidgets.QRadioButton("96-well assay plate", self)
		self.type96.setGeometry(10, 120, 160, 24)
		self.type96.setChecked(True)
		self.type384 = QtWidgets.QRadioButton("384-well assay plate", self)
		self.type384.setGeometry(10, 144, 160, 24)

		self.type_btns = QtWidgets.QButtonGroup(self)
		self.type_btns.setExclusive(True)
		self.type_btns.addButton(self.type96, id = 96)
		self.type_btns.addButton(self.type384, id = 384)

	def run_select_file(self, accept_mode, file_mode, callbacks, option = 0,
							option_on = False):
		self.file_selector.setAcceptMode(accept_mode)
		self.file_selector.setFileMode(file_mode)
		self.file_selector.setOption(option, option_on)
		self.file_selector.fileSelected.connect(callbacks)
		self.file_selector.exec_()
		self.file_selector.fileSelected.disconnect(callbacks)

	def onClick_select_datafile(self):
		self.run_select_file(0, 1, self.dataf_edit.setText)
		self._set_default_assay_name()

	def onClick_select_layoutfile(self):
		self.run_select_file(0, 1, self.layoutf_edit.setText)

	def onClick_select_outdir(self):
		self.run_select_file(0, 4, self.outdir_edit.setText, 1, True)

	############################################################################
	# set the default name of the assay sample
	def _set_default_assay_name(self):
		if not self.aname_edit.text():
			bn = os.path.basename(self.dataf_edit.text())
			# trim the extension, if this leaves an empty string (start with .),
			# then use the original string
			bn = (re.sub("\.[^.]*$", "", bn) or bn)
			# replace any character not digit, alphabatical, -, _ or . into '_'
			bn = re.sub("[^-_.0-9a-zA-Z]", "_", bn)
			self.aname_edit.setText(bn)


@PlateGUIBasicSetup.onEnable
def onEnable(self):
	self.parentWidget().setFixedSize(670, 183)

@PlateGUIBasicSetup.checkOnNextClick
def checkOnNextClick(self):
	data_file = self.dataf_edit.text()
	layout_file = self.layoutf_edit.text()
	out_dir = self.outdir_edit.text()
	assay_name = self.aname_edit.text()

	# datafile is set and file exists
	if not data_file:
		self.parentWidget().fire_msg("Data file cannot be empty", "Error")
		return 1
	if not os.path.isfile(data_file):
		self.parentWidget().fire_msg("File '%s' not exists" % data_file, "Error")
		return 1

	# layout file is set and succesfully parsed
	if not layout_file:
		self.parentWidget().fire_msg("Layout file cannot be empty", "Error")
		return 1
	try:
		layout = Layout(layout = layout_file)
	except:
		self.parentWidget().fire_msg("""Layout file parse failed
Make sure file exists and is in valid layout format""", "Error")
		return 1

	# output dir is set or set to default
	if not out_dir:
		out_dir = "./output/"
		self.outdir_edit.setText(out_dir)
		self.parentWidget().fire_msg("Output dir set to '%s' by default" % out_dir)

	# assay name is set or set to default
	if not assay_name:
		self._set_default_assay_name()
		assay_name = self.aname_edit.text()
		self.parentWidget().fire_msg("Assay name set to '%s' by default" % assay_name)


	self.parentWidget().set_basic_config(data_file = data_file,
										layout_file = layout_file,
										layout = layout,
										out_dir = out_dir,
										assay_name = assay_name,
										plate_type = self.type_btns.checkedId())
	return 0





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
