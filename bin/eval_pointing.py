#!/usr/bin/env python3
"""In order to evaluate the quality of a pointing model, this script checks
a series of images from the engineering camera and evaluates the pointing
accuracy"""

__author__ = "Dylan Gatlin"

import tqdm
import json
import copy
import numpy as np
import matplotlib as mpl
# mpl.use("GTK3Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path
from argparse import ArgumentParser
from astropy.io import fits
from astropy.time import Time
from astropy.stats import sigma_clipped_stats
from photutils.detection import DAOStarFinder
from photutils.aperture import CircularAperture

from bin import sjd
from sdssobstools import sdss_paths

class ECamData:
    def __init__(self, master_img: int = None):
        self.times = []
        self.img_nums = []
        self.ras = []
        self.decs = []
        self.azs = []
        self.alts = []
        self.rots = []
        self.stars = []
        self.seeings = []
        self.master_img = master_img

    def sort(self):
        self.times = Time(self.times)
        sorter = np.argsort(self.times)
        self.img_nums = np.array(self.img_nums)[sorter]
        self.ras = np.array(self.ras)[sorter]
        self.decs = np.array(self.decs)[sorter]
        self.azs = np.array(self.azs)[sorter]
        self.alts = np.array(self.alts)[sorter]
        self.rots = np.array(self.rots)[sorter]
        tmp_stars = copy.deepcopy(self.stars)
        # Stars is an object array, hard to work with
        # self.stars = np.array(self.stars)[sorter]
        self.stars = [tmp_stars[i] for i in sorter]
        self.seeings = np.array(self.seeings)[sorter]
        self.master_i = np.where(self.master_img == self.img_nums)[0][0]
        if self.master_img is not None:
            self.brightest_i = np.where(self.stars[self.master_i]["flux"]
                                        == self.stars[self.master_i]["flux"].max())[0][0]

    def build_set(self):
        avg_stars = np.mean([len(s) for s in self.stars])
        master_n_stars = len(self.stars[self.master_i])
        if round(avg_stars) != master_n_stars:
            print(f"The number of stars in the master image"
                  f" ({master_n_stars}) doesn't match the"
                  f" average number of stars ({avg_stars:.1f})")

        self.coord_pairs = np.empty(
            (len(self.stars), master_n_stars, 2), dtype=float)
        self.coord_pairs[:] = np.nan  # Guilty until proven innocent
        for j, stars in enumerate(self.stars):
            for k, ref in enumerate(self.stars[self.master_i]):
                for s in stars:
                    if ((np.abs(s["xcentroid"] - ref["xcentroid"]) < 15)
                            and np.abs(s["ycentroid"] - ref["ycentroid"]) < 15):
                        self.coord_pairs[j, k] = np.array([s["xcentroid"],
                                                           s["ycentroid"]])
                        continue

        return self.coord_pairs

    def to_json(self, outfile):
        output = {}
        output["Time"] = [t.iso for t in self.times]
        output["ImgID"] = np.ndarray.tolist(self.img_nums)
        output["RA"] = np.ndarray.tolist(self.ras)
        output["Dec"] = np.ndarray.tolist(self.decs)
        output["Alt"] = np.ndarray.tolist(self.alts)
        output["Az"] = np.ndarray.tolist(self.azs)
        output["Rot"] = np.ndarray.tolist(self.rots)
        output["Coords"] = np.ndarray.tolist(self.coord_pairs)
        output["Brightest"] = int(self.brightest_i)
        if self.master_img:
            output["MasterID"] = int(self.master_img)
            output["MasterInd"] = int(self.master_i)
        json.dump(output, outfile.open('w'), indent=4)
        return

    def __iter__(self):
        return zip(self.times, self.img_nums, self.ras, self.decs, self.azs,
                   self.alts, self.rots, self.coord_pairs)


ecam_mask = np.zeros((512, 524), dtype=bool)
ecam_mask[:6, :] = True
ecam_mask[-5:, :] = True
ecam_mask[:, :6] = True
ecam_mask[:, -10:] = True  # This side has lots of bad pixels


