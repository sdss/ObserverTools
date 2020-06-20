#!/usr/bin/env python
import argparse
from pathlib import Path
import sys
from astropy.time import Time
from scipy.optimize import leastsq
import fitsio
sys.path.append(Path(__file__).absolute().parent.parent)
from bin import epics_fetch


class APOGEERaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like sdss.autoscheduler changes, which many libraries depend on. This
    will hopefully help SDSS-V logging"""

    def __init__(self, fil, ext):
        self.file = fil
        self.ext = ext
        header = fitsio.read_header(fil, ext=ext)
        self.telemetry = epics_fetch.telemetry
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

    def compute_offset(self, fiber=30, w0=939, dw=40, sigma=1.2745):
        """This is based off of apogeeThar.OneFileFitting written by Elena. It
        is supposed to generate a float for the pixel offsets of an APOGEE
        ThAr cal."""
        mjd = self.file.absolute.parent.name
        quickred_file = (self.file.absolute().parent.parent.parent
            / 'quickred/{}/ap1D-a-{}.fits.fz'.format(self.mjd, self.exp_id))
        try:
            if not self.data:
                self.data = fitsio.read(quickred_file, 0)
        except OSError:
            return np.nan
        p0 = np.array([53864., 939.646, 1.2745])
        lower = w0 - dw // 2
        upper = w0 + dw // 2
        line = self.data[fiber, lower:upper]
        
        fit_func = lambda w, x: np.exp(-0.5*((x-w)/sigma)**2)
        err_func = lambda w, x, y: fit_func(w, x) - y

        w_model, success = leastsq(err_func, w0, args=(x, spectra))

        diff = w_model - w0
        return diff



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
        mjd_today = int(Time.now().sjd)
        data_dir = '/data/apogee/archive/{}/'.format(mjd_today)
    elif args.mjd:
        data_dir = '/data/apogee/archive/{}/'.format(args.mjd)
    else:
        raise Exception('No date specified')
    print(data_dir)
    for path in Path(data_dir).rglob('apR*.apz'):
        print(path)


if __name__ == '__main__':
    main()
