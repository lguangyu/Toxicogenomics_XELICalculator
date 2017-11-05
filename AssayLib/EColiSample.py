#!/usr/bin/env python3

import numpy
from AssayLib.Exceptions import AsRuntimeError
from AssayLib.SamplePrototype import SamplePrototype
from AssayLib.ELineCorre import ELineCorre
from AssayLib.UtilFunctions import array2d2string


################################################################################
# sample handling class only used by E-Coli assays
# it has a special method for eline correction, which is unique in E-Coli assays
class EColiSample(SamplePrototype):
	def __init__(self, blank = "BLANK", eline = "ELINE", sd_factor = 2.0, **kw):
		super(EColiSample, self).__init__(**kw)
		# these two should be the same as in layout files to distinguish these
		# special categories from ordinary genes
		self._blank = blank
		self._eline = eline
		self._create_eline_corrector()
		# this is used in _OD_Correction
		# a threshold to determine 'significe' if varies farther than 'n' times
		# of sd, basically
		self._sd_factor = sd_factor

	def __repr__(self):
		return "<EColiSample name='%s' id=%d>" % (self.name(), self.id())

	def _create_eline_corrector(self):
		self.eline_corre = ELineCorre(parent = self)

	############################################################################
	# define an E-Coli assay unique method
	@classmethod
	def onELineCorrection(cls, func):
		cls._bind_method("_eline_correction", func)


################################################################################
# specific method definition
# implement the virtual entries in base class
@EColiSample.onBlankCorrection
def _blank_correction(self):
	where_blank = self.layout.mask_by_category(self._blank)
	if not where_blank.any():
		raise AsRuntimeError("background correction requires at least one 'BLANK' category in layout")
	OD_blank = self.OD()[:, where_blank].mean(axis = 1, keepdims = True)
	self.OD()[:] = self.OD() - OD_blank

	GFP_blank = self.GFP()[:, where_blank].mean(axis = 1, keepdims = True)
	self.GFP()[:] = self.GFP() - GFP_blank

	m = ">%s:BLANK_CORRECTION\n%s\n"
	return m % (self.name(), self.cat_OD_GFP_tables())

@EColiSample.onELineCorrection
def _eline_correction(self):
	eline_where = self.layout.mask_by_category(self._eline)
	if not eline_where.any():
		raise AsRuntimeError("e-line correction requires at least one 'ELINE' category in layout")
	OD_el = self.OD()[:, eline_where]
	GFP_el = self.GFP()[:, eline_where]
	MASK_el = self.MASK()[:, eline_where]

	# use a linear model for eline correction
	# the background gfp signal is estimated to be (slope * OD + intercept)

	slope, inter, inter_sd, msg = self.eline_corre.feed(OD_el, GFP_el, MASK_el)
	self.model_slope = slope
	self.model_inter = inter
	self.model_inter_sd = inter_sd

	m = ">%s:ELINE_CORRECTION\n%s\n"
	return m % (self.name(), msg)

@EColiSample.onODCorrection
def _OD_correction(self):
	# subtract the GFP signal by real-time OD
	bg_GFP = self.OD() * self.model_slope + self.model_inter
	self.GFP()[:] = self.GFP() - bg_GFP
	# the sd of intercepts got will be used as a threshold
	# to determine whether a 'significant' GFP signal is detected, otherwise set
	# it to 2 * sd in order to prevent zero-division
	threshold = self._sd_factor * self.model_inter_sd
	self.GFP()[self.GFP() < threshold] = threshold

	m = ">%s:OD_CORRECTION\nGFP:\n%s\n"
	return m % (self.name(),  array2d2string(self.GFP(), "%.2f"))

@EColiSample.onRunPAnalysis
def _run_P_analysis(self):
	self.extract_data()
	self._blank_correction()
	self._eline_correction()
	self._OD_correction()
	self._calculate_and_save_P()




################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest
# 	from AssayPlate import AssayPlate

# 	class test(unittest.TestCase):
# 		def test_construct(self):
# 			assay = AssayPlate("test_assay", 96, force = True,
# 							layout = "../.devel/test_data/EColi.96.P2.layout",
# 							data_file = "../.devel/test_data/DataParser_96.txt")
# 			assay.AddSample(EColiSample, name = "S1", offset = (0, 0))
# 			assay.AddSample(EColiSample, name = "S2", offset = (0, 1))
# 			assay.AddSample(EColiSample, name = "S3", offset = (0, 2))
# 			assay.AddSample(EColiSample, name = "S4", offset = (0, 3))
# 			assay.AddSample(EColiSample, name = "S5", offset = (0, 4))
# 			assay.AddSample(EColiSample, name = "S6", offset = (0, 5))

# 			sample = assay.GetSample(0)
# 			sample.run_analysis()

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
