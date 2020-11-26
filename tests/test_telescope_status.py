#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import telescope_status


class TestTelStatus(unittest.TestCase):
    def setUp(self):
        self.file = (Path(__file__).absolute().parent.parent
                     / 'bin/telescope_status.py')

    def test_print(self):
        telescope_status.main()


if __name__ == '__main__':
    unittest.main()
