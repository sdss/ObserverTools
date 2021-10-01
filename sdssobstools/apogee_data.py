#!/usr/bin/env python
import argparse
from pathlib import Path
from astropy.time import Time
from scipy.optimize import leastsq
import fitsio
import numpy as np
import textwrap
from . import sdss_paths

try:
    from bin import epics_fetch
except ImportError as e:
    raise ImportError('Please add ObserverTools/bin to your PYTHONPATH:\n'
                      '    {}'.format(e))

__version__ = '3.2.1'


class APOGEERaw:
    """A class to parse raw data from APOGEE. The purpose of this class is to
    read raw image files from /data/apogee/archive, regardless of any future
    changes in SDSS. This
    will hopefully help SDSS-V logging.

    Methods:
        compute_offets: Returns the offsets of an arc/object to compute the
        relative dither

        ap_test: Returns a list of faint fibers and missing fibers from a flat
        """

    def __init__(self, fil, args, ext=1, ):
        self.file = Path(fil)
        if not self.file.exists():
            raise FileNotFoundError(f"Could not find file {self.file.absolute()}")
        self.ext = ext
        self.args = args
        header = fitsio.read_header(fil, ext=ext)
        self.telemetry = epics_fetch.telemetry
        dithers = self.telemetry.get('25m:apogee:ditherNamedPositions',
                                     start=(Time.now() - 5 / 24 / 60).datetime,
                                     end=Time.now().datetime,
                                     scan_archives=False, interpolation='raw')
        # layer = self.image[layer_ind]
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        if (header['DITHPIX'] - dithers.values[-1][0]) < 0.05:
            self.dither = 'A'
        elif (header['DITHPIX'] - dithers.values[-1][1]) < 0.05:
            self.dither = 'B'
        else:
            self.dither = '{:.1f}'.format(header['DITHPIX'])
        self.exp_time = header['EXPTIME']
        self.isot = Time(header['DATE-OBS'])  # Local
        self.plate_id = header['PLATEID']
        self.cart_id = header['CARTID']
        self.exp_id = int(str(fil).split('-')[-1].split('.')[0])
        if header['EXPTYPE'].capitalize() == 'Arclamp':
            if header['LAMPUNE']:
                self.exp_type = 'UNe Arc'
            elif header['LAMPTHAR']:
                self.exp_type = 'ThAr Arc'
            elif "FPI" in header["OBSCMNT"]:
                self.exp_type = "FPI Lamp"
            else:
                print('Could not process exposure type of {}'.format(self.file))
        else:
            self.exp_type = header['EXPTYPE'].capitalize()
        self.n_read = header['NREAD']
        self.lead = header['PLATETYP']
        self.img_type = header['IMAGETYP'].capitalize()
        if header['EXPTYPE'] == 'OBJECT':
            self.seeing = header['SEEING']
        else:
            self.seeing = 0.0

        self.quickred_data = np.array([[]])
        self.quickred_file = ''
        self.utr_file = ''
        self.utr_data = np.array([[]])

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
        self.quickred_file = (self.file.absolute().parent.parent.parent
                              / 'quickred/{}/ap1D-a-{}.fits.fz'
                                ''.format(mjd, self.exp_id))
        try:
            if not self.quickred_data:
                self.quickred_data = fitsio.read(self.quickred_file, 1)
        except OSError as e:
            if self.args.verbose:
                print('Offsets for {} produced this error\n{}'.format(self.file,
                                                                      e))
            return np.nan
        lower = w0 - dw // 2
        upper = w0 + dw // 2
        line_inds = np.arange(self.quickred_data.shape[1])[lower:upper]
        line = np.average(self.quickred_data[fibers[0]:fibers[1], lower:upper],
                          axis=0)

        def fit_func(w, x):
            return np.exp(-0.5 * ((x - w) / sigma) ** 2)

        def err_func(w, x, y):
            return fit_func(w, x) - y

        w_model, success = leastsq(err_func, w0, args=(line_inds, line))

        diff = w_model[0] - w0
        if np.abs(diff) > 10:
            print('A large dither was reported for exposure {}: {:.3f}'
                  '\n  This may mean the zero point needs to be'
                  ' adjusted, currently it is {}'
                  ''.format(self.exp_id, diff, w0))
        return diff

    def ap_test(self, ws=(900, 910), master_col=None, plot=False, legacy=False,
                dome_flat_shape=None, n_fibers=300, print_it=False):
        if master_col is None:
            raise ValueError("APTest didn't receive a valid master_col: {}"
                             "".format(master_col))
        if legacy:
            mjd = self.file.absolute().parent.name
            self.utr_file = sdss_paths.ap_utr / f"{mjd}/apRaw-{self.exp_id}.fits"
            if not self.utr_file.exists():
                raise FileNotFoundError(f"Couldn't fine the file: {self.utr_file.as_posix()}")
            try:
                self.utr_data = fitsio.read(self.utr_file, 0)
            except OSError as e:
                if self.args.verbose:
                    print('APTest for {} produced this error\n{}'.format(
                        self.file, e))
            slc0 = np.average(self.utr_data[::-1, ws[0]:ws[1]], axis=1)
            # print(slc0.mean(), slc0.shape, slc0[0])
            slc = np.zeros(n_fibers)
            for j in range(n_fibers):
                for k in range(10):
                    if dome_flat_shape[j, k] != 0:
                        slc[j] += slc0[dome_flat_shape[j, k]]
            # print(slc.mean(), slc.shape, slc[100])

        else:
            if self.quickred_data.size == 0:
                mjd = self.file.absolute().parent.name
                self.quickred_file = (self.file.absolute().parent.parent.parent
                                      / 'quickred/{}/ap1D-a-{}.fits.fz'
                                        ''.format(mjd, self.exp_id))
                try:
                    self.quickred_data = fitsio.read(self.quickred_file, 1)
                except OSError as e:
                    if self.args.verbose:
                        print('APTest for {} produced this error\n{}'.format(
                            self.file, e))
            slc = np.average(self.quickred_data[:, ws[0]:ws[1]], axis=1)
        # print(master_col.mean(), master_col.shape, master_col[100])
        flux_ratio = slc / master_col
        # flux_ratio = flux_ratio / flux_ratio.sum() / flux_ratio.shape[0]
        flux_ratio = flux_ratio / flux_ratio.sum() * flux_ratio.shape[0]
        # print(flux_ratio.mean(), flux_ratio.shape, flux_ratio[100])
        bad_data = ((flux_ratio == np.inf)
                    | (flux_ratio == -np.inf)
                    | np.isnan(flux_ratio))
        flux_ratio[bad_data] = np.nan
        avg = np.nanmean(flux_ratio)
        missing = flux_ratio < 0.2
        faint = (flux_ratio < 0.7) & (0.2 <= flux_ratio)
        bright = ~missing & ~faint
        i_missing = np.where(missing)[0].astype(int) + 1
        i_faint = np.where(faint)[0].astype(int) + 1
        i_bright = np.where(bright)[0]
        missing_bundles = self.create_bundles(i_missing)
        faint_bundles = self.create_bundles(i_faint)
        if print_it:

            print(textwrap.fill('Missing Fibers: {}'.format(missing_bundles),
                                80))
            print(textwrap.fill('Faint Fibers: {}'.format(faint_bundles), 80))
            print()

        if plot:
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(9, 4))
            ax = fig.gca()
            x = np.arange(len(flux_ratio)) + 1
            ax.plot(x[i_bright], flux_ratio[i_bright], 'o', c=(0, 0.6, 0.533))
            ax.plot(x[i_faint], flux_ratio[i_faint], 'o', c=(0.933, 0.466, 0.2))
            ax.plot(x[i_missing], flux_ratio[i_missing], 'o',
                    c=(0.8, 0.2, 0.066))
            ax.set_xlabel('Fiber ID')
            ax.set_ylabel('Throughput Efficiency')
            ax.axis([1, 300, -0.2, 1.35])
            ax.grid(True)
            ax.axhline(0.7, c=(0, 0.6, 0.533))
            ax.axhline(0.2, c=(0.933, 0.466, 0.2))
            ax.set_title('APOGEE Fiber Relative Intensity {}'.format(
                self.exp_id), size=15)
            fig.show()

        return missing_bundles, faint_bundles, avg

    @staticmethod
    def create_bundles(subset):
        """This method converts an array of ints into a list of strings that
        describe a large series of fibers and ints for lone fibers.

        Ex: [1, 2, 3, 5] -> ['1 - 3', 5]

        """
        if len(subset) == 0:
            return []
        bundles = [subset[0]]
        b = 0
        for fib in subset[1:]:
            if isinstance(bundles[b], np.int64):
                if bundles[b] + 1 == fib:
                    if fib % 30 == 0:
                        bundles.append(fib)
                        b += 1
                    else:
                        # All strings are created here
                        bundles[b] = '{} - {}'.format(bundles[b], fib)
                else:
                    bundles.append(fib)
                    b += 1
            elif isinstance(bundles[b], str):
                if int(bundles[b].split()[-1]) + 1 == fib:
                    if fib % 30 == 1:
                        bundles.append(fib)
                        b += 1
                    else:
                        bundles[b] = '{} - {}'.format(
                            bundles[b].split()[0], fib)
                else:
                    bundles.append(fib)
                    b += 1
        # for i, bundle in enumerate(bundles):
        #     if isinstance(bundle, str):
        #         low, high = np.array(bundle.split(' - ')).astype(int)
        #         if ((low - 1) // 30) == ((high - 1) // 30):
        #             bundles[i] = '{} bundle'.format(low)
        return bundles


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
        data_dir = sdss_paths.ap_archive / f"{mjd_today}/"
    elif args.mjd:
        data_dir = sdss_paths.ap_archive / f"{args.mjd}"
    else:
        raise Exception('No date specified')
    # print(data_dir)
    for path in data_dir.rglob('apR*.apz'):
        print(path)


if __name__ == '__main__':
    main()
