#!/usr/bin/env python3
################################################################################
# File: AssayLib/PlateGUIPlateViewer.py
#   Author: Guangyu Li, Northeastern University, C&E Engineering
#   E-mail: li.gua@husky.neu.edu
################################################################################
# SYNOPSIS
#   Class for handling and displaying cell grid GUI, slaves a CellPlate object,
#   with row and column labels. Several functions are just a forwarding call to
#   the underneath CellPlate object. Defines two classes:
#     PlateGUIPlateViewer: static displaying cell plate grid
#     PlateGUIPlateViewerInteractive: a derived class which allows interaction
#
# DEFINES
#   PlateGUIPlateViewer
#     methods:
#       get_row_col_capacity
#       set_row_labels
#       set_col_labels
#       clear_all_cells
#       set_cell_content
#       adjust_size_to_child_plate
#       update_appearance
#
#   InteractiveCellPlate
#     methods:
#       get_row_col_capacity
#       set_row_labels
#       set_col_labels
#       clear_all_cells
#       set_cell_content
#       adjust_size_to_child_plate
#       update_appearance
#       onCellClick
################################################################################
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from AssayLib.PlateGUICellPlate import CellPlate, InteractiveCellPlate
################################################################################
# PlateGUIPlateViewer object manages a cell lattice plate, and two label series
# (row and column)
# the labels are managed by this object,
# while the functions manipulating or interacting with cells are just interfaces
# which forward calls to synonym functions of the underneath CellPlate object
class PlateGUIPlateViewer(QtWidgets.QFrame):
	def __init__(self, parent, nrow = 16, ncol = 24):
		super(PlateGUIPlateViewer, self).__init__(parent)
		self._nrow = nrow
		self._ncol = ncol
		self._setup_widgets()

	def _setup_widgets(self):
		self.row_labels = [self._create_label() for i in range(self._nrow)]
		self.col_labels = [self._create_label() for i in range(self._ncol)]
		self._create_cell_plate()

	############################################################################
	# this method will be reimplemented by derived interactive class
	def _create_cell_plate(self):
		self.cell_plate = CellPlate(self, self._nrow, self._ncol)

	def _create_label(self):
		label = QtWidgets.QLabel(parent = self)
		label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
		return label

	def get_row_col_capacity(self):
		return self._nrow, self._ncol

	############################################################################
	# set row and column labels, the labels should be set with a list with the
	# length the same number as the total labels
	def set_row_labels(self, labels):
		if len(labels) != self._nrow:
			raise RuntimeError("length of 'labels' must be %d" % self._nrow)
		for text, obj in zip(labels, self.row_labels):
			obj.setText(text)

	def set_col_labels(self, labels):
		if len(labels) != self._ncol:
			raise RuntimeError("length of 'labels' must be %d" % self._ncol)
		for text, obj in zip(labels, self.col_labels):
			obj.setText(text)

	def clear_all_cells(self):
		self.cell_plate.clear_all_cells()

	def set_cell_content(self, **kw):
		self.cell_plate.set_cell_content(**kw)

	def _refresh_labels(self, show_nrow, show_ncol, cell_w, cell_h):
		for i, label in enumerate(self.row_labels):
			if (i < show_nrow):
				label.setGeometry(0, cell_h * i + 26, 24, cell_h)
				label.show()
			else:
				label.hide()
		for i, label in enumerate(self.col_labels):
			if (i < show_ncol):
				label.setGeometry(cell_w * i + 26, 0, cell_w, 24)
				label.show()
			else:
				label.hide()

	def adjust_size_to_child_plate(self, offset_x, offset_y, border_x, border_y):
		self.setGeometry(offset_x,
						offset_y,
						self.cell_plate.width() + border_x * 2,
						self.cell_plate.height() + border_y * 2)

	def update_appearance(self, show_nrow, show_ncol, cell_w, cell_h = None,
						offset_x = 0, offset_y = 0, **kw):
		if not cell_h:
			cell_h = cell_w
		self._refresh_labels(show_nrow, show_ncol, cell_w, cell_h)
		self.cell_plate.update_cells(show_nrow, show_ncol, cell_w, cell_h, **kw)
		self.adjust_size_to_child_plate(offset_x, offset_y, 12, 12)


################################################################################
# interactive version of PlateGUIPlateViewer class
# use the InteractiveCellPlate as the plate object and implemeneted the click
# handler of processing click events on the cells
class PlateGUIPlateViewerInteractive(PlateGUIPlateViewer):
	def __init__(self, *ka, **kw):
		super(PlateGUIPlateViewerInteractive, self).__init__(*ka, **kw)
		
	############################################################################
	# reimplement this function use InteractiveCellPlate class
	def _create_cell_plate(self):
		self.cell_plate = InteractiveCellPlate(self, self._nrow, self._ncol)

	# still throw back, this class is just for displaying, not event handling
	def onCellClick(self, caller, arg):
		self.parentWidget().onCellClick(caller, arg)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
#	import unittest

#	app = QtWidgets.QApplication([])

#	class test(unittest.TestCase):

#		def test_constr(self):
#			p = PlateGUIPlateViewer(None, 16, 24)
#			p.setFixedSize(660, 468)
#			p.set_row_labels([chr(65 + i) for i in range(16)])
#			p.set_col_labels([str(i + 1) for i in range(24)])
#			p.update_appearance(16, 24, 24)
#			# p.update_appearance(8, 12, 48)
#			p.exec()


#	suite = unittest.TestLoader().loadTestsFromTestCase(test)
#	unittest.TextTestRunner(verbosity = 2).run(suite)
