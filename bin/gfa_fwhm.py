#!/usr/bin/env python3
"""A script to process gfa images with the SDSS-V FPS"""
import time
import tqdm
import fitsio
import sep
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from matplotlib import animation
from matplotlib.patches import Ellipse
from astropy.time import Time

from bin import sjd
from sdssobstools import sdss_paths

sns.set(style="darkgrid")

__author__ = "Dylan Gatlin"

# camera_offsets = np.array([0.0, -50.2985, -41.05837499999998,
#    11.466562500000009, 52.425531914893625, 0.0])
camera_offsets = np.array([-1.8474999999999977, -52.08291666666667,
                           -111.43416666666663, 0.0,
                           35.64791666666667, 54.41166666666667])
camera_shifts = np.array([0., 0., +0.05, 0., -0.02])


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


def get_img_path(mjd: int, cam_num: int, exp_num: int):
    """Resolves a path of a gfa image, if none can be found, it will return a
    path object 'Null'
    """
    p = (sdss_paths.gcam / f"{mjd}/proc-gimg-gfa{cam_num:.0f}n-"
         f"{exp_num:0>4.0f}.fits")
    try:
        p.exists()
    except OSError:
        time.sleep(1)
    if not p.exists():
        p = (sdss_paths.gcam / f"{mjd}/proc-gimg-gfa{cam_num:.0f}n-"
             f"{exp_num:0>4.0f}.fits.gz")
    if not p.exists():
        p = (sdss_paths.gcam / f"{mjd}/gimg-gfa{cam_num:.0f}n-"
             f"{exp_num:0>4.0f}.fits")
    if not p.exists():
        p = (sdss_paths.gcam / f"{mjd}/gimg-gfa{cam_num:.0f}n-"
             f"{exp_num:0>4.0f}.fits.gz")
    if not p.exists():
        p = Path("Null")
    return p


