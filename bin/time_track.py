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
from bin import sjd
# import warnings
from pathlib import Path
import fitsio
import tqdm
from bs4 import BeautifulSoup
import sys
import textwrap
from typing import Union, Tuple
from sdssobstools import sdss_paths

# warnings.filterwarnings('ignore')
sys.setrecursionlimit(10000)  # This is a very dangerous operation that


# BeautifulSoup seems to need for many SOS pages. It needs to recursively look
# through the whole html file to make a fancy python object out of it. If this
# number is too high, it could easily trigger a segmentation fault


class Plate:
    def __init__(self, plate_id: int, lead_survey: str, cart: int):
        self.plate_id = plate_id
        self.lead_survey = lead_survey
        self.cart = cart
        self.b_count = 0
        self.a_count = 0

    def __str__(self):
        return (f'{self.plate_id:5}, {self.lead_survey:11},'
                f' {self.b_count:3} BOSS, {self.a_count:3} APOGEE')

    def __eq__(self, other: str):
        return other == self.lead_survey


def summarize(mission_name: str, mission_key: Union[str, Tuple[str, str]],
              plates: dict, verbose: bool = False):
    print('=' * 80)
    print(f'{mission_name:^80}')
    print('=' * 80)
    b_tot = 0
    a_tot = 0
    plate_ids = []
    for plate_id in sorted(plates.keys()):
        plate = plates[plate_id]
        condition = (mission_key == plate if isinstance(mission_key, str)
                     else any([key == plate for key in mission_key]))
        if condition:
            if verbose:
                print(plate)
            plate_ids.append(f'{plate_id:.0f}')
            b_tot += plate.b_count
            a_tot += plate.a_count
    print(textwrap.fill(', '.join(plate_ids), width=80))
    print(f'Total BOSS exposures: {b_tot}\nTotal APOGEE Exposures:'
          f' {a_tot}\nPlates Visited: {len(plate_ids)}\n')
    return b_tot, a_tot


def parse_args():
    print("Run")
    desc = 'Creates a report of all observed plates for time tracking'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--m1', help='start mjd, default current mjd',
                        default=sjd.sjd(), type=int)
    parser.add_argument('--m2', help='end mjd, default current mjd',
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
    parser.add_argument('-f', '--force', action='store_true',
                        help='Forces analysis to conitinue even if a file is'
                             ' missing from /data or ~/data')

    args = parser.parse_args()
    return args


def main(args=None):
    if args is None:
        args = parse_args()
    if not any((args.apogee, args.bhm, args.mwm, args.eboss, args.manga)):
        raise args.error('No mission arguments given, nothing to do')
    plates = {}
    for mjd in tqdm.tqdm(list(range(args.m1, args.m2 + 1))):

        # APOGEE QL Check

        qr_path = sdss_paths.ap_qr / f"{mjd}"
        # The quickred image needs to exist. If you're on a Mac using Catalina,
        # you can't make /data, so a ~/data directory with 1D quickreds will
        # work.
        if not qr_path.exists():
            qr_path = Path.home() / f'data/apogee/quickred/{mjd}/'
            if not qr_path.exists():
                if not args.force:
                    raise FileNotFoundError('No path to apogee quickred files'
                                            ' found, cannot build plate list\n'
                                            f'{qr_path.as_posix()}')
                else:
                    print(f'Failed to parse APOGEE quickred on {mjd} with'
                          f' plate {qr_path}')
                    continue
        # Checks each 1D-a- image for plate info, and add it to the count if
        # it's a science image
        if len(list(qr_path.glob("ap1D-a-*.fits.fz"))) == 0:
            ap_re = "ap2D-a-*.fits.fz"
        else:
            ap_re = "ap1D-a-*.fits.fz"
        for fits in qr_path.glob(ap_re):
            header = fitsio.read_header(fits.as_posix())
            if header['EXPTYPE'] == 'OBJECT':
                if header['PLATEID'] in plates.keys():
                    # If a BHM plate is observed with a MWM bypass, then it will
                    # be saved with SRVYMODE="MWM lead". To fix this, I need
                    # to see if they match, and if they don't check to see if
                    # either is BHM, and if so, replace the lead with BHM.
                    # This won't be an issue if glob finds a non-bypassed plate
                    # first, which is kinda random, so it doesn't show up all
                    # the time.
                    if plates[header['PLATEID']] != header['SRVYMODE']:
                        if ((header['SRVYMODE'] == 'BHM lead')
                                or (plates[header["PLATEID"]] == "BHM lead")):
                            plates[header["PLATEID"]].lead_survey = "BHM lead"

                    plates[header["PLATEID"]].a_count += 1
                else:
                    if header['SRVYMODE'] != 'None':
                        plates[header['PLATEID']] = Plate(header['PLATEID'],
                                                          header['SRVYMODE'],
                                                          header['CARTID'])
                        plates[header['PLATEID']].a_count += 1
                    else:  # APOGEE-2
                        plates[header['PLATEID']] = Plate(header['PLATEID'],
                                                          header['PLATETYP'],
                                                          header['CARTID'])
                        plates[header['PLATEID']].a_count += 1

        # SOS Check
        sos_path = sdss_paths.sos / f"{mjd}/logfile-{mjd}.html"
        if not sos_path.exists():
            sos_path = sdss_paths.dos / f"{mjd}/web/logfile-{mjd}.html"
            if not sos_path.exists():
                if not args.force:
                    raise FileNotFoundError('No path to SOS file'
                                            ' found, cannot build plate'
                                            f' list\n{sos_path.as_posix()}')
                else:
                    continue
        sos_soup = BeautifulSoup(sos_path.open('r').read(), 'html.parser')
        for plate in sos_soup.find_all('caption'):
            plate_id = int(plate.find('b').decode().split()[2])
            try:
                for line in plate.find('tr').decode().split('<tr>'):
                    if '>(S/N)^2' in line:
                        plates[plate_id].b_count += 1
            except AttributeError:
                print(f'Failed to parse SOS on {mjd} with plate {plate_id}')
                continue
    if args.verbose:
        print('Plates Data')
        for plate in plates.values():
            print(plate)
        print()
    b_big_total = 0
    a_big_total = 0

    if args.manga:
        b, a = summarize('MaNGA', 'MaNGA dither', plates, args.verbose)
        b_big_total += b
        a_big_total += a

    if args.apogee:
        b, a = summarize('APOGEE-2', ('APOGEE lead', 'APOGEE-2'), plates,
                         args.verbose)
        b_big_total += b
        a_big_total += a

    if args.mwm:
        b, a = summarize('Milky Way Mapper', 'MWM lead', plates, args.verbose)
        b_big_total += b
        a_big_total += a

    if args.bhm:
        b, a = summarize('Black Hole Mapper', 'BHM lead', plates, args.verbose)
        b_big_total += b
        a_big_total += a

    print('=' * 80)
    print(f'{"Overall":^80}')
    print('=' * 80)

    print(f'Total BOSS exposures: {b_big_total}\nTotal APOGEE Exposures:'
          f' {a_big_total}\nTotal Plates Visited: {len(plates)}')

    return 0


if __name__ == "__main__":
    main()
