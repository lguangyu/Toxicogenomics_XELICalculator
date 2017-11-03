#!/usr/bin/env python3

from PyQt5 import QtWidgets
from PyQt5 import QtCore


################################################################################
# Cell and InteractiveCell classes
# InteractiveCell is used by InteractiveCellPlate to react to the mouse click
# event, while ordinary Cell instances will not
class Cell(QtWidgets.QLabel):
	def __init__(self, parent, coords):
		super(Cell, self).__init__(parent)
		self._coords = coords
		self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)


class InteractiveCell(Cell):
	def __init__(self, parent, coords):
		super(InteractiveCell, self).__init__(parent, coords)

	def mouseReleaseEvent(self, event):
		# pass the coords back to the parent handler
		self.parentWidget().onCellClick(caller = self, arg = self._coords)
		

################################################################################
# this class is a prototype of the derived cell plate classes
# this base class does not define the cell object used
# this information should be provided by the derived class constructor
################################################################################
# an underlying object of the PlateGUIPlateViewer class holds the Cell objects
# any method should not be called directly to it
# call the API of PlateGUIPlateViewer instead
class CellPlatePrototype(QtWidgets.QFrame):
	def __init__(self, parent, nrow, ncol, CellClass):
		super(CellPlatePrototype, self).__init__(parent)
		self._nrow = nrow
		self._ncol = ncol
		self.setStyleSheet("""QFrame{background-color:#B0B0B0;}
							QLabel{background-color:#FFFFFF;
							border-style:solid;
							border-width:1;
							border-color:#C0C0C0;}""")
		# derived class should provide CellClass information!
		self._setup_cells(nrow, ncol, CellClass)

	############################################################################
	# use different CellClass to create cell objects
	def _setup_cells(self, nrow, ncol, CellClass):
		self.cells = [[CellClass(self, (j, i))
						for i in range(ncol)]
						for j in range(nrow)]

	def get_row_col_capacity(self):
		return self._nrow, self._ncol

	def clear_all_cells(self):
		for i in range(self._nrow):
			for j in range(self._ncol):
				self.cells[i][j].setText("")

	############################################################################
	# contents: should be a list, each item is a 2-element list or tuple:
	#   1st) a tuple of 2 elements, indicating row# and col#
	#   2nd) text to show
	# for example:
	# contents = [((0, 1), "text1"), # -> display "text1" in cell row-0 col-1
	#				(1, 1), "text2")]
	def set_cell_content(self, contents = None):
		if contents:
			for (r, c), text in contents:
				self.cells[r][c].setText(text)
		return

	def update_cells(self, show_nrow, show_ncol, cell_w, cell_h, contents = None):
		# adjust geometry to the content
		self.setGeometry(24, 24, show_ncol * cell_w + 4, show_nrow * cell_h + 4)

		for i in range(self._nrow):
			for j in range(self._ncol):
				cell = self.cells[i][j]
				if (i >= show_nrow) or (j >= show_ncol):
					cell.hide()
				else:
					cell.show()
					cell.setGeometry(cell_w * j + 2,
									cell_h * i + 2,
									cell_w,
									cell_h)
		self.set_cell_content(contents)


################################################################################
# these two classes are the ordinary classes called from outside of the module
################################################################################
# ordinary CellPlate object with no mouse event handler
class CellPlate(CellPlatePrototype):
	def __init__(self, parent, nrow, ncol):
		cell_cls = Cell ##
		super(CellPlate, self).__init__(parent, nrow, ncol, cell_cls)


################################################################################
# a specified CellPlate object interactive to mouse click on cells, a specificates of the
# CellPlate object
class InteractiveCellPlate(CellPlatePrototype):
	def __init__(self, parent, nrow, ncol):
		cell_cls = InteractiveCell ##
		super(InteractiveCellPlate, self).__init__(parent, nrow, ncol, cell_cls)

	############################################################################
	# since cell plate object is just an intermediate frame organizing the cells
	# this method is just an interface forwading the events fired by the cells
	# to the the parent handler
	def onCellClick(self, caller, arg):
		self.parentWidget().onCellClick(caller, arg)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
#	import unittest

#	class test(unittest.TestCase):

#		def test_constr(self):
#			pass


#	suite = unittest.TestLoader().loadTestsFromTestCase(test)
#	unittest.TextTestRunner(verbosity = 2).run(suite)
