#!/usr/bin/env python3
import unittest
from astropy.time import Time
from bin import sjd


class TestSJD(unittest.TestCase):

    def test_astropy(self):
        """Checks to see if astropy.time agrees with mjd.mjd"""
        astropy_mjd = int(Time.now().mjd + 0.3)
        mjd_mjd = sjd.sjd()
        print(astropy_mjd, mjd_mjd)
        self.assertEqual(astropy_mjd, mjd_mjd)


if __name__ == '__main__':
    unittest.main()
