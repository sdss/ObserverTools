#!/usr/bin/env python3
"""sloan_log.py

A script to automate the bulk of logging and to replace various tools
 like log function, log support, list_ap, list_m, and more. This code is
 entirely dependent on raw images, and their headers, unlike Log Function
 which is dependent on callbacks it catches while open only and is subject to
 crashes. It's inspired by some outputs from time tracking, but it avoids the
 sdss python module and platedb

The intent of this is to create a more future-proof tool for logging through
Sloan V

In order to run it locally, you will need to either have access to /data, or
 fake it with a single night. You'll need a date from /data/spectro and
 /data/apogee/archive. You'll also need setup local forwarding for InfluxDB
"""
import argparse
import sys
import textwrap
import warnings
import fitsio

import numpy as np
try:
    from bin import m4l, telescope_status, get_dust
except ImportError as e:
    raise ImportError('Please add ObserverTools/bin to your PYTHONPATH:'
        '\n    {}'.format(e))
from pathlib import Path
from tqdm import tqdm
from astropy.time import Time

from sdssobstools import apogee_data, log_support, boss_data, sdss_paths
    
from bin import sjd

if sys.version_info.major < 3:
    raise Exception('Interpretter must be python 3.5 or newer')

# For astropy
warnings.filterwarnings('ignore', category=UserWarning, append=True)
# For numpy boolean arrays
warnings.filterwarnings('ignore', category=FutureWarning, append=True)

__version__ = '3.7.5'

