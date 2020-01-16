#!/usr/bin/env python
import numpy as np
import argparse
from pathlib import Path
import starcoder42 as s
try:
    from astropy.time import Time
except ImportError:
    raise s.GatlinError('Astropy is needed for this library')
import fitsio
#     print('Astropy not found')
#     import pyfits as fits
#     
# 
#     class Time:
#         """An awful workaround to avoid crashes when astropy is unavailable
#         """
#         def __init__(self, time):
#             self.in_time = time
#             if 'T' in time:
#                 date, time = time.split('T')
#             else:
#                 date, time = time.split()
#             self.yr, self.mo, self.da = date.split('-')
#             self.hr, self.mi, self.sec = time.split(':')
#             self.date = datetime.date(int(self.yr), int(self.mo),
#                                       int(self.da))
#             self.time = datetime.time(int(self.hr), int(self.mi),
#                                       int(self.sec.split('.')[0]))
#             self.mjd = str(self.date).split()



class APOGEERaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like sdss.autoscheduler changes, which many libraries depend on. This
    will hopefully help SDSS-V logging"""
    def __init__(self, fil, ext):
        header = fitsio.read_header(fil, ext=ext)
        # layer = self.image[layer_ind]
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        if (header['DITHPIX'] > 12.95) and (header['DITHPIX'] < 13.05):
            self.dither = 'A'
        elif (header['DITHPIX'] > 13.45) and (header['DITHPIX'] < 13.55):
            self.dither = 'B'
        else:
            self.dither = ''.format(header['DITHPIX'])
        self.exp_time = header['EXPTIME']
        self.datetimet = Time(header['DATE-OBS'])  # Local
        self.plate_id = header['PLATEID']
        self.cart_id = header['CARTID']
        self.exp_id = int(str(fil).split('-')[-1].split('.')[0])
        self.seeing = header['SEEING']
        self.img_type = header['IMAGETYP']
        self.n_read = header['NREAD']
        self.exp_type = header['EXPTYPE']
        self.lead = header['PLATETYP']

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
        mjd_today = int(Time.now().mjd)
        data_dir = '/data/apogee/archive/{}/'.format(mjd_today)
    elif args.mjd:
        data_dir = '/data/apogee/archive/{}/'.format(args.mjd)
    else:
        raise s.GatlinError('No date specified')
    print(data_dir)
    for path in Path(data_dir).rglob('apR*.apz'):
        print(path)


if __name__ == '__main__':
    main()
