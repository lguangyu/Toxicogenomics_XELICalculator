#!/usr/bin/env python3
################################################################################
# AssayLib/Exceptions
#
# this module reimplements some errors that was used in 

################################################################################
# base exceptions
class AsRuntimeError(RuntimeError):
	pass

class AsValueError(AsRuntimeError):
	pass

class PrerequestError(AsRuntimeError):
	pass
