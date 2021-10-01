#!/usr/bin/env python3

"""
DG: A rewrite of Elena's aptest script.

2020-06-18  DG  3.1  Most prints are under self.args.verbose, added fiber list
 to function returns to make it easier to use while imported in sloan_log.py
2020-08-13  DG  3.2  Replaced most of the code with
 apogee_data.APOGEERaw.ap_test, which uses quickred files
"""

import numpy as np
from argparse import ArgumentParser
from pathlib import Path
from sdssobstools import apogee_data, sdss_paths

__version__ = '3.2.1'


class ApogeeFlat:
    def __init__(self, args):
        self.args = args
        # self.args.verbose = True
        imax1 = 500
        imax2 = 100  # vm cutoff=120
        self.n_fibers = 300
        self.dome_flat_shape = np.zeros((imax1, imax2), dtype=np.int64)
        # Copied from sloan_log.py
        if self.args.legacy:
            master_path = (Path(apogee_data.__file__).absolute().parent.parent
                           / 'dat/utr_master_flat_21180043.npy')
            if not master_path.exists():
                master_path = (Path(apogee_data.__file__).absolute(
                ).parent.parent.parent / 'dat/utr_master_flat_21180043.npy')
            self.ap_master_all = np.load(master_path.as_posix())
            # Cut and paste from aptest, don't ask how it works
            cutoff = 200.
            self.n_fibers = 0  # fiber number
            k = 0  # pix number in fiber
            qj = False
            for i in range(2048):
                if (self.n_fibers >= imax1) or (k >= imax2):
                    print("break", self.n_fibers, k)
                    break
                if self.ap_master_all[i] >= cutoff:
                    self.dome_flat_shape[self.n_fibers, k] = i
                    qj = True
                    k = k + 1
                else:
                    if qj:
                        qj = False
                        self.n_fibers += 1
                        k = 0
            self.ap_master = np.zeros(300)
            for j in range(self.n_fibers):
                self.ap_master[j] = 0
                for k in range(10):
                    if self.dome_flat_shape[j, k] != 0:
                        self.ap_master[j] += self.ap_master_all[
                            self.dome_flat_shape[j, k]]

        else:
            master_path = (Path(apogee_data.__file__).absolute().parent.parent
                           / 'dat/master_dome_flat_1.npy')
            if not master_path.exists():
                master_path = (Path(apogee_data.__file__).absolute(
                ).parent.parent.parent / 'dat/master_dome_flat_1.npy')
            master_data = np.load(master_path.as_posix())
            self.ap_master = np.average(master_data[:, 900:910], axis=1)


    def run_inputs(self):
        for i, sjd in enumerate(self.args.sjds):
            for exp in self.args.exps[i]:
                ap_img = apogee_data.APOGEERaw(sdss_paths.ap_archive / 
                                               f"{sjd}/apR-a-{exp}.apz",
                                               self.args)
                if self.args.legacy:
                    ap_img.ap_test((2952, 2953), master_col=self.ap_master,
                                   plot=self.args.plot, legacy=self.args.legacy,
                                   dome_flat_shape=self.dome_flat_shape,
                                   print_it=True)

                else:
                    ap_img.ap_test((900, 910), master_col=self.ap_master,
                                   plot=self.args.plot, legacy=self.args.legacy,
                                   dome_flat_shape=self.dome_flat_shape,
                                   print_it=True)


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
    parser.add_argument('--legacy', action='store_true',
                        help='Whether or not to use the old aptest algorithm')
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose debugging output")
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

    apogee = ApogeeFlat(args)
    apogee.run_inputs()


if __name__ == '__main__':
    main()
