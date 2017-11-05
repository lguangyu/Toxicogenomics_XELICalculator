#!/usr/bin/env python3
################################################################################
# File: AssayLib/Palettes.py
#   Author: Guangyu Li, Northeastern University, C&E Engineering
#   E-mail: li.gua@husky.neu.edu
################################################################################
# SYNOPSIS
#   Color palettes used in visulizing cell plate grid, and the Classes to build
#   these palettes
#
# DEFINES
#   DictPalette
#     methods:
#       set
#       get
#       __getitem__
#
#   ListPalette
#     methods:
#       set
#       get
#       __getitem__
#
#   CategoriesPalette: DictPalette instance
#   SampleSeriesPalette: ListPalette instance
################################################################################
class DictPalette(object):
	def __init__(self, palette = None, no_case = True):
		super(DictPalette, self).__init__()
		self.palette = {}
		self.no_case = no_case
		self.set(palette)

	def set(self, palette = None):
		if palette:
			if self.no_case:
				# copy the original data
				self.palette = dict((k.lower(), v) for k, v in palette.items())
			else:
				self.palette = palette
		return self

	def get(self, key):
		try:
			if self.no_case:
				return self.palette[key.lower()]
			else:
				return self.palette[key]
		except:
			# if key miss, return default value (black)
			return "#000000"

	def __getitem__(self, key):
		return self.get(key)


################################################################################
class ListPalette(object):
	def __init__(self, palette = None):
		super(ListPalette, self).__init__()
		self.palette = []
		self.set(palette)

	def set(self, palette = None):
		if palette:
			# copy the original data
			self.palette = list(palette)
		return self

	def get(self, index):
		try:
			return self.palette[index]
		except:
			# if index out-of-bound, return default value (black)
			return "#000000"

	def __getitem__(self, index):
		return self.get(index)


CategoriesPalette = DictPalette({
	"blank": "#A0A0A0",
	"eline": "#000000",
	"hkeep": "#000000",
	"redox": "#FF0000",
	"oxidative": "#FF0000",
	"membrane": "#0080FF",
	"protein": "#00A000",
	"general": "#804000",
	"dna": "#FF8000",
})

SampleSeriesPalette = ListPalette([
	"#FF4000",
	"#21FF21",
	"#534BE5",
	"#FFB523",
	"#20C11B",
	"#BC57D6",
	"#B9FF22",
	"#10CCBF",
	"#E072AB",
	"#A3E01F",
	"#0D94D8",
	"#AAAAAA",
])
