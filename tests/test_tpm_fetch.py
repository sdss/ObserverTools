#!/usr/bin/env python3
import pytest
from pathlib import Path
from bin import tpm_fetch


class DummyArgs(object):
    pass


args = DummyArgs()
args.t1 = '2020-11-05T06:00:00'
args.t2 = '2020-11-06T06:30:00'
args.mjd = None
args.channels = ['alt_pos', 'az_pos']
args.verbose = True


class TestTPMFetch():

    def test_time_range(self):
        tpm_fetch.main(args=args)

    def test_one_mjd(self):
        args.t1 = None
        args.t2 = None
        args.mjd = 59159
        tpm_fetch.main(args=args)


if __name__ == '__main__':
    pytest.main()
