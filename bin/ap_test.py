#!/usr/bin/env python3

"""
DG: A rewrite of Elena's aptest script.

2020-06-18  DG  3.1  Most prints are under self.args.verbose, added fiber list
 to function returns to make it easier to use while imported in sloan_log.py
2020-08-13  DG  3.2  Replaced most of the code with
 apogee_data.APOGEERaw.ap_test, which uses quickred files
"""

import numpy as np
import fitsio
from argparse import ArgumentParser
# from pathlib import Path
from python import apogee_data

__version__ = '3.2.0'


class ApogeeFlat:
    def __init__(self, master_flat, args):
        master_data = fitsio.read(master_flat)
        self.ap_master = np.average(master_data[:, 900:910], axis=1)
        self.args = args
        self.args.verbose = True

    def run_inputs(self):
        for i, sjd in enumerate(self.args.sjds):
            for exp in self.args.exps[i]:
                ap_img = apogee_data.APOGEERaw('/data/apogee/archive/{}/apR-a'
                                               '-{}.apz'.format(
                                                   sjd, exp), self.args)
                ap_img.ap_test((900, 910), master_col=self.ap_master,
                               plot=self.args.plot)


def parse_args():
    parser = ArgumentParser(usage='ap_test.py <mjd> <exp_id> [<exp_id_2>]'
                                  ' [<mjd_2> <exp_id>]',
                            description='A script to test the transparency of'
                                        ' an APOGEE dome flat. It compares the '
                                        ' flat to a known master.')
    parser.add_argument('positionals', nargs='+',
                        help='SJD, followed by any dome flats in that night.'
                             ' Multiple MJDs can be included, as long as the'
                             ' exposures follow the correct MJD')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='Whether or not to plot the output using'
                             ' matplotlib')
    args = parser.parse_args()

    # The end result of this section is that you end up with a 1D array of mjds
    # and a 2D list of shape mjd by exps of exp ids in that day.
    args.sjds = []
    args.exps = [[]]
    day_i = 0
    for arg in args.positionals:
        if len(str(arg)) <= 5:
            args.sjds.append(arg)
            args.exps.append([])
            day_i = len(args.sjds) - 1
        else:
            if len(args.sjds) == 0:
                raise Exception('Must provide a 5-digit mjd before an 8-digit'
                                ' exposure number')
            else:
                args.exps[day_i].append(arg)

    return args


def main():
    args = parse_args()
    master_path = '/data/apogee/quickred/59011/ap1D-a-34490027.fits.fz'
    apogee = ApogeeFlat(master_path, args)
    apogee.run_inputs()


if __name__ == '__main__':
    main()
