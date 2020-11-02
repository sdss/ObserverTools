#!/usr/bin/env python3
import unittest
import subprocess as sub
from pathlib import Path


class TestTelStatus(unittest.TestCase):
    def setUp(self):
        self.file = (Path(__file__).absolute().parent.parent
                     / 'bin/telescope_status.py')

    def test_print(self):
        out = sub.check_output([self.file], shell=True)
        for line in out.decode('utf-8').splitlines():
            print(line)
            self.assertNotIn('Error', line)
            self.assertNotIn('Exception', line)


if __name__ == '__main__':
    unittest.main()
