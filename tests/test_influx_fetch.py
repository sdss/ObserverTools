#!/usr/bin/env python3
import unittest
from pathlib import Path
import subprocess as sub
from astropy.time import Time
from bin import influx_fetch
    
class TestInfluxFetch(unittest.TestCase):
    def test_known_date(self):
        dust = Path(__file__).parent.parent / "flux/dust.flux"
        with dust.open('r') as fil:
            query = fil.read()
        influx_fetch.query(query, Time.now(), Time.now() - 1, interval="1h")

    def test_archive(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        client = influx_fetch.get_client()
        print(client.ready())

    def test_help(self):
        """"Prints the help if -h is provided"""
        sub.call('{} -h'.format(epics_fetch.__file__), shell=True)


if __name__ == '__main__':
    unittest.main()
