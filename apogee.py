import numpy as np
import argparse
from astropy.io import fits
from astropy.time import Time
from pathlib import Path
import starcoder42 as s


class APOGEERaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like sdss.autoscheduler changes, which many libraries depend on. This
    will hopefully help SDSS-V logging"""
    def __init__(self, fil, ext):
        fil = fits.open(fil)
        # layer = self.image[layer_ind]
        header = fil[ext].header
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        if header['DITHPIX'] < 13.25:
            self.dither = 'A'
        else:
            self.dither = 'B'
        self.exp_time = header['EXPTIME']
        self.datetimet = Time(header['DATE-OBS'])  # Local
        self.plate_id = header['PLATEID']
        self.cart_id = header['CARTID']
        self.exp_id = int(str(file).split('-')[-1].split('.')[0])
        self.seeing = header['SEEING']
        self.img_type = header['IMAGETYP']
        self.n_read = len(fil) - 1
        self.exp_type = header['EXPTYPE']  # TODO Check if this is a correct key
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true',
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 00:00Z")
    parser.add_argument('-m', '--mjd',
                        help='If not today (-t), the mjd to search')
    parser.add_argument('-v', '--verbose', action='count', default=1,
                        help='Show details, can be stacked')
    args = parser.parse_args()
    if args.today:
        mjd_today = int(Time().mjd)
        data_dir = '/data/apogee/archive/{}/'.format(mjd_today)
    elif args.mjd:
        data_dir = '/data/apogee/archive/{}/'.format(args.mjd)
    else:
        raise s.GatlinError('No date specified')

    for path in Path(data_dir).rglob('apRaw*.apz'):
        print(path)


if __name__ == '__main__':
    main()
