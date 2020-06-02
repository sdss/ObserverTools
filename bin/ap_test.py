#!/usr/bin/env python3

"""
DG: A rewrite of Elena's aptest script.
"""

import numpy as np
import fitsio
from argparse import ArgumentParser
from pathlib import Path
import starcoder42 as s


class ApogeeFlat:
    def __init__(self, master_path, args):
        self.args = args
        self.master_data = np.loadtxt(master_path)
        self.master_fiber_data = self.ap_bin(self.master_data)

    def test_image(self, fil):
        data = fitsio.read(fil, 0)
        fiber_data = self.red_1d(data)
        flux_ratio = fiber_data / self.master_fiber_data
        s.describe(flux_ratio)

    def run_inputs(self):
        for i, mjd in enumerate(self.args.mjds):
            self.test_mjd(mjd, self.args.exps[i])

    def red_1d(self, arr):
        """Returns a 1d slice of a 2d array given"""
        # This slice method is the one used in the original aptest, but there
        # are some issues with it since it looks at a single column, and ignores
        # a lot of useful data.
        slce = arr[:, 2952]
        binned_slce = self.ap_bin(slce)
        return binned_slce

    @staticmethod
    def ap_bin(arr):
        """Bins the rows by fiber, for now, it bins every 10"""
        assert arr.ndim == 1, 'ap_bin only takes 1D arrays'

        # Goes through the array and adds a fiber every time it goes from below
        # 200 to above 200, and then appends every row number that it stays
        # above 200.
        limits = []
        n_fibers = 0
        on_fiber = False
        for i, x in enumerate(arr):
            if x >= 200:
                if not on_fiber:
                    on_fiber = True
                    limits.append([])
                    n_fibers += 1
                limits[n_fibers - 1].append(i)
            else:
                if on_fiber:
                    on_fiber = False
        # Now that there is a 2D list of shape n_fiber by fiber_pix_width, we
        # can go through and bin them
        data = []
        for i, lims in enumerate(limits):
            data.append(0)
            for j, pix in enumerate(lims):
                data[i] += arr[pix]  # Adds the pixel to the fiber bin data[j]

        data = np.array(data)
        return data


    def test_mjd(self, mjd, exps):
        for exp in exps:
            fil = Path('/data/apogee/utr_cdr/{}/apRaw-{}.fits'.format(mjd, exp))
            if fil.exists():
                self.test_image(fil)
            else:
                print("The following file doesn't exist\n {}".format(fil))


def parse_args():
    parser = ArgumentParser('A script to test the transparency of an APOGEE'
                            ' dome flat. It compares the flat to a known'
                            ' master.')
    parser.add_argument('positional')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='Whether or not to plot the output using'
                             ' matplotlib')
    args = parser.parse_args()

    # The end result of this section is that you end up with a 1D array of mjds
    # and a 2D list of shape mjd by exps of exp ids in that day.
    args.mjds = []
    args.exps = [[]]
    day_i = 0
    for arg in args.positional:
        if len(str(arg)) <= 5:
            args.mjds.append(arg)
            day_i += 1
            args.exps.append([])
        else:
            args.exps[day_i].append(arg)

    args.mjds = args.mjds
    args.exps = args.exps


def main():
    args = parse_args()
    master_path = Path(__file__).parent.parent / 'tests/apRaw-03720068.fits'
    apogee = ApogeeFlat(master_path, args)


if __name__ == '__main__':
    main()
