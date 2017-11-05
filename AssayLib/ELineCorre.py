#!/usr/bin/env python3

import numpy
from scipy import stats
from matplotlib import pyplot
from AssayLib.Exceptions import AsRuntimeError
from AssayLib.ELineCorreGUI import ELineCorreGUI
from AssayLib.UtilFunctions import array2d2string_by_row, vector2string


class NoValueSelectedError(RuntimeError):
	pass

class ELineCorre(object):
	# all instances of ELineCorre need only one selector
	# it is expected no two eline corrections from the same assay plate will run 
	# simultaneously
	selector = ELineCorreGUI()

	def __init__(self, parent):
		super(ELineCorre, self).__init__()
		self.sample_name = parent.name()
		self.plot_path = "%s/%s_eline.png" % (parent.output_dir(),
											parent.name())

	############################################################################
	# thif func attempts a 4x (horizontal) by 3 (vertical) layout for all plots
	# here are some example output:
	#  n   h   v
	# ----------
	#  1   1   1
	#  2   2   1
	#  3   2   2
	#  4   2   2
	#  5   3   2
	@staticmethod
	def auto_fit_subplots(n):
		# attempt as 4 (horizontal) * 3 (vertical)
		nc = numpy.ceil(numpy.sqrt(n / 9) * 3)
		nr = numpy.ceil(n / nc)
		return int(nr), int(nc)

	############################################################################
	# draw the regression line based on reg result 'reg' on the 'axes'
	@staticmethod
	def _plot_regression_line(axes, reg):
		slope, intercept, r, p, se = reg
		x1, x2 = axes.get_xlim()
		y1, y2 = x1 * slope + intercept, x2 * slope + intercept
		axes.plot([x1, x2], [y1, y2], ls = "-", lw = 1, color = "#FF8000")

	############################################################################
	# print the lin regssion equaions, including r_val, p_val and std.err etc.,
	# to the 'axes'
	@staticmethod
	def _write_regression_equation(axes, reg):
		slope, intercept, r, p, se = reg
		xmin, xmax = axes.get_xlim()
		ymin, ymax = axes.get_ylim()
		x_text = xmin + 0.01
		y_step = (ymax - ymin) * 0.07

		axes.text(x_text, ymax - y_step * 1, "GFP = %.1f * OD + %.1f" % (
				slope, intercept), color = "#FF8000", weight = "semibold")
		axes.text(x_text, ymax - y_step * 3, r"r = %.8f" % (r ** 2))
		axes.text(x_text, ymax - y_step * 4, "p = %.5e" % p)
		axes.text(x_text, ymax - y_step * 5, "s.e = %.4f" % se)

	############################################################################
	# do lin regression and make multi-plots
	# save to png file, which will be used later, by the interactive select GUI
	def run_linreg_and_plot(self, _pyplot, save_path, nr, nc, OD, GFP, mask,
								plot_w = 4.5, plot_h = 4.5):
		fig, ax = _pyplot.subplots(nrows = nr, ncols = nc,
									figsize = (plot_w * nc, plot_h * nr))
		ax_1d = ax.flatten()
		all_regs = []
		for od, gfp, m, axes in zip(OD.T, GFP.T, mask.T, ax_1d):
			od_msk, gfp_msk = od[m], gfp[m]

			axes.scatter(od_msk, gfp_msk, s = 10, c = "#0040FF", marker = None)
			reg = tuple(stats.linregress(od_msk, gfp_msk))
			all_regs.append(reg)
			self._plot_regression_line(axes, reg)
			self._write_regression_equation(axes, reg)
			axes.set_xlabel("OD")
			axes.set_ylabel("GFP")
		_pyplot.tight_layout()
		_pyplot.savefig(save_path)
		_pyplot.close()
		return numpy.asarray(all_regs, dtype = float)

	############################################################################
	# launch an interative selector if needed
	# and return the values chosen for slope and intercept for final model
	# each is the mean of selected values
	def select_slope_and_intercept(self, nr, nc, all_regs):
		# select slope and intercept by interactive selector
		# however if only one, no need for interactive select
		# you have to use that
		n = len(all_regs)
		if n == 1:
			slope_i, inter_i = [0], [0]
		else:
			slope_i, inter_i = self.selector.launch(n, nr, nc,
													self.plot_path,
													self.sample_name)

		if not slope_i:
			raise NoValueSelectedError("slopes cannot be null selection")
		if not inter_i:
			raise NoValueSelectedError("intercepts cannot be null selection")

		slopes = all_regs[slope_i, 0]
		inters = all_regs[inter_i, 1]
		if len(inters) == 1:
			raise AsRuntimeError("must be at least 2 intercepts (this exception is thrown due to not implemented yet)")

		slope = slopes.mean()
		inter = inters.mean()
		inter_sd = inters.std()

		ret_msg = """Raw regressions:
Slope\tIntercept\tr^2\tp\tStd.err
%s
Selected:
Slopes: %s
Intercepts: %s
Final:
Slope: %f
Intercept: %f
Inter.SD: %f""" % (array2d2string_by_row(all_regs.tolist(), "%f\t%f\t%f\t%.8e\t%f"),
					vector2string(slopes),
					vector2string(inters),
					slope, inter, inter_sd)

		return slope, inter, inter_sd, ret_msg

	############################################################################
	# Feed the ELineCorre object with OD and GFP data
	# it should contain only the OD and GFP for 'ELINE' category of the layout
	# linear regression is used to figure out the slope and intercept
	def feed(self, OD, GFP, mask):
		_, num_eline_samples = OD.shape
		nr, nc = self.auto_fit_subplots(num_eline_samples)
		all_regs = self.run_linreg_and_plot(pyplot, self.plot_path,
												nr, nc, OD, GFP, mask)
		return self.select_slope_and_intercept(nr, nc, all_regs)





################################################################################
# test
################################################################################
# if __name__ == "__main__":
# 	import unittest

# 	class test(unittest.TestCase):
# 		def row_cols(self):
# 			pass

# 	suite = unittest.TestLoader().loadTestsFromTestCase(test)
# 	unittest.TextTestRunner(verbosity = 2).run(suite)
