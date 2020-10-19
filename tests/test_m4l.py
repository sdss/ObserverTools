#!/usr/bin/env python3
import unittest
from bin import m4l


class TestM4L(unittest.TestCase):

    def test_noargs(self):
        """Run m4l like normal"""
        m4l.mirrors()


if __name__ == '__main__':
    unittest.main()
