#!/usr/bin/env python3


################################################################################
# this module only defines functions
def vector2string(vec, fmt = "%f", sep = "\t"):
	return sep.join([fmt % i for i in vec])

def array2d2string(A, fmt = "%.4f", sep = "\t"):
	return ("\n").join([sep.join([fmt % i for i in j]) for j in A])

def array2d2string_by_row(A, row_fmt):
	return ("\n").join([row_fmt % tuple(i) for i in A])
