#!/usr/bin/env python3
import unittest
import subprocess as sub
from bin import get_dust


class TestMJD(unittest.TestCase):
    def test_main(self):
        sub.call(get_dust.__file__, shell=True)


if __name__ == '__main__':
    unittest.main()
