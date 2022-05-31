#!/usr/bin/env python3
import pytest
from pathlib import Path
import subprocess as sub
from astropy.time import Time
from bin import influx_fetch
    
class TestInfluxFetch():
    def test_known_date(self):
        dust = Path(__file__).parent.parent / "flux/dust.flux"
        with dust.open('r') as fil:
            query = fil.read()
        influx_fetch.query(query, Time.now() - 1, Time.now(), interval="1h",
                           verbose=True)

    def test_archive(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        user_id, org_id, token = influx_fetch.get_key()
        client = influx_fetch.get_client(org_id, token)

    def test_help(self):
        """"Prints the help if -h is provided"""
        sub.call('{} -h'.format(influx_fetch.__file__), shell=True)


if __name__ == '__main__':
    pytest.main()
