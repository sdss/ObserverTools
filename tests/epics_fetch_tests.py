#!/usr/bin/env python3
import unittest
from bin import epics_fetch
import subprocess as sub


class TestAPTest(unittest.TestCase):
    def test_known_date(self):
        epics_fetch.main()

    def test_archive(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        from channelarchiver import Archiver
        archive = Archiver(epics_fetch.server)
        archive.scan_archives()

    def test_help(self):
        """"Prints the help if -h is provided"""
        sub.call('../bin/epics_fetch.py -h', shell=True)


if __name__ == '__main__':
    unittest.main()
