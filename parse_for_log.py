"""A script to automate the bulk of logging and to replace log-function with
a callback-free structure. This code is entirely dependent on raw images and
their headers, unlike Log Function which is dependent on callbacks it catches
while active, which are subject to crashes.

The intent of this is to create a more future-proof tool for logging through
Sloan V

2019-11-01      dgatlin     init, in response to some issues with gcam tracking
    and identifying slew errors
"""
import argparse
import datetime
import warnings
import subprocess as sub
import numpy as np
try:
    from astropy.io import fits
    from astropy.time import Time
except ImportError:
    raise s.GatlinError('Astropy not found')
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

from pathlib import Path
from tqdm import tqdm

import apogee
import manga

import starcoder42 as s

# For astropy
warnings.filterwarnings('ignore', category=UserWarning, append=True)

class Schedule:
    def __init__(self, ap_images, m_images):
        self.ap_images = ap_images
        self.m_images = m_images
        # Variables that begin with carts have len of the number of carts in
        # that night. Variables that begin with img have len nimages
        self.data = {'cCart': [], 'cTime': [], 'cPlate': [], 'cMissing':[],
                     'cFaint': [], 'cNMissing': [], 'cNFaint': [],
                     'cTestCart': []}
        self.ap_data = {'cCart': [], 'cTime': [],
                        'iTime': [], 'iID': [],
                        'iSeeing': [], 'iDetector': [], 'iDither': [],
                        'iNRead': [], 'iEType': [], }
        self.m_data = {'cCart': [], 'cTime': [],
                       'iTime': [], 'iID': [],
                       'iDetector': [], 'iDither': [],
                       'iEType': [], 'iExdt': []}
    def ap_test(self, mjd, imid):
        test = sub.Popen('ssh observer@sdss-hub "~/bin/aptest {} {}"'
                         ''.format(mjd, imid), shell=True, stdout=sub.PIPE)
        lines = test.stdout.read().split('\n')[3:]
        missing = eval(lines[0].split('Missing fibers: ')[-1])
        faint = eval(lines[1].split('Faint fibers:   ')[-1])
        n_missing = 0
        n_faint = 0
        for miss in missing:
            if isinstance(miss, str):
                n_miss += abs(eval(miss))
            else:
                n_missing += 1
        for fain in faint:
            if isinstance(miss, str):
                n_faint += abs(eval(fain))
            else:
                n_faint += 1
        return n_missing, n_faint, missing, faint

    def parse_images(self):
        """Goes through every image in ap_images and m_images to put them in
        dictionaries."""
        print('Reading APOGEE Data')
        for image in list(self.ap_images):
            # print(image)
            img = apogee.APOGEERaw(image, 1)
            # img.parse_layer(1)
            if img.cart_id not in self.data['cCart']:
                self.data['cCart'].append(img.cart_id)
                self.data['cTime'].append(img.datetimet)
                self.data['cPlate'].append(img.plate_id)
                print(img.cart_id)
            else:
                i = self.data['cCart'].index(img.cart_id)
                if img.datetimet < self.data['cTime'][i]:
                    self.data['cTime'].pop(i)
                    self.data['cTime'].insert(i, img.datetimet)
            if img.exp_type == 'DOMEFLAT':
                if img.cart_id not in self.data['cTestCart']:
                    print(img.cart_id)
                    test = self.ap_test(self.mjd, img.exp_id)
                    self.data['cNMissing'].append(test[0])
                    self.data['cNFaint'].append(test[1])
                    self.data['cMissing'].append(test[2])
                    self.data['cFaint'].append(test[3])
                    self.data['cTestCart'].append(img.cart_id)

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

        print('Reading MaNGA Data')
        for image in tqdm(list(self.m_images)):
            img = manga.MaNGARaw(image, 0)
            if img.cart_id not in self.data['cCart']:
                self.data['cCart'].append(img.cart_id)
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
            self.m_data['iDetector'].append('-'.join(detectors))
            self.m_data['iDither'].append(img.dither)
            self.m_data['iEType'].append(img.flavor)
            self.m_data['iExdt'].append(img.exp_time)

            detectors = []
            if image.exists():
                detectors.append('r1')
            else:
                detectors.append('xx')
            if (image.parent / image.name.replace('r1', 'b1')).exists():
                detectors.append('b1')
            else:
                detectors.append('xx')
            if (image.parent / image.name.replace('r1', 'r2')).exists():
                detectors.append('r2')
            else:
                detectors.append('xx')
            if (image.parent / image.name.replace('r1', 'b2')).exists():
                detectors.append('b2')
            else:
                detectors.append('xx')
            self.m_data['iDetector'].append('-'.join(detectors))
    
    def sort(self):
        """Sorts self.ap_data by cart time and by image time and converts to
        arrays"""
        for key, item in self.ap_data.iteritems():
            if 'Time' in key:
                self.ap_data[key] = Time(item)
            else:
                self.ap_data[key] = np.array(item)
        for key, item in self.m_data.iteritems():
            if 'Time' in key:
                self.m_data[key] = Time(item)
            else:
                self.m_data[key] = np.array(item)
        ap_cart_sorter = self.ap_data['cTime'].argsort()
        ap_img_sorter = self.ap_data['iTime'].argsort()
        m_cart_sorter = self.m_data['cTime'].argsort()
        m_img_sorter = self.m_data['iTime'].argsort()
        for key, item in self.ap_data.iteritems():
            if key[0] == 'c':
                self.ap_data[key] = item[ap_cart_sorter]
            elif key[0] == 'i':
                self.ap_data[key] = item[ap_img_sorter]
        for key, item in self.m_data.iteritems():
            if key[0] == 'c':
                self.m_data[key] = item[m_cart_sorter]
            elif key[0] == 'i':
                self.m_data[key] = item[m_img_sorter]
        for key, item in self.data.iteritems():
            if 'Time' in key:
                self.data[key] = Time(item)
                data_sort = self.data[key].argsort()
            else:
                self.data[key] = np.array(item)
        for key, item in self.data.iteritems():
            print((key), len(item), len(self.data['cTime']))
            self.data[key] = item[data_sort]

    def print_data(self):
        print('-'*80)
        print('{:^80}'.format('Data Summary'))
        print('-'*80)
        print('')
        for i, cart in enumerate(self.data['cCart']):
            print('')
            print('')
            print('# Cart {}, Plate {}'.format(cart,
                self.data['cPlate'][i]))
            print('# APOGEE')
            print('{:<5} {:<8} {:<8} {:<10} {:<4} {:<6} {:<7}'
                  ' {:<4}'.format('MJD', 'UTC', 'Exposure', 'Type', 'Dith',
                                  'nReads', 'Detectors', 'Seeing'))
            print('-'*80)
            try:
                window = ((self.ap_data['iTime'] >= self.data['cTime'][i])
                          & (self.ap_data['iTime'] < self.data['cTime'][i+1])
                          )
            
            except IndexError:
                window = ((self.ap_data['iTime'] >= self.data['cTime'][i])
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
                     print('{:<5.0f} {:<8} {:<8.0f} {:<10} {:<4} {:<6}'
                           ' {:<7} {:<4.1f}'.format(mjd, iso[12:19], exp_id,
                                                    exp_type, dith, nread,
                                                    detectors, see))
            if cart <= 6:
                print('')
                print('# MaNGA')
                print('{:<5} {:<8} {:<8} {:<7} {:<4} {:<11} {:<5}'
                      ''.format('MJD', 'UTC', 'Exposure', 'Type', 'Dith',
                                      'Sensors', 'ETime'))
                print('-'*80)
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
                     detectors, etime) in zip(
                    self.m_data['iTime'][window].mjd,
                    self.m_data['iTime'][window].iso,
                    self.m_data['iID'][window],
                    self.m_data['iEType'][window],
                    self.m_data['iDither'][window],
                    self.m_data['iDetector'][window],
                    self.m_data['iExdt'][window],
                ):
                         print('{:<5.0f} {:<8} {:<8.0f} {:<7} {:<4}'
                                 ' {:<11} {:<5.0f}'.format(mjd, iso[12:19], exp_id,
                                                        exp_type, dith,
                                                        detectors, etime))
            print('Missing fibers: {}'.format(self.data['cMissing'][i]))
            print('Faint fibers: {}'.format(self.data['cFaint'][i]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true',
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 00:00Z")
    parser.add_argument('-m', '--mjd',
                       help='If not today (-t), the mjd to search')
    args = parser.parse_args()
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

    
    schedule = Schedule(ap_images, m_images)
    schedule.mjd = mjd
    schedule.parse_images()
    schedule.sort()
    schedule.print_data()


if __name__ == '__main__':
    main()
