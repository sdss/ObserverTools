#!/usr/bin/env python3
"""
Written by Dylan. This script gets the dust counts in a
 night and prints it

Changelog:
2020-06-20  DG  Moving main contents into a function for import functionality
 """
import argparse
import datetime
from astropy.time import Time
import numpy as np
from pathlib import Path
from bin import sjd, influx_fetch

__version__ = '3.3.0'


def parse_args():
    today = sjd.sjd()
    desc = ('Integrates the dust accumulated in a night using TRON and prints'
            ' it. Needs no args for the current date.')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', '--mjd', help='enter mjd, default is current mjd',
                        default=today, type=int)
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='print incremental dust data')
    args = parser.parse_args()
    
    if (not args.mjd ) and (not args.start_time and not args.end_time):
        args.start_time = Time(sjd.sjd(), format="mjd")
        args.end_time = Time.now()
    elif args.mjd:
        args.start_time = Time(args.mjd - 1, format="mjd")
        args.end_time = Time(args.mjd, format="mjd")
    return args


def main(args=None):
    if args is None:
        args = parse_args()
    q_path = Path(__file__).parent.parent / "flux/dust.flux"
    if not q_path.exists():
        raise FileNotFoundError(f"Couldn't find Flux query {q_path.absolute()}")
    query = q_path.open('r').read()
    result = influx_fetch.query(query, args.start_time, args.end_time)
    dust_sum = result[0].records[-1]["_value"]
    print("Integrated Dust Counts: ~{:<5.0f}dust-hrs".format(
          dust_sum - dust_sum % 100))


if __name__ == '__main__':
    main()
