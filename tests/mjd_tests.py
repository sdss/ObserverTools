#!/usr/bin/env python3
import unittest
from bin import mjd
from astropy.time import Time

class TestMJD(unittest.TestCase):

    def test_astropy(self):
        """Checks to see if astropy.time agrees with mjd.mjd"""
        astropy_mjd = int(Time.now().mjd)
        mjd_mjd = mjd.mjd()
        print(astropy_mjd, mjd_mjd)
        self.assertEqual(astropy_mjd, mjd_mjd)


if __name__ == '__main__':
    unittest.main()