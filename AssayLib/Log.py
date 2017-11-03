#!/usr/bin/env python3


################################################################################
# manages the log file
# called only by the AssayPlate module
class Log(object):
	# by default, the log file will be saved as ./log
	# by default of the AssayPlate, the log file will be saved as
	# path/to/output/dir/log
	def __init__(self, file = "log", dir = "."):
		super(Log, self).__init__()
		self.log_file = dir + "/" + file
		self._fh = open(self.log_file, "w")

	def __del__(self):
		self._fh.close()

	def fh(self):
		return self._fh

	# protected write message to file, only if message contains something
	def write(self, message = None):
		if message:
			self._fh.write(message)
