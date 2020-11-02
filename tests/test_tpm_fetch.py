#!/usr/bin/env python3
import unittest
import subprocess as sub
from pathlib import Path


class TestTPMFetch(unittest.TestCase):
    def setUp(self):
        self.file = Path(__file__).absolute().parent.parent / 'bin/tpm_fetch.py'

    def test_print(self):
        try:
            sub.check_output([self.file, '-p'], shell=True, stderr=sub.PIPE,
                             timeout=12)
        except sub.TimeoutExpired:
            print('No Errors in 10s')
            return


if __name__ == '__main__':
    unittest.main()
