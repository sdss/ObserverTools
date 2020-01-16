"""A script to automate the bulk of logging and to replace log-function with
 a callback-free structure. This code is entirely dependent on raw images
 and their headers, unlike Log Function which is dependent on callbacks it
 catches while active, which are subject to crashes, unlike other files in
 time tracking with use the sdss python package

The intent of this is to create a more future-proof tool for logging through
Sloan V

2019-11-01      dgatlin     init, in response to some issues with gcam
    tracking and identifying slew errors
2019-12-13      dgatlin     This has received a lot of work and can now
    build a data log and some summary
"""
import argparse
import datetime
import warnings
import subprocess as sub
import sys
import numpy as np
try:
    import starcoder42 as s
except ImportError:
    sys.path.append('/Users/dylangatlin/python/')
    sys.path.append('/home/gatlin/python/')
    import starcoder42 as s
try:
    from astropy.time import Time
except ImportError:
    raise s.GatlinError('Astropy not found for interpreter\n'
                        '{}'.format(sys.executable))
try:
    import fitsio
except ImportError:
    raise s.GatlinError('fitsio not found by interpreter\n'
                        '{}'.format(sys.executable))
from pathlib import Path
from tqdm import tqdm
# from multiprocessing import Process

import log_apogee
import log_manga


# For astropy
warnings.filterwarnings('ignore', category=UserWarning, append=True)


