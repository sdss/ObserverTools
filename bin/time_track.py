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
        return(f'{self.plate_id:5}, {self.cart:2}, {self.lead_survey:11},'
               f' {self.b_count:3} BOSS, {self.a_count:3} APOGEE')

    def __eq__(self, other: str):
        return other == self.lead_survey


def parse_args():
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


def main(args=parse_args()):
    if not any((args.apogee, args.bhm, args.mwm, args.eboss, args.manga)):
        raise args.error('No mission arguments given, nothing to do')
    plates = {}
    for mjd in tqdm.tqdm(list(range(args.m1, args.m2 + 1))):

        # APOGEE QL Check
        qr_path = Path(f'/data/apogee/quickred/{mjd}/')
        # The quickred image needs to exist. If you're on a Mac using Catalina,
        # you can't make /data, so a ~/data directory with 1D quickreds will
        # work.
        if not qr_path.exists():
            qr_path = Path(f'~/data/apogee/quickred/{mjd}/')
            if not qr_path.exists():
                if not args.force:
                    raise FileNotFoundError('No path to apogee quickred files'
                                            ' found, cannot build plate list\n'
                                            f'{qr_path.as_posix()}')
                else:
                    continue
        # Checks each 1D-a- image for plate info, and add it to the count if
        # it's a science image
        for fits in qr_path.glob('ap1D-a-*.fits.fz'):
            header = fitsio.read_header(fits.as_posix())
            if header['EXPTYPE'] == 'OBJECT':
                if header['PLATEID'] in plates.keys():
                    plates[header['PLATEID']].a_count += 1
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

        # SOSS Check
        sos_path = Path(f'/data/boss/sos/{mjd}/logfile-{mjd}.html')
        if not sos_path.exists():
            sos_path = Path(f'/data/manga/dos/{mjd}/web/logfile-{mjd}.html')
            if not sos_path.exists():
                sos_path = Path(f'~/data/boss/sos/{mjd}/logfile-{mjd}.html')
                if not sos_path.exists():
                    if not args.force:
                        raise FileNotFoundError('No path to SOS file'
                                                ' found, cannot build plate'
                                                f' list\n{sos_path.as_posix()}')
                    else:
                        continue
        sos_soup = BeautifulSoup(sos_path.open('r').read(), 'html.parser')
        for plate in sos_soup.find_all('caption'):
            plateid = int(plate.find('b').decode().split()[2])
            try:
                for line in plate.find('tr').decode().split('<tr>'):
                    if '>(S/N)^2' in line:
                        plates[plateid].b_count += 1
            except AttributeError:
                print(f'Failed to parse SOS on {mjd} with plate {plateid}')
                print(line)
                continue
    if args.verbose:
        print('Plates Data')
        for plate in plates.values():
            print(plate)
        print()
    b_big_total = 0
    a_big_total = 0


    if args.manga:
        print('='* 80)
        print(f'{"MaNGA":^80}')
        print('='* 80)
        b_tot = 0
        a_tot = 0
        p_count = 0
        for plateid in sorted(plates.keys()):
            plate = plates[plateid]
            if 'MaNGA dither' == plate:
                if args.verbose:
                    print(plate)
                p_count += 1
                b_tot += plate.b_count
                a_tot += plate.a_count
        print(f'Total BOSS exposures: {b_tot}\nTotal APOGEE Exposures:'
                f' {a_tot}\nPlates Visited: {p_count}')
        b_big_total += b_tot
        a_big_total += a_tot



    if args.apogee:
        print('='* 80)
        print(f'{"APOGEE-2":^80}')
        print('='* 80)
        b_tot = 0
        a_tot = 0
        p_count = 0
        for plateid in sorted(plates.keys()):
            plate = plates[plateid]
            if ('APOGEE-2' == plate) or ('APOGEE lead' == plate):
                if args.verbose:
                    print(plate)
                p_count += 1
                b_tot += plate.b_count
                a_tot += plate.a_count
        print(f'Total BOSS exposures: {b_tot}\nTotal APOGEE Exposures:'
                f' {a_tot}\nPlates Visited: {p_count}')
        b_big_total += b_tot
        a_big_total += a_tot

    if args.mwm:
        print('='* 80)
        print(f'{"Milky Way Mapper":^80}')
        print('='* 80)
        b_tot = 0
        a_tot = 0
        p_count = 0
        for plateid in sorted(plates.keys()):
            plate = plates[plateid]
            if 'MWM lead' == plate:
                if args.verbose:
                    print(plate)
                p_count += 1
                b_tot += plate.b_count
                a_tot += plate.a_count
        print(f'Total BOSS exposures: {b_tot}\nTotal APOGEE Exposures:'
              f' {a_tot}\nPlates Visited: {p_count}')
        b_big_total += b_tot
        a_big_total += a_tot

    if args.bhm:
        print('='* 80)
        print(f'{"Black Hole Mapper":^80}')
        print('='* 80)
        p_count = 0
        b_tot = 0
        a_tot = 0
        for plateid in sorted(plates.keys()):
            plate = plates[plateid]
            if 'BHM lead' == plate:
                if args.verbose:
                    print(plate)
                p_count += 1
                b_tot += plate.b_count
                a_tot += plate.a_count
        print(f'Total BOSS exposures: {b_tot}\nTotal APOGEE Exposures:'
              f' {a_tot}\nPlates Visited: {p_count}')
        b_big_total += b_tot
        a_big_total += a_tot
    print('='*80)
    print(f'{"Overall":^80}')
    print('='*80)

    print(f'Total BOSS exposures: {b_big_total}\nTotal APOGEE Exposures:'
            f' {a_big_total}\nTotal Plates Visited: {len(plates)}')

    return 0


if __name__ == "__main__":
    main()

