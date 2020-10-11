#!/usr/bin/env python3
import unittest
import subprocess as sub
from pathlib import Path


class TestXMID(unittest.TestCase):

    def test_4cam(self):
        """Runs a test from a normal 4-camera xmid
        """
        here = Path(__file__).parent.absolute()
        bin = here.parent / 'bin'
        sub.call([bin / 'WAVEMID', '4907.9', '7989.9', '5000.8', '8037.1'])


if __name__ == '__main__':
    unittest.main()