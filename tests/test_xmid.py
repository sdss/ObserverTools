#!/usr/bin/env python3
import pytest
import subprocess as sub
from pathlib import Path


class TestXMID():

    def test_4cam(self):
        """Runs a test from a normal 4-camera xmid
        """
        here = Path(__file__).parent.absolute()
        bin_dir = here.parent / 'bin'
        x = sub.check_output([bin_dir / 'XMID', '2043.7', '2046.8', '2042.7',
                              '2019.0'])
        assert "Traceback" not in x.decode('utf-8')

    def test_2cam(self):
        """Runs a test from a normal 4-camera xmid
        """
        here = Path(__file__).parent.absolute()
        bin_dir = here.parent / 'bin'
        x = sub.check_output([bin_dir / 'XMID', '2049.2', '2046.9'])
        assert "Traceback" not in x.decode('utf-8')


if __name__ == '__main__':
    pytest.main()
