#!/usr/bin/env python3
import unittest
import os
from bin import boss_sha1sum
from pathlib import Path


class TestBOSSSHA1Sum(unittest.TestCase):

    def test_here(self):
        """Runs it on 3 boss images that are in this directory"""
        here = Path(__file__).parent
        boss_sha1sum.write_hashes(here, here / 'boss.sha1sum')

    def test_check_unique(self):
        """This ensures that test_here creates unique hashes"""
        hashes_file = Path(__file__).parent / 'boss.sha1sum'
        lines = hashes_file.open('r').readlines()
        hashes_list = []
        for line in lines:
            hsh = line.split()[0]
            self.assertNotIn(hsh, hashes_list)
            hashes_list.append(hsh)

    def test_old(self):
        """This is how it used to be written, and can be used a benchmark, this
        should be slower"""
        sjd = 0
        cmd = 'sha1sum sdR-*.fit.gz > %d.sha1sum' % sjd
        os.system(cmd)


if __name__ == '__main__':
    unittest.main()
    (Path(__file__).parent / 'boss.sha1sum').unlink()
