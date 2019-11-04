#!/usr/bin/env python
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

import numpy as np
from astropy.time import Time
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
        self.data = {'cCart': []}
        self.ap_data = {'cCart': [], 'cTime': [],
                        'iTime': [], 'iID': [],
                        'iSeeing': [], 'iDetector': [], 'iDither': [],
                        'iNRead': [], 'iEType': [], }
        self.m_data = {'cCart': [], 'cTime': [],
                       'iTime': [], 'iID': [],
                       'iSeeing': [], 'iDetector': [], 'iDither': [],
                       'iNRead': [], 'iEType': [], }

    def parse_images(self):
        """Goes through every image in ap_images and m_images to put them in
        dictionaries."""
        print('Reading APOGEE Data')
        for image in tqdm(self.ap_images):
            # print(image)
            img = apogee.APOGEERaw(image, 1)
            # img.parse_layer(1)
            if img.cart_id not in self.data['Cart']:
                self.data['cCart'].append(img.cart_id)
                self.data['cTime'].append(img.datetimet)
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
            if (image.parent / image.name.replace('-a-', '-b-')).exists():
                detectors.append('b')
            if (image.parent / image.name.replace('-a-', '-c-')).exists():
                detectors.append('c')
            self.ap_data['iTime'].append(img.datetimet)
            self.ap_data['iID'].append(img.exp_id)
            self.ap_data['iSeeing'].append(img.seeing)
            self.ap_data['iDetector'].append(detectors)
            self.ap_data['iDither'].append(img.seeing)
            self.ap_data['iNRead'].append(img.n_read)
            self.ap_data['iEType'].append(img.exp_type)

        print('Reading MaNGA Data')
        for image in tqdm(self.m_images):
            img = manga.MaNGARaw(image, 1)
            if img.cart_id not in self.data['Cart']:
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
    
    def sort(self):
        """Sorts self.ap_data by cart time and by image time and converts to
        arrays"""
        for key, item in self.ap_data.iteritems():
            if 'Time' in key:
                self.ap_data[key] = Time(item)
            else:
                self.ap_data[key] = np.array(item)
        cart_sorter = self.ap_data['cTime'].argsort()
        img_sorter = self.ap_data['iTime'].argsort()
        for key, item in self.ap_data.iteritems():
            if key[0] == 'c':
                self.ap_data[key] = item[cart_sorter]
            elif key[1] == 'i':
                self.ap_data[key] = item[img_sorter]

    def print_data(self):
        print('-'*80)
        print('{:^80}'.format('Data Summary'))
        print('-'*80)
        print('')
        for i, cart in enumerate(self.ap_data['cCart']):
            print('')
            print('# Cart {}'.format(cart))
            print('# APOGEE')
            print('MJD   UTC     Exp       Exp Type Dith Nreads Detectors'
                  ' Seeing')
            print('-'*80)
            try:
                window = ((self.ap_data['iTime'] < self.ap_data['cTime'][i])
                          & (self.ap_data['iTime'] < self.ap_data['cTime'][i+1])
                          )
            except IndexError:
                window = ((self.ap_data['iTime'] < self.ap_data['cTime'][i])
                          & (self.ap_data['iTime'] < Time.now()))
            for mjd, iso, exp_id, exp_type, dith, nread, detectors, see in zip(
                self.ap_data['iTime'][window].mjd,
                self.ap_data['iTime'][window].iso, self.ap_data['iID'][window],
                self.ap_data['iEType'],
                self.ap_data['iDither'][window], self.ap_data['iNRead'][window],
                self.ap_data['iDetector'][window],
                self.ap_data['iSeeing'][window]
            ):
                print('{:<5.0f} {} {:<9.0f} {:8} {:4} {:<6}'.format(mjd,
                      iso[12:19], exp_id, exp_type, dith, nread)
                      + ' {}-{}-{}    '.format(*detectors)
                      + ' {}'.format(see))
            print('')
            print('\nMaNGA')


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
        mjd_today = int(Time(now).mjd)
        ap_data_dir = '/data/apogee/archive/{}/'.format(mjd_today)
        ma_data_dir = '/data/spectro/{}/'.format(mjd_today)
        ap_images = Path(ap_data_dir).glob('apR-a*.apz')
        m_images = Path(ma_data_dir).glob('*fit.gz')
    elif args.mjd:
        ap_data_dir = '/data/apogee/archive/{}/'.format(args.mjd)
        ma_data_dir = '/data/spectro/{}/'.format(args.mjd)
        ap_images = Path(ap_data_dir).glob('apR-a*.apz')
        m_images = Path(ma_data_dir).glob('*fit.gz')
    else:
        raise s.GatlinError('Must provide -t or -m in arguments')
    
    schedule = Schedule(ap_images, m_images)
    schedule.parse_images()
    schedule.sort()
    schedule.print_data()


if __name__ == '__main__':
    main()
