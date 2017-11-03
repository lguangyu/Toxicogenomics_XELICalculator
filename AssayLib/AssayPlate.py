#!/usr/bin/env python3

import os
import sys
import numpy
from AssayLib.Exceptions import AsRuntimeError
from AssayLib.Layout import Layout
from AssayLib.DataParser import DataParser
from AssayLib.Log import Log
from AssayLib.ArrayFormatting import array2d2string


################################################################################
# AssayPlate class holds all plate information needed, manages samples and
# organizes calculations
# it also manages output, all end-term users is recommended to use ONLY this
# class as an interface for command-line calculation
class AssayPlate(object):
	def __init__(self, name, size, outdir = "./output/", **kw):
		super(AssayPlate, self).__init__()
		self.name = name
		self.outdir = outdir + name
		self.create_output_dir(self.outdir, **kw)
		self.create_log()
		self.size = size
		self.set_plate_layout(**kw)
		self.samples = []
		# for now only allow one untreated sample
		self._control = None
		self.load_data_file(**kw)
	
	def __repr__(self):
		return ("<AssayPlate size='%d', samples='%d'>" %
				(self.size, len(self.samples)))

	############################################################################
	# output setup
	# if overwrite is not True, raise error when exists
	def create_output_dir(self, outdir, overwrite = False, **kw):
		if os.path.exists(outdir):
			if not overwrite:
				raise AsRuntimeError("output dir '%s' already exists" % outdir)
		else:
			os.makedirs(outdir)

	def output_dir(self):
		return self.outdir

	def create_log(self, file = None):
		if file:
			self.log_obj = Log(file = file)
		else:
			self.log_obj = Log(dir = self.outdir)

	def log(self):
		return self.log_obj

	############################################################################
	# layout functions
	# the layout here are not position specific
	# samples using this layout should calculate the actual coords themselves
	def set_plate_layout(self, layout = None, **kw):
		self.shared_layout = Layout(layout)

	def plate_layout(self):
		return self.shared_layout

	############################################################################
	# sample functions
	def add_sample(self, SampleClass, name, layout = None, offset = None,
				untreated = False, **kw):
		# internal _id is same as the position in the self.samples array
		_id = len(self.samples)
		sample = SampleClass(name = name,
							layout = layout or self.shared_layout,
							log = self.log(),
							assay_data = self.data(),
							outdir = self.output_dir(),
							offset = offset,
							_id = len(self.samples), **kw)
		self.samples.append(sample)
		if untreated:
			if not (self._control is None):
				raise AsRuntimeError("assign more than one sample as untreated is not allowed")
			self._control = sample

	def get_sample(self, index):
		return self.samples[index]

	def untreated_sample(self):
		return self._control

	def all_samples(self):
		return self.samples

	def get_samples_except_untreated(self):
		control = self.untreated_sample()
		return [i for i in self.all_samples() if (not(i is control))]

	############################################################################
	# raw data
	def load_data_file(self, data_file = None, **kw):
		if data_file:
			self._data = DataParser(data_file, self.size).parse()

	def data(self):
		return self._data

	############################################################################
	# analysis samples
	def analyze(self):
		# analyze P
		for sample in self.samples:
			sample.run_P_analysis()
		# analyze I
		if (self.untreated_sample() is None):
			raise AsRuntimeError("cannot canculate I with no assign of untreated sample")
		untreated_P = self.untreated_sample().P()
		for sample in self.get_samples_except_untreated():
			sample.run_XELI_analysis(untreated_P)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest

# 	class test(unittest.TestCase):
# 		def test_construct(self):
# 			assay = AssayPlate("test_assay", 96, overwrite = True,
# 							layout = "../.devel/test_data/EColi.96.P2.layout",
# 							data_file = "../.devel/test_data/DataParser_96.txt")

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
