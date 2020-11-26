#!/usr/bin/env python3
import unittest
import subprocess as sub
from astropy.time import Time
from bin import epics_fetch


class TestEPICSFetch(unittest.TestCase):
    def test_known_date(self):
        t = Time('2020-06-07T00:00', format='isot')
        data = epics_fetch.get_data('25m:mcp:cwPositions', t.datetime,
                                    (t-1).datetime)
        epics_fetch.print_data(data)

    def test_archive(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        # This serves no purpose because simply importing the library is a pass
        return 

    def test_help(self):
        """"Prints the help if -h is provided"""
        sub.call('{} -h'.format(epics_fetch.__file__), shell=True)


if __name__ == '__main__':
    unittest.main()