def analyze_ecam(img_path, data_class, args):
    img = fits.open(img_path.as_posix())
    if img[0].header["IMAGETYP"] != "object":
        return
    data_class.times.append(img[0].header["DATE-OBS"][:19])
    data_class.img_nums.append(int(img_path.name.split('-')[-1].split('.')[0]))
    data_class.ras.append(img[0].header["RA"])
    data_class.decs.append(img[0].header["DEC"])
    data_class.azs.append(img[0].header["AZ"])
    data_class.alts.append(img[0].header["ALT"])
    data_class.rots.append(img[0].header["ROTPOS"])
    data_class.seeings.append(img[0].header["SEEING"])  # Usually 0
    mean, median, std = sigma_clipped_stats(img[0].data)
    if not args.threshold:
        daofind = DAOStarFinder(fwhm=5, threshold=mean + std * 5)
    else:
        daofind = DAOStarFinder(fwhm=5, threshold=args.threshold)
    sources = daofind(img[0].data, mask=ecam_mask)
    if sources is None:
        if args.verbose:
            print(f"    Skipping {img_path.name}")
        data_class.stars.append(sources)  # Prevents operations on nonetype
        # while maintaining data_class' list lengths

        return
    sources = sources[sources["flux"] > 1.5]  # Gets rid of the faint targets
    data_class.stars.append(sources)
    if args.verbose:
        print(f"File: {img_path.name} NSource: {len(sources)},"
              f" Mean: {mean:.1f}, Std: {std:.1f}")
    return img


def plot_img(fits_obj, sources, args):
    mean, median, std = sigma_clipped_stats(fits_obj[0].data)
    positions = np.transpose((sources["xcentroid"], sources["ycentroid"]))
    apertures = CircularAperture(positions, r=10)
    fig, ax = plt.subplots(1, 1)
    ax.imshow(fits_obj[0].data, cmap="Greys", origin="lower",
              vmin=mean+std, vmax=mean+std*10, interpolation="nearest")
    apertures.plot(axes=ax, color="blue", lw=1.5, alpha=0.5)
    mask = Rectangle((5, 5), width=524-15, height=512-10, alpha=1, fill=False,
                     linestyle="--", color="red", label="Mask")
    ax.add_patch(mask,)
    if args.plot_file:
        fig.savefig(args.plot_file)
    else:
        plt.show()


