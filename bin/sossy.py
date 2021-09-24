#!/usr/bin/env python3
"""This is a tool to help us parse SOS outputs during the night
Author: Dylan Gatlin
"""

import sys
import numpy as np
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from pathlib import Path

try:
    import sjd
except ImportError as e:
    from bin import sjd

from sdssobstools import sdss_paths


__version__ = '3.0.1'

sys.setrecursionlimit(10000)  # This is a very dangerous operation that
# BeautifulSoup seems to need for many SOS pages. It needs to recursively look
# through the whole html file to make a fancy python object out of it. If this
# number is too high, it could easily trigger a segmentation fault


class Plate:
    def __init__(self, plate_id, sjds, args):
        self.plate_id = plate_id
        self.sjds = sjds
        self.args = args
        self.useful_sjds = []
        self.all_exp_ids = []
        self.all_snrs = []
        self.snr_totals = []

    def parse_sjd(self, mjd):
        if self.args.verbose:
            print('Searching {}'.format(mjd))
        log_html = sdss_paths.sos / f"{mjd}/logfile-{mjd}.html"
        if not log_html.exists():
            return
        log_soup = BeautifulSoup(log_html.open('r').read(), 'html.parser')
        exp_ids = []
        exp_snrs = []
        for plate in log_soup.find_all('caption'):
            if self.plate_id in plate.find('b').decode():
                for line in plate.find('tr').decode().split('<tr>'):
                    if '>(S/N)^2' in line:
                        sci_images = line.split('<td align="RIGHT">')
                        exp_ids.append(sci_images[0].split('SCIENCE-')[-1][:-1])
                        if 'bold' not in sci_images[2]:
                            exp_snrs.append(sci_images[2:4])
                        else:
                            exp_snrs.append([sci_images[2].split()[-1],
                                             sci_images[3].split()[-1]])
                last_line = plate.find_all('tr')[-1].decode().split(
                    '<td align="RIGHT">')
                try:
                    last_line[1]
                except IndexError:
                    continue
                if 'TOTAL (S/N)^2' in last_line[1]:
                    self.useful_sjds.append(mjd)
                    self.all_exp_ids.append(np.array(exp_ids).astype(int))
                    self.all_snrs.append(np.array(exp_snrs).astype(float))
                    # Sometimes there's a bold secion in the S/N values, this
                    # loop ignores any of those values on the left
                    # The if is in case there is no reported S/N^2 (I think tha
                    # means the exposures were bad or no science exposures were
                    # taken.
                    if (('bold' not in last_line[2])
                       and ('bold' not in last_line[3])):
                        self.snr_totals.append(last_line[2:4])
                    else:
                        if 'bold' not in last_line[2].split()[-1]:
                            self.snr_totals.append([last_line[2].split()[-1],
                                                    last_line[3].split()[-1]])
                        else:
                            self.snr_totals.append([0., 0.])

    def parse_plate(self):
        for mjd in self.sjds:
            self.parse_sjd(mjd)
        # print(self.useful_sjds)
        self.useful_sjds = np.array(self.useful_sjds).astype(int)
        self.all_exp_ids = self.all_exp_ids
        self.all_snrs = np.array(self.all_snrs)
        self.snr_totals = np.array(self.snr_totals).astype(float)

    def print_summary(self):

        for i, mjd in enumerate(self.useful_sjds):
            print('    SJD: {}'.format(mjd))
            print('        {:^8} {:^4} {:^4}'.format('ExpID', 'R1', 'B1'))
            for expid, snr in zip(self.all_exp_ids[i], self.all_snrs[i]):
                print('        {:0>8.0f} {:4.1f} {:4.1f}'.format(
                    expid, snr[0], snr[1]))
            print('    Night total: {:4.1f} {:4.1f}'.format(
                *self.snr_totals[i]))
        if bool(self.snr_totals.sum()):
            print('\nTotal S/N^2: {:4.1f} {:4.1f}\n'.format(
                    *self.snr_totals.sum(axis=0)))

        else:
            print("This plate hasn't been observed\n")


def parse_args():
    parser = ArgumentParser(description='A tool to help guide observations by'
                                        ' reading SOS S/N^2 and summing the'
                                        ' S/N^2 across multiple days. Default'
                                        ' usage is to use the -p argument for'
                                        ' each plate you want, which will check'
                                        ' the last 40 mjds.')
    parser.add_argument('-p', '--plates', nargs='+',
                        help='Plate numbers to create a summary for')
    parser.add_argument('-m', '--mjds', dest='sjds', nargs='+',
                        help='mjds (actually sjds) to search')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbosity for debugging')
    parser.add_argument('--version', action='store_true',
                        help='Print script version')
    args = parser.parse_args()

    if args.version:
        print(__version__)

    if not args.sjds:
        today = sjd.sjd()
        first_sjd = today - 40
        args.sjds = np.arange(first_sjd, today + 1).astype(int)

    return args


def main():
    args = parse_args()

    for plate in args.plates:
        print('Plate: {}'.format(plate))
        pl = Plate(plate, args.sjds, args)
        pl.parse_plate()
        pl.print_summary()


if __name__ == '__main__':
    main()
