#!/usr/bin/env python3

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


app = QtWidgets.QApplication([])

class ELineCorreGUI(QtWidgets.QDialog):
	def __init__(self):
		super(ELineCorreGUI, self).__init__()
		self.setModal(True)
		self.setStyleSheet("QDialog{background-color:white;}")
		self.plot_img = QtGui.QPixmap()
		self.plot_frame = QtWidgets.QLabel(parent = self)
		self.slope_chkboxes = []
		self.inter_chkboxes = []

	def adjust_widgets_geometry(self):
		img_size = self.plot_img.size()
		w, h = img_size.width(), img_size.height()
		self.setFixedSize(w, h)
		self.plot_frame.setGeometry(0, 0, w, h)

	def create_checkbox(self, x, y, w = 50, h = 20):
		check_box  = QtWidgets.QCheckBox(parent = self)
		check_box.setCheckState(True)
		check_box.setTristate(False)
		check_box.setText("use")
		check_box.setGeometry(x, y, w, h)
		return check_box

	def create_checkboxes(self, n, nr, nc, x_offset, y_offset):
		ret = []
		ct = 0
		for r in range(nr):
			y = y_offset + 439 * r
			for c in range(nc):
				if ct < n:
					x = x_offset + 439 * c
					ret.append(self.create_checkbox(x, y))
					ct = ct + 1
		return ret
				
	def launch(self, n, nr, nc, plot_path, s_name):
		self.setWindowTitle("Interactive ELine Correction: %s" % s_name)
		self.plot_img.load(plot_path)
		self.plot_frame.setPixmap(self.plot_img)
		self.adjust_widgets_geometry()

		self.slope_chkboxes = self.create_checkboxes(n, nr, nc, 157, 50)
		self.inter_chkboxes = self.create_checkboxes(n, nr, nc, 278, 50)

		self._slope_selected = []
		self._inter_selected = []
		self.exec_()
		return self._slope_selected, self._inter_selected

	############################################################################
	# reimplement the closeEvent method to also check the checkbox status and
	# store as instance attributes to be read by parent object
	def closeEvent(self, event):
		self._slope_selected = [bool(i.checkState()) for i in self.slope_chkboxes]
		self._inter_selected = [bool(i.checkState()) for i in self.inter_chkboxes]

	def selected_slopes(self):
		return self._slope_selected

	def selected_intercepts(self):
		return self._inter_selected





################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest

# 	# app = QtWidgets.QApplication([])

# 	class test(unittest.TestCase):

# 		def test_construct(self):
# 			selector = ELineCorreGUI()

# 			slope, inter = selector.launch(2, 1, 2, "./output/test_assay/S1_eline.png", "s")
# 			print(slope, inter)

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
