#!/usr/bin/env python3
import unittest
import subprocess as sub
from pathlib import Path


class TestHelp(unittest.TestCase):

    def test_noargs(self):
        """Runs the help like a user normally would"""
        here = Path(__file__).absolute().parent.parent
        sub.call([(here / 'bin/help.py').as_posix(), '-h'])


if __name__ == '__main__':
    unittest.main()