class GFASet:
    def __init__(self, verbose: bool = False, gfas=np.array([2, 3, 4, 5, 6])):
        self.paths = []
        self.filter = []
        self.isots = []
        self.fwhms = []
        self.focuses = []
        self.n_objs = []
        self.im_nums = []
        self.verbose = verbose
        self.ani_fig = None
        self.ani_ax = None
        self.gfas = gfas

    def add_index(self, paths_iter, im_num: int):
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
                isots.append(hdr["DATE-OBS"])
                fwhms.append(fwhm)
                n_objs.append(n)
            else:
                filter.append(False)
                focus.append(np.nan)
                fwhms.append(np.nan)
                isots.append("2000-01-01")
                n_objs.append(np.nan)
        self.im_nums.append(im_num)
        self.paths.append(paths)
        self.focuses.append(focus)
        self.filter.append(filter)
        self.fwhms.append(fwhms)
        self.n_objs.append(n_objs)
        self.isots.append(isots)

    def remove_first_index(self):
        self.paths.pop(0)
        self.filter.pop(0)
        self.isots.pop(0)
        self.fwhms.pop(0)
        self.focuses.pop(0)
        self.n_objs.pop(0)
        self.im_nums.pop(0)

    @staticmethod
    def get_fwhm(path: Path, verbose: bool = False):
        try:
            path.exists()
        except OSError:
            pass
        try:
            data = fitsio.read(path, 1)
        except OSError:
            # For cases when the file is actively being written
            time.sleep(1)
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
            2 * np.sqrt(np.log(2) * (objs['a'][filt]**2 + objs['b'][filt]**2))
        )
        if fwhm > 5:
            fwhm = np.nan
        return fwhm, filt.sum(), objs

    def sort(self):
        self.aim_nums = np.array(self.im_nums)
        self.apaths = np.array(self.paths)
        self.afocuses = np.array(self.focuses)
        self.afilter = np.array(self.filter)
        self.afwhms = np.array(self.fwhms)
        self.an_objs = np.array(self.n_objs)
        self.aisots = Time(self.isots)
        sorter = self.aim_nums.argsort()
        self.aim_nums = self.aim_nums[sorter]
        self.apaths = self.apaths[sorter]
        self.afocuses = self.afocuses[sorter]
        self.afilter = self.afilter[sorter]
        self.afwhms = self.afwhms[sorter]
        self.an_objs = self.an_objs[sorter]
        self.aisots = self.aisots[sorter]

    def print(self):
        if self.verbose:
            print("Measurements in arcseconds with a place scale of 0.216")
        print(f"{'Img #':<6} {'Focus':<5} {'GFA1':<6} {'GFA2':<6} {'GFA3':<6}"
              f" {'GFA4':<6}"
              f" {'GFA5':<6} {'GFA6':<6} {'N Objs':<6}")
        print('=' * 80)
        for i, (im, foc) in enumerate(zip(self.aim_nums, self.afocuses)):
            if np.isnan(foc[1]):
                foc = f"{'-':>5}"
            else:
                foc = f"{foc[1]:>5.0f}"
            if np.all(np.isnan(self.an_objs[i])):
                n_objs = f"{'-':>6}"
            else:
                n_objs = f"{np.nanmean(self.an_objs[i]):>6.0f}"
            print(f"{im:>6} {foc:>5} "
                  + " ".join([f"{f:>6.2f}"
                              if not np.isnan(f) else f"{'-':>6}"
                              for (j, f) in enumerate(self.afwhms[i])]
                             ) + f" {n_objs:6>}"
                  )

    @staticmethod
    def quadratic(x: float, a: float, b: float, c: float):
        return a * x**2 + x * b + c

    def plot(self, plot_file, fig=None, ax=None, dont_print=False):
        flat_foc = (self.afocuses + camera_offsets[self.gfas - 1]).flatten()
        flat_fwhms = self.afwhms.flatten()
        flat_nstars = self.an_objs.flatten()
        nan_filt = ~np.isnan(flat_fwhms)
        if flat_nstars[nan_filt].size == 0:
            if not dont_print:
                print("Nothing to plot")
            return
        weight_nstars = flat_nstars[nan_filt] / np.nanmax(flat_nstars)
        weight_times = (20 - (np.nanmax(self.aisots)
                              - self.aisots.flatten()[nan_filt]
                              ) * 24 * 60)
        weight_times[weight_times < 0] = 0
        weight_times = weight_times / 30
        weight = weight_nstars * weight_times
        weight = weight / np.nanmax(weight)
        a, b, c = np.polyfit(flat_foc[nan_filt],
                             flat_fwhms[nan_filt], deg=2,
                             w=weight)
        expected = self.quadratic(flat_foc[nan_filt], a, b, c)
        chi_squared = (expected - flat_fwhms[nan_filt])**2 / expected
        chi_rejects = chi_squared > np.percentile(chi_squared, 85)
        a, b, c = np.polyfit(flat_foc[nan_filt][~chi_rejects],
                             flat_fwhms[nan_filt][~chi_rejects],
                             deg=2, w=weight[~chi_rejects])
        focs = np.linspace(flat_foc[nan_filt].min(),
                           flat_foc[nan_filt].max(), 100)
        fit = -b / 2 / a
        fwhm = self.quadratic(fit, a, b, c)
        mum = "\u03BCm"
        if a < 0:  # Not a parabola with a minimum
            fit_found = False
            print("Optimal focus not found")
        else:
            fit_found = True
            if not dont_print:
                print(f'Optimal focus is at {fit:>4.0f}{mum} with FWHM'
                      f' {fwhm:>4.1f}"')
        if fig is None:
            for_ani = False
            fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        else:
            for_ani = True

        if fit_found:
            ax.plot(focs, self.quadratic(focs, a, b, c),
                    alpha=0.8,
                    # label="Best Fit"
                    )
            ax.set_title(f"Best Focus is {-b / 2 / a:.0f}{mum} with FWHM"
                         f' {fwhm:.1f}"')
            ax.axvline(-b / 2 / a, c="r", linestyle="--", alpha=0.6)

        not_old = 10 - (np.nanmax(self.aisots) - self.aisots) > 0
        for i, cam in enumerate(self.gfas):
            ax.scatter(self.afocuses[not_old[:, i], i]
                       + camera_offsets[self.gfas - 1][i],
                       self.afwhms[not_old[:, i], i], s=6,
                       alpha=0.7,
                       label=f"{cam}")
        ax.scatter(flat_foc[nan_filt][chi_rejects],
                   flat_fwhms[nan_filt][chi_rejects], marker="x", alpha=0.7,
                   linewidth=0.5, c="k")
        ax.legend(ncol=6, loc=1)
        ax.set_xlabel("Focus ($\mu m$)")
        ax.set_ylabel("FWHM (arcseconds)")
        if not for_ani:
            plt.show()
            if plot_file:
                fig.savefig(plot_file, dpi=100)
        return fig

    def separate_plot(self, plot_file=None):
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        xs = np.linspace(np.nanmin(self.afocuses), np.nanmax(self.afocuses))
        mum = "\u03BCm"
        for i, cam in enumerate(self.gfas):
            if np.all(np.isnan(self.afwhms[:, i])):
                continue
            a, b, c = np.polyfit(self.afocuses[:, i], self.afwhms[:, i], deg=2)
            best = -b / 2 / a
            print(f'GFA {i+1:<4.0f} {best:>6.2f}{mum}'
                  f' {self.quadratic(best, a, b, c):>6.2f}"')
            ax.scatter(self.afocuses[:, i], self.afwhms[:, i], alpha=0.6,
                       label=f"GFA {cam:.0f}")
            ax.plot(xs, self.quadratic(xs, a, b, c), alpha=0.8)
        ax.legend()
        ax.set_title(f"{np.min(self.im_nums)}-{np.max(self.im_nums)}")
        ax.set_xlabel("Focus ($\mu m$)")
        ax.set_ylabel("FWHM (arcseconds)")
        plt.show()
        if plot_file:
            fig.savefig(plot_file, dpi=100)
        return fig

    def exp_num_plot(self, plot_file=None):
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        for i, cam in enumerate(self.gfas):
            ax.plot(self.aim_nums, self.afwhms[:, i], linewidth=1,
                    alpha=0.8,
                    label=f"GFA {cam}")
            ax.scatter(self.aim_nums, self.afwhms[:, i], s=6,
                       alpha=0.8)
        ax.legend()
        ax.set_xlabel("Exposure Number")
        ax.set_ylabel("FWHM (arcseconds)")
        plt.show()
        if plot_file:
            fig.savefig(plot_file, dpi=100)
        return fig

    def init_continuous_plot(self, window="0-15", ignore=[]):
        low, high = window.split("-")
        n_images = int(high) - int(low)
        today = sjd.sjd()
        img_dir = sdss_paths.gcam / f"{today:.0f}/"
        latest = 0
        try:
            img_dir.exists()
        except OSError:
            pass
        for fil in img_dir.glob("gimg-gfa4n-*.fits"):
            if "snap" in fil.name:
                continue
            current_num = int(fil.name.split("gfa4n-")[-1].split(".fits")[0])
            latest = max(latest, current_num)
        for im_num in tqdm.tqdm(range(latest - n_images, latest + 1)):
            if im_num in ignore:
                continue
            im_ps = []
            for n in self.gfas:
                p = get_img_path(today, n, im_num)
                im_ps.append(p)
            self.add_index(im_ps, im_num)
        self.sort()
        self.ani_fig, self.ani_ax = plt.subplots(1, 1, figsize=(6, 4))
        return self.plot(None, self.ani_fig, self.ani_ax,
                         dont_print=not self.verbose)

    def continuous_plot_update(self, i):
        today = sjd.sjd()
        im_num = self.im_nums[-1] + 1
        im_num_0 = im_num
        p = get_img_path(today, 4, im_num)
        current_range = self.im_nums[-1] - self.im_nums[0]
        if self.verbose:
            print(im_num, p.exists(), im_num_0)
            print(current_range)
        while p.exists() and (im_num - im_num_0 < current_range):
            im_ps = []
            for n in self.gfas:
                p = get_img_path(today, n, im_num)
                im_ps.append(p)
            self.add_index(im_ps, im_num)
            self.remove_first_index()
            im_num += 1
        self.sort()
        self.ani_ax.clear()
        if self.verbose:
            print(f"Plotting from {self.im_nums[0]:>3.0f}-{self.im_nums[-1]:>3.0f}"
                  ", ", end="")
        return self.plot(None, fig=self.ani_fig, ax=self.ani_ax,
                         dont_print=not self.verbose)


