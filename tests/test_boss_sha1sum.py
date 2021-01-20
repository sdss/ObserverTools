#!/usr/bin/env python3
import unittest
import subprocess as sub
from bin import boss_sha1sum
from pathlib import Path


class TestBOSSSHA1Sum(unittest.TestCase):

    def test_find_sha1sum(self):
        """Checks to see if sha1sum is installed"""
        x = sub.check_output('which sha1sum', shell=True)
        self.assertTrue(x)

    def test_here(self):
        """Runs it on 3 boss images that are in this directory"""
        here = Path(__file__).parent
        boss_sha1sum.write_hashes(here, here / 'boss.sha1sum')
        (here / 'boss.sha1sum').unlink()

    def test_check_unique(self):
        """This ensures that test_here creates unique hashes"""
        here = Path(__file__).parent
        boss_sha1sum.write_hashes(here, here / 'boss.sha1sum')
        hashes_file = here / 'boss.sha1sum'
        with hashes_file.open('r')as fil:
            hashes_list = []
            for line in fil:
                hsh = line.split()[0]
                self.assertNotIn(hsh, hashes_list)
                hashes_list.append(hsh)

    def inactive_test_old(self):
        """This is how it used to be written, and can be used a benchmark, this
        should be slower"""
        mjd_known = 59009
        cmd = 'sha1sum sdR-*.fit.gz > {}.sha1sum'.format(mjd_known)
        sub.call(cmd, shell=True)
        sub.call('rm {}.sha1sum'.format(mjd_known), shell=True)


if __name__ == '__main__':
    unittest.main()

