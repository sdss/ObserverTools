#!/usr/bin/env python3
import pytest
from bin import m4l


class TestM4L():

    def test_noargs(self):
        """Run m4l like normal"""
        print(m4l.mirrors())


if __name__ == '__main__':
    pytest.main()
