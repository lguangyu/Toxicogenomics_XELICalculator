#!/usr/bin/env python3


################################################################################
# this module only defines functions
def plate_type_to_shape(plate_type):
	if ((plate_type == 96) or (plate_type == "96")):
		return 8, 12
	elif ((plate_type == 384) or (plate_type == "384")):
		return 16, 24
	else:
		raise ValueError("bad plate size '%s'" % str(plate_type))
