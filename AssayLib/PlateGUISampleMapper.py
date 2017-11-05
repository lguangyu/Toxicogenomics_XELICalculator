#!/usr/bin/env python3
################################################################################
# File: AssayLib/PlateGUISampleMapper.py
#   Author: Guangyu Li, Northeastern University, C&E Engineering
#   E-mail: li.gua@husky.neu.edu
################################################################################
# SYNOPSIS
#   Allows the user to interactively map samples onto the plate. Must be called
#   after basic config is finished.
#   PlateGUISampleMapper is the class that actually handles the mouse click
#   event happened to the cells. The event is forwarded through parent classes
#   back here.
#   Defines two classes:
#     LayoutViewDialog: a dialog window previewing the current layout
#     PlateGUISampleMapper: the exported GUI module
#
# DEFINES
#   LayoutViewDialog
#     methods:
#       format_layout_contents
#       adjust_size_to_child_plate
#       launch
#
#   InteractiveCellPlate
#     methods:
#       show_layout_viewer
#       update_cell_plate
#       reset_mapper
#       add_selection
#       onCellClick
################################################################################
import numpy
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from AssayLib.PlateGUIModulePrototype import PlateGUIModulePrototype
from AssayLib.PlateGUIPlateViewer import PlateGUIPlateViewer, PlateGUIPlateViewerInteractive
from AssayLib.Palettes import CategoriesPalette, SampleSeriesPalette
from AssayLib.UtilFunctions import plate_type_to_shape
################################################################################
# popup window shows the content of current layout
class LayoutViewDialog(QtWidgets.QDialog):
	def __init__(self, parent):
		super(LayoutViewDialog, self).__init__(parent)
		self.setWindowTitle("Layout viewer")
		self.cell_plate = PlateGUIPlateViewer(parent = self)
		self.cell_plate.setStyleSheet("QFrame{background-color:#FFFFFF;}")
		self.cell_plate.set_row_labels([str(i + 1) for i in range(16)])
		self.cell_plate.set_col_labels([str(i + 1) for i in range(24)])

	@staticmethod
	def _format_cell(gene, cate):
		fmt = "<font color='%s'><b>%s</b></font>"
		return fmt % (CategoriesPalette[cate], gene)

	def format_layout_contents(self, layout):
		coords, genes, cates = layout.get_all()
		show_nrow, show_ncol = layout.extension_size()
		contents = [(cd, self._format_cell(gn, ct))
					for cd, gn, ct in zip(coords, genes, cates)]
		return show_nrow, show_ncol, contents

	def adjust_size_to_child_plate(self, border_x, border_y):
		self.setFixedSize(	self.cell_plate.width() + border_x * 2,
							self.cell_plate.height() + border_y * 2)

	def launch(self, layout):
		show_nrow, show_ncol, contents = self.format_layout_contents(layout)

		self.cell_plate.clear_all_cells()
		self.cell_plate.update_appearance(show_nrow, show_ncol,
											cell_w = 56, cell_h = 24,
											offset_x = 6, offset_y = 6,
											contents = contents)
		# adjust the self geometry to ensure the entire child can be displayed
		# 6 is the expand that allows a 6-pix border around the child plate
		self.adjust_size_to_child_plate(border_x = 6, border_y = 6)
		self.show()


