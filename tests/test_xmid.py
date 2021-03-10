#!/usr/bin/env python3
import unittest
import subprocess as sub
from pathlib import Path


class TestXMID(unittest.TestCase):

    def test_4cam(self):
        """Runs a test from a normal 4-camera xmid
        """
        here = Path(__file__).parent.absolute()
        bin_dir = here.parent / 'bin'
        x = sub.check_output([bin_dir / 'XMID', '2043.7', '2046.8', '2042.7',
                              '2019.0'])
        self.assertNotIn(x.decode('utf-8'), 'Traceback')

    def test_2cam(self):
        """Runs a test from a normal 4-camera xmid
        """
        here = Path(__file__).parent.absolute()
        bin_dir = here.parent / 'bin'
        x = sub.check_output([bin_dir / 'XMID', '2049.2', '2046.9'])
        self.assertNotIn(x.decode('utf-8'), 'Traceback')


if __name__ == '__main__':
    unittest.main()
