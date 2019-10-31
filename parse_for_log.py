# Standart plain
import argparse
import datetime
# Standard as
import numpy as np
# Standard from
# from pathlib import Path
from astropy.time import Time
import glob
# Local imports
import apogee
# import manga


class Schedule:
    def __init__(self, ap_images, m_images):
        self.ap_images = ap_images
        self.m_images = m_images
        self.carts = []
        self.cart_start_times = []
        self.img_seeings = []
        self.cart_images = []

    def parse_images(self):
        for image in self.ap_images:
            print(image)
            img = apogee.APOGEERaw(image)
            img.parse_layer(1)
            if img.cart_id not in self.carts:
                self.carts.append(img.cart_id)
                self.cart_start_times.append(img.datetimet)
            else:
                i = self.carts.index(img.cart_id)
                if img.datetimet < self.cart_start_times[i]:
                    self.cart_start_times.pop(i)
                    self.cart_start_times.insert(i, img.datetimet)
    
    def sort_carts(self):
        self.carts = np.array(self.carts)
        self.cart_start_times = np.array(self.cart_start_times)
        cart_sorter = self.cart_start_times.argsort()
        self.carts = self.carts[cart_sorter]
        self.cart_start_times = self.cart_start_times[cart_sorter]
    
    def print_data(self):
        print('-'*80)
        print('{:^80}'.format('Data Summary'))
        print('-'*80)
        print
        for i, cart in enumerate(self.carts):
            print('# Cart {}'.format(cart))
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true')
    args = parser.parse_args()
    if args.today:
        now = datetime.datetime.now()
        mjd_today = int(Time(now).mjd)
        ap_data_dir = '/data/apogee/archive/{}/'.format(mjd_today)
        ma_data_dir = '/data/spectro/{}/'.format(mjd_today)
        ap_images = glob.glob(ap_data_dir + '*.apz')
        m_images = glob.glob(ma_data_dir + '*fit.gz')

    schedule = Schedule(ap_images, m_images)
    schedule.parse_images()
    schedule.sort_carts()
    schedule.print_data()


if __name__ == '__main__':
    main()
