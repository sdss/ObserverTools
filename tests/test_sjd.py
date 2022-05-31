#!/usr/bin/env python3
import pytest
from astropy.time import Time
from bin import sjd


class TestSJD():

    def test_astropy(self):
        """Checks to see if astropy.time agrees with mjd.mjd"""
        astropy_mjd = int(Time.now().mjd + 0.3)
        mjd_mjd = sjd.sjd()
        print(astropy_mjd, mjd_mjd)
        assert astropy_mjd == mjd_mjd, "Astropy solution must match sjd.sjd"


if __name__ == '__main__':
    pytest.main()
