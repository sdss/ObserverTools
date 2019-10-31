import numpy as np
import datetime
import argparse
from astropy.io import fits
from astropy.time import Time
# from pathlib import Path


class APOGEERaw:
	"""A class to parse raw data from APOGEE. The purpose of collecting this
	raw data is to future-proof things that need these ouptuts in case
	things like autoschedulers change, which many libraries depend on. This
	will hopefully help SDSS-V logging"""
	def __init__(self, file):
		self.image = fits.open(file)
	
	def parse_layer(self, layer_ind):
		layer = self.image[layer_ind]
		# An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
		if layer.header['DITHPIX'] < 12.25:
			self.dither = 'A'
		else:
			self.dither = 'B'
		self.exp_time = layer.header['EXPTIME']
		self.datetimet = Time(layer.header['DATE-OBS']) # Local
		self.plate_id = layer.header['PLATEID']
		self.cart_id = layer.header['CARTID']
		return layer


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-t', '--today', action='store_true')
	args = parser.parse_args()
	if args.today:
		now = datetime.datetime.now()
		mjd_today = int(Time(now).mjd)
		data_dir = '/data/apogee/archive/{}/'.format(mjd_today)

		


if __name__ == '__main__':
	main()
