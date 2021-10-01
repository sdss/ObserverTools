#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import time_track


class TestTPMFetch(unittest.TestCase):

    def setUp(self):
        self.file = time_track.__file__

        class DummyArgs(object):
            pass

        self.args = DummyArgs()
        self.args.m1 = 59216
        self.args.m2 = 59246
        self.args.apogee = True
        self.args.bhm = True
        self.args.mwm = True
        self.args.eboss = False
        self.args.manga = False
        self.args.force = True
        self.args.verbose = True

    def test_january_2021(self):
        time_track.main(args=self.args)


if __name__ == '__main__':
    unittest.main()
