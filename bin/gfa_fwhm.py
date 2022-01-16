#!/usr/bin/env python3
"""A script to process gfa images with the SDSS-V FPS"""
import tqdm
import fitsio
import sep
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from matplotlib.patches import Ellipse

from bin import sjd
from sdssobstools import sdss_paths

sns.set(style="darkgrid")

__author__ = "Dylan Gatlin"


def build_filt(obj_arr: np.ndarray):
    ecc = np.sqrt(obj_arr['a']**2 - obj_arr['b']**2) / obj_arr['a']
    # print(np.percentile(ecc, 75))
    # print(obj_arr["cpeak"], obj_arr["peak"].max())
    # print(ecc, np.mean(ecc), np.percentile(ecc, 95))
    filt = (
        # (obj_arr["flux"] > np.percentile(obj_arr["flux"], 80))
        ((obj_arr["a"] * 0.216) > 0.5)
        & (obj_arr["cpeak"] < 60000)
        # & (obj_arr["npix"] > 5)
        & (ecc < 0.7)
        )
    # print(obj_arr["a"] * 0.216, obj_arr["b"] * 0.216,
    # np.mean([obj_arr["a"], obj_arr["b"]]))
    return filt

def show_img(obj_arr: np.ndarray, obj_filt, data_sub: np.ndarray, plot_file=""):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    m, s = np.mean(data_sub), np.std(data_sub)
    im = ax.imshow(data_sub, interpolation='nearest', cmap='gray',
                   vmin=m-s, vmax=m+s, origin='lower')

    # plot an ellipse for each object
    for i, obj in enumerate(obj_arr[obj_filt]):
        e = Ellipse(xy=(obj['x'], obj['y']),
                    width=6*obj['a'],
                    height=6*obj['b'],
                    angle=obj['theta'] * 180. / np.pi)
        e.set_facecolor('none')
        e.set_edgecolor('red')
        ax.add_artist(e)
    plt.show()
    if plot_file:
        fig.savefig(plot_file)



class GFASet:
    def __init__(self, verbose=False, exp_num_plot=False):
        self.paths = []
        self.filter = []
        self.isots = []
        self.fwhms = []
        self.focuses = []
        self.n_objs = []
        self.im_nums = []
        self.verbose = verbose
        self.exp_num_plot = exp_num_plot

    def add_index(self, paths_iter, im_num):
        paths = []
        filter = []
        focus = []
        isots = []
        fwhms = []
        n_objs = []
        for p in paths_iter:
            paths.append(p)
            if p.exists():
                filter.append(True)
                fwhm, n, objs = self.get_fwhm(p, verbose=self.verbose)
                hdr = fitsio.read_header(p, 1)
                focus.append(hdr["FOCUS"])
                fwhms.append(fwhm)
                n_objs.append(n)
            else:
                filter.append(False)
                focus.append(np.nan)
                fwhms.append(np.nan)
                n_objs.append(0)
        self.im_nums.append(im_num)
        self.paths.append(paths)
        self.focuses.append(focus)
        self.filter.append(filter)
        self.fwhms.append(fwhms)
        self.n_objs.append(n_objs)

    @staticmethod
    def get_fwhm(path: Path, verbose: bool=False):
        data = fitsio.read(path, 1)
        bkg = sep.Background(data.astype(float))
        objs = sep.extract(data - bkg, 1.5, bkg.globalrms)
        filt = build_filt(objs)
        if verbose:
            print(f"Using {filt.sum()}/{filt.shape[0]} points")
        # fwhm = 0.216 * np.mean(2.0*np.sqrt(
            # 2.0*np.log(2)*(objs['a'][filt]**2 + objs['b'][filt]**2))
        # )
        fwhm = 0.216 * np.mean(
             np.sqrt(2 *  np.log(2) * objs['a'][filt]**2 + objs['b'][filt]**2)
            )
        return fwhm, filt.sum(), objs

    def sort(self):
        self.im_nums = np.array(self.im_nums)
        self.paths = np.array(self.paths)
        self.focuses = np.array(self.focuses)
        self.filter = np.array(self.filter)
        self.fwhms = np.array(self.fwhms)
        self.n_objs = np.array(self.n_objs)
        sorter = self.im_nums.argsort()
        self.im_nums = self.im_nums[sorter]
        self.paths = self.paths[sorter]
        self.focuses = self.focuses[sorter]
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
    
    @staticmethod
    def quadratic(x, a, b, c): 
        return a * x**2 + x * b + c

    def plot(self, plot_file):
        if not self.exp_num_plot:
            flat_foc = self.focuses.flatten()
            flat_fwhms = self.fwhms.flatten()
            nan_filt = ~np.isnan(flat_fwhms)
            a, b, c = np.polyfit(flat_foc[nan_filt],
                                 flat_fwhms[nan_filt], deg=2)
            focs = np.linspace(flat_foc[nan_filt].min(),
                               flat_foc[nan_filt].max(), 100)
            fit = -b / 2 /a
            fwhm = self.quadratic(fit, a, b, c)
            mum = "\u03BCm"
            if a > 0:
                fit_found = False
                print("Optimal focus not found")
            else:
                fit_found = True
                print(f'Optimal Focus is at {fit:.0f}{mum} with Width {fwhm:.1f}"')
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        if (not self.exp_num_plot) and fit_found:
            ax.plot(focs, self.quadratic(focs, a, b, c),
                    label=f"Quad Fit, best={-b / 2 / a:.0f}", alpha=0.8)
            ax.axvline(-b / 2 / a, c="r", linestyle="--", alpha=0.6)
        for i in range(6):
            if self.exp_num_plot:
                ax.plot(self.im_nums, self.fwhms[:, i], linewidth=1, alpha=0.8,
                label=f"GFA {i+1}")
                ax.scatter(self.im_nums, self.fwhms[:, i], s=6, alpha=0.8)
            else:
                ax.scatter(self.focuses[:, i], self.fwhms[:, i], s=6, alpha=0.8,
                label=f"GFA {i+1}")
        ax.legend()
        if self.exp_num_plot:
            ax.set_xlabel("Exposure Number")
        else:
            ax.set_xlabel("Focus ($\mu m$)")
        ax.set_ylabel("FWHM (arcseconds)")
        plt.show()
        if plot_file:
            fig.savefig(plot_file, dpi=100)


