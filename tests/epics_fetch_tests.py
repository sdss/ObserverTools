#!/usr/bin/env python3
import unittest
import subprocess as sub
from astropy.time import Time
from bin import epics_fetch


class TestAPTest(unittest.TestCase):
    def test_known_date(self):
        t = Time('2020-06-07T00:00', format='isot')
        t - 1.
        data = epics_fetch.get_data('25m:mcp:cwPositions', t.isot, (t-1).isot)
        epics_fetch.print_data(data)

    def test_archive(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        from channelarchiver import Archiver
        archive = Archiver(epics_fetch.server)
        archive.scan_archives()

    def test_help(self):
        """"Prints the help if -h is provided"""
        sub.call('{} -h'.format(epics_fetch.__file__), shell=True)


if __name__ == '__main__':
    unittest.main()
