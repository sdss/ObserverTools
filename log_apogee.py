#!/usr/bin/env python
import argparse
from pathlib import Path
from channelarchiver import Archiver
import starcoder42 as s

try:
    from astropy.time import Time
except ImportError:
    raise s.GatlinError('Astropy is needed for this library')
import fitsio


class APOGEERaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like sdss.autoscheduler changes, which many libraries depend on. This
    will hopefully help SDSS-V logging"""

    def __init__(self, fil, ext):
        header = fitsio.read_header(fil, ext=ext)
        self.telemetry = Archiver('http://sdss-telemetry.apo.nmsu.edu/'
                                  'telemetry/cgi/ArchiveDataServer.cgi')
        self.telemetry.scan_archives()
        dithers = self.telemetry.get('25m:apogee:ditherNamedPositions',
                                     start=(Time.now() - 1 / 24 / 60 * 5).isot,
                                     end=Time.now().isot,
                                     scan_archives=False, interpolation='raw')
        # layer = self.image[layer_ind]
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        if (header['DITHPIX'] - dithers.values[-1][0]) < 0.05:
            self.dither = 'A'
        elif (header['DITHPIX'] - dithers.values[-1][1]) < 0.05:
            self.dither = 'B'
        else:
            self.dither = header['DITHPIX']
        self.exp_time = header['EXPTIME']
        self.isot = Time(header['DATE-OBS'])  # Local
        self.plate_id = header['PLATEID']
        self.cart_id = header['CARTID']
        self.exp_id = int(str(fil).split('-')[-1].split('.')[0])
        self.img_type = header['IMAGETYP'].capitalize()
        self.n_read = header['NREAD']
        self.lead = header['PLATETYP']
        self.exp_type = header['EXPTYPE'].capitalize()
        if header['EXPTYPE'] == 'OBJECT':
            self.seeing = header['SEEING']
        else:
            self.seeing = 0.0


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
