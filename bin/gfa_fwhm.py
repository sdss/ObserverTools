#!/usr/bin/env python3

__author__ = "Dylan Gatlin"


import tqdm
import fitsio
import sep
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

from bin import sjd
from sdssobstools import sdss_paths


sns.set(style="darkgrid")

class GFASet:
    def __init__(self, verbose=False):
        self.paths = []
        self.filter = []
        self.isots = []
        self.fwhms = []
        self.n_objs = []
        self.im_nums = []
        self.verbose = verbose

    def add_index(self, paths_iter, im_num):
        paths = []
        filter = []
        isots = []
        fwhms = []
        n_objs = []
        for p in paths_iter:
            paths.append(p)
            if p.exists():
                filter.append(True)
                fwhm, n = self.get_fwhm(p, verbose=self.verbose)
                fwhms.append(fwhm)
                n_objs.append(n)
            else:
                filter.append(False)
                fwhms.append(np.nan)
                n_objs.append(0)
        self.im_nums.append(im_num)
        self.paths.append(paths)
        self.filter.append(filter)
        self.fwhms.append(fwhms)
        self.n_objs.append(n_objs)

    @staticmethod
    def get_fwhm(path: Path, verbose: bool=False):
        data = fitsio.read(path, 1)
        bkg = sep.Background(data.astype(float))
        objects = sep.extract(data - bkg, 1.5, bkg.globalrms)
        filt = ((objects['a'] / objects['b'] < 2)
            & (objects['b'] / objects['a'] < 2)
            & (objects["flux"] > np.percentile(objects["flux"], 80))
            )
        if verbose:
            print(f"Using {filt.sum()}/{filt.shape[0]} points")
        fwhm = 0.216 * np.mean(2.0*np.sqrt(
            2.0*np.log(2)*(objects['a'][filt]**2 + objects['b'][filt]**2))
        )
        return fwhm, filt.sum()

    def sort(self):
        self.im_nums = np.array(self.im_nums)
        self.paths = np.array(self.paths)
        self.filter = np.array(self.filter)
        self.fwhms = np.array(self.fwhms)
        self.n_objs = np.array(self.n_objs)
        sorter = self.im_nums.argsort()
        self.im_nums = self.im_nums[sorter]
        self.paths = self.paths[sorter]
        self.filter = self.filter[sorter]
        self.fwhms = self.fwhms[sorter]
        self.n_objs = self.n_objs[sorter]

    
    def print(self):
        if self.verbose:
            print("Measurements in arcseconds with a place scale of 0.216")
        print(f"{'Img #':<6} {'GFA1':<6} {'GFA2':<6} {'GFA3':<6} {'GFA4':<6}"
            f" {'GFA5':<6} {'GFA6':<6} {'N Objs':<6}")
        print('=' * 80)
        for i, im, in enumerate(self.im_nums):
            print(f"{im:>6} "
                + " ".join([f"{f:>6.2f}"
                    if not np.isnan(f) else f"{'-':>6}"
                    for (j, f) in enumerate(self.fwhms[i])]
                ) + f" {np.mean(self.n_objs[i]):>6.0f}"
            )
    
    def plot(self):
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        for i in range(6):
            ax.plot(self.im_nums, self.fwhms[:, i], linewidth=1, alpha=0.8)
            ax.scatter(self.im_nums, self.fwhms[:, i], linewidth=1, alpha=0.8,
                label=f"GFA {i+1}")
        ax.legend()
        ax.set_xlabel("Image Number")
        ax.set_ylabel("FWHM (arcseconds)")
        plt.show()



def parse_args():
    parser = argparse.ArgumentParser("Prints a table of FWHMs from GFAs, useful"
                                     " for focus sweeps")
    parser.add_argument("-b", "--bias", help="The index of a bias frame")
    parser.add_argument("-m", "--mjd", default=sjd.sjd())
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose debugging output")
    parser.add_argument("-f", "--file", nargs="+",
                        help="Specific files to process")
    parser.add_argument("-n", "--gfas", nargs="+", type=int, default=[2, 5])
    parser.add_argument("-w", "--window",
                        help="A dash separated beginning and end of the window."
                             " Always include a --master-field with your window."
                             " Ex: -w 15-50 -s 35")
    # parser.add_argument("-s", "--master-field", type=int,
    #                     help="The master field with all stars you want. Only"
    #                     " used in conjunction with --window. You need both"
    #                     " arguments.")
    parser.add_argument("-p", "--plot", action="store_true",
                        help="Show plot to analyze fit quality")
    parser.add_argument("-k", "--plot-file", help="Filename to save plot to."
                        " only works with --plot and --window together. If not"
                        " included, the plot will show up in a new window (or"
                        " maybe not depending on X11).")
    args = parser.parse_args()

    return args


def main(args=None):
    if args is None:
        args = parse_args()
    gfas = GFASet(verbose=args.verbose)
    if args.bias:
        raise NotImplementedError("This script doesn't support bias reduction")
    if args.file:
        print(f"{'File Name':20<} {'FWHM':6<} {'N Objects':9<}")
        print('=' * 80)
        for file in args.file:
            if '*' not in file:
                file = Path(file)
                if not file.exists():
                    raise FileNotFoundError(f"Couldn't find {file.absolute()}")
                fwhm, n_objs = gfas.get_fwhm(file)
                print(f"{file.name:20<} {fwhm:6>.2f} {n_objs:9>.0f}")
            else:
                file = Path(file)
                for p in file.parent.glob(file.name):
                    pass

    elif args.window:
        low, high = args.window.split("-")
        try:
            low = int(low)
            high = int(high)
        except ValueError:
            raise ValueError(f"Window range must be filled with ints"
                             f" {args.window}")
        if args.verbose:
            print(f"Reading Images from {low} to {high} in MJD {args.mjd}")
        for im_num in tqdm.tqdm(range(low, high + 1)):
            im_ps = []
            for n in range(1, 7):
                p = sdss_paths.gcam / f"{args.mjd}/gimg-gfa{n:.0f}n-{im_num:0>4.0f}.fits"
                im_ps.append(p)

            gfas.add_index(im_ps, im_num)
        gfas.sort()
        gfas.print()
        if args.plot:
            gfas.plot()

    return 0


if __name__ == "__main__":
    main()
