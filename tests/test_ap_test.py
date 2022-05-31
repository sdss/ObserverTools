#!/usr/bin/env python3
import pytest
from pathlib import Path
from bin import ap_test
import numpy as np
from sdssobstools import sdss_paths


class Args(object):
    pass

args = Args()
args.sjds = [59730]
args.exps = [[41680010, 41680011, 41680012, 41680013, 41680014, 41680015,
              41680016, 41680017, 41680018]]
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
