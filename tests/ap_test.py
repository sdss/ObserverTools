#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import ap_test


class TestAPTest(unittest.TestCase):
    def test_no_args(self):
        pass

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        pass


if __name__ == '__main__':
    unittest.main()
