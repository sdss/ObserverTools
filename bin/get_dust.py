#!/usr/bin/env python3
"""
Written by Elena, rewritten by Dylan. This script gets the dust counts in a
 night and prints it

Changelog:
2020-06-20  DG  Moving main contents into a function for import functionality
 """
import argparse
import datetime
from astropy.time import Time
import numpy as np
from bin import sjd, epics_fetch

__version__ = '3.2.2'

telemetry = epics_fetch.telemetry

# TAI_UTC =34;
TAI_UTC = 0
aSjd = 40587.3
bSjd = 86400.0


def get_time_stamps(mjd):
    startStamp = sjd.sjd_to_time(int(mjd))
    endStamp = sjd.sjd_to_time(int(mjd + 1))
    start = datetime.datetime.fromtimestamp(startStamp)
    end = datetime.datetime.fromtimestamp(endStamp)
    return start, end


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
    return args


def get_dust(mjd, args):
    start, end = get_time_stamps(mjd)
    if args.verbose:
        print("mjd= {}".format(mjd))
        print("MJD start/end times")
        print(start)
        print(end)
    dust_data = telemetry.get('25m:apo:dustb', start, end, interpolation='raw',
                              scan_archives=False)
    enclosure_data = telemetry.get('25m:apo:encl25m', start, end,
                                   interpolation='raw', scan_archives=False)
    if args.verbose:
        print("         Enlosure open/close times")
        print(enclosure_data)
        print("")
    dust_data.times = Time(dust_data.times)
    dust_data.values = np.array(dust_data.values)
    enclosure_data.times = Time(enclosure_data.times)
    enclosure_data.values = np.array(enclosure_data.values)
    dust_sum = 0
    if args.verbose:
        print("date   time    dust    encl    sum")
    for t, d in zip(dust_data.times, dust_data.values):
        enclosure_state = enclosure_data.values[enclosure_data.times < t][-1]
        if enclosure_state > 0:
            dust_sum = dust_sum + d * 5 / 60.0
        if args.verbose:
            print("{} {:7.0f}    {:.0f}    {:10.0f}"
                  "".format(t, d, enclosure_state, dust_sum))
    return dust_sum


def main():
    args = parse_args()
    dust_sum = get_dust(args.mjd, args)
    print("Integrated Dust Counts: ~{:<5.0f}dust-hrs".format(
          dust_sum - dust_sum % 100))


if __name__ == '__main__':
    main()
