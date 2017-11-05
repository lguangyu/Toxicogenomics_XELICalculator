#!/usr/bin/env python3

import numpy
from AssayLib.Exceptions import PrerequestError
from AssayLib.Layout import Layout
from AssayLib.UtilFunctions import vector2string, array2d2string


################################################################################
# abstracted sample class prototype that inherited by other sample classes
# this class defines some common API's, one method binding method and
# several virtual functions that should be implemented by any derived classes
class SamplePrototype(object):
	def __init__(self, name, layout, log, assay_data, outdir, offset = (0, 0),
				_id = None, **kw):
		super(SamplePrototype, self).__init__()
		if (_id == None):
			raise RuntimeError("use plate API to create sample rather than bare call this constructor")
		self._set_id(_id)
		self.set_name(name)
		# if no layout assigned, use plate layout; if neither, raise error
		self.layout = layout
		self.offset = offset
		self.log = log
		self.raw_data = assay_data
		self.set_output_dir(outdir)
		self._OD = None
		self._GFP = None
		self._MASK = None
		self._P = None
		self._I = None

	def __repr__(self):
		return "<Sample name='%s' id=%d>" % (self.name(), self.id())

	# FOR INTERNAL USE ONLY
	def _set_id(self, _id):
		self._id = _id

	def id(self):
		return self._id

	def name(self):
		return self._name

	def set_name(self, name):
		self._name = name

	def output_dir(self):
		return self.outdir

	def set_output_dir(self, outdir):
		self.outdir = outdir

	def save_table_with_genes(self, path, array2d):
		with open(path, "w") as fh:
			fh.write(vector2string(self.layout.all_genes(), "%s") + "\n")
			fh.write(vector2string(self.layout.all_categories(), "%s") + "\n")
			fh.write(array2d2string(array2d, "%2f") + "\n")

	############################################################################
	# query functions for fetch data
	# recommended to use these functions as protected by raising specific error
	def OD(self):
		if (self._OD is None):
			raise PrerequestError("prerequest not completed (OD)")
		return self._OD

	def GFP(self):
		if (self._GFP is None):
			raise PrerequestError("prerequest not completed (GFP)")
		return self._GFP

	def MASK(self):
		if (self._MASK is None):
			raise PrerequestError("prerequest not completed (MASK)")
		return self._MASK

	def P(self):
		if (self._P is None):
			raise PrerequestError("prerequest not completed (P)")
		return self._P

	def I(self):
		if (self._I is None):
			raise PrerequestError("prerequest not completed (I)")
		return self._I

	def XELI(self):
		if (self.XELI is None):
			raise PrerequestError("prerequest not completed (XELI)")
		return self.XELI

	############################################################################
	# this method saves the P results, which is correcred GFP / OD
	# P is an important intermediate result of each sample object
	def _calculate_and_save_P(self):
		with numpy.errstate(divide = "ignore"):
			self._P = self.GFP() / self.OD()
			self._P[self._P == numpy.inf] = numpy.nan
		self.save_table_with_genes("%s/%s.P.tsv" % (self.output_dir(),
													self.name()),
								self._P)

	############################################################################
	# calculate I, I is the division of sample P to the untreated P
	# from this step on, no longer needs log, since everthing is reported
	def _calculate_and_save_I(self, untreated_P):
		self._I = self.P() / untreated_P
		self.save_table_with_genes("%s/%s.I.tsv" % (self.output_dir(),
													self.name()),
													self._I)

	############################################################################
	# calculated XELI
	def _calculate_and_save_XELI(self):
		I = self._I.copy()
		I[I < 1] = (1 / I[I < 1])
		self.XELI = I.sum(axis = 0, keepdims = True) / I.shape[0]
		self.save_table_with_genes("%s/%s.XELI.tsv" % (self.output_dir(),
														self.name()), self.XELI)
	def run_XELI_analysis(self, untreated_P):
		self._calculate_and_save_I(untreated_P)
		self._calculate_and_save_XELI()

	############################################################################
	# handle layout offset
	def layout2plate_coords(self, layout_coords):
		return layout_coords + self.offset

	############################################################################
	# cat tables with tab-delimted format
	# used for log
	def cat_OD_GFP_tables(self):
		m = "OD:\n%s\nGFP:\n%s"
		return m % (array2d2string(self.OD()),
					array2d2string(self.GFP(), "%d"))

	############################################################################
	# called by extract_data for internal use
	# take a set of coords and extract a set of cells defined by these coords
	# MUST be plate coords, not layout local coords
	# the result will be horizontally stacked into a single ndarray
	def _extract_by_coords_set(self, dset, coords):
		ex = [self.raw_data.cell_data(dset, c).reshape(-1, 1) for c in coords]
		return numpy.hstack(ex).copy()

	############################################################################
	# extract data from raw data
	# data is copied to make the original data intact
	# extracted data will be saved as self._OD and self._GFP, both are ndarrays
	# self._MASK is a boolean ndarray, this is for internal use only to mask
	# bad values only doing something like linear regression
	def extract_data(self):
		layout_coords = self.layout.all_coords()
		plate_coords = self.layout2plate_coords(layout_coords)
		self._OD = self._extract_by_coords_set("OD", plate_coords)
		self._GFP = self._extract_by_coords_set("GFP", plate_coords)
		self._MASK = self._extract_by_coords_set("MASK", plate_coords)
		m = ">%s:DATA_EXTRACT\n%s\n"
		self.log.write(m % (self.name(), self.cat_OD_GFP_tables()))

	############################################################################
	# binds func to cls.entry method call
	# all bound func is recommended (not required) to return a string for log
	# equals cls.entry = func
	@classmethod
	def _bind_method(cls, entry, func):
		def wrap(self):
			message = func(self)
			self.log.write(message)
		setattr(cls, entry, wrap)

	############################################################################
	# use above method to define a set of virtual entries below
	# each entry need to be implement for detailed calculation by any derived
	# classes
	@classmethod
	def onBlankCorrection(cls, func):
		cls._bind_method("_blank_correction", func)

	############################################################################
	# OD correction is also called population normalization
	# is for get the population density of GFP signal
	@classmethod
	def onODCorrection(cls, func):
		cls._bind_method("_OD_correction", func)

	# used as a single call for the whole set of analysis
	@classmethod
	def onRunPAnalysis(cls, func):
		cls._bind_method("run_P_analysis", func)

def _not_implemented(self):
	raise NotImplementedError("derived class must implement this method")
SamplePrototype.onBlankCorrection(_not_implemented)
SamplePrototype.onODCorrection(_not_implemented)
SamplePrototype.onRunPAnalysis(_not_implemented)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest

# 	class test(unittest.TestCase):
# 		def test1(self):
# 			pass

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
