#!/usr/bin/env python3
import pytest
from pathlib import Path
from bin import ap_test
import numpy as np
from sdssobstools import sdss_paths


class Args(object):
    pass


args = Args()
args.sjds = [59900]
args.exps = [[43380010, 43380011, 43380012, 43380021, 43380022, 43380023]]
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