class Schedule:
    def __init__(self, ap_images, m_images, mjd, args):
        self.ap_images = ap_images
        self.m_images = m_images
        self.mjd = mjd
        self.args = args
        # Variables that begin with carts have len of the number of carts in
        # that night. Variables that begin with img have len nimages
        self.data = {'cCart': [], 'cTime': [], 'cPlate': [], 'cLead': []}
        # If there is a cart without dome flats, then dome data may not be
        # of the same shape as cart data, so it needs its own prefix and dic
        self.dome_data = {'dMissing':[], 'dFaint': [], 'dNMissing': [],
                          'dNFaint': [], 'dCart': [], 'dTime': []}
        self.ap_data = {'cCart': [], 'cTime': [],
                        'iTime': [], 'iID': [],
                        'iSeeing': [], 'iDetector': [], 'iDither': [],
                        'iNRead': [], 'iEType': [], 'iCart': []}
        self.m_data = {'cCart': [], 'cTime': [],
                       'iTime': [], 'iID': [],
                       'iDetector': [], 'iDither': [],
                       'iEType': [], 'iExdt': [], 'iCart': [], 'iHart': []}
        # These values are not known from the header and must be created
        # after self.sort.
        self.cart_data = {'cNAPA': [], 'cNAPB': [], 'cNMN': [], 'cNMS': [],
                          'cNME': [], 'cNMC': [], 'cAPSummary': [],
                          'cMSummary': []}
        self.test_procs = []

    def ap_test(self, img):
        test = sub.Popen('ssh observer@sdss-hub "~/bin/aptest {} {}"'
                         ''.format(self.mjd, img.exp_id), shell=True,
                         stdout=sub.PIPE)
        lines = test.stdout.read().split(b'\n')[3:]
        missing = eval(lines[0].split(b'Missing fibers: ')[-1])
        faint = eval(lines[1].split(b'Faint fibers:   ')[-1])
        n_missing = 0
        n_faint = 0
        for miss in missing:
            if isinstance(miss, bytes) or isinstance(miss, str):
                n_missing += abs(eval(miss))
            else:
                n_missing += 1
        for fain in faint:
            if isinstance(fain, bytes) or isinstance(fain, str):
                n_faint += np.abs(eval(fain))
            else:
                n_faint += 1
        # return (n_missing, n_faint, missing, faint, img.cart_id,
        #         img.datetimet)
        self.dome_data['dNMissing'].append(n_missing)
        self.dome_data['dNFaint'].append(n_faint)
        self.dome_data['dMissing'].append(missing)
        self.dome_data['dFaint'].append(faint)
        self.dome_data['dCart'].append(img.cart_id)
        self.dome_data['dTime'].append(img.datetimet)

    def parse_images(self):
        """Goes through every image in ap_images and m_images to put them in
        dictionaries."""
        print('Reading APOGEE Data')
        for image in tqdm(list(self.ap_images)):
            # print(image)
            img = log_apogee.APOGEERaw(image, 1)
            # img.parse_layer(1)
            if not img.plate_id: # If the first exposure is still
                # writing, plate_id will be empty and without this if,
                # it would fail. With this if, it will skip the plate
                continue
            if img.exp_type == 'DOMEFLAT':
                if img.cart_id not in self.dome_data['dCart']:
                    self.ap_test(img)
                    self.test_procs.append(img.cart_id)

            if img.cart_id not in self.data['cCart']:
                
                self.data['cPlate'].append(img.plate_id)
                self.data['cCart'].append(img.cart_id)
                self.data['cTime'].append(img.datetimet)
                self.data['cLead'].append(img.lead)
            else:
                i = self.data['cCart'].index(img.cart_id)
                if img.datetimet < self.data['cTime'][i]:
                    self.data['cTime'].pop(i)
                    self.data['cTime'].insert(i, img.datetimet)
            if img.cart_id not in self.ap_data['cCart']:
                self.ap_data['cCart'].append(img.cart_id)
                self.ap_data['cTime'].append(img.datetimet)
            else:
                i = self.ap_data['cCart'].index(img.cart_id)
                if img.datetimet < self.ap_data['cTime'][i]:
                    self.ap_data['cTime'].pop(i)
                    self.ap_data['cTime'].insert(i, img.datetimet)
            detectors = []
            if image.exists():
                detectors.append('a')
            else:
                detectors.append('x')
            if (image.parent / image.name.replace('-a-', '-b-')).exists():
                detectors.append('b')
            else:
                detectors.append('x')
            if (image.parent / image.name.replace('-a-', '-c-')).exists():
                detectors.append('c')
            else:
                detectors.append('x')
            self.ap_data['iTime'].append(img.datetimet)
            self.ap_data['iID'].append(img.exp_id)
            self.ap_data['iSeeing'].append(img.seeing)
            self.ap_data['iDetector'].append('-'.join(detectors))
            self.ap_data['iDither'].append(img.dither)
            self.ap_data['iNRead'].append(img.n_read)
            self.ap_data['iEType'].append(img.exp_type)
            self.ap_data['iCart'].append(img.cart_id)
        
        print('Reading MaNGA Data')
        for image in tqdm(list(self.m_images)):
            img = log_manga.MaNGARaw(image)
            if img.cart_id not in self.data['cCart']:
                self.data['cCart'].append(img.cart_id)
                self.data['cPlate'].append(img.plate_id)
                self.data['cLead'].append(img.lead)
                self.data['cTime'].append(img.datetimet)
            else:
                i = self.data['cCart'].index(img.cart_id)
                if img.datetimet < self.data['cTime'][i]:
                    self.data['cTime'].pop(i)
                    self.data['cTime'].insert(i, img.datetimet)
            if img.cart_id not in self.m_data['cCart']:
                self.m_data['cCart'].append(img.cart_id)
                self.m_data['cTime'].append(img.datetimet)
            else:
                i = self.m_data['cCart'].index(img.cart_id)
                if img.datetimet < self.m_data['cTime'][i]:
                    self.m_data['cTime'].pop(i)
                    self.m_data['cTime'].insert(i, img.datetimet)
            self.m_data['iTime'].append(img.datetimet)
            self.m_data['iID'].append(img.exp_id)
            # self.m_data['iSeeing'].append(img.seeing)
            self.m_data['iDither'].append(img.dither)
            self.m_data['iEType'].append(img.flavor)
            self.m_data['iExdt'].append(img.exp_time)
            self.m_data['iCart'].append(img.cart_id)
            self.m_data['iHart'].append(img.hartmann)

            m_detectors = []
            if image.exists():
                m_detectors.append('r1')
            else:
                m_detectors.append('xx')
            if (image.parent / image.name.replace('r1', 'b1')).exists():
                m_detectors.append('b1')
            else:
                m_detectors.append('xx')
            if (image.parent / image.name.replace('r1', 'r2')).exists():
                m_detectors.append('r2')
            else:
                m_detectors.append('xx')
            if (image.parent / image.name.replace('r1', 'b2')).exists():
                m_detectors.append('b2')
            else:
                m_detectors.append('xx')
            self.m_data['iDetector'].append('-'.join(m_detectors))
    
    def sort(self):
        """Sorts self.ap_data by cart time and by image time and converts to
        arrays"""
        for key, item in self.ap_data.items():
            if 'Time' in key:
                self.ap_data[key] = Time(item)
            else:
                self.ap_data[key] = np.array(item)
        for key, item in self.m_data.items():
            if 'Time' in key:
                self.m_data[key] = Time(item)
            else:
                self.m_data[key] = np.array(item)
        ap_cart_sorter = self.ap_data['cTime'].argsort()
        ap_img_sorter = self.ap_data['iTime'].argsort()
        m_cart_sorter = self.m_data['cTime'].argsort()
        m_img_sorter = self.m_data['iTime'].argsort()
        for key, item in self.ap_data.items():
            if key[0] == 'c':
                self.ap_data[key] = item[ap_cart_sorter]
            elif key[0] == 'i':
                self.ap_data[key] = item[ap_img_sorter]
        for key, item in self.m_data.items():
            if key[0] == 'c':
                self.m_data[key] = item[m_cart_sorter]
            elif key[0] == 'i':
                self.m_data[key] = item[m_img_sorter]
        for key, item in self.data.items():
            if 'Time' in key:
                self.data[key] = Time(item)
                data_sort = self.data[key].argsort()
            else:
                self.data[key] = np.array(item)
        for key, item in self.data.items():
            # print(key, item)
            self.data[key] = item[data_sort]
        # print(self.test_procs)
        # print(self.dome_data['dTime'], self.dome_data['dNMissing'])
        if self.dome_data['dTime']:
            for key, item in self.dome_data.items():
                if 'Time' in key:
                    self.dome_data[key] = Time(item)
                    data_sort = self.dome_data[key].argsort()
                else:
                    self.dome_data[key] = np.array(item)

    def count_dithers(self):
        for i, cart in enumerate(self.data['cCart']):
            # print(self.ap_data['iCart'], cart)
            # print(self.ap_data['iCart'] == cart)
            # print(self.ap_data['iDither'])
            # print(self.ap_data['iDither'] == 'A')
            self.cart_data['cNAPA'].append(np.sum((
                (self.ap_data['iCart'] == cart)
                & (self.ap_data['iDither'] == 'A'))
                & (self.ap_data['iEType'] == 'OBJECT')))
            self.cart_data['cNAPB'].append(np.sum(
                (self.ap_data['iCart'] == cart)
                & (self.ap_data['iDither'] == 'B')
                & (self.ap_data['iEType'] == 'OBJECT')))
            self.cart_data['cNMN'].append(np.sum(
                (self.m_data['iCart'] == cart)
                & (self.m_data['iDither'] == 'N')
                & (self.m_data['iEType'] == 'science')))
            self.cart_data['cNMS'].append(np.sum(
                (self.m_data['iCart'] == cart)
                & (self.m_data['iDither'] == 'S')
                & (self.m_data['iEType'] == 'science')))
            self.cart_data['cNME'].append(np.sum(
                (self.m_data['iCart'] == cart)
                & (self.m_data['iDither'] == 'E')
                & (self.m_data['iEType'] == 'science')))
            self.cart_data['cNMC'].append(np.sum(
                (self.m_data['iCart'] == cart)
                & (self.m_data['iDither'] == 'C')
                & (self.m_data['iEType'] == 'science')))
        for i, cart in enumerate(self.data['cCart']):
            if self.cart_data['cNAPA'][i] == self.cart_data['cNAPB'][i]:
                self.cart_data['cAPSummary'].append(
                    '{}xAB'.format(self.cart_data['cNAPA'][i]))
            else:
                self.cart_data['cAPSummary'].append(
                    '{}xA {}xB'.format(self.cart_data['cNAPA'][i],
                                       self.cart_data['cNAPB'][i]))
            if self.cart_data['cNMC'][i] == 0:
                if (self.cart_data['cNMN'][i]
                    == self.cart_data['cNMS'][i]
                    == self.cart_data['cNME'][i]):
                    self.cart_data['cMSummary'].append(
                        '{}xNSE'.format(self.cart_data['cNMN'][i]))
                else:
                    self.cart_data['cMSummary'].append(
                        '{}xN {}xS {}xE'.format(self.cart_data['cNMN'][i],
                                                self.cart_data['cNMS'][i],
                                                self.cart_data['cNME'][i]))
            else:
                self.cart_data['cMSummary'].append(
                    '{}xC'.format(self.cart_data['cNMC'][i]))


    def print_data(self):
        if self.args.summary:
            print('='*80)
            print('{:^80}'.format('Observing Summary'))
            print('='*80)
            for i, cart in enumerate(self.data['cCart']):
                print('')
                print('Cart {}, plate {}, {}'
                      ', {},'.format(cart, self.data['cPlate'][i],
                                    self.cart_data['cAPSummary'][i],
                                    self.cart_data['cMSummary'][i]))
                try:
                    j = np.where(self.dome_data['dCart'] == cart)[0][0]
                    print('Missing Fibers: {}, Faint fibers: {}'.format(
                        self.dome_data['dNMissing'][j],
                        self.dome_data['dNFaint'][j]))
                except IndexError:
                    pass
            print('')
            print('')
        if self.args.data:
            print('='*80)
            print('{:^80}'.format('Data Log'))
            print('='*80)
            for i, cart in enumerate(self.data['cCart']):
                print('')
                print('')
                print('# Cart {}, Plate {}, {}'.format(cart,
                    self.data['cPlate'][i], self.data['cLead'][i]))
                print('# GSOGTF, ===INSERT WEATHER CONDITIONS===')
                print('# APOGEE')
                print('{:<5} {:<8} {:<8} {:<12} {:<4} {:<6} {:<9}'
                      ' {:<4}'.format('MJD', 'UTC', 'Exposure', 'Type',
                                      'Dith', 'nReads', 'Detectors',
                                      'Seeing'))
                print('='*80)
                try:
                    window = ((self.ap_data['iTime']
                              >= self.data['cTime'][i])
                              & (self.ap_data['iTime']
                                 < self.data['cTime'][i+1])
                              )
                
                except IndexError:
                    window = ((self.ap_data['iTime']
                              >= self.data['cTime'][i])
                              & (self.ap_data['iTime'] < Time.now()))
                for (mjd, iso, exp_id, exp_type, dith, nread,
                     detectors, see) in zip(
                    self.ap_data['iTime'][window].mjd,
                    self.ap_data['iTime'][window].iso,
                    self.ap_data['iID'][window],
                    self.ap_data['iEType'][window],
                    self.ap_data['iDither'][window],
                    self.ap_data['iNRead'][window],
                    self.ap_data['iDetector'][window],
                    self.ap_data['iSeeing'][window]
                ):
                    print('{:<5.0f} {:<8} {:<8.0f} {:<12} {:<4} {:<6} {:<9}'
                          ' {:<4.1f}'.format(mjd, iso[12:19], exp_id,
                                             exp_type,
                                             dith, nread, detectors, see))
                if self.data['cCart'][i] in self.dome_data['dCart']:
                    try:
                        j = np.where(self.dome_data['dCart'] == cart)[0][0]
                    except IndexError:
                        pass
                    print('Missing fibers:'
                          '{}'.format(self.dome_data['dMissing'][j]))
                    print('Faint fibers:'
                          '{}'.format(self.dome_data['dFaint'][j]))
                if cart <= 6:
                    print('')
                    print('# MaNGA')
                    print('{:<5} {:<8} {:<8} {:<7} {:<4} {:<11} {:<5} {:<5}'
                          ''.format('MJD', 'UTC', 'Exposure', 'Type',
                                    'Dith', 'Detectors', 'ETime', 'Hart'))
                    print('='*80)
                    try:
                        window = ((self.m_data['iTime']
                                   >= self.data['cTime'][i])
                                  & (self.m_data['iTime']
                                     < self.data['cTime'][i+1])
                                  )
                    
                    except IndexError:
                        window = ((self.m_data['iTime']
                                   >= self.data['cTime'][i])
                                  & (self.m_data['iTime'] < Time.now()))
                    for (mjd, iso, exp_id, exp_type, dith,
                         detectors, etime, hart) in zip(
                        self.m_data['iTime'][window].mjd,
                        self.m_data['iTime'][window].iso,
                        self.m_data['iID'][window],
                        self.m_data['iEType'][window],
                        self.m_data['iDither'][window],
                        self.m_data['iDetector'][window],
                        self.m_data['iExdt'][window],
                        self.m_data['iHart'][window],
                    ):
                        print('{:<5.0f} {:<8} {:<8.0f} {:<7} {:<4} {:<11}'
                               ' {:<5.0f} {:<5}'
                               ''.format(mjd, iso[12:19], exp_id,
                                         exp_type.strip(),
                                         dith.strip(), detectors, etime,
                                         hart))
                    print('====HARTMANN====')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true',
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 00:00Z")
    parser.add_argument('-m', '--mjd',
                       help='If not today (-t), the mjd to search')
    parser.add_argument('-s', '--summary', help='Print the data summary',
            action='store_true')
    parser.add_argument('-d', '--data', action='store_true',
            help='Print the data log')
    parser.add_argument('-p', '--print', action='store_true',
            help='Print all possible outputs')
    args = parser.parse_args()
    if args.print:
        args.data = True
        args.summary = True
    if args.today:
        now = datetime.datetime.now()
        mjd = int(Time(now).mjd)
    elif args.mjd:
        mjd = args.mjd
    else:
        raise s.GatlinError('Must provide -t or -m in arguments')
    
    ap_data_dir = '/data/apogee/archive/{}/'.format(mjd)
    ma_data_dir = '/data/spectro/{}/'.format(mjd)
    ap_images = Path(ap_data_dir).glob('apR-a*.apz')
    m_images = Path(ma_data_dir).glob('sdR-r1*fit.gz')


    schedule = Schedule(ap_images, m_images, mjd, args)
    schedule.parse_images()
    schedule.sort()
    schedule.count_dithers()
    if not args.summary or args.data:
        schedule.print_data()


if __name__ == '__main__':
    main()
