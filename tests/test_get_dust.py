#!/usr/bin/env python3
import pytest
import subprocess as sub
from bin import get_dust


def test_main():
    sub.call(get_dust.__file__, shell=True)


if __name__ == '__main__':
    pytest.main()
