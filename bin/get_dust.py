#!/usr/bin/env python3

import argparse
import datetime
from channelarchiver import Archiver
import mjd
from astropy.time import Time
import numpy as np

ss = 'http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'
# ss='http://localhost:5080/telemetry/cgi/ArchiveDataServer.cgi'
archiver = Archiver(ss)
archiver.scan_archives()

# TAI_UTC =34;
TAI_UTC = 0
aSjd = 40587.3
bSjd = 86400.0


def get_time_stamps(sjd):
    startStamp = mjd.mjd_to_time(int(sjd + 0.3))
    endStamp = mjd.mjd_to_time(int(sjd + 1 + 0.3))
    start = datetime.datetime.fromtimestamp(startStamp)
    end = datetime.datetime.fromtimestamp(endStamp)
    return start, end


def parse_args():
    today = mjd.mjd()
    desc = 'integral dust calculation for one mjd'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', '--mjd', help='enter mjd, default is current mjd',
                        default=today, type=int)
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='print incremental dust data')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    start, end = get_time_stamps(args.mjd)
    if args.verbose:
        print("mjd= {}".format(today))
        print("MJD start/end times")
        print(start)
        print(end)
    dust_data = archiver.get('25m:apo:dustb', start, end, interpolation='raw',
                             scan_archives=False)
    enclosure_data = archiver.get('25m:apo:encl25m', start, end,
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

    print("Integrated Dust Counts: ~{:6.0f} dust-hrs".format(
          dust_sum - dust_sum % 100))


if __name__ == '__main__':
    main()

