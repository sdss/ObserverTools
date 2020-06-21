#!/usr/bin/env python3
import unittest
import subprocess as sub
from bin import boss_sha1sum
from pathlib import Path


class TestBOSSSHA1Sum(unittest.TestCase):

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
        lines = hashes_file.open('r').readlines()
        hashes_list = []
        for line in lines:
            hsh = line.split()[0]
            self.assertNotIn(hsh, hashes_list)
            hashes_list.append(hsh)

    def test_old(self):
        """This is how it used to be written, and can be used a benchmark, this
        should be slower"""
        mjd_known = 59009
        check_sha1sum = sub.Popen('which sha1sum', shell=True, stdout=sub.PIPE)
        sha1sum_loc = check_sha1sum.stdout.read().decode('utf-8')
        print(sha1sum_loc)
        if sha1sum_loc:
            cmd = 'sha1sum sdR-*.fit.gz > {}.sha1sum'.format(mjd_known)
            sub.call(cmd, shell=True)
            sub.call('rm {}.sha1sum'.format(mjd_known), shell=True)

        else:
            print('sha1sum not found, skipping')


if __name__ == '__main__':
    unittest.main()

