#!/usr/bin/env python
"""A script to automate the bulk of logging and to replace log-function with
a callback-free structure. This code is entirely dependent on raw images and
their headers, unlike Log Function which is dependent on callbacks it catches
while active, which are subject to crashes.

The intent of this is to create a more future-proof tool for logging through
Sloan V
"""
# Standart plain
import argparse
import datetime
import warnings
# Standard as
import numpy as np
# Standard from
# from pathlib import Path
from astropy.time import Time
import glob
# Local imports
import apogee
# import manga
warnings.filterwarnings('ignore', category=UserWarning, append=True)


class Schedule:
    def __init__(self, ap_images, m_images):
        self.ap_images = ap_images
        self.m_images = m_images
        # Variables that begin with carts have len of the number of carts in
        # that night. Variables that begin with img have len nimages
        self.carts = []
        self.cart_start_times = []
        self.img_ap = []
        # self.img_ap['Time'] = [] # TODO Convert all of these to dict elements
        self.img_ap_times = []
        self.img_ap_ids = []
        self.img_ap_seeings = []
        self.img_ap_detectors = []
        self.img_ap_ids = []
        self.img_ap_dithers = []
        self.img_ap_n_reads = []

    def parse_images(self):
        for image in self.ap_images:
            print(image)
            img = apogee.APOGEERaw(image, 1)
            # img.parse_layer(1)
            if img.cart_id not in self.carts:
                self.carts.append(img.cart_id)
                self.cart_start_times.append(img.datetimet)
            else:
                i = self.carts.index(img.cart_id)
                if img.datetimet < self.cart_start_times[i]:
                    self.cart_start_times.pop(i)
                    self.cart_start_times.insert(i, img.datetimet)
            detectors = []
            #if image.exists():
            detectors.append('a')
            #if (image.parent / image.name.replace('-a-', '-b-')).exists():
            detectors.append('b')
            #if (image.parent / image.name.replace('-a-', '-c-')).exists():
            detectors.append('c')
            self.img_ap_detectors.append(detectors)
            self.img_ap_seeings.append(img.seeing)
            self.img_ap_ids.append(img.exp_id)
            self.img_ap_times.append(img.datetimet)
            self.img_ap_dithers.append(img.dither)
            self.img_ap_n_reads.append(img.n_read) 
    
    def sort(self):
        self.carts = np.array(self.carts)
        self.cart_start_times = np.array(self.cart_start_times)
        cart_sorter = self.cart_start_times.argsort()
        self.carts = self.carts[cart_sorter]
        self.cart_start_times = self.cart_start_times[cart_sorter]
        self.cart_start_times = Time(self.cart_start_times)
        self.img_ap_times = np.array(self.img_ap_times)
        img_ap_sorter = self.img_ap_times.argsort()
        self.img_ap_times = Time(self.img_ap_times)
        self.img_ap_ids = np.array(self.img_ap_ids)
        self.img_ap_seeings = np.array(self.img_ap_seeings)
        self.img_ap_detectors = np.array(self.img_ap_detectors)
        self.img_ap_dithers = np.array(self.img_ap_dithers)
        self.img_ap_n_reads = np.array(self.img_ap_n_reads)
       
        self.img_ap_ids = self.img_ap_ids[img_ap_sorter]
        self.img_ap_seeings = self.img_ap_seeings[img_ap_sorter]
        self.img_ap_detectors = self.img_ap_detectors[img_ap_sorter]
        self.img_ap_dithers = self.img_ap_dithers[img_ap_sorter]
        self.img_ap_n_reads = self.img_ap_n_reads[img_ap_sorter]
    
    def print_data(self):
        print('-'*80)
        print('{:^80}'.format('Data Summary'))
        print('-'*80)
        print('')
        for i, cart in enumerate(self.carts):
            print('# Cart {}'.format(cart))
            print('# APOGEE')
            print('MJD   UTC     Exp       Dith Nreads Detectors Seeing')
            print('-'*80)
            try:
                window = ((self.img_ap_times < self.cart_start_times[i])
                         & (self.img_ap_times < self.cart_start_times[i+1]))
            except IndexError:
                window = ((self.img_ap_times < self.cart_start_times[i])
                         & (self.img_ap_times < Time.now()))
            for mjd, iso, exp_id, dith, nred, detectors, see in zip(
            self.img_ap_times[window].mjd,
            self.img_ap_times[window].iso, self.img_ap_ids[window],
            self.img_ap_dithers, self.img_ap_n_reads[window],
            self.img_ap_detectors[window], self.img_ap_seeings[window]
            ):
                print('{:<5.0f} {} {:<9.0f} {:4} {:<6}'.format(mjd,
                          iso[12:19], exp_id, dith, nred)
                      + ' {}-{}-{}    '.format(*detectors)
                      + ' {}'.format(see))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true')
    args = parser.parse_args()
    if args.today:
        now = datetime.datetime.now()
        mjd_today = int(Time(now).mjd)
        ap_data_dir = '/data/apogee/archive/{}/'.format(mjd_today)
        ma_data_dir = '/data/spectro/{}/'.format(mjd_today)
        ap_images = glob.glob(ap_data_dir + 'apR-a*.apz')
        m_images = glob.glob(ma_data_dir + '*fit.gz')
    
    schedule = Schedule(ap_images, m_images)
    schedule.parse_images()
    schedule.sort()
    schedule.print_data()

if __name__ == '__main__':
    main()
