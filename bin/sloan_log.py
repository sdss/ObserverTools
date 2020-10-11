#!/usr/bin/env python3
"""sloan_log.py

A script to automate the bulk of logging and to replace various tools
 like log function, log support, list_ap, list_m, and more. This code is
 entirely dependent on raw images, their headers, and EPICS, unlike Log Function
 which is dependent on callbacks it catches while open only and is subject to
 crashes. It's inspired by some outputs from time tracking, but it avoids the
 sdss python module and platedb

The intent of this is to create a more future-proof tool for logging through
Sloan V

In order to run it locally, you will need to either have access to /data, or
 fake it with a single night. You'll need a date from /data/spectro and
 /data/apogoee/archive. You'll also need to tunnel into port 80 of
 sdss-telemetry using
 ssh -L 5080:telemetry.apo.nmsu.edu:80 observer@sdss-gateway.apo.nmsu.edu
 Currently, you'll need access to hub to run aptest, but I'm working on removing
 that dependency since aptest can be done using /data/apogee/archive

2019-11-01      dgatlin     init, in response to some issues with gcam
    tracking and identifying slew errors
2019-12-13      dgatlin     This has received a lot of work and can now
    build a data log and some summary
2020-06-01      dgatlin     Changed some methods to @staticmethods, moved to
    bin, refactored some names to more appropriately fit the role of logging.
2020-06-17      dgatlin     Moved telemetry to epics_fetch
2020-06-30      dgatlin     Added morning option for morning cals
2020-08-12      dgatlin     Added apogee object offsets and a quickred aptest
"""
import argparse
import sys
import warnings
import textwrap

import numpy as np

# import ap_test
try:
    import epics_fetch
    import get_dust
except ImportError as e:
    try:
        from bin import epics_fetch, get_dust
    except ImportError as e:
        raise ImportError('Please add ObserverTools/bin to your PYTHONPATH:'
                          '\n    {}'.format(e))


try:
    import fitsio
except ImportError:
    raise Exception('fitsio not found by interpreter\n'
                    '{}'.format(sys.executable))

from pathlib import Path
from tqdm import tqdm
from astropy.time import Time

try:
    import apogee_data
    import boss_data
    import log_support
except ImportError as e:
    try:
        from python import apogee_data, boss_data, log_support
    except ImportError as e:
        raise ImportError('Please add ObserverTools/python to your PYTHONPATH:'
                          '\n    {}'.format(e))

if sys.version_info.major < 3:
    raise Exception('Interpretter must be python 3 or newer')

# For astropy
warnings.filterwarnings('ignore', category=UserWarning, append=True)
# For numpy boolean arrays
warnings.filterwarnings('ignore', category=FutureWarning, append=True)

__version__ = '3.6.0'

ap_dir = Path('/data/apogee/archive/')
b_dir = Path('/data/spectro/')


