#!(conda activate tui27; which python)
import numpy as np
import argparse
from pathlib import Path
import starcoder42 as s
try:
    from astropy.time import Time
except ImportError:
     raise s.GatlinError('Astropy is needed for this library')
import fitsio

# except ImportError:
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
# 


class MaNGARaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like autoschedulers change, which many libraries depend on. This
    will hopefully help SDSS-V logging"""
    def __init__(self, fil):
        header = fitsio.read_header(fil)
        # ler = self.image[layer_ind]
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        self.dither = header['MGDPOS']
        self.exp_time = header['EXPTIME']
        self.flavor = header['FLAVOR']
        self.datetimet = Time(header['DATE-OBS'])  # Local
        self.plate_id = header['PLATEID']
        self.cart_id = header['CARTID']
        self.exp_id = int(str(fil).split('-')[-1].split('.')[0])
        if 'Closed' in header['HARTMANN']:
            self.hartmann = 'Closed'
        else:
            self.hartmann = header['HARTMANN']
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
        mjd_today = int(Time.now().mjd)
        data_dir = '/data/spectro/{}/'.format(mjd_today)
    elif args.mjd:
        data_dir = '/data/spectro/{}/'.format(args.mjd)
    else:
        raise s.GatlinError('No date specified')

    for path in Path(data_dir).rglob('sdR*.fit.gz'):
        print(path)


if __name__ == '__main__':
    main()
