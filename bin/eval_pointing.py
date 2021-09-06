#!/usr/bin/env python3
"""In order to evaluate the quality of a pointing model, this script checks
a series of images from the engineering camera and evaluates the pointing
accuracy"""

__author__ = "Dylan Gatlin"

import tqdm
import json
import copy
import numpy as np
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

ecam_path_stem = Path("/data/ecam/")
if not ecam_path_stem.exists():
    ecam_path_stem = (Path.home() / "data/ecam/").absolute()
    if not ecam_path_stem.exists():
        raise NotADirectoryError("The ecam data path /data/ecam could not be"
                                 " found")


class ECamData:
    def __init__(self):
        self.times = []
        self.img_nums = []
        self.ras = []
        self.decs = []
        self.azs = []
        self.alts = []
        self.rots = []
        self.stars = []
        self.seeings = []

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

    def build_set(self, master_img: int):
        avg_stars = np.mean([len(s) for s in self.stars])
        master_i = np.where(self.img_nums == master_img)[0][0]
        master_n_stars = len(self.stars[master_i])
        if round(avg_stars) != master_n_stars:
            print(f"The number of stars in the master image"
                  f" ({master_n_stars}) doesn't match the"
                  f" average number of stars ({avg_stars})")

        self.coord_pairs = np.empty(
            (len(self.stars), master_n_stars, 2), dtype=float)
        self.coord_pairs[:] = np.nan  # Guilty until proven innocent
        for j, stars in enumerate(self.stars):
            for k, ref in enumerate(self.stars[master_i]):
                for s in stars:
                    if ((np.abs(s["xcentroid"] - ref["xcentroid"]) < 10)
                            and np.abs(s["ycentroid"] - ref["ycentroid"]) < 10):
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
        json.dump(output, outfile.open('w'))
        return

    def __iter__(self):
        return zip(self.times, self.img_nums, self.ras, self.decs, self.azs,
                   self.alts, self.rots, self.stars)


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
    daofind = DAOStarFinder(fwhm=5, threshold=mean + std * 3)
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


def plot_img(fits_obj, sources):
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
    plt.show()


def print_fit_table(data_class):
    print(f"{'Time':20}{'Image':6}{'RA':6}{'Dec':6}{'Alt':6}{'Az':6}{'Rot':6}"
          f"{'Offset':17}")
    print('=' * 80)
    for t, n, r, d, al, az, rot, s in data_class:
        try:
            brightest = s["flux"] == s["flux"].max()
        except (ValueError, TypeError):  # For some empty star lists
            continue
        offset = np.sqrt((s[brightest]["xcentroid"] - 524 // 2)**2
                         + (s[brightest]["ycentroid"] - 512 // 2)**2)[0]
        print(f"{t.iso[:19]:19}{n:6.0f}{r:6.1f}{d:6.1f}{al:6.1f}{az:6.1f}"
              f"{rot:6.1f}{offset:17.1f}")


def parse_args():
    parser = ArgumentParser("A tool to evaluate SDSS' pointing and tracking."
                            " If no arguments are given, it will check through"
                            " an entire night's worth of data and print a table"
                            " of offsets from the center for the brightest star."
                            " If a window is specified, you'll get results"
                            " split by the specified windows. If a file is"
                            " specified, you can check a single image.")
    parser.add_argument("-m", "--mjd", default=sjd.sjd())
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
    parser.add_argument("-j", "--json", type=str,
                        help="Output a dataset to a json file")
    args = parser.parse_args()
    return args


def main(args=parse_args()):
    if args.verbose:
        print(f"ECamera mask covers {ecam_mask.sum()/ecam_mask.size:.1f}%"
              f" of the total image")
    ecam = ECamData()
    if args.file:
        for i, fil in enumerate(args.file):
            fil_path = Path(fil)
            if fil_path.exists():
                fits_img = analyze_ecam(fil_path, ecam, args)
            else:
                raise FileNotFoundError(
                    f"File {fil_path.absolute()} not found")
            if args.plot:
                plot_img(fits_img, ecam.stars[i])
    elif args.window:
        low, high = args.window.split("-")
        try:
            low = int(low)
            high = int(high)
        except ValueError:
            raise ValueError(f"Window range must be filled with ints"
                             f" {args.window}")
        ecam = ECamData()
        for j in tqdm.tqdm(list(range(low, high+1))):
            ecam_path = (
                ecam_path_stem / f"{args.mjd}/proc-gimg-{j:04.0f}.fits.gz")
            analyze_ecam(ecam_path, ecam, args)
        ecam.sort()
        coord_pairs = ecam.build_set(args.master_field)
        if args.json:
            ecam.to_json(Path(args.json))
        if args.plot:
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            for j, star in enumerate(coord_pairs[:, :, 0].T):
                ax.plot_date(ecam.times.plot_date[~np.isnan(star)],
                             star[~np.isnan(star)] - star[0],
                             fmt="-", label=f"({coord_pairs[0, j, 0]:.1f},"
                                            f" {coord_pairs[0, j, 1]:.1f})",
                             alpha=0.4)
            ax.plot_date(ecam.times.plot_date,
                         np.nanmean(coord_pairs[:, :, 0]
                                    - coord_pairs[0, :, 0], axis=1),
                         fmt="-", label="Mean")
            ax.set_xlabel("Time")
            ax.set_ylabel("X axis drift")
            ax.legend()
            plt.show()

    else:
        day_path = (ecam_path_stem / f"{args.mjd}").absolute()
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
