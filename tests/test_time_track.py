#!/usr/bin/env python3
import pytest
from pathlib import Path
from bin import time_track


class DummyArgs(object):
    pass

args = DummyArgs()
args.m1 = 59216
args.m2 = 59246
args.apogee = True
args.bhm = True
args.mwm = True
args.eboss = False
args.manga = False
args.force = True
args.verbose = True


class TestTimeTrack():

    def test_january_2021(self):
        # time_track.main(args=args)
        pass


if __name__ == '__main__':
    pytest.main()
