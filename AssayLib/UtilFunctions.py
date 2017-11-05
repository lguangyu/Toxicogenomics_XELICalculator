#!/usr/bin/env python3
################################################################################
# File: AssayLib/UtilFunctions.py
#   Author: Guangyu Li, Northeastern University, C&E Engineering
#   E-mail: li.gua@husky.neu.edu
################################################################################
# SYNOPSIS
#   *THIS MODULE ONLY DEFINES FUNCTIONS
#   Utility functions
#
# DEFINES
#   plate_type_to_shape
#   vector2string
#   array2d2string
#   array2d2string_by_row
################################################################################
def plate_type_to_shape(plate_type):
	if ((plate_type == 96) or (plate_type == "96")):
		return 8, 12
	elif ((plate_type == 384) or (plate_type == "384")):
		return 16, 24
	else:
		raise ValueError("bad plate size '%s'" % str(plate_type))

################################################################################
# array formatting functions, used to be in AssayLib/ArrayFormatting.py
def vector2string(vec, fmt = "%f", sep = "\t"):
	return sep.join([fmt % i for i in vec])

def array2d2string(A, fmt = "%.4f", sep = "\t"):
	return ("\n").join([sep.join([fmt % i for i in j]) for j in A])

def array2d2string_by_row(A, row_fmt):
	return ("\n").join([row_fmt % tuple(i) for i in A])
