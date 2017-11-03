#!/usr/bin/env python3

import numpy
from AssayLib.Exceptions import AsRuntimeError


################################################################################
# Layout object is used to manage the plate layout information
#   the position described in this object is the raw coordinates relative to the
#   layout
#   the layout can be mapped to the plate so the real coordinates on the plate
#   for each cell is then coordinatec as layout plus the offset of the layout
#   itself relative to the parent plate 
# this class can also handle basic selection by field or gene
# basic selection returns a list which contains the coords (coords on layout) of
# all cells matching the search condition
# however the actuall search which, select the cells in data, will be processed
# by the Sample object, where the layout offset to the plate is considered
################################################################################
# the Layout object can load an ordinary *.layout format file, whose each line
# represents a cell with its 'coords_row', 'coords_col', 'gene' and 'category',
# must in tab-delimited format
# it can also build such information from pair-wise gene to category mappings,
# and also save the result into a *.layout file for furthur use
class Layout(object):
	def __init__(self, layout = None, layout_maps = None, **kw):
		super(Layout, self).__init__()
		if not (layout is None):
			self.load(layout)
		elif not (layout_maps is None):
			self.build_from_maps(*layout_maps)

	############################################################################
	# extension size is the minimum rectangular area that needed to display the
	# whole layout
	# easily found by get the max row/column coordinates of defined cells
	def _set_extension_size(self):
		self._row_ext = self._coords[:, 0].max() + 1
		self._col_ext = self._coords[:, 1].max() + 1

	def extension_size(self):
		return (self._row_ext, self._col_ext)
		
	############################################################################
	# load from a layout file
	# MUST be tab-delimited
	def load(self, file):
		loaded = numpy.loadtxt(file, dtype = object, delimiter = "\t")
		self._coords = loaded[:, :2].astype(int)
		self._genes = loaded[:, 2].astype(str)
		self._cates = loaded[:, 3].astype(str)
		self._set_extension_size()
		return self

	############################################################################
	# build layout from gene mapping and category mapping
	# both files should be in same shape
	# and separated by tab (\t), since comma may have special meanings here
	def build_from_maps(self, gene_map, cate_map):
		with open(gene_map, "r") as gene_fh:
			gene_map = [l.split("\t") for l in gene_fh.read().splitlines()]
		with open(cate_map, "r") as cate_fh:
			cate_map = [l.split("\t") for l in cate_fh.read().splitlines()]
		self._check_shape(gene_map, cate_map)
		self._coords, self._genes, self._cates = self._parse_maps(gene_map,
																cate_map)
		self._set_extension_size()
		return self

	def all_coords(self):
		return self._coords

	def all_genes(self):
		return self._genes

	def all_categories(self):
		return self._cates

	############################################################################
	# return everthing
	def get_all(self):
		return self._coords, self._genes, self._cates

	############################################################################
	# called by build_from_maps to check if two files are in same shape
	@staticmethod
	def _check_shape(f1, f2):
		if (len(f1) != len(f2)):
			raise AsRuntimeError("map files must be in exact same shape")
		for s1, s2 in zip(f1, f2):
			if (len(s1) != len(s2)):
				raise AsRuntimeError("map files must be in exact same shape")

	############################################################################
	# called by build_from_maps to parse map into coordinates
	@staticmethod
	def _parse_maps(gene_map, cate_map):
		coords_list, genes_list, cates_list = [], [], []
		for row_id, row in enumerate(gene_map):
			for col_id, gene in enumerate(row):
				cate = cate_map[row_id][col_id]
				if (gene and cate):
					coords_list.append([row_id, col_id])
					genes_list.append(gene)
					cates_list.append(cate)
				elif not (gene or cate):
					continue
				else:
					e = "'gene' or 'category' missing at (row %d, col %d)"
					raise AsRuntimeError(e % (row_id, col_id))
		coords = numpy.asarray(coords_list, dtype = int)
		genes = numpy.asarray(genes_list, dtype = str)
		cates = numpy.asarray(cates_list, dtype = str)
		return coords, genes, cates

	############################################################################
	# save built layout into layout file
	def save_layout(self, path):
		with open(path, "w") as fh:
			for c, g, t in zip(self._coords, self._genes, self._cates):
				fh.write("%d\t%d\t%s\t%s\n" % (c[0], c[1], g, t))

	############################################################################
	# select all cells have exact matched substring "key" in "field"
	# returns an T/F array
	def _mask_field_by_key(self, field, key):
		mask = numpy.array(numpy.char.find(field, key) + 1, dtype = bool)
		return mask

	def mask_by_gene(self, gene):
		return self._mask_field_by_key(self.all_genes(), gene)

	def mask_by_category(self, cate):
		return self._mask_field_by_key(self.all_categories(), cate)

	############################################################################
	# select all cells by a T/F array
	def _filter_coords_mask(self, mask):
		return self.all_coords()[mask]

	def coords_of_genes(self, gene):
		mask = self._mask_field_by_key(self.all_genes(), key = gene)
		return self._filter_coords_mask(mask)

	def coords_of_category(self, cate):
		mask = self._mask_field_by_key(self.all_categories(), key = cate)
		return self._filter_coords_mask(mask)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest

# 	class test(unittest.TestCase):
# 		def test_load_and_select(self):
# 			layout = Layout()
# 			layout.load("../.devel/test_data/Layout.layout")

# 			self.assertEqual(len(layout.all_coords()), 8)
# 			self.assertEqual(tuple(layout.GetCoordsByGene("Gene1")[0]), (0, 0))
# 			self.assertEqual(len(layout.GetCoordsByGene("Gene2")), 2)
# 			self.assertEqual(tuple(layout.GetCoordsByCategory("O")[1]), (0, 1))
# 			self.assertEqual(len(layout.GetCoordsByCategory("P")), 4)

# 		def test_build(self):
# 			layout = Layout()
# 			layout.build_from_maps(	"../.devel/test_data/EColi.96.P2.gene_map.tsv",
# 										"../.devel/test_data/EColi.96.P2.cate_map.tsv"
# 				).save_layout("../.devel/test_data/EColi.96.P2.layout")
# 			self.assertEqual(len(layout.GetCoordsByCategory("Oxidative")), 6)

# 		@unittest.expectedFailure
# 		def test_build_fail_unmatch(self):
# 			layout = Layout()
# 			layout.build_from_maps(	"../.devel/test_data/gene_map_bad.tsv",
# 										"../.devel/test_data/cate_map.tsv"
# 				).save_layout("../.devel/test_data/saved.layout")

# 		@unittest.expectedFailure
# 		def test_build_fail_missing(self):
# 			layout = Layout()
# 			layout.build_from_maps(	"../.devel/test_data/gene_map.tsv",
# 										"../.devel/test_data/cate_map_bad.tsv"
# 				).save_layout("../.devel/test_data/saved.layout")

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
