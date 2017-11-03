#!/usr/bin/env python3
################################################################################
# this module stores the color palettes used in rendering categories
################################################################################


################################################################################
class DictPalette(object):
	def __init__(self, pallete = None, no_case = True):
		super(DictPalette, self).__init__()
		self.pallete = {}
		self.no_case = no_case
		self.set_pallete_dict(pallete)

	def set_pallete_dict(self, pallete = None):
		if pallete:
			if self.no_case:
				self.pallete = dict((k.lower(), v) for k, v in pallete.items())
			else:
				self.pallete = pallete
		return self

	def get(self, key):
		try:
			if self.no_case:
				return self.pallete[key.lower()]
			else:
				return self.pallete[key]
		except:
			# if key miss, return default value (black)
			return "#000000"

	def __getitem__(self, key):
		return self.get(key)


################################################################################
class ListPalette(object):
	def __init__(self, pallete = None):
		super(ListPalette, self).__init__()
		self.pallete = []
		self.set_pallete_list(pallete)

	def set_pallete_list(self, pallete = None):
		if pallete:
			self.pallete = pallete
		return self

	def get(self, index):
		try:
			return self.pallete[index]
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
