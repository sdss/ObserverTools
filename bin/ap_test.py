#!/usr/bin/env python3

"""
DG: A rewrite of Elena's aptest script.

2020-06-18  DG  3.1  Most prints are under self.args.verbose, added fiber list
 to function returns to make it easier to use while imported in sloan_log.py
 TODO: This usually doesn't work
"""

import numpy as np
import fitsio
from argparse import ArgumentParser
from pathlib import Path

__version__ = 3.1


class ApogeeFlat:
    def __init__(self, master_path, args):
        self.args = args
        self.limits = []
        self.n_fibers = 0
        self.master_data = np.loadtxt(master_path)
        self.master_fiber_data = self.ap_bin(self.master_data)
        self.standard_path = Path('/data/apogee/archive/')
        if self.args.verbose:
            print('Master={}'.format(master_path.name))

    def run_inputs(self):
        for i, mjd in enumerate(self.args.mjds):
            self.test_mjd(mjd, self.args.exps[i])

    def test_mjd(self, mjd, exps):
        for exp in exps:
            fil = self.standard_path / '{}/apR-b-{}.apz'.format(mjd, exp)
            if fil.exists():
                self.test_image(fil)
            else:
                print("The following file doesn't exist\n {}".format(fil))

    def test_image(self, fil):
        try:
            if self.args.verbose:
                print('    Flat {}'.format(fil.relative_to(self.standard_path)))
        except ValueError:
            if self.args.verbose:
                print('    Flat {}'. format(fil))
        data = fitsio.read(fil, 1)

        fiber_data = self.red_1d(data)

        flux_ratio = fiber_data / self.master_fiber_data
        missing = flux_ratio < 0.2
        faint = (0.2 <= flux_ratio) & (flux_ratio < 0.7)
        bright = ~missing & ~faint
        i_missing = np.where(missing)
        i_faint = np.where(faint)
        i_bright = np.where(bright)
        missing_bundles = self.create_bundles(i_missing)
        faint_bundles = self.create_bundles(i_faint)
        if self.args.verbose:
            print('Missing Fibers: {}'.format(missing_bundles))
            print('Faint Fibers: {}'.format(faint_bundles))
            print()

        if self.args.plot:
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9, 4))
            ax = fig.gca()
            x = np.arange(self.n_fibers) + 1
            ax.plot(x[i_bright], flux_ratio[i_bright], 'o', c=(0, 0.6, 0.533))
            ax.plot(x[i_faint], flux_ratio[i_faint], 'o', c=(0.933, 0.466, 0.2))
            ax.plot(x[i_missing], flux_ratio[i_missing], 'o',
                    c=(0.8, 0.2, 0.066))
            ax.set_xlabel('Fiber ID')
            ax.set_ylabel('Throughput Efficiency')
            ax.axis([1, 300, -0.2, 1.35])
            ax.grid(True)
            ax.axhline(0.7, c=(0, 0.6, 0.533))
            ax.axhline(0.2, c=(0.933, 0.466, 0.2))
            ax.set_title('APOGEE Fiber Relative Intensity', size=15)
            fig.show()
        return missing_bundles, faint_bundles

    def red_1d(self, arr):
        """Returns a 1d slice of a 2d array given"""
        # This slice method is similar to the one used in the original aptest,
        # but TODO this needs to be tested rigorously
        # There are some science concerns about this algorithm's effectiveness
        # because it only uses a single column and doesn't account for dithers
        # well. This could be greatly improved.
        slce = np.average(arr[:, 900:910], axis=1)
        binned_slce = self.ap_bin(slce)
        return binned_slce

    def count_fibers(self, arr):

        assert arr.ndim == 1, 'ap_bin only takes 1D arrays'
        # Goes through the array and adds a fiber every time it goes from below
        # 200 to above 200, and then appends every row number that it stays
        # above 200.
        on_fiber = False
        for i, x in enumerate(arr):
            if x >= 200:
                if not on_fiber:
                    on_fiber = True
                    self.limits.append([])
                    self.n_fibers += 1
                self.limits[self.n_fibers - 1].append(i)
            else:
                if on_fiber:
                    on_fiber = False
        print('N Fibers: {}'.format(self.n_fibers))

    def ap_bin(self, arr):
        """Bins the rows by fiber, for now, it bins every 10"""
        assert arr.ndim == 1, 'ap_bin only takes 1D arrays'

        # Now that there is a 2D list of shape n_fiber by fiber_pix_width, we
        # can go through and bin them
        data = []
        for i, lims in enumerate(self.limits):
            data.append(0)
            for j, pix in enumerate(lims):
                data[i] += arr[pix]  # Adds the pixel to the fiber bin data[j]

        data = np.array(data)
        return data

    @staticmethod
    def create_bundles(subset):
        bundles = [subset[0]]
        b = 0
        for loc in subset:
            if bundles[b].size > 0:
                if bundles[b] + 1 == loc:
                    if loc % 30 == 1:
                        bundles.append(loc)
                        b += 1
                    else:
                        bundles[b] = '{} - {}'.format(
                            bundles[b].split()[0], loc)
                else:
                    bundles.append(loc)
                    b += 1
        return bundles


def parse_args():
    parser = ArgumentParser('A script to test the transparency of an APOGEE'
                            ' dome flat. It compares the flat to a known'
                            ' master.')
    parser.add_argument('positionals', nargs='+',
                        help='MJDs, followed by any dome flats in that night.'
                             ' Multiple MJDs can be included, as long as the'
                             ' exposures follow the correct MJD')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='Whether or not to plot the output using'
                             ' matplotlib')
    args = parser.parse_args()

    # The end result of this section is that you end up with a 1D array of mjds
    # and a 2D list of shape mjd by exps of exp ids in that day.
    args.mjds = []
    args.exps = [[]]
    for arg in args.positionals:
        if len(str(arg)) <= 5:
            args.mjds.append(arg)
            args.exps.append([])
            day_i = len(args.mjds) - 1
        else:
            try:
                args.exps[day_i].append(arg)
            except IndexError:
                raise Exception('Must provide a 5-digit mjd before an 8-digit'
                                ' exposure number')

    args.mjds = args.mjds
    args.exps = args.exps
    return args


def main():
    args = parse_args()
    master_path = (Path(__file__).absolute().parent.parent
                   / 'dat/ap_master_flat_col_array.dat').absolute()
    apogee = ApogeeFlat(master_path, args)
    apogee.run_inputs()


if __name__ == '__main__':
    main()
