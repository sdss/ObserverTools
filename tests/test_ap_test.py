#!/usr/bin/env python3
import pytest
from pathlib import Path
from bin import ap_test
import numpy as np
from sdssobstools import sdss_paths


class Args(object):
    pass

args = Args()
args.sjds = [59801]
args.exps = [[42390012, 42390013, 42390014, 42390033, 42390034, 42390035,
              42390036]]
args.plot = False
args.verbose = True

class TestAPTest:
    def test_known_date(self):
        self.atest = ap_test.ApogeeFlat(args)
        self.atest.run_inputs()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        assert sdss_paths.ap_utr.exists()

    def test_plotting(self):
        """Tests the plotting routine"""
        args.plot = True
        self.atest = ap_test.ApogeeFlat(args)
        self.atest.run_inputs()


if __name__ == '__main__':
    pytest.main()
