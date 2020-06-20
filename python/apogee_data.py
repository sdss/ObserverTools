#!/usr/bin/env python
import argparse
from pathlib import Path
import sys
from astropy.time import Time
from scipy.optimize import leastsq
import fitsio
import numpy as np

sys.path.append(Path(__file__).absolute().parent.parent)
from bin import epics_fetch


class APOGEERaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like sdss.autoscheduler changes, which many libraries depend on. This
    will hopefully help SDSS-V logging"""

    def __init__(self, fil, args, ext=1,):
        self.file = Path(fil)
        self.ext = ext
        self.args = args
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
        if header['IMAGETYP'] == 'ArcLamp':
            if header['LAMPUNE']:
                self.img_type = 'UNe Arc'
            elif header['LAMPTHAR']:
                self.img_type = 'ThAr Arc'
            else:
                print('Could not process image type of {}'.format(self.file))
        else:
            self.img_type = header['IMAGETYP'].capitalize()
        self.n_read = header['NREAD']
        self.lead = header['PLATETYP']
        self.exp_type = header['EXPTYPE'].capitalize()
        if header['EXPTYPE'] == 'OBJECT':
            self.seeing = header['SEEING']
        else:
            self.seeing = 0.0

        self.data = np.array([[]])

    # noinspection PyTupleAssignmentBalance,PyTypeChecker
    def compute_offset(self, fibers=(30, 35), w0=939, dw=40, sigma=1.2745):
        """This is based off of apogeeThar.OneFileFitting written by Elena. It
        is supposed to generate a float for the pixel offsets of an APOGEE
        ThAr cal. Here is how it works:
        It opens a quickred file, which is of shape n_fiber*n_dispersion_pixels,
        and then it averages the fibers inside the fibers tuple. It then based
        off of the provided w0 (mean) and sigma, it creates a gaussian function
        and then creates a function called err_func that compares the gaussian
        with a slice of the data, from w0-dw/2 to w0+dw/2. It then uses scipy's
        least squared equation solver to find the difference between w0 given as
        an input and the actual w0 of the spectral line. This only works if you
        pick a prominent line to go off of. The default parameters are given for
        ThAr lines, but UNe lines could also be used, with the following inputs:
        fibers: (30, 35)
        w0: 1761
        dw: 20
        sigma: 3
        """
        w0 = int(w0)
        dw = int(dw)
        mjd = self.file.absolute().parent.name
        quickred_file = (self.file.absolute().parent.parent.parent
                         / 'quickred/{}/ap1D-a-{}.fits.fz'.format(mjd,
                                                                  self.exp_id))
        try:
            if not self.data:
                self.data = fitsio.read(quickred_file, 1)
        except OSError as e:
            if self.args.verbose:
                print('Offsets for {} produced this error\n{}'.format(self.file,
                      e))
            return np.nan
        lower = w0 - dw // 2
        upper = w0 + dw // 2
        line_inds = np.arange(self.data.shape[1])[lower:upper]
        line = np.average(self.data[fibers[0]:fibers[1], lower:upper], axis=0)

        def fit_func(w, x):
            return np.exp(-0.5 * ((x - w) / sigma) ** 2)

        def err_func(w, x, y):
            return fit_func(w, x) - y

        w_model, success = leastsq(err_func, w0, args=(line_inds, line))

        diff = w_model[0] - w0
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