def parse_args():
    parser = argparse.ArgumentParser(description="Prints a table of FWHMs from"
                                     " GFAs, useful for focus sweeps")
    parser.add_argument("-c", "--continuous", action="store_true",
                        help="Update plot/fit continuously, overrides all other"
                        " plots")
    parser.add_argument("-m", "--mjd", default=sjd.sjd())
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose debugging output")
    parser.add_argument("-f", "--file", nargs="+",
                        help="Specific files to process")
    parser.add_argument("-n", "--gfas", nargs="+", type=int, default=[1, 2, 3,
                                                                      4, 5, 6])
    parser.add_argument("-w", "--window",
                        help="A dash separated beginning and end of the window."
                             " Always include a --master-field with your window."
                             " Ex: -w 15-50 -s 35")
    parser.add_argument("-i", "--ignore", nargs="+", type=int, default=[],
                        help="Image numbers to ignore in a window")
    parser.add_argument("-e", "--exp-num", action="store_true",
                        help="Plot fwhm relative to exposure number")
    parser.add_argument("-t", "--interval", default=15,
                        help="Gap between reading images when using -c")
    # parser.add_argument("-s", "--master-field", type=int,
    #                     help="The master field with all stars you want. Only"
    #                     " used in conjunction with --window. You need both"
    #                     " arguments.")
    parser.add_argument("-p", "--plot", action="store_true",
                        help="A plot to find best fit")
    parser.add_argument("-k", "--plot-file", help="Filename to save plot to."
                        " only works with --plot and --window together. If not"
                        " included, the plot will show up in a new window (or"
                        " maybe not depending on X11).")
    parser.add_argument("-s", "--separate", action="store_true",
                        help="Creates separate fits for each gfa in a plot")
    parser.add_argument("-d", "--plot-image", action="store_true",
                        help="Plot an the sky image with ellipses traced, only works with -f"
                        )
    args = parser.parse_args()

    args.gfas = np.array(args.gfas)

    return args