def print_fit_table(data_class, master_i: int = None):
    print(f"{'Time':20}{'Image':6}{'RA':6}{'Dec':6}{'Alt':6}{'Az':6}{'Rot':6}"
          f"{'Offset':6}")
    print('=' * 80)
    for t, n, r, d, al, az, rot, s in data_class:
        try:
            brightest = (data_class.stars[master_i]["flux"]
                         == data_class.stars[master_i]["flux"].max())
        except (ValueError, TypeError):  # For some empty star lists
            continue

        if master_i is None:
            offset = np.sqrt((s[brightest, 0] - 524 // 2)**2
                             + (s[brightest, 1] - 512 // 2)**2)[0]
        else:
            offset = np.sqrt(
                (s[brightest, 0]
                    - data_class.coord_pairs[master_i, brightest, 0])**2
                + (s[brightest, 1]
                    - data_class.coord_pairs[master_i, brightest, 1])**2)[0]

        print(f"{t.iso[:19]:19}{n:6.0f}{r:6.1f}{d:6.1f}{al:6.1f}{az:6.1f}"
              f"{rot:6.1f}{offset:6.1f}")


def parse_args():
    parser = ArgumentParser("A tool to evaluate SDSS' pointing and tracking."
                            " If no arguments are given, it will check through"
                            " an entire night's worth of data and print a table"
                            " of offsets from the center for the brightest star."
                            " If a window is specified, you'll get results"
                            " split by the specified windows. If a file is"
                            " specified, you can check a single image.")
    parser.add_argument("-m", "--mjd", default=sjd.sjd())
    parser.add_argument("-t", "--threshold", type=int,
                        help="A lower limit on the peak"
                             " flux of a target. By default, it is 3 sigma"
                             " above the mean, but an integer could be provided"
                             " instead.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose debugging output")
    parser.add_argument("-f", "--file", nargs="+",
                        help="Specific files to process")
    parser.add_argument("-w", "--window",
                        help="A dash separated beginning and end of the window."
                             " Always include a --master-field with your window."
                             " Ex: -w 15-50 -s 35")
    parser.add_argument("-s", "--master-field", type=int,
                        help="The master field with all stars you want. Only"
                        " used in conjunction with --window. You need both"
                        " arguments.")
    parser.add_argument("-p", "--plot", action="store_true",
                        help="Show plot to analyze fit quality")
    parser.add_argument("-k", "--plot-file", help="Filename to save plot to."
                        " only works with --plot and --window together. If not"
                        " included, the plot will show up in a new window (or"
                        " maybe not depending on X11).")
    parser.add_argument("-j", "--json", type=str,
                        help="Output a dataset to a json file")
    # TODO Add a way to ignore stars within a field's window
    args = parser.parse_args()
    return args


def main(args=parse_args()):
    if args.verbose:
        print(f"ECamera mask covers {ecam_mask.sum()/ecam_mask.size:.1f}%"
              f" of the total image")
    if args.file:
        ecam = ECamData()
        for i, fil in enumerate(args.file):
            fil_path = Path(fil)
            if fil_path.exists():
                fits_img = analyze_ecam(fil_path, ecam, args)
            else:
                raise FileNotFoundError(
                    f"File {fil_path.absolute()} not found")
            if args.plot:
                plot_img(fits_img, ecam.stars[i], args)
    elif args.window:
        low, high = args.window.split("-")
        try:
            low = int(low)
            high = int(high)
        except ValueError:
            raise ValueError(f"Window range must be filled with ints"
                             f" {args.window}")
        ecam = ECamData(args.master_field)
        for j in tqdm.tqdm(list(range(low, high+1))):
            ecam_path = (
                sdss_paths.ecam / f"{args.mjd}/proc-gimg-{j:04.0f}.fits.gz")
            analyze_ecam(ecam_path, ecam, args)
        ecam.sort()
        coord_pairs = ecam.build_set()
        if args.json:
            ecam.to_json(Path(args.json))
        if args.plot:
            fig, axs = plt.subplots(2, 2, figsize=(16, 8), sharex=True)
            fig.set_tight_layout("tight")
            # TODO set a suptitle of the field position
            labels = ["x", "y"]
            brightest = (ecam.stars[ecam.master_i]["flux"]
                         == ecam.stars[ecam.master_i]["flux"].max())
            for i, ax in enumerate(axs[0]):
                for j, star in enumerate(coord_pairs[:, :, i].T):
                    ax.plot_date(ecam.times.plot_date[~np.isnan(star)],
                                 (star[~np.isnan(star)] -
                                  star[ecam.master_i]) * 0.428,
                                 fmt="-", alpha=0.3)
                ax.plot_date(ecam.times.plot_date,
                             np.nanmean(coord_pairs[:, :, i]
                                        - coord_pairs[ecam.master_i, :, i],
                                        axis=1) * 0.428,
                             fmt="-", label="Mean")
                ax.plot_date(ecam.times.plot_date,
                             (coord_pairs[:, brightest, i]
                              - coord_pairs[ecam.master_i, brightest, i]) * 0.428,
                             fmt="-", label="Brightest")
                ax.set_ylabel(f"{labels[i]} Axis Drift (arcsec)")
                ax.legend()
            axs[1, 0].plot_date(ecam.times.plot_date[~np.isnan(ecam.coord_pairs[:, brightest, 0]).T[0]],
                                np.sqrt((ecam.coord_pairs[~np.isnan(ecam.coord_pairs[:, brightest, 0].T[0]), brightest, 0]
                                         - ecam.coord_pairs[ecam.master_i, brightest, 0])**2
                                + (ecam.coord_pairs[~np.isnan(ecam.coord_pairs[:, brightest, 0]).T[0], brightest, 1]
                                   - ecam.coord_pairs[ecam.master_i, brightest, 1])**2) * 0.428,
                                fmt="-", label="Brightest")
            axs[1, 0].set_xlabel("Time")
            axs[1, 0].set_ylabel(
                r"Total Drift $\sqrt{\Delta x^2+\Delta y^2}$ (arcsec)")
            axs[1, 0].legend()
            axs[1, 1].set_xlabel("Time")
            if args.plot_file:
                fig.savefig(args.plot_file)
            else:
                plt.show()
        else:
            print_fit_table(ecam, ecam.master_i)

    else:
        ecam = ECamData()
        day_path = (sdss_paths.ecam / f"{args.mjd}").absolute()
        if not day_path.exists():
            raise NotADirectoryError(
                f"Directory {day_path.as_posix()} not found")

        for proc in tqdm.tqdm(list(day_path.glob("proc-gimg-*.fits.gz"))):
            if args.verbose:
                print(proc.absolute())
            analyze_ecam(proc, ecam, args)
        ecam.sort()
        print_fit_table(ecam)

    return 0


if __name__ == "__main__":
    main()