ap_dir = sdss_paths.ap_archive
b_dir = sdss_paths.boss

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
        self.b_images = m_images
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
        self.data = {'dDesign': [], 'dTime': [], 'dConfig': [], 'cLead': []}
        self.ap_data = {'dDesign': [], 'dTime': [],
                        'iTime': [], 'iID': [],
                        'iSeeing': [], 'iDetector': [], 'iDither': [],
                        'iNRead': [], 'iEType': [], 'iDesign': [], 
                        "iDesign": [], "iConfig": [],
                        'fDesign': [], 'fTime': [], 'fMissing': [], 'fFaint': [],
                        'fNMissing': [], 'fNFaint': [], 'fRatio': [], 'aTime': [],
                        'aOffset': [], 'aID': [], 'aLamp': [], 'oTime': [],
                        'oOffset': [], 'oDither': []}
        self.b_data = {'dDesign': [], 'dTime': [],
                       'iTime': [], 'iID': [],
                       'iDetector': [], 'iDither': [],
                       'iEType': [], 'idt': [], 'iDesign': [], 'iHart': [],
                       'iDesign': [], "iConfig": [], 'hHart': [], 'hTime': []}
        # These values are not known from the header and must be created
        # after self.sort. N for number, AP or B for APOGEE or BOSS, and NSE
        # for BOSS dithers, and AB for APOGEE dithers, dt for boss exposure
        # time, since some boss carts use shorter exposures. All these are
        # combined to fill Summary in self.count_dithers
        self.design_data = {'cNAPA': [], 'cNAPB': [], 'cNBN': [], 'cNBS': [],
                          'cNBE': [], 'cNBC': [], 'cBdt': [], 'cNB': [],
                          'cAPSummary': [],
                          'cBSummary': []}
        self.test_procs = []
        master_path = (Path(apogee_data.__file__).absolute().parent.parent
                           / "dat/master_dome_flat.fits.gz")
        if not master_path.exists():
            master_path = (Path(apogee_data.__file__).absolute(
                ).parent.parent.parent / "dat/master_dome_flat.fits.gz")
        master_data = fitsio.read(master_path.as_posix())
        self.ap_master = np.median(master_data[:, 550:910], axis=1)
        self.morning_filter = None
        self.ap_image = None

    def ap_test(self, img):
        """Calls aptest on hub, this could certainly be replaced in the near
        future.
        """
        # This is from ap_test
        self.args.plot = False
        missing, faint, flux_ratio = img.ap_test((550, 910), self.ap_master)
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
        self.ap_data['fNMissing'].append(n_missing)
        self.ap_data['fNFaint'].append(n_faint)
        self.ap_data['fMissing'].append(missing)
        self.ap_data['fFaint'].append(faint)
        self.ap_data['fRatio'].append(flux_ratio)
        self.ap_data['fDesign'].append(img.design_id)
        self.ap_data['fTime'].append(img.isot)

    def parse_images(self):
        """Goes through every image in ap_images and m_images to put them in
        dictionaries."""
        if self.args.apogee:
            print('Reading APOGEE Data ({})'.format(len(self.ap_images)))
            img = None
            for image in tqdm(self.ap_images):
                if self.args.verbose:
                    print(image.name)
                img = apogee_data.APOGEERaw(image, self.args, 1)
                # img.parse_layer(1)
                if img.lead is None:  # If the first exposure is still
                    # writing, plate_id will be empty and without this if,
                    # it would fail. With this if, it will skip the plate
                    print(f"Skipping {image}")
                    continue
                if (img.exp_type == 'Domeflat') and ('-a-' in img.file.name):
                    self.ap_test(img)
                    self.test_procs.append(img.design_id)
                elif ('Arc' in img.exp_type) and ('-a-' in img.file.name):
                    self.ap_data['aTime'].append(img.isot)
                    self.ap_data['aID'].append(img.exp_id)
                    if 'ThAr' in img.exp_type:
                        self.ap_data['aOffset'].append(
                            img.compute_offset((60, 70), 1105, 40, 1.27))
                        self.ap_data['aLamp'].append('ThAr')
                    elif 'UNe' in img.exp_type:
                        self.ap_data['aOffset'].append(
                            img.compute_offset((60, 70), 1180, 30, 3))
                        self.ap_data['aLamp'].append('UNe')
                    else:
                        print("Couldn't parse the arc image: {} with exposure"
                              " type {}".format(img.file, img.exp_type))
                        self.ap_data["aTime"].pop()
                        self.ap_data["aID"].pop()
                elif ('Object' in img.exp_type) and ('-a-' in img.file.name):
                    # TODO check an object image for a good FWHM (last
                    # input)
                    self.ap_data['oTime'].append(img.isot)
                    self.ap_data['oOffset'].append(
                        img.compute_offset((30, 35), 1090, 40, 2))
                    self.ap_data['oDither'].append(img.dither)

                if img.design_id not in self.data['dDesign']:
                    self.data['dConfig'].append(img.plate_id)
                    self.data['dDesign'].append(img.design_id)
                    self.data['dTime'].append(img.isot)
                    try:
                        self.data['cLead'].append(img.lead)
                    except AttributeError:
                        self.data["cLead"].append("")
                else:
                    i = self.data['dDesign'].index(img.design_id)
                    if img.isot < self.data['dTime'][i]:
                        self.data['dTime'].pop(i)
                        self.data['dTime'].insert(i, img.isot)
                if img.design_id not in self.ap_data['dDesign']:
                    self.ap_data['dDesign'].append(img.design_id)
                    self.ap_data['dTime'].append(img.isot)
                else:
                    i = self.ap_data['dDesign'].index(img.design_id)
                    if img.isot < self.ap_data['dTime'][i]:
                        self.ap_data['dTime'].pop(i)
                        self.ap_data['dTime'].insert(i, img.isot)
                detectors = []
                arch_dir = sdss_paths.ap_archive / f"{self.args.sjd}/"
                # red_dir = Path('/data/apogee/quickred/{}/'.format(
                #     self.args.sjd))
                # This used to see if quickred processed, but others preferred
                # to see if the archive image was written
                arch_name = 'apR-a-{}.apz'.format(img.exp_id)
                if (arch_dir / arch_name).exists():
                    detectors.append('a')
                # elif (red_dir / arch_name.replace('1D', '2D')).exists():
                # detectors.append('2')
                else:
                    detectors.append('x')
                if (arch_dir / arch_name.replace('-a-', '-b-')).exists():
                    detectors.append('b')
                # elif (red_dir / arch_name.replace('-a-', '-b-').replace(
                # '1D', '2D')).exists():
                # detectors.append('2')
                else:
                    detectors.append('x')
                if (arch_dir / arch_name.replace('-a-', '-c-')).exists():
                    detectors.append('c')
                # elif (red_dir / arch_name.replace('-a-', '-c-').replace(
                # '1D', '2D')).exists():
                # detectors.append('2')
                else:
                    detectors.append('x')
                self.ap_data['iTime'].append(img.isot)
                self.ap_data['iID'].append(img.exp_id)
                self.ap_data['iSeeing'].append(img.seeing)
                self.ap_data['iDetector'].append('-'.join(detectors))
                self.ap_data['iDither'].append(img.dither)
                self.ap_data['iNRead'].append(img.n_read)
                self.ap_data['iEType'].append(img.exp_type)
                self.ap_data['iDesign'].append(img.design_id)
                self.ap_data['iConfig'].append(img.config_id)
            if img is not None:
                self.ap_image = img
        if self.args.boss:
            print('Reading BOSS Data ({})'.format(len(self.b_images)))
            for image in tqdm(self.b_images):
                img = boss_data.BOSSRaw(image)
                if img.design_id not in self.data['dDesign']:
                    self.data['dDesign'].append(img.design_id)
                    self.data['dConfig'].append(img.plate_id)
                    try:
                        self.data['cLead'].append(img.lead)
                    except AttributeError:
                        self.data["cLead"].append("")    
                    self.data['dTime'].append(img.isot)
                else:
                    i = self.data['dDesign'].index(img.design_id)
                    if img.isot < self.data['dTime'][i]:
                        self.data['dTime'].pop(i)
                        self.data['dTime'].insert(i, img.isot)
                if img.design_id not in self.b_data['dDesign']:
                    self.b_data['dDesign'].append(img.design_id)
                    self.b_data['dTime'].append(img.isot)
                else:
                    i = self.b_data['dDesign'].index(img.design_id)
                    if img.isot < self.b_data['dTime'][i]:
                        self.b_data['dTime'].pop(i)
                        self.b_data['dTime'].insert(i, img.isot)
                self.b_data['iTime'].append(img.isot)
                self.b_data['iID'].append(img.exp_id)
                # self.b_data['iSeeing'].append(img.seeing)
                self.b_data['iDither'].append(img.dither)
                self.b_data['iEType'].append(img.flavor)
                self.b_data['idt'].append(img.exp_time)
                self.b_data['iDesign'].append(img.design_id)
                self.b_data['iHart'].append(img.hartmann)
                self.b_data['iConfig'].append(img.config_id)

                # if img.hartmann == 'Left' and self.telemetry:
                #     # Note that times are sent in UTC and received in local, yet
                #     # those times are marked as UTC
                #     tstart = Time(img.isot).datetime
                #     tend = (Time(img.isot) + 5 / 24 / 60).datetime
                #     hart = self.telemetry.get([
                #         '25m:hartmann:r1PistonMove',
                #         # '25m:hartmann:r2PistonMove',
                #         '25m:hartmann:b1RingMove',
                #         # '25m:hartmann:b2RingMove',
                #         '25m:hartmann:sp1AverageMove',
                #         # '25m:hartmann:sp2AverageMove',
                #         '25m:hartmann:sp1Residuals:steps',
                #         '25m:hartmann:sp1Residuals:deg',
                #         # '25m:hartmann:sp2Residuals:deg',
                #         '25m:boss:sp1Temp:median',
                #         # '25m:boss:sp2Temp:median',
                #         # '25m:hartmann:sp2Residuals:steps'
                #     ],
                #         start=tstart,
                #         end=tend,
                #         interpolation='raw', scan_archives=False)

                #     self.b_data['hHart'].append(hart)
                #     self.b_data['hTime'].append(img.isot)
                sos_files = []
                # img_mjd = int(Time(img.isot).mjd)
                # All boss exposures write as splog, but manga writes different
                red_dir = sdss_paths.sos / f"{self.args.sjd}"
                red_fil = red_dir / 'splog-r1-{:0>8}.log'.format(img.exp_id)
                if red_fil.exists():
                    sos_files.append('r1')
                else:
                    sos_files.append('xx')
                if (red_fil.parent / red_fil.name.replace('r1', 'b1')).exists():
                    sos_files.append('b1')
                else:
                    sos_files.append('xx')
                if (red_fil.parent / red_fil.name.replace('r1', 'r2')).exists():
                    sos_files.append('r2')
                # else:
                #     m_detectors.append('xx')
                if (red_fil.parent / red_fil.name.replace('r1', 'b2')).exists():
                    sos_files.append('b2')
                # else:
                #     m_detectors.append('xx')
                self.b_data['iDetector'].append('-'.join(sos_files))

    def sort(self):
        """Sorts self.ap_data by design time and by image time and converts to
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
        data_sort = self.data['dTime'].argsort()
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
            ap_design_sorter = self.ap_data['dTime'].argsort()
            ap_img_sorter = self.ap_data['iTime'].argsort()
            ap_dome_sorter = self.ap_data['fTime'].argsort()
            ap_arc_sorter = self.ap_data['aTime'].argsort()
            ap_obj_sorter = self.ap_data['oTime'].argsort()
            for key, item in self.ap_data.items():
                if key[0] == 'd':
                    self.ap_data[key] = item[ap_design_sorter]
                elif key[0] == 'i':
                    self.ap_data[key] = item[ap_img_sorter]
                elif key[0] == 'f':
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
                upper = Time(self.args.sjd + 1, format='mjd')
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
            b_design_sorter = self.b_data['dTime'].argsort()
            b_img_sorter = self.b_data['iTime'].argsort()
            b_h_sorter = self.b_data['hTime'].argsort()
            for key, item in self.b_data.items():
                if key[0] == 'c':
                    self.b_data[key] = item[b_design_sorter]
                elif key[0] == 'i':
                    self.b_data[key] = item[b_img_sorter]
                elif key[0] == 'h':
                    self.b_data[key] = item[b_h_sorter]

    def count_dithers(self):
        for i, design in enumerate(self.data['dDesign']):
            self.design_data['cNAPA'].append(np.sum(
                (self.ap_data['iDesign'] == design)
                & (self.ap_data['iDither'] == 'A')
                & (self.ap_data['iEType'] == 'Object')))
            self.design_data['cNAPB'].append(np.sum(
                (self.ap_data['iDesign'] == design)
                & (self.ap_data['iDither'] == 'B')
                & (self.ap_data['iEType'] == 'Object')))
            # self.design_data['cNBN'].append(np.sum(
            # (self.b_data['iDesign'] == design)
            # & (self.b_data['iDither'] == 'N')
            # & (self.b_data['iEType'] == 'Science')))
            # self.design_data['cNBS'].append(np.sum(
            # (self.b_data['iDesign'] == design)
            # & (self.b_data['iDither'] == 'S')
            # & (self.b_data['iEType'] == 'Science')))
            # self.design_data['cNBE'].append(np.sum(
            # (self.b_data['iDesign'] == design)
            # & (self.b_data['iDither'] == 'E')
            # & (self.b_data['iEType'] == 'Science')))
            # self.design_data['cNBC'].append(np.sum(
            # (self.b_data['iDesign'] == design)
            # & (self.b_data['iDither'] == 'C')
            # & (self.b_data['iEType'] == 'Science')))
            self.design_data['cNB'].append(np.sum(
                (self.b_data['iDesign'] == design)
                & (self.b_data['iEType'] == 'Science')))
            if self.design_data['cNB'][-1] != 0:
                self.design_data['cBdt'].append(np.max(
                    self.b_data['idt'][
                        (self.b_data['iDesign'] == design)
                        & (self.b_data['iEType'] == 'Science')]))
            else:
                self.design_data['cBdt'].append(0)

        for i, design in enumerate(self.data['dDesign']):
            """To determine the number of apogee a dithers per design (cNAPA),
            as well as b dithers (cNAPB), and the same for NSE dithers."""
            # APOGEE dithers
            if self.design_data['cNAPA'][i] == self.design_data['cNAPB'][i]:
                if self.design_data['cNAPA'][i] != 0:
                    self.design_data['cAPSummary'].append(
                        '{}xAB'.format(self.design_data['cNAPA'][i]))
                else:
                    self.design_data['cAPSummary'].append('No APOGEE Science')
            else:
                self.design_data['cAPSummary'].append(
                    '{}xA {}xB'.format(self.design_data['cNAPA'][i],
                                       self.design_data['cNAPB'][i]))
            # BOSS (MaNGA) dithers
            # if self.design_data['cNBC'][i] == 0:
            # if (self.design_data['cNBN'][i]
            # == self.design_data['cNBS'][i]
            # == self.design_data['cNBE'][i]):
            # self.design_data['cBSummary'].append(
            # '{}xNSE'.format(self.design_data['cNBN'][i]))
            # else:
            # self.design_data['cBSummary'].append(
            # '{}xN {}xS {}xE'.format(self.design_data['cNBN'][i],
            # self.design_data['cNBS'][i],
            # self.design_data['cNBE'][i]))
            # else:
            if self.design_data['cNB'][i] != 0:
                self.design_data['cBSummary'].append(
                    '{}x{}s'.format(self.design_data['cNB'][i],
                                    self.design_data['cBdt'][i]))
            else:
                self.design_data['cBSummary'].append('No BOSS Science')

    @staticmethod
    def hartmann_parse(hart):
        output = '{}\n'.format(str(hart[0].times[-1])[:19])
        output += 'r1: {:>6.0f}, b1: {:>6.1f}\n'.format(
            hart[0].values[-1], hart[1].values[-1])
        # output += 'r2: {:>6.0f}, b2: {:>6.1f}\n'.format(
        #  hart[1].values[-1], hart[3].values[-1])
        output += 'Average Move: {:>6.0f}\n'.format(hart[2].values[-1])
        # output += 'SP1: {:>6.0f}, SP2: {:>6.0f}\n'.format(
        # hart[4].values[-1], hart[5].values[-1])
        output += 'R Residuals: {:>6.0f}\n'.format(hart[3].values[-1])
        # output += 'SP1: {:>6.0f}, SP2: {:>6.0f}\n'.format(
        # hart[10].values[-1], hart[11].values[-1])
        output += 'B Residuals: {:>6.1f}\n'.format(hart[4].values[-1])
        # output += 'SP1: {:>6.1f}, SP2: {:>6.1f}\n'.format(
        # hart[6].values[-1], hart[7].values[-1])
        output += 'SP1 Temperature: {:>6.1f}\n'.format(hart[5].values[-1])
        # output += 'SP1: {:>6.1f}, SP2: {:>6.1f}'.format(
        # hart[8].values[-1], hart[9].values[-1])
        return output

    def p_summary(self):
        print('=' * 80)
        print('{:^80}'.format('Observing Summary'))
        print('=' * 80)
        for i, design  in enumerate(self.data['dDesign']):
            print('')
            print("Design {}, {}, {}".format(design, self.data['dConfig'][i],
                                 self.design_data['cAPSummary'][i],
                                 self.design_data['cBSummary'][i]))
        print()
        if len(self.ap_data["fRatio"]) > 0:
            flux_ratio = np.nanmean(np.array(self.ap_data["fRatio"]), axis=0)
            avg = np.nanmean(flux_ratio)
            missing = flux_ratio < 0.2
            faint = (flux_ratio < 0.7) & (0.2 <= flux_ratio)
            bright = ~missing & ~faint
            i_missing = np.where(missing)[0].astype(int) + 1
            i_faint = np.where(faint)[0].astype(int) + 1
            i_bright = np.where(bright)[0]
            if self.ap_image is not None:
                missing_bundles = self.ap_image.create_bundles(i_missing)
                faint_bundles = self.ap_image.create_bundles(i_faint)
                print("APOGEE Dome Flats\n"
                    f"Missing Fibers: {missing_bundles}\n"
                    f" Faint fibers: {faint_bundles}\n"
                    f" Average Throughput: {avg:.3f}")
                print()

        print('### Notes:\n')
        start_time = Time(self.args.sjd, format="mjd")
        end_time = Time(self.args.sjd + 1, format="mjd")
        dust_sum = get_dust.get_dust(start_time, end_time, self.args.verbose)
        print('- Integrated Dust Counts: ~{:5.0f} dust-hrs'.format(
            dust_sum - dust_sum % 100))
        print('\n')

        # print('=' * 80)
        # print('{:^80}'.format('Comments Timeline'))
        # print('=' * 80)
        # print()

    @staticmethod
    def get_window(data, i):
        try:
            window = ((data['iTime']
                       >= data['dTime'][i])
                      & (data['iTime']
                         < data['dTime'][i + 1])
                      )

        except IndexError:
            try:
                window = ((data['iTime'] >= data['dTime'][i])
                          & (data['iTime'] < Time.now() + 0.3))
            except IndexError:
                window = np.array([False] * len(data['iTime']))

        return window

    def p_data(self):
        print('=' * 80)
        print('{:^80}'.format('Data Log'))
        print('=' * 80 + '\n')
        for i, design in enumerate(self.data['dDesign']):
            print('### Design {}\n'.format(design))
            if design  in self.ap_data['dDesign']:
                ap_design = np.where(design == self.ap_data['dDesign'])[0][0]

                print('# APOGEE')
                print('{:<5} {:<8} {:<8} {:<12} {:<4} {:<6} {:<5}'
                      ' {:<4}'.format('MJD', 'UTC', 'Exposure', 'Type',
                                      'Dith', 'Reads', 'Arch',
                                      'Seeing'))
                print('-' * 80)
                window = self.get_window(self.ap_data, ap_design)
                for (mjd, iso, exp_id, exp_type, dith, nread,
                     detectors, see) in zip(
                    self.ap_data['iTime'][window].mjd + 0.3,
                    self.ap_data['iTime'][window].iso,
                    self.ap_data['iID'][window],
                    self.ap_data['iEType'][window],
                    self.ap_data['iDither'][window],
                    self.ap_data['iNRead'][window],
                    self.ap_data['iDetector'][window],
                    self.ap_data['iSeeing'][window]
                ):
                    print('{:<5.0f} {:0>8} {:<8.0f} {:<12} {:<4} {:>5} {:<5}'
                          ' {:>4.1f}'.format(int(mjd), iso[11:19], exp_id,
                                             exp_type,
                                             dith, nread, detectors, see))
                print()
                if design in self.ap_data['dDesign']:
                    for j, dome in enumerate(self.ap_data['fDesign']):
                        if dome == design:
                            print(self.ap_data['fTime'][j].iso)
                            print(textwrap.fill('Missing fibers: {}'.format(
                                self.ap_data['fMissing'][j]), 80))
                            print(textwrap.fill('Faint fibers: {}'.format(
                                self.ap_data['fFaint'][j]), 80))
                            print()

            if design in self.b_data['dDesign']:
                print('# BOSS')
                print('{:<5} {:<8} {:<8} {:<7} {:<4} {:<11} {:<5} {:<5}'
                      ''.format('MJD', 'UTC', 'Exposure', 'Type',
                                'Dith', 'SOS', 'ETime', 'Hart'))
                print('-' * 80)
                # i is an index for data, but it will disagree with b_data
                # if there is an apogee-onlydesign 
                b_design = np.where(design == self.b_data['dDesign'])[0][0]
                window = self.get_window(self.b_data, b_design)
                for (mjd, iso, exp_id, exp_type, dith,
                     detectors, etime, hart) in zip(
                    self.b_data['iTime'][window].mjd + 0.3,
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
                          ''.format(int(mjd), iso[11:19], exp_id,
                                    exp_type.strip(),
                                    dith.strip(), detectors, etime,
                                    hart))
                try:
                    window = ((self.b_data['hTime']
                               >= self.data['dTime'][i])
                              & (self.b_data['hTime']
                                 < self.data['dTime'][i + 1])
                              )

                except IndexError:
                    window = ((self.b_data['hTime']
                               >= self.data['dTime'][i])
                              & (self.b_data['hTime'] < Time.now()))
                if self.b_data['hTime'][window]:
                    print()
                    # print('Hartmanns')
                for t, hart in zip(self.b_data['hTime'][window],
                                   self.b_data['hHart'][window]):
                    print(self.hartmann_parse(hart))
                print()

    def p_boss(self):
        print('=' * 80)
        print('{:^80}'.format('BOSS Data Summary'))
        print('=' * 80 + '\n')
        print('{:<5} {:<8} {:<13} {:<8} {:<7} {:<4} {:<11} {:<5} {:<5}'
              ''.format('MJD', 'UTC', 'Design-Config', 'Exposure', 'Type', 'Dith',
                        'SOS', 'ETime', 'Hart'))
        print('-' * 80)
        for (mjd, iso, design, design, config, exp_id, exp_type, dith, detectors, etime,
             hart) in zip(self.b_data['iTime'].mjd + 0.3,
                          self.b_data['iTime'].iso,
                          self.b_data['iDesign'],
                          self.b_data["iDesign"],
                          self.b_data['iConfig'],
                          self.b_data['iID'],
                          self.b_data['iEType'],
                          self.b_data['iDither'],
                          self.b_data['iDetector'],
                          self.b_data['idt'],
                          self.b_data['iHart']):
            print('{:<5.0f} {:>8} {:>6}-{:<6.0f} {:0>8.0f} {:<7} {:<4}'
                  ' {:<11}'
                  ' {:>5.0f} {:<5}'
                  ''.format(int(mjd), iso[11:19], design, config, exp_id,
                            exp_type.strip(),
                            dith.strip(), detectors, etime, hart))
        print()

    def p_apogee(self):
        print('=' * 80)
        print('{:^80}'.format('APOGEE Data Summary'))
        print('=' * 80 + '\n')
        print('{:<5} {:<8} {:<13} {:<8} {:<12} {:<4} {:<5} {:<5}'
              ''.format('MJD', 'UTC', 'Design-Config', 'Exposure', 'Type',
                              'Dith', 'Reads', 'Arch'))
        print('-' * 80)
        if self.args.morning:
            for (mjd, iso, design, config, exp_id, exp_type, dith, nread,
                 detectors) in zip(
                self.ap_data['iTime'].mjd[self.morning_filter] + 0.3,
                self.ap_data['iTime'].iso[self.morning_filter],
                self.ap_data["iDesign"][self.morning_filter],
                self.ap_data["iConfig"][self.morning_filter],
                self.ap_data['iID'][self.morning_filter],
                self.ap_data['iEType'][self.morning_filter],
                self.ap_data['iDither'][self.morning_filter],
                self.ap_data['iNRead'][self.morning_filter],
                self.ap_data['iDetector'][self.morning_filter],
            ):
                print('{:<5.0f} {:>8} {:>6.0f}-{:<6.0f} {:<8.0f} {:<12} {:<4}'
                      ' {:>5}'
                      ' {:<5}'
                      ''.format(int(mjd), iso[11:19], design, config,
                                         exp_id, exp_type,
                                         dith, nread, detectors))

        else:
            for (mjd, iso, design, config, exp_id, exp_type, dith, nread,
                 detectors) in zip(
                self.ap_data['iTime'].mjd,
                self.ap_data['iTime'].iso,
                self.ap_data["iDesign"],
                self.ap_data["iConfig"],
                self.ap_data['iID'], self.ap_data['iEType'],
                self.ap_data['iDither'], self.ap_data['iNRead'],
                self.ap_data['iDetector'],
            ):
                # print('{:<5.0f} {:>8} {:>2.0f}-{:<5.0f} {:<8.0f} {:<12} {:<4}'
                #       ' {:>6}'
                #       ' {:<8}'
                #       ' {:>6.1f}'.format(int(mjd), iso[11:19], design, plate,
                #                          exp_id, exp_type,
                #                          dith, nread, detectors, see))
                print('{:<5.0f} {:>8} {:>6.0f}-{:<6.0f} {:<8.0f} {:<12} {:<4}'
                      ' {:>5}'
                      ' {:<5}'
                      ''.format(int(mjd), iso[11:19], design, config,
                                         exp_id, exp_type,
                                         dith, nread, detectors))

        # Usually, there are 4 ThAr and 4 UNe arcs in a night, and they're
        # assumed to be alternating ThAr UNe ThAr UNe. When you grab every
        # other, you'll have only one type, that's the first slicing, and the
        # second slicing is that you only care about the diffs between two
        # dithers taken back to back.
        wrapper = textwrap.TextWrapper(80)
        thar_str = 'ThAr Offsets: {}'.format(
            ['{:.2f}'.format(f) for f in np.diff(
                self.ap_data['aOffset'][self.ap_data['aLamp'] == 'ThAr'])])
        print('\n'.join(wrapper.wrap(thar_str)))
        une_str = 'UNe Offsets: {}'.format(
            ['{:.2f}'.format(f) for f in np.diff(
                self.ap_data['aOffset'][self.ap_data['aLamp'] == 'UNe'])])
        print('\n'.join(wrapper.wrap(une_str)))
        if len(self.ap_data['oOffset']) > 1:
            # Put it under an if in case we didn't open.
            rel_offsets = np.abs(np.diff(self.ap_data['oOffset']))
            obj_str = ('Object Offsets: Max: {:.2f}, Min: {:.2f}, Mean: {:.2f}'
                       ''.format(rel_offsets.max(), rel_offsets.min(),
                                 rel_offsets.mean()))
            # ['{:>6.3f}'.format(f) for f in np.diff(
            #     self.ap_data['oOffset'])])
            print('\n'.join(wrapper.wrap(obj_str)))
        # obj_offsets = []
        # prev_dither = None
        # prev_f = 0.
        # for d, f in zip(self.ap_data['oDither'], self.ap_data['oOffset']):
        #     if d != prev_dither:
        #         obj_offsets.append('{:.3f}'.format(f - prev_f))
        #     prev_dither = d
        #     prev_f = f
        # obj_str = 'Object Offsets: {}'.format(obj_offsets)
        print('\n')

    def log_support(self):
        print('=' * 80)
        print(f"{'Log Support':^80}")
        print('=' * 80)
        start = Time(self.args.sjd - 0.3, format='mjd')
        end = Time(self.args.sjd + 1, format='mjd') - 0.3
        end = Time.now() if Time.now() < end else end
        tel = log_support.LogSupport(start, end, self.args)
        tel.set_callbacks()
        tel.get_offsets()
        tel.get_focus()
        tel.get_weather()
        tel.get_hartmann()
        print(tel.offsets)
        print(tel.focus)
        print(tel.weather)
        print(tel.hartmann)

    @staticmethod
    def mirror_numbers():
        print('=' * 80)
        print('{:^80}'.format('Mirror Numbers'))
        print('=' * 80 + '\n')
        try:
            mirror_nums = m4l.mirrors()
            print(mirror_nums)
        except (ConnectionRefusedError, TimeoutError) as me:
            print('Could not fetch mirror numbers:\n{}'.format(me))

    @staticmethod
    def tel_status():
        print('=' * 80)
        print('{:^80}'.format('Telescope Status'))
        print('=' * 80 + '\n')
        try:
            status = telescope_status.query()
            print(status)
        except OSError as oe:
            print(f"Couldn't get telescope status:\n{oe}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--today', action='store_true', default=True,
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 18:00Z to get the"
                             " correct sjd")
    parser.add_argument('-m', '--mjd', type=int,
                        help='If not today (-t), the mjd to search (actually'
                             ' sjd)')
    parser.add_argument('--mirrors', '--mirror', action='store_true',
                        help='Print mirror numbers using m4l.py')
    parser.add_argument("-s", '--summary', help='Print the data summary',
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
    parser.add_argument("-t", '--telstatus', action='store_true',
                        help='Print telescope status')
    parser.add_argument('--morning', action='store_true',
                        help='Only output apogee morning cals')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increased printing for debugging')
    parser.add_argument('--legacy-aptest', action='store_true',
                        help='Use utr_cdr images for aptest instead of'
                             ' quickred for the ap_test')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if args.mjd:
        args.sjd = args.mjd
    elif args.today:
        args.sjd = sjd.sjd()
    else:
        raise argparse.ArgumentError(args.sjd,
                                     'Must provide -t or -m in arguments')
    if args.verbose:
        print(args.sjd)
    ap_data_dir = ap_dir / '{}'.format(args.sjd)
    b_data_dir = b_dir / '{}'.format(args.sjd)
    ap_images = Path(ap_data_dir).glob('apR-a*.apz')
    b_images = Path(b_data_dir).glob('sdR-r1*fit.gz')

    if not args.noprogress:
        try:
            ap_images = list(ap_images)
            b_images = list(b_images)
        except OSError:  # Stale NFS handle
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
        # args.log_support = True  # Because this usually produces wrong results
        args.mirrors = True
        args.telstatus = True

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

    if p_apogee:
        log.p_apogee()

    if p_boss:
        log.p_boss()

    if args.log_support:
        log.log_support()

    if args.mirrors:
        pass
        # log.mirror_numbers()

    if args.telstatus:
        log.tel_status()
    return log


if __name__ == '__main__':
    main()