def main(args=None):
    if args is None:
        args = parse_args()
    gfas = GFASet(verbose=args.verbose, gfas=args.gfas)
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

    if args.continuous:
        anis = []
        print("Plotting continuously")
        if args.window is None:
            gfas.init_continuous_plot(ignore=args.ignore)
        else:
            gfas.init_continuous_plot(args.window)
        # I cannot explain why I must create a list I will never use to get an
        # animation to run. By rights, it should not be necessary. However,
        # it is apparently essential to the existence of an animation loop
        anis.append(animation.FuncAnimation(gfas.ani_fig,
                                            gfas.continuous_plot_update,
                                            interval=1000 * args.interval))
        plt.show()

    elif not args.window and not args.continuous:
        path_stem = sdss_paths.gcam / f"{args.mjd}"
        low = 1000
        high = 0
        for file in path_stem.glob("gimg-gfa5n-*.fits*"):
            print(file.name)
            ind = int(file.name.split("n-")[-1].rstrip(
                "-snap.fits.gz"))
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
            if im_num in args.ignore:
                continue
            im_ps = []
            for n in args.gfas:
                p = get_img_path(args.mjd, n, im_num)
                im_ps.append(p)

            gfas.add_index(im_ps, im_num)
        gfas.sort()
        gfas.print()

        if args.separate:
            gfas.separate_plot(args.plot_file)
        elif args.exp_num:
            gfas.exp_num_plot(args.plot_file)
        elif args.plot:
            gfas.plot(args.plot_file)

    return 0


if __name__ == "__main__":
    main()
