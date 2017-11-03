#!/usr/bin/env python3

import numpy
from AssayLib.Exceptions import AsRuntimeError, AsValueError
from AssayLib.UtilFunctions import plate_type_to_shape


################################################################################
# _PlateData object is used for storing the raw data parsed by the DataParser
# data strored in a 3-d array: (time, row, column) in order
# it also handles basic indexing, but be careful, this object is intended to be
# used only internally, the major operation should be conducted through other
# objects
# note this contains three arrays, OD, GFP and mask
# mask stands for invalid data that should be masked
class _PlateData(object):
	def __init__(self, _OD, _GFP, MASK):
		super(_PlateData, self).__init__()
		self._OD = numpy.copy(_OD)
		self._GFP = numpy.copy(_GFP)
		self._MASK = numpy.copy(MASK)

	def cell_data(self, dset, coords):
		pos_row, pos_col = coords
		if dset == "OD":
			return self._OD[:, pos_row, pos_col]
		elif dset == "GFP":
			return self._GFP[:, pos_row, pos_col]
		elif dset == "MASK":
			return self._MASK[:, pos_row, pos_col]
		else:
			raise AsValueError("DataParser: don't know how to handle '%s' of argument 'dset'" % dset)

	def OD(self, coords):
		return self.cell_data("OD", coords)

	def GFP(self, coords):
		return self.cell_data("GFP", coords)

	def MASK(self, coords):
		return self.cell_data("MASK", coords)


################################################################################
# DataParser object is used for parsing data from raw file
# since raw file is from windows and contains unicode characters .SUCKS..
# thus in python3 it is processed with encoding
class DataParser(object):
	def __init__(self, file, size, sep = "\t", encoding = "cp1252",
				 parse_func = None):
		super(DataParser, self).__init__()
		self.file = file
		self._shape = plate_type_to_shape(size)
		self.sep = sep
		self.encoding = encoding
		self.parse_func = parse_func or self._default_parse_func

	def __repr__(self):
		return "<DataParser file='%s'>" % self.file

	############################################################################
	# this function is called if no specific function is assigned to parse_func
	# when constructing
	############################################################################
	# any custom parse_func should should be implemented as a method and use
	# the same context as below, self.Parser() will wrap it further as a method
	@staticmethod
	def _default_parse_func(file, shape, sep, encoding):
		data = []
		nr, nc = shape
		rxc = nr * nc
		with open(file, "r", encoding = encoding) as fh:
			for line in fh:
				splitted = line.replace("\n", "").split(sep)[2:]
				if (len(splitted) == rxc):
					data.append(splitted)

		if not data:
			raise AsRuntimeError("""DataParser: parse failed, no any valid line found
make sure data file is in correct format""")
		if (len(data) % 2):
			raise AsRuntimeError("""DataParser: parse failed, uneven GFP and OD sections
make sure data file is in correct format""")

		data = numpy.asarray(data, dtype = object)
		sz_d1 = len(data) // 2

		# replace overflow with 100000
		data[data == "OVRFLW"] = 100000
		OD  = data[1:sz_d1, :].reshape(-1, nr, nc).astype(float)
		GFP = data[sz_d1 + 1:].reshape(-1, nr, nc).astype(int)
		MASK = (GFP != 100000)

		return _PlateData(OD, GFP, MASK)

	############################################################################
	# major interface called to run parse
	def parse(self):
		return self.parse_func(self.file, self._shape, self.sep, self.encoding)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest

# 	class test(unittest.TestCase):
# 		@unittest.expectedFailure
# 		def test_uneven_fail(self):
# 			DataParser("../.devel/test_data/DataParser_96_bad.txt",
# 				size = 96).parse()

# 		@unittest.expectedFailure
# 		def test_nofound_fail(self):
# 			DataParser("../.devel/test_data/DataParser_96.txt",
# 				size = 384).parse()

# 		@unittest.expectedFailure
# 		def test_invalid_size(self):
# 			DataParser("../.devel/test_data/DataParser_96.txt",
# 				size = 1).parse()

# 		def test_ok(self):
# 			cell = DataParser("../.devel/test_data/DataParser_96.txt",
# 				size = 96).parse()
# 			self.assertEqual(cell.cell_data("OD", (0, 0))[0], 0.365)
# 			self.assertEqual(cell.cell_data("OD", (1, 3))[7], 0.429)
# 			self.assertEqual(cell.cell_data("GFP", (7, 11))[23], 100000)

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
