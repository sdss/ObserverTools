#!/usr/bin/env python3
"""
A tool to grab a single BOSS image and pull a few items from its header. It is
 used in bin/sloan_log.py, but it could be used directly as well.
"""
import argparse
from pathlib import Path
from astropy.time import Time
import fitsio


class BOSSRaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like autoschedulers change, which many libraries depend on. This
    will hopefully help SDSS-V logging"""

    def __init__(self, fil):
        self.fil = fil
        header = fitsio.read_header(fil)

        # ler = self.image[layer_ind]
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        self.dither = header['MGDPOS']
        self.exp_time = int(header['EXPTIME'])
        self.isot = Time(header['DATE-OBS'])  # UTC
        self.plate_id = header['PLATEID']
        self.cart_id = header['CARTID']
        self.exp_id = int(str(fil).split('-')[-1].split('.')[0])
        self.lead = header['PLATETYP']
        if 'Closed' in header['HARTMANN']:
            self.hartmann = 'Closed'
            self.flavor = header['FLAVOR'].capitalize()
        elif 'Out' in header['HARTMANN']:
            self.hartmann = 'Open'
            self.flavor = header['FLAVOR'].capitalize()
            self.hart_resids = []
        else:
            self.hartmann = header['HARTMANN']
            self.flavor = 'Hart'

        # self.seeing = header['SEEING']
        # self.img_type = header['IMAGETYP']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true')
    args = parser.parse_args()
    parser.add_argument('-m', '--mjd',
                        help='If not today (-t), the mjd to search')
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='Show details, can be stacked')
    if args.today:
        mjd_today = int(Time.now().sjd)
        data_dir = '/data/spectro/{}/'.format(mjd_today)
    elif args.mjd:
        data_dir = '/data/spectro/{}/'.format(args.mjd)
    else:
        raise Exception('No date specified')

    for path in Path(data_dir).rglob('sdR*.fit.gz'):
        print(path)


if __name__ == '__main__':
    main()