class Logging:
    """
    A tool to produce a ton of various outputs used for logging. This tool uses
    the images in the /data directory and epics to build a nightlog that doesn't
    require STUI output. It is best run as follow:

    log = Logging(ap_images, b_images, args)
    log.parse_images()
    log.sort()
    log.count_dithers()
    log.p_summary()
    log.p_data()
    log.p_boss()
    log.p_apogee()
    log.log_support()

    or via command line as

    ./sloan_log.py -pt

    or for a previous date

    ./sloan_log.py -pm 59011

    """

    def __init__(self, ap_images, m_images, args):
        self.ap_images = ap_images
        self.m_images = m_images
        self.args = args
        # Dictionary keys that begin with c are of len(carts_in_a_night),
        # keys that begin with i are of len(images_in_a_night), keys that begin
        # with d are of len(dome_flats) (which is not always the same as carts,
        # keys that begin with a are of len(apogee_arcs), which is usually 4 in
        # a full night (morning and evening cals), keys that begin with h are of
        # len(hartmanns), which is usually a few longer than len(carts). Each
        # first letter is used to choose which sorting key to use. There must be
        # a Time key for each new letter, and a new sorter argument must be
        # added to self.sort. All of these dictionary items begin as lists,
        # and are converted to np.arrays or astropy.time.Times in self.sort.
        self.data = {'cCart': [], 'cTime': [], 'cPlate': [], 'cLead': []}
        self.ap_data = {'cCart': [], 'cTime': [],
                        'iTime': [], 'iID': [],
                        'iSeeing': [], 'iDetector': [], 'iDither': [],
                        'iNRead': [], 'iEType': [], 'iCart': [], 'iPlate': [],
                        'dCart': [], 'dTime': [], 'dMissing': [], 'dFaint': [],
                        'dNMissing': [], 'dNFaint': [], 'aTime': [],
                        'aOffset': [], 'aID': [], 'aLamp': [], 'oTime': [],
                        'oOffset': [], 'oDither': []}
        self.b_data = {'cCart': [], 'cTime': [],
                       'iTime': [], 'iID': [],
                       'iDetector': [], 'iDither': [],
                       'iEType': [], 'idt': [], 'iCart': [], 'iHart': [],
                       'iPlate': [], 'hHart': [], 'hTime': []}
        # These values are not known from the header and must be created
        # after self.sort. N for number, AP or B for APOGEE or BOSS, and NSE
        # for BOSS dithers, and AB for APOGEE dithers, dt for boss exposure
        # time, since some boss carts use shorter exposures. All these are
        # combined to fill Summary in self.count_dithers
        self.cart_data = {'cNAPA': [], 'cNAPB': [], 'cNBN': [], 'cNBS': [],
                          'cNBE': [], 'cNBC': [], 'cBdt': [],
                          'cAPSummary': [],
                          'cBSummary': []}
        self.test_procs = []
        self.telemetry = epics_fetch.telemetry
        # Commented out to test the apogee_data.APOGEERaw.ap_test method
        # self.ap_tester = ap_test.ApogeeFlat(
        #     Path(__file__).absolute().parent.parent
        #     / 'dat/ap_master_flat_col_array.dat', self.args)
        master_data = fitsio.read('/data/apogee/quickred/59011/ap1D-a-34490027'
                                  '.fits.fz')
        self.ap_master = np.average(master_data[:, 900:910], axis=1)

        self.morning_filter = None

    def ap_test(self, img):
        """Calls aptest on hub, this could certainly be replaced in the near
        future.
        """
        # This is from ap_test
        self.args.plot = False
        missing, faint = img.ap_test((900, 910), self.ap_master)
        # test = sub.Popen((Path(__file__).absolute().parent.parent
        #                   / 'old_bin/aptest').__str__() + ' {} {}'
        #                  ''.format(self.args.mjd, img.exp_id), shell=True,
        #                  stdout=sub.PIPE, stderr=sub.PIPE)
        # lines = test.stdout.read().decode('utf-8').splitlines()[3:]
        # err = test.stderr.read().decode('utf-8')
        # if err:
        #     raise Exception(err)
        # missing = eval(lines[0].split('Missing fibers: ')[-1])
        # faint = eval(lines[1].split('Faint fibers:   ')[-1])
        if self.args.verbose:
            print('Exposure {}'.format(img.exp_id))
            print(missing, faint)
        n_missing = 0
        n_faint = 0
        for miss in missing:
            if isinstance(miss, bytes) or isinstance(miss, str):
                if 'bundle' in miss:
                    n_missing += 30
                else:
                    n_missing += abs(eval(miss))
            else:
                n_missing += 1
        for fain in faint:
            if isinstance(fain, bytes) or isinstance(fain, str):
                if 'bundle' in fain:
                    n_faint += 30
                else:
                    n_faint += np.abs(eval(fain))
            else:
                n_faint += 1
        # return (n_missing, n_faint, missing, faint, img.cart_id,
        #         img.isot)
        self.ap_data['dNMissing'].append(n_missing)
        self.ap_data['dNFaint'].append(n_faint)
        self.ap_data['dMissing'].append(missing)
        self.ap_data['dFaint'].append(faint)
        self.ap_data['dCart'].append(img.cart_id)
        self.ap_data['dTime'].append(img.isot)

    def parse_images(self):
        """Goes through every image in ap_images and m_images to put them in
        dictionaries."""
        if self.args.apogee:
            print('Reading APOGEE Data')
            for image in tqdm(self.ap_images):
                # print(image)
                img = apogee_data.APOGEERaw(image, self.args, 1)
                # img.parse_layer(1)
                if not img.plate_id:  # If the first exposure is still
                    # writing, plate_id will be empty and without this if,
                    # it would fail. With this if, it will skip the plate
                    continue
                if (img.exp_type == 'Domeflat') and ('-a-' in img.file.name):
                    self.ap_test(img)
                    self.test_procs.append(img.cart_id)
                elif ('Arc' in img.exp_type) and ('-a-' in img.file.name):
                    self.ap_data['aTime'].append(img.isot)
                    self.ap_data['aID'].append(img.exp_id)
                    if 'ThAr' in img.exp_type:
                        self.ap_data['aOffset'].append(
                            img.compute_offset((30, 35), 939, 40, 1.27))
                        self.ap_data['aLamp'].append('ThAr')
                    elif 'UNe' in img.exp_type:
                        self.ap_data['aOffset'].append(
                            img.compute_offset((30, 35), 1761, 20, 3))
                        self.ap_data['aLamp'].append('UNe')
                    else:
                        print("Couldn't parse the arc image: {} with exposure"
                              " type {}".format(img.file, img.exp_type))
                elif ('Object' in img.exp_type) and ('-a-' in img.file.name):
                    # TODO check an object image for a good FWHM (last
                    #  input)
                    self.ap_data['oTime'].append(img.isot)
                    self.ap_data['oOffset'].append(
                        img.compute_offset((30, 35), 1090, 40, 2))
                    self.ap_data['oDither'].append(img.dither)

                if img.cart_id not in self.data['cCart']:
                    self.data['cPlate'].append(img.plate_id)
                    self.data['cCart'].append(img.cart_id)
                    self.data['cTime'].append(img.isot)
                    self.data['cLead'].append(img.lead)
                else:
                    i = self.data['cCart'].index(img.cart_id)
                    if img.isot < self.data['cTime'][i]:
                        self.data['cTime'].pop(i)
                        self.data['cTime'].insert(i, img.isot)
                if img.cart_id not in self.ap_data['cCart']:
                    self.ap_data['cCart'].append(img.cart_id)
                    self.ap_data['cTime'].append(img.isot)
                else:
                    i = self.ap_data['cCart'].index(img.cart_id)
                    if img.isot < self.ap_data['cTime'][i]:
                        self.ap_data['cTime'].pop(i)
                        self.ap_data['cTime'].insert(i, img.isot)
                detectors = []
                red_dir = Path('/data/apogee/quickred/{}/'.format(
                    self.args.mjd))
                red_fil = red_dir / 'ap1D-a-{}.fits.fz'.format(img.exp_id)
                if red_fil.exists():
                    detectors.append('a')
                else:
                    detectors.append('x')
                if (red_fil.parent / red_fil.name.replace(
                        '-a-', '-b-')).exists():
                    detectors.append('b')
                else:
                    detectors.append('x')
                if (red_fil.parent / red_fil.name.replace(
                        '-a-', '-c-')).exists():
                    detectors.append('c')
                else:
                    detectors.append('x')
                self.ap_data['iTime'].append(img.isot)
                self.ap_data['iID'].append(img.exp_id)
                self.ap_data['iSeeing'].append(img.seeing)
                self.ap_data['iDetector'].append('-'.join(detectors))
                self.ap_data['iDither'].append(img.dither)
                self.ap_data['iNRead'].append(img.n_read)
                self.ap_data['iEType'].append(img.exp_type)
                self.ap_data['iCart'].append(img.cart_id)
                self.ap_data['iPlate'].append(img.plate_id)
        if self.args.boss:
            print('Reading BOSS Data')
            for image in tqdm(self.m_images):
                img = boss_data.BOSSRaw(image)
                if img.cart_id not in self.data['cCart']:
                    self.data['cCart'].append(img.cart_id)
                    self.data['cPlate'].append(img.plate_id)
                    self.data['cLead'].append(img.lead)
                    self.data['cTime'].append(img.isot)
                else:
                    i = self.data['cCart'].index(img.cart_id)
                    if img.isot < self.data['cTime'][i]:
                        self.data['cTime'].pop(i)
                        self.data['cTime'].insert(i, img.isot)
                if img.cart_id not in self.b_data['cCart']:
                    self.b_data['cCart'].append(img.cart_id)
                    self.b_data['cTime'].append(img.isot)
                else:
                    i = self.b_data['cCart'].index(img.cart_id)
                    if img.isot < self.b_data['cTime'][i]:
                        self.b_data['cTime'].pop(i)
                        self.b_data['cTime'].insert(i, img.isot)
                self.b_data['iTime'].append(img.isot)
                self.b_data['iID'].append(img.exp_id)
                # self.b_data['iSeeing'].append(img.seeing)
                self.b_data['iDither'].append(img.dither)
                self.b_data['iEType'].append(img.flavor)
                self.b_data['idt'].append(img.exp_time)
                self.b_data['iCart'].append(img.cart_id)
                self.b_data['iHart'].append(img.hartmann)
                self.b_data['iPlate'].append(img.plate_id)

                if img.hartmann == 'Left':
                    # Note that times are sent in UTC and received in local, yet
                    # those times are marked as UTC
                    tstart = Time(img.isot).datetime
                    tend = (Time(img.isot) + 5 / 24 / 60).datetime
                    hart = self.telemetry.get([
                        '25m:hartmann:r1PistonMove',
                        '25m:hartmann:r2PistonMove',
                        '25m:hartmann:b1RingMove',
                        '25m:hartmann:b2RingMove',
                        '25m:hartmann:sp1AverageMove',
                        '25m:hartmann:sp2AverageMove',
                        '25m:hartmann:sp1Residuals:deg',
                        '25m:hartmann:sp2Residuals:deg',
                        '25m:boss:sp1Temp:median', '25m:boss:sp2Temp:median',
                        '25m:hartmann:sp1Residuals:steps',
                        '25m:hartmann:sp2Residuals:steps'
                    ],
                        start=tstart,
                        end=tend,
                        interpolation='raw', scan_archives=False)

                    self.b_data['hHart'].append(hart)
                    self.b_data['hTime'].append(img.isot)
                m_detectors = []
                # img_mjd = int(Time(img.isot).mjd)
                if 'BOSS' in img.lead:
                    red_dir = Path('/data/boss/sos/{}/'.format(self.args.mjd))
                    red_fil = red_dir / 'splog-r1-{:0>8}.log'.format(
                        img.exp_id)
                else:  # MaNGA
                    if img.flavor == 'Science':
                        red_dir = Path('/data/manga/dos/{}/'.format(
                            self.args.mjd))
                        red_fil = red_dir / 'mgscisky-{}-r1-{:0>8}.fits'.format(
                            img.plate_id, img.exp_id)
                    elif img.flavor == 'Flat':
                        red_dir = Path('/data/manga/dos/{}/'.format(
                            self.args.mjd))
                        red_fil = red_dir / 'mgtset-{}-{}-{:0>8}-r1.fits' \
                                            ''.format(self.args.mjd,
                                                      img.plate_id, img.exp_id)
                    elif img.flavor == 'Arc':
                        red_dir = Path('/data/manga/dos/{}/'.format(
                            self.args.mjd))
                        red_fil = red_dir / 'mgwset-{}-{}-{:0>8}-r1.fits' \
                                            ''.format(self.args.mjd,
                                                      img.plate_id, img.exp_id)
                    else:  # Harts and Bias, no file written there
                        red_dir = Path('/data/manga/dos/{}/logs/'.format(
                            self.args.mjd))
                        red_fil = red_dir / 'splog-r1-{:0>8}.log'.format(
                            img.exp_id)
                if red_fil.exists():
                    m_detectors.append('r1')
                else:
                    m_detectors.append('xx')
                if (red_fil.parent / red_fil.name.replace('r1', 'b1')).exists():
                    m_detectors.append('b1')
                else:
                    m_detectors.append('xx')
                if (red_fil.parent / red_fil.name.replace('r1', 'r2')).exists():
                    m_detectors.append('r2')
                else:
                    m_detectors.append('xx')
                if (red_fil.parent / red_fil.name.replace('r1', 'b2')).exists():
                    m_detectors.append('b2')
                else:
                    m_detectors.append('xx')
                self.b_data['iDetector'].append('-'.join(m_detectors))

    def sort(self):
        """Sorts self.ap_data by cart time and by image time and converts to
        arrays"""
        # Data
        for key, item in self.data.items():
            if 'Time' in key:
                try:
                    self.data[key] = Time(item)
                except ValueError:
                    self.data[key] = Time(item, format='isot')
            else:
                self.data[key] = np.array(item)
        data_sort = self.data['cTime'].argsort()
        for key, item in self.data.items():
            self.data[key] = item[data_sort]

        if self.args.apogee:
            for key, item in self.ap_data.items():
                if 'Time' in key:
                    try:
                        self.ap_data[key] = Time(item)
                    except ValueError:
                        self.ap_data[key] = Time(item, format='isot')
                else:
                    self.ap_data[key] = np.array(item)
            ap_cart_sorter = self.ap_data['cTime'].argsort()
            ap_img_sorter = self.ap_data['iTime'].argsort()
            ap_dome_sorter = self.ap_data['dTime'].argsort()
            ap_arc_sorter = self.ap_data['aTime'].argsort()
            ap_obj_sorter = self.ap_data['oTime'].argsort()
            for key, item in self.ap_data.items():
                if key[0] == 'c':
                    self.ap_data[key] = item[ap_cart_sorter]
                elif key[0] == 'i':
                    self.ap_data[key] = item[ap_img_sorter]
                elif key[0] == 'd':
                    self.ap_data[key] = item[ap_dome_sorter]
                elif key[0] == 'a':
                    self.ap_data[key] = item[ap_arc_sorter]
                elif key[0] == 'o':
                    self.ap_data[key] = item[ap_obj_sorter]
            if self.args.morning:
                was_dark = False
                prev_time = 0
                lower = None
                for t, reads, exp in zip(self.ap_data['iTime'],
                                         self.ap_data['iNRead'],
                                         self.ap_data['iEType']):
                    if (reads == 60) and (exp == 'Dark'):
                        if was_dark:
                            lower = prev_time
                            break
                        else:
                            was_dark = True
                            prev_time = t
                            if self.args.verbose:
                                print('Morning lower limit: {}'.format(
                                    prev_time))
                    else:
                        was_dark = False
                upper = Time(self.args.mjd + 1, format='mjd')
                if lower is None:
                    raise Exception('Morning cals not completed for this date')
                self.morning_filter = ((lower <= self.ap_data['iTime'])
                                       & (self.ap_data['iTime'] <= upper))

        if self.args.boss:
            for key, item in self.b_data.items():
                if 'Time' in key:
                    try:
                        self.b_data[key] = Time(item)
                    except ValueError:
                        self.b_data[key] = Time(item, format='isot')
                else:
                    self.b_data[key] = np.array(item)
            b_cart_sorter = self.b_data['cTime'].argsort()
            b_img_sorter = self.b_data['iTime'].argsort()
            b_h_sorter = self.b_data['hTime'].argsort()
            for key, item in self.b_data.items():
                if key[0] == 'c':
                    self.b_data[key] = item[b_cart_sorter]
                elif key[0] == 'i':
                    self.b_data[key] = item[b_img_sorter]
                elif key[0] == 'h':
                    self.b_data[key] = item[b_h_sorter]

    def count_dithers(self):
        for i, cart in enumerate(self.data['cCart']):
            self.cart_data['cNAPA'].append(np.sum(
                (self.ap_data['iCart'] == cart)
                & (self.ap_data['iDither'] == 'A')
                & (self.ap_data['iEType'] == 'Object')))
            self.cart_data['cNAPB'].append(np.sum(
                (self.ap_data['iCart'] == cart)
                & (self.ap_data['iDither'] == 'B')
                & (self.ap_data['iEType'] == 'Object')))
            self.cart_data['cNBN'].append(np.sum(
                (self.b_data['iCart'] == cart)
                & (self.b_data['iDither'] == 'N')
                & (self.b_data['iEType'] == 'Science')))
            self.cart_data['cNBS'].append(np.sum(
                (self.b_data['iCart'] == cart)
                & (self.b_data['iDither'] == 'S')
                & (self.b_data['iEType'] == 'Science')))
            self.cart_data['cNBE'].append(np.sum(
                (self.b_data['iCart'] == cart)
                & (self.b_data['iDither'] == 'E')
                & (self.b_data['iEType'] == 'Science')))
            self.cart_data['cNBC'].append(np.sum(
                (self.b_data['iCart'] == cart)
                & (self.b_data['iDither'] == 'C')
                & (self.b_data['iEType'] == 'Science')))
            if np.any((self.b_data['iCart'] == cart)
                      & (self.b_data['iEType'] == 'Science')):
                self.cart_data['cBdt'].append(np.max(
                    self.b_data['idt'][(self.b_data['iCart'] == cart)
                                       & (self.b_data['iEType'] == 'Science')]
                ))

        for i, cart in enumerate(self.data['cCart']):
            """To determine the number of apogee a dithers per cart (cNAPA),
            as well as b dithers (cNAPB), and the same for NSE dithers."""
            # APOGEE dithers
            if self.cart_data['cNAPA'][i] == self.cart_data['cNAPB'][i]:
                self.cart_data['cAPSummary'].append(
                    '{}xAB'.format(self.cart_data['cNAPA'][i]))
            else:
                self.cart_data['cAPSummary'].append(
                    '{}xA {}xB'.format(self.cart_data['cNAPA'][i],
                                       self.cart_data['cNAPB'][i]))
            # BOSS (MaNGA) dithers
            if self.cart_data['cNBC'][i] == 0:
                if (self.cart_data['cNBN'][i]
                        == self.cart_data['cNBS'][i]
                        == self.cart_data['cNBE'][i]):
                    self.cart_data['cBSummary'].append(
                        '{}xNSE'.format(self.cart_data['cNBN'][i]))
                else:
                    self.cart_data['cBSummary'].append(
                        '{}xN {}xS {}xE'.format(self.cart_data['cNBN'][i],
                                                self.cart_data['cNBS'][i],
                                                self.cart_data['cNBE'][i]))
            else:
                self.cart_data['cBSummary'].append(
                    '{}xC'.format(self.cart_data['cNBC'][i]))
            if len(self.cart_data['cBdt']):
                try:
                    if self.cart_data['cBdt'][i] != 900:
                        self.cart_data['cBSummary'][-1] += '@{}s'.format(
                            self.cart_data['cBdt'][i])
                except IndexError:
                    # Happens if there is no science frame yet with an exposure
                    # time.
                    pass

    @staticmethod
    def hartmann_parse(hart):
        output = ''  # .format((Time(hart[0].times[-1])).isot)
        output += 'r1: {:>6.0f}, b1: {:>6.1f}\n'.format(
            hart[0].values[-1], hart[2].values[-1])
        output += 'r2: {:>6.0f}, b2: {:>6.1f}\n'.format(
            hart[1].values[-1], hart[3].values[-1])
        output += 'Average Moves:\n'
        output += 'SP1: {:>6.0f}, SP2: {:>6.0f}\n'.format(
            hart[4].values[-1], hart[5].values[-1])
        output += 'Red Residuals:\n'
        output += 'SP1: {:>6.0f}, SP2: {:>6.0f}\n'.format(
            hart[10].values[-1], hart[11].values[-1])
        output += 'Blue Residuals:\n'
        output += 'SP1: {:>6.1f}, SP2: {:>6.1f}\n'.format(
            hart[6].values[-1], hart[7].values[-1])
        output += 'Spectrograph Temperatures:\n'
        output += 'SP1: {:>6.1f}, SP2: {:>6.1f}'.format(
            hart[8].values[-1], hart[9].values[-1])
        return output

    def p_summary(self):
        print('=' * 80)
        print('{:^80}'.format('Observing Summary'))
        print('=' * 80)
        for i, cart in enumerate(self.data['cCart']):
            print('')
            print('Cart {}, plate {}, {}'
                  ', {},'.format(cart, self.data['cPlate'][i],
                                 self.cart_data['cAPSummary'][i],
                                 self.cart_data['cBSummary'][i]))
            try:
                j = np.where(self.ap_data['dCart'] == cart)[0][0]
                print('Missing Fibers: {}, Faint fibers: {}'.format(
                    self.ap_data['dNMissing'][j],
                    self.ap_data['dNFaint'][j]))
            except IndexError:
                pass
        print()
        print('### Notes:\n')
        dust_sum = get_dust.get_dust(self.args.mjd, self.args)
        print('- Integrated Dust Counts: ~{:5.0f} dust-hrs'.format(
            dust_sum - dust_sum % 100))
        print('\n')

        print('=' * 80)
        print('{:^80}'.format('Comments Timeline'))
        print('=' * 80)
        print()

    @staticmethod
    def get_window(data, i):
        try:
            window = ((data['iTime']
                       >= data['cTime'][i])
                      & (data['iTime']
                         < data['cTime'][i + 1])
                      )

        except IndexError:
            try:
                window = ((data['iTime'] >= data['cTime'][i])
                          & (data['iTime'] < Time.now() + 0.25))
            except IndexError:
                window = np.array([False] * len(data['iTime']))

        return window

    def p_data(self):
        print('=' * 80)
        print('{:^80}'.format('Data Log'))
        print('=' * 80 + '\n')
        for i, cart in enumerate(self.data['cCart']):
            print('### Cart {}, Plate {}, {}\n'.format(cart,
                                                     self.data['cPlate'][i],
                                                     self.data['cLead'][i]))
            if cart in self.ap_data['cCart']:
                ap_cart = np.where(cart == self.ap_data['cCart'])[0][0]

                print('# APOGEE')
                print('{:<5} {:<8} {:<8} {:<12} {:<4} {:<6} {:<9}'
                      ' {:<4}'.format('MJD', 'UTC', 'Exposure', 'Type',
                                      'Dith', 'nReads', 'Pipeline',
                                      'Seeing'))
                print('-' * 80)
                window = self.get_window(self.ap_data, ap_cart)
                for (mjd, iso, exp_id, exp_type, dith, nread,
                     detectors, see) in zip(
                    self.ap_data['iTime'][window].mjd + 0.25,
                    self.ap_data['iTime'][window].iso,
                    self.ap_data['iID'][window],
                    self.ap_data['iEType'][window],
                    self.ap_data['iDither'][window],
                    self.ap_data['iNRead'][window],
                    self.ap_data['iDetector'][window],
                    self.ap_data['iSeeing'][window]
                ):
                    print('{:<5.0f} {:0>8} {:<8.0f} {:<12} {:<4} {:>6} {:<9}'
                          ' {:>4.1f}'.format(int(mjd), iso[12:19], exp_id,
                                             exp_type,
                                             dith, nread, detectors, see))
                print()
                if cart in self.ap_data['dCart']:
                    for j, dome in enumerate(self.ap_data['dCart']):
                        if dome == cart:
                            print(self.ap_data['dTime'][j].iso)
                            print('Missing fibers: {}'.format(
                                self.ap_data['dMissing'][j]))
                            print('Faint fibers: {}'.format(
                                self.ap_data['dFaint'][j]))
                            print()

            if cart in self.b_data['cCart']:
                print('# BOSS')
                print('{:<5} {:<8} {:<8} {:<7} {:<4} {:<11} {:<5} {:<5}'
                      ''.format('MJD', 'UTC', 'Exposure', 'Type',
                                'Dith', 'Pipeline', 'ETime', 'Hart'))
                print('-' * 80)
                # i is an index for data, but it will disagree with b_data
                # if there is an apogee-only cart
                b_cart = np.where(cart == self.b_data['cCart'])[0][0]
                window = self.get_window(self.b_data, b_cart)
                for (mjd, iso, exp_id, exp_type, dith,
                     detectors, etime, hart) in zip(
                    self.b_data['iTime'][window].mjd + 0.25,
                    self.b_data['iTime'][window].iso,
                    self.b_data['iID'][window],
                    self.b_data['iEType'][window],
                    self.b_data['iDither'][window],
                    self.b_data['iDetector'][window],
                    self.b_data['idt'][window],
                    self.b_data['iHart'][window],
                ):
                    print('{:<5.0f} {:0>8} {:0>8.0f} {:<7} {:<4} {:<11}'
                          ' {:>5.0f} {:<5}'
                          ''.format(int(mjd), iso[12:19], exp_id,
                                    exp_type.strip(),
                                    dith.strip(), detectors, etime,
                                    hart))
                try:
                    window = ((self.b_data['hTime']
                               >= self.data['cTime'][i])
                              & (self.b_data['hTime']
                                 < self.data['cTime'][i + 1])
                              )

                except IndexError:
                    window = ((self.b_data['hTime']
                               >= self.data['cTime'][i])
                              & (self.b_data['hTime'] < Time.now()))
                for t, hart in zip(self.b_data['hTime'][window],
                                   self.b_data['hHart'][window]):
                    print()
                    print(t.iso)
                    print(self.hartmann_parse(hart))
                print('\n')

    def p_boss(self):
        print('=' * 80)
        print('{:^80}'.format('BOSS Data Summary'))
        print('=' * 80 + '\n')
        print('{:<5} {:<8} {:<8} {:<8} {:<7} {:<4} {:<11} {:<5} {:<5}'
              ''.format('MJD', 'UTC', 'Cart', 'Exposure', 'Type', 'Dith',
                        'Pipeline', 'ETime', 'Hart'))
        print('-' * 80)
        for (mjd, iso, cart, plate, exp_id, exp_type, dith, detectors, etime,
             hart) in zip(self.b_data['iTime'].mjd + 0.25,
                          self.b_data['iTime'].iso,
                          self.b_data['iCart'],
                          self.b_data['iPlate'],
                          self.b_data['iID'],
                          self.b_data['iEType'],
                          self.b_data['iDither'],
                          self.b_data['iDetector'],
                          self.b_data['idt'],
                          self.b_data['iHart']):
            print('{:<5.0f} {:>8} {:>2.0f}-{:<5.0f} {:0>8.0f} {:<7} {:<4}'
                  ' {:<11}'
                  ' {:>5.0f} {:<5}'
                  ''.format(int(mjd), iso[12:19], cart, plate, exp_id,
                            exp_type.strip(),
                            dith.strip(), detectors, etime, hart))
        print()

    def p_apogee(self):
        print('=' * 80)
        print('{:^80}'.format('APOGEE Data Summary'))
        print('=' * 80 + '\n')
        print('{:<5} {:<8} {:<8} {:<8} {:<12} {:<4} {:<6} {:<8}'
              ' {:<6}'.format('MJD', 'UTC', 'Cart', 'Exposure', 'Type',
                              'Dith', 'nReads', 'Pipeline',
                              'Seeing'))
        print('-' * 80)
        if self.args.morning:
            for (mjd, iso, cart, plate, exp_id, exp_type, dith, nread,
                 detectors, see) in zip(
                self.ap_data['iTime'].mjd[self.morning_filter] + 0.25,
                self.ap_data['iTime'].iso[self.morning_filter],
                self.ap_data['iCart'][self.morning_filter],
                self.ap_data['iPlate'][self.morning_filter],
                self.ap_data['iID'][self.morning_filter],
                self.ap_data['iEType'][self.morning_filter],
                self.ap_data['iDither'][self.morning_filter],
                self.ap_data['iNRead'][self.morning_filter],
                self.ap_data['iDetector'][self.morning_filter],
                self.ap_data['iSeeing'][self.morning_filter]
            ):
                print('{:<5.0f} {:>8} {:>2.0f}-{:<5.0f} {:<8.0f} {:<12} {:<4}'
                      ' {:>6}'
                      ' {:<8}'
                      ' {:>6.1f}'.format(int(mjd), iso[11:19], cart, plate,
                                         exp_id, exp_type,
                                         dith, nread, detectors, see))

        else:
            for (mjd, iso, cart, plate, exp_id, exp_type, dith, nread,
                 detectors, see) in zip(
                self.ap_data['iTime'].mjd,
                self.ap_data['iTime'].iso,
                self.ap_data['iCart'],
                self.ap_data['iPlate'],
                self.ap_data['iID'], self.ap_data['iEType'],
                self.ap_data['iDither'], self.ap_data['iNRead'],
                self.ap_data['iDetector'],
                self.ap_data['iSeeing']
            ):
                print('{:<5.0f} {:>8} {:>2.0f}-{:<5.0f} {:<8.0f} {:<12} {:<4}'
                      ' {:>6}'
                      ' {:<8}'
                      ' {:>6.1f}'.format(int(mjd), iso[12:19], cart, plate,
                                         exp_id, exp_type,
                                         dith, nread, detectors, see))
        # Usually, there are 4 ThAr and 4 UNe arcs in a night, and they're
        # assumed to be alternating ThAr UNe ThAr UNe. When you grab every
        # other, you'll have only one type, that's the first slicing, and the
        # second slicing is that you only care about the diffs between two
        # dithers taken back to back.
        print('ThAr Offsets: {}'.format(['{:.3f}'.format(f) for f in np.diff(
            self.ap_data['aOffset'][self.ap_data['aLamp'] == 'ThAr'])]))
        print('UNe Offsets: {}'.format(['{:.3f}'.format(f) for f in np.diff(
            self.ap_data['aOffset'][self.ap_data['aLamp'] == 'UNe'])]))
        obj_offsets = []
        prev_dither = None
        prev_f = 0.
        for d, f in zip(self.ap_data['oDither'], self.ap_data['oOffset']):
            if d != prev_dither:
                obj_offsets.append('{:.3f}'.format(f - prev_f))
            prev_dither = d
            prev_f = f
        print('Object Offsets:\n{}'.format(textwrap.fill(str(
            obj_offsets), 80)))
        print('\n')

    def log_support(self):
        start = Time(self.args.mjd, format='mjd').isot
        end = Time(self.args.mjd + 1, format='mjd').isot
        tel = log_support.LogSupport(start, end, self.args)
        tel.set_callbacks()
        tel.get_offsets()
        tel.get_focus()
        tel.get_weather()
        tel.get_hartmann()
        print(tel.offsets)
        print()
        print(tel.focus)
        print()
        print(tel.weather)
        print()
        print(tel.hartmann)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true', default=True,
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 18:00Z to get the"
                             " correct sjd")
    parser.add_argument('-m', '--mjd', type=int,
                        help='If not today (-t), the mjd to search')
    parser.add_argument('-s', '--summary', help='Print the data summary',
                        action='store_true')
    parser.add_argument('-d', '--data', action='store_true',
                        help='Print the data log')
    parser.add_argument('-p', '--print', action='store_true',
                        help='Print all possible outputs')
    parser.add_argument('-b', '--boss', action='store_true',
                        help='Print BOSS Summary')
    parser.add_argument('-a', '--apogee', action='store_true',
                        help='Print APOGEE Summary')
    parser.add_argument('-l', '--log-support', action='store_true',
                        help='Print 4 log support sections')
    parser.add_argument('-n', '--noprogress', action='store_true',
                        help='Show no progress in processing images. WARNING:'
                             ' Might be slower, but it could go either way.')
    parser.add_argument('--morning', action='store_true',
                        help='Only output apogee morning cals')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increased printing for debugging')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if args.mjd:
        args.mjd = args.mjd
    elif args.today:
        now = Time.now() + 0.25
        args.mjd = int(now.mjd)
    else:
        raise argparse.ArgumentError(args.mjd,
                                     'Must provide -t or -m in arguments')

    ap_data_dir = ap_dir / '{}'.format(args.mjd)
    b_data_dir = b_dir / '{}'.format(args.mjd)
    ap_images = Path(ap_data_dir).glob('apR-a*.apz')
    b_images = Path(b_data_dir).glob('sdR-r1*fit.gz')

    if not args.noprogress:
        ap_images = list(ap_images)
        b_images = list(b_images)
    p_boss = args.boss
    p_apogee = args.apogee

    if args.print:
        args.summary = True
        args.data = True
        args.boss = True
        args.apogee = True
        p_boss = True
        p_apogee = True
        args.log_support = True

    if args.summary:
        args.boss = True
        args.apogee = True

    if args.morning:
        args.apogee = True
        p_apogee = True

    if args.data:
        args.boss = True
        args.apogee = True

    log = Logging(ap_images, b_images, args)
    log.parse_images()
    log.sort()
    log.count_dithers()

    if args.summary:
        log.p_summary()

    if args.data:
        log.p_data()

    if p_boss:
        log.p_boss()

    if p_apogee:
        log.p_apogee()

    if args.log_support:
        log.log_support()
    return log


if __name__ == '__main__':
    main()
