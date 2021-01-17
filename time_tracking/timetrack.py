#!/usr/bin/env python

"""
mount disk to read data from sdss-hub

May (SJD 58240) - (SJD 58270)
April 58210 -- 58239
mjd 58271 - data with boss, apogee, manga

Examples:
timeTrack.py -a -m1 58268 -m2 58269 -v
timetrack.py -a -m1 58268 -m2 58269
timetrack.py -a -m1 58240 -m2 58270 -v
timetrack.py -b -v
timetrack.py -b -m1 58240 -m2 58270 -v

timetrack.py -b -a -m  -m1 58271 -m2 58271

"""

import argparse
# import eboss
# import manga
# import apogee
from bin import sjd
import warnings
import numpy as np
from pathlib import Path
import fitsio

warnings.filterwarnings('ignore')


def parse_args():
    desc = 'Creates a report of all observed plates for time tracking'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m1', '--mjd1', help='start mjd, default current mjd',
                        default=sjd.sjd(), type=int)
    parser.add_argument('-m2', '--mjd2', help='end mjd, default current mjd',
                        default=sjd.sjd(), type=int)
    parser.add_argument('-a', '--apogee', help='get APOGEE-2 report',
                        action="store_true")
    parser.add_argument('-b', '--bhm', help='get BHM report',
                        action="store_true")
    parser.add_argument('-e', '--eboss', help='get eBOSS report',
                        action="store_true")
    parser.add_argument('-m', '--mwm', help='get MWM report',
                        action="store_true")
    parser.add_argument('--manga', help='get MaNGA report',
                        action="store_true")
    parser.add_argument('-v', '--verbose', help='verbose data',
                        action="store_true")
    args = parser.parse_args()
    return args


def main(args=parse_args()):
    if np.any((args.apogee, args.bhm, args.mwm, args.eboss, args.manga)):
        plate_dates = {}
        for mjd in range(args.mjd1, args.mjd2 + 1):
            qr_path = Path(f'/data/apogee/quickred/{mjd}/')
            if not qr_path.exists():
                qr_path = Path(f'~/data/apogee/quickred/{mjd}/')
                if not qr_path.exists():
                    raise FileNotFoundError('No path to apogee quickred'
                                            ' files found, cannot build'
                                            ' plate list\n'
                                            f'{qr_path.as_posix()}')
            for fits in qr_path.glob('ap1D-a-*.fits.fz'):
                header = fitsio.read_header(fits.as_posix())
                if header['PLATEID'] in plate_dates.keys():
                    if mjd not in plate_dates[header['PLATEID']]:
                        plate_dates[header['PLATEID']].append(mjd)
                else:
                    plate_dates[header['PLATEID']] = [mjd]

    else:
        raise argparse.ArgumentTypeError('No mission arguments given,'
                                         ' nothing to do')
    # if args.boss:
    #     eboss.eboss(args.mjd1, args.mjd2, args.verbose)
    # if args.apogee:
    #     apogee.apogee(args.mjd1, args.mjd2, args.verbose)
    # if args.manga:
    #     manga.manga(args.mjd1, args.mjd2, args.verbose)
    # if args.mwm:
    #     pass
    # if args.bhm:
    #     pass

    return 0


if __name__ == "__main__":
    main()
