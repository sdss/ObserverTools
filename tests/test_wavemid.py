#!/usr/bin/env python3
import unittest
import subprocess as sub
from pathlib import Path


class TestWAVEMID(unittest.TestCase):

    def test_4cam(self):
        """Runs a test from a normal 4-camera xmid
        """
        here = Path(__file__).absolute().parent
        bin_dir = here.parent / 'bin'
        x = sub.check_output(' '.join([(bin_dir / 'WAVEMID').as_posix(),
                                       '4907.9', '7989.9', '5000.8', '8037.1']),
                             shell=True)
        self.assertNotIn(x.decode('utf-8'), 'Traceback')

    def test_2cam(self):
        """Runs a test from a normal 4-camera xmid
        """
        here = Path(__file__).parent.absolute()
        bin_dir = here.parent / 'bin'
        x = sub.check_output([(bin_dir / 'WAVEMID').as_posix(), '4907.9',
                              '7989.9'])
        self.assertNotIn(x.decode('utf-8'), 'Traceback')


if __name__ == '__main__':
    unittest.main()
