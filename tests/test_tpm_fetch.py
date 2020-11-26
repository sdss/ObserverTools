#!/usr/bin/env python3
import unittest
import sys
import subprocess as sub
from pathlib import Path
from bin import tpm_fetch


class TestTPMFetch(unittest.TestCase):
    def setUp(self):
        self.file = Path(__file__).absolute().parent.parent / 'bin/tpm_fetch.py'

        class DummyArgs(object):
            pass

        self.args = DummyArgs()
        self.args.t1 = '2020-11-05T06:00:00'
        self.args.t2 = '2020-11-06T06:30:00'
        self.args.channels = ['alt_pos', 'az_pos']
        self.args.verbose = True

    def test_print(self):
        tpm_fetch.main(args=self.args)


if __name__ == '__main__':
    unittest.main()