def parse_args():
    parser = argparse.ArgumentParser(description="Prints a table of FWHMs from"
        " GFAs, useful for focus sweeps")
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
    parser.add_argument("-e", "--exp-num", action="store_true",
                        help="Don't fit the images to a curve,"
                        " produce a time series across exposure numbers")
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
    parser.add_argument("-d", "--plot-image", action="store_true",
        help="Plot an the sky image with ellipses traced, only works with -f"
    )
    args = parser.parse_args()

    return args


def main(args=None):
    if args is None:
        args = parse_args()
    gfas = GFASet(verbose=args.verbose, exp_num_plot=args.exp_num)
    if args.bias:
        raise NotImplementedError("This script doesn't support bias reduction")
    if args.file:
        print(f"{'File Name':<20} {'FWHM':<6} {'N Objects':<11} {'Mean Ecc':<6}")
        print('=' * 80)
        for file in args.file:
            if '*' not in file:
                file = Path(file)
                if not file.exists():
                    raise FileNotFoundError(f"Couldn't find {file.absolute()}")
                fwhm, n_objs, objs = gfas.get_fwhm(file)
                filt = build_filt(objs)
                ecc = (np.sqrt(objs['a'][filt]**2 - objs['b'][filt]**2)
                    / objs['a'][filt])
                print(f"{file.name:<20} {fwhm:>6.2f} {filt.sum():>5.0f}"
                    f"/{len(objs):<5.0f}  {np.mean(ecc):>6.2f}")
                if args.plot_image:
                    data = fitsio.read(file, 1)
                    bkg = sep.Background(data.astype(float))
                    show_img(objs, filt, data - bkg)
            else:
                file = Path(file)
                for p in file.parent.glob(file.name):
                    pass
    elif not args.window:
        path_stem = sdss_paths.gcam / f"{args.mjd}"
        low = 1000
        high = 0
        for file in path_stem.glob("gimg-gfa5n-*.fits*"):
            ind = int(file.name.split("-")[-1].rstrip(
                ".fits").rstrip(".fits.gz"))
            if ind < low:
                low = ind
            if ind > high:
                high = ind
        if high > low:
            args.window = f"{low:.0f}-{high:.0f}"

    if args.window:
        low, high = args.window.split("-")
        try:
            low = int(low)
            high = int(high)
        except ValueError:
            raise ValueError(f"Window range must be two ints with a - between"
                             f" them {args.window}")
        if args.verbose:
            print(f"Reading Images from {low} to {high} in MJD {args.mjd}")
        for im_num in tqdm.tqdm(range(low, high + 1)):
            im_ps = []
            for n in range(1, 7):
                p = (sdss_paths.gcam / f"{args.mjd}/proc-gimg-gfa{n:.0f}n-"
                     f"{im_num:0>4.0f}.fits")
                if not p.exists():
                    p = (sdss_paths.gcam / f"{args.mjd}/proc-gimg-gfa{n:.0f}n-"
                         f"{im_num:0>4.0f}.fits.gz")
                if not p.exists():
                    p = (sdss_paths.gcam / f"{args.mjd}/gimg-gfa{n:.0f}n-"
                         f"{im_num:0>4.0f}.fits")
                if not p.exists():
                    p = (sdss_paths.gcam / f"{args.mjd}/gimg-gfa{n:.0f}n-"
                         f"{im_num:0>4.0f}.fits.gz")
                im_ps.append(p)

            gfas.add_index(im_ps, im_num)
        gfas.sort()
        gfas.print()
        if args.plot:
            gfas.plot(args.plot_file)
    return 0


if __name__ == "__main__":
    main()
