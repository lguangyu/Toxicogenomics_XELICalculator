#!/usr/bin/env python3

from AssayLib.Exceptions import AsRuntimeError
from AssayLib.AssayPlate import AssayPlate
from AssayLib.EColiSample import EColiSample

assay = AssayPlate("example_assay", 96, overwrite = True,
					# this layout will be used across the board, for each sample
					layout = "./example/EColi.96.P2.layout",
					# load the plate data here
					data_file = "./example/plate_data.txt")

# tell the plate this sample is for E-Coli, so should use EColiSample object
# and the name, it is essential to distinguish other samples
# NOTE: no need to include assay name here, since all output will be written
# into output/assay_name/
# offset is the (ROW, COLUMN) coordinates on the plate, relative to the TOP-LEFT cell,
# which, is (0, 0); thus sample anchored at A2 will be offset (0, 1)
assay.add_sample(EColiSample, name = "C1", offset = (0, 0), untreated = True)
# untreated=True tells the plate: this should be treated as an inner control
assay.add_sample(EColiSample, name = "C2", offset = (0, 1))
assay.add_sample(EColiSample, name = "C3", offset = (0, 2))
assay.add_sample(EColiSample, name = "C4", offset = (0, 3))
assay.add_sample(EColiSample, name = "C5", offset = (0, 4))
assay.add_sample(EColiSample, name = "C6", offset = (0, 5))
# call this to run for all samples, to calculate final OD and GFP
assay.analyze()
