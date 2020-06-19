#!/usr/bin/env python
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import seaborn as sns
from astropy.time import Time
try:
    import starcoder42 as s
except ImportError:
    import sys
    sys.path.append('/home/dylangatlin/python/')
    sys.path.append('/home/gatlin/python/')
    import starcoder42 as s
import argparse
from pathlib import Path

sns.set(style='darkgrid')

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--today', action='store_true',
                    help="Whether or not you want to search for today's"
                         " data, whether or not the night is complete."
                         " Note: must be run after 00:00Z")
parser.add_argument('-m', '--mjd',
                    help='If not today (-t), the mjd to search')


def main():
    args = parser.parse_args()
    if args.today:
        date = str(int(Time.now().sjd))
        print(date)
    elif args.mjd:
        date = args.mjd
    else:
        raise s.GatlinError('Must specify a date to plot')
    date_dir = Path(__file__).parent / date
    if not date_dir.exists():
        raise s.GatlinError('No folder for that date')

    ra = np.load(date_dir / 'ra.npy')
    dec = np.load(date_dir / 'dec.npy')
    rot = np.load(date_dir / 'rotator.npy')
    times = Time(np.load(date_dir / 'times.npy', allow_pickle=True))
    ids = np.load(date_dir / 'ids.npy')
    lurches = np.load(date_dir / 'lurches.npy')

    # print(times)
    good_exposures = ra > -50000

    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(8, 5))
    raax, decax, rotax = axs
    raax.plot_date(times.plot_date[good_exposures], ra[good_exposures],
                   alpha=0.7, c=(0.257, 0.451, 0.644), markersize=2.5)
    raax.set_ylim(-4, 4)
    raax.set_ylabel("Right Ascension\nError ('')")
    # raax.axhline(-0.8, linewidth=0.5)
    # raax.axhline(0.8, linewidth=0.5)
    # raax.annotate('MaNGA Dither Envelope',
    #               (Time('2019-11-01 04:00').plot_date, 0.95))

    decax.plot_date(times.plot_date[good_exposures], dec[good_exposures],
                    alpha=0.7, c=(0.386, 0.773, 0.238), markersize=2.5)
    decax.set_ylim(-4, 4)
    decax.set_ylabel("Declination\nError ('')")

    rotax.plot_date(times.plot_date[good_exposures], rot[good_exposures],
                    alpha=0.7, c=(0.128, 0.515, 0.193), markersize=2.5)
    rotax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%H:%M'))
    rotax.set_xlabel('t (UTC)')
    rotax.set_ylim(-10, 10)
    rotax.set_ylabel("Rotator\nError ('')")

    for lurch in lurches:
        i = np.where(ids == lurch)[0][0]
        lurch_time = times[i]
        raax.axvline(lurch_time.plot_date, alpha=0.4, c=(0.700, 0.322, 0.386),
                     linewidth=1)
        decax.axvline(lurch_time.plot_date, alpha=0.4, c=(0.700, 0.322, 0.386),
                      linewidth=1)
        rotax.axvline(lurch_time.plot_date, alpha=0.4, c=(0.700, 0.322, 0.386),
                      linewidth=1)

    fig.suptitle('Guider Axis Errors {}'.format(date))
    print(date_dir / 'guider_plot.png')
    fig.savefig(str(date_dir / 'guider_plot.png'))


if __name__ == '__main__':
    main()