################################################################################
class PlateGUISampleMapper(PlateGUIModulePrototype):
	def __init__(self, parent):
		super(PlateGUISampleMapper, self).__init__(parent, _mid = 1,
												geometry = (5, 183, 660, 492))
		self._setup_widgets()
		self._mapped_samples = []
		self._mapped_cells = numpy.zeros((16, 24), dtype = bool)

	def _setup_widgets(self):
		self.add_fc_prev_button()
		self.add_fc_next_button()
		self.add_fc_cancel_button()

		self.bottom_hint = QtWidgets.QLabel("<b>Click cells to add sample:</b>",
											parent = self)
		self.bottom_hint.setGeometry(12, 6, 200, 24)

		self.reset_btn = self._add_button((10, 463, 100, 24), "Reset",
											self.reset_mapper)
		self.layout_viewer = LayoutViewDialog(parent = self)
		self.view_layout = self._add_button((120, 463, 100, 24), "View layout",
											self.show_layout_viewer)

		self.plate_viewer = PlateGUIPlateViewerInteractive(parent = self)
		# geometry of this widget is dynamically adjusted based on the shown
		# elements, in function 'self.update_cell_plate'
		self.plate_viewer.set_row_labels([chr(65 + i) for i in range(16)])
		self.plate_viewer.set_col_labels([str(i + 1) for i in range(24)])

	def show_layout_viewer(self):
		layout = self.parentWidget().get_basic_config("layout")
		self.layout_viewer.launch(layout)

	@staticmethod
	def _format_cell(index, anchor, coords):
		position = coords + anchor
		fmt = "<font color='%s'>%d</font>"
		return (position, fmt % (SampleSeriesPalette[index], index + 1))

	############################################################################
	# only update the appearance of currently mapped cells by any samples
	def _format_current_mapped_cells(self):
		layout = self.parentWidget().get_basic_config("layout")
		contents = []
		for i, anchor in enumerate(self._mapped_samples):
			for coords in layout.all_coords():
				contents.append(self._format_cell(i, anchor, coords))
		return contents

	def update_cell_plate(self, clear = False):
		plate_type = self.parentWidget().get_basic_config("plate_type")
		if clear:
			self.plate_viewer.clear_all_cells()
		contents = self._format_current_mapped_cells()
		if plate_type == 96:
			self.plate_viewer.update_appearance(show_nrow = 8, show_ncol = 12,
												cell_w = 48,
												offset_x = 24, offset_y = 36,
												contents = contents)
		else:
			self.plate_viewer.update_appearance(show_nrow = 16, show_ncol = 24,
												cell_w = 24,
												offset_x = 24, offset_y = 36,
												contents = contents)

	############################################################################
	# these methods handle the sample mapping actions
	# reset, add_selection, etc.
	############################################################################
	# reset the whole plate to no samples
	def reset_mapper(self):
		self._mapped_samples = []
		self._mapped_cells.fill(0)
		self.update_cell_plate(clear = True)

	############################################################################
	# check if new sample can be placed
	def _is_cell_taken(self, r, c):
		return self._mapped_cells[r, c]

	def _mark_cell_taken(self, r, c):
		self._mapped_cells[r, c] = True

	def _is_any_cell_taken(self, anchor, layout):
		for coords in layout.all_coords():
			(r, c) = coords + anchor
			if self._is_cell_taken(r, c):
				return True
		# assign taken now, after the check is done
		for coords in layout.all_coords():
			(r, c) = coords + anchor
			self._mark_cell_taken(r, c)
		return False

	############################################################################
	# returns True if it is possible (enough space) to map new sample at coords
	# two possible reasons to fail:
	#   out of plate boundary
	#   some cells are not available (taken by another sample, since we only
	#   allow each cell cannot serve two samples)
	def _is_new_selection_placable(self, anchor, layout):
		ach_r, ach_c = anchor
		lay_r, lay_c = layout.extension_size()
		plate_type = self.parentWidget().get_basic_config("plate_type")
		max_r, max_c = plate_type_to_shape(plate_type)
		# check this first to prevent out-of-bound error
		if ((ach_r + lay_r > max_r) or (ach_c + lay_c > max_c)):
			self.parentWidget().fire_msg("""no room to place a (%d*%d) layout on a (%d*%d) plate
at position (%d,%d)""" % (lay_r, lay_c, max_r, max_c, ach_r, ach_c), "Error")
			return False
		# check if any cell will be redundantly assigned
		if self._is_any_cell_taken(anchor, layout):
			self.parentWidget().fire_msg("cell(s) under assigning is already taken by another sample", "Error")
			return False
		# if succeed, return True
		return True

	############################################################################
	# add new sample mapping to the collection list
	def add_selection(self, cell_coords):
		layout = self.parentWidget().get_basic_config("layout")
		if self._is_new_selection_placable(cell_coords, layout):
			self._mapped_samples.append(cell_coords)
		self.update_cell_plate()

	############################################################################
	# the event handler for deeply thrown back click events
	def onCellClick(self, caller_cell, cell_coords):
		if caller_cell.__class__.__name__ != "InteractiveCell":
			raise TypeError("""I don't know what you have done to make something
respond to the mouse click and triggered this
handler, but only InteractiveCell class is allowed
to react to interactions""")
		self.add_selection(cell_coords)


@PlateGUISampleMapper.onEnable
def OnEnable(self, reset = False):
	if reset:
		self.reset_mapper()

@PlateGUISampleMapper.checkOnNextClick
def checkOnNextClick(self):
	if len(self._mapped_samples) < 2:
		self.parentWidget().fire_msg("at least <b>TWO</b> samples should be assigned", "Error")
		return 1
	self.layout_viewer.close()
	self.parentWidget().set_sample_mapping(self._mapped_samples)
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
