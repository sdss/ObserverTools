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
import datetime
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
from channelarchiver import Archiver
# from multiprocessing import Process

import log_apogee
import log_boss


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
                         'iNRead': [], 'iEType': [], 'iCart': [], 'iPlate': []}
         self.b_data = {'cCart': [], 'cTime': [],
                        'iTime': [], 'iID': [],
                        'iDetector': [], 'iDither': [],
                        'iEType': [], 'iExdt': [], 'iCart': [], 'iHart': [],
                        'iPlate': [], 'hHart':[], 'hTime': []}
         # These values are not known from the header and must be created
         # after self.sort.
         self.cart_data = {'cNAPA': [], 'cNAPB': [], 'cNMN': [], 'cNMS': [],
                           'cNME': [], 'cNMC': [], 'cAPSummary': [],
                           'cMSummary': []}
         self.test_procs = []
         
         self.telemetry = Archiver('http://sdss-telemetry.apo.nmsu.edu/'
                                   'telemetry/cgi/ArchiveDataServer.cgi')
         self.telemetry.scan_archives()

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
          #         img.isot)
          self.dome_data['dNMissing'].append(n_missing)
          self.dome_data['dNFaint'].append(n_faint)
          self.dome_data['dMissing'].append(missing)
          self.dome_data['dFaint'].append(faint)
          self.dome_data['dCart'].append(img.cart_id)
          self.dome_data['dTime'].append(img.isot)

     def parse_images(self):
          """Goes through every image in ap_images and m_images to put them in
          dictionaries."""
          if self.args.apogee:
              print('Reading APOGEE Data')
              for image in tqdm(self.ap_images):
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
                  red_dir = Path('/data/apogee/quickred/{}/'.format(self.mjd))
                  red_fil = red_dir / 'ap2D-a-{}.fits.fz'.format(img.exp_id)
                  if (red_fil).exists():
                      detectors.append('a')
                  else:
                      detectors.append('x')
                  if (red_fil.parent / red_fil.name.replace('-a-', '-b-')
                          ).exists():
                      detectors.append('b')
                  else:
                      detectors.append('x')
                  if (red_fil.parent / red_fil.name.replace('-a-', '-c-')
                          ).exists():
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
                 img = log_boss.BOSSRaw(image)
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
                 self.b_data['iExdt'].append(img.exp_time)
                 self.b_data['iCart'].append(img.cart_id)
                 self.b_data['iHart'].append(img.hartmann)
                 self.b_data['iPlate'].append(img.plate_id)
                 
                 if img.hartmann == 'Left':
                     # Note that times are sent in UTC and received in local, yet
                     # those times are marked as UTC
                     tstart = Time(img.isot).isot
                     tend = (Time(img.isot)+1/24/60*5).isot
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
                 flav = 't' if img.flavor == 'flat' else 'w'
                 if img.lead == 'eBOSS':
                     red_dir = Path('/data/boss/sos/{}/'.format(self.mjd))
                     red_fil = red_dir / 'splog-r1-{3:0>8}.log'.format(
                             flav, self.mjd, img.plate_id, img.exp_id)
                 else:
                     red_dir = Path('/data/manga/dos/{}/logs/'.format(self.mjd))
                     red_fil = red_dir / 'splog-r1-{3:0>8}.log'.format(
                     # red_fil = red_dir / 'mg{}set-{}-{}-{:0>8}-r1.fits'.format(
                             flav, self.mjd, img.plate_id, img.exp_id)
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
         if self.args.apogee:
             for key, item in self.ap_data.items():
                 if 'Time' in key:
                     self.ap_data[key] = Time(item)
                 else:
                     self.ap_data[key] = np.array(item)
             ap_cart_sorter = self.ap_data['cTime'].argsort()
             ap_img_sorter = self.ap_data['iTime'].argsort()
             for key, item in self.ap_data.items():
                 if key[0] == 'c':
                     self.ap_data[key] = item[ap_cart_sorter]
                 elif key[0] == 'i':
                     self.ap_data[key] = item[ap_img_sorter]
             if self.dome_data['dTime']:
                 for key, item in self.dome_data.items():
                     if 'Time' in key:
                         self.dome_data[key] = Time(item)
                         data_sort = self.dome_data[key].argsort()
                     else:
                         self.dome_data[key] = np.array(item)
 
         for key, item in self.data.items():
             if 'Time' in key:
                 self.data[key] = Time(item, format='isot')
                 data_sort = self.data[key].argsort()
             else:
                 self.data[key] = np.array(item)
         for key, item in self.data.items():
             self.data[key] = item[data_sort]
         if self.args.boss:
             if len(self.b_data['cCart']) != 0:
                 for key, item in self.b_data.items():
                     if 'Time' in key:
                         if len(item) != 0:
                             self.b_data[key] = Time(item)
                         else:
                             print(key)
                             self.b_data[key] = Time(item, format='isot')
                     else:
                         self.b_data[key] = np.array(item)
                 m_cart_sorter = self.b_data['cTime'].argsort()
                 m_img_sorter = self.b_data['iTime'].argsort()
                 m_h_sorter = self.b_data['hTime'].argsort()
                 for key, item in self.b_data.items():
                     if key[0] == 'c':
                         self.b_data[key] = item[m_cart_sorter]
                     elif key[0] == 'i':
                         self.b_data[key] = item[m_img_sorter]
                     elif key[0] == 'h':
                         self.b_data[key] = item[m_h_sorter]

     def count_dithers(self):
         for i, cart in enumerate(self.data['cCart']):
             self.cart_data['cNAPA'].append(np.sum((
                 (self.ap_data['iCart'] == cart)
                 & (self.ap_data['iDither'] == 'A'))
                 & (self.ap_data['iEType'] == 'OBJECT')))
             self.cart_data['cNAPB'].append(np.sum(
                 (self.ap_data['iCart'] == cart)
                 & (self.ap_data['iDither'] == 'B')
                 & (self.ap_data['iEType'] == 'OBJECT')))
             self.cart_data['cNMN'].append(np.sum(
                 (self.b_data['iCart'] == cart)
                 & (self.b_data['iDither'] == 'N')
                 & (self.b_data['iEType'] == 'science')))
             self.cart_data['cNMS'].append(np.sum(
                 (self.b_data['iCart'] == cart)
                 & (self.b_data['iDither'] == 'S')
                 & (self.b_data['iEType'] == 'science')))
             self.cart_data['cNME'].append(np.sum(
                 (self.b_data['iCart'] == cart)
                 & (self.b_data['iDither'] == 'E')
                 & (self.b_data['iEType'] == 'science')))
             self.cart_data['cNMC'].append(np.sum(
                 (self.b_data['iCart'] == cart)
                 & (self.b_data['iDither'] == 'C')
                 & (self.b_data['iEType'] == 'science')))
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

    def hartmann_parse(self, hart):
        output = ''  #.format((Time(hart[0].times[-1])).isot)
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
        output += 'SP1: {:>6.1f}, SP2: {:>6.1f}\n'.format(
                hart[8].values[-1], hart[9].values[-1])
        return output

    def psummary(self):
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

    def pdata(self):
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
                                  'Dith', 'nReads', 'Pipeline',
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
                print('{:<5.0f} {:0>8} {:<8.0f} {:<12} {:<4} {:<6} {:<9}'
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
                print('# BOSS')
                print('{:<5} {:<8} {:<8} {:<7} {:<4} {:<11} {:<5} {:<5}'
                      ''.format('MJD', 'UTC', 'Exposure', 'Type',
                                'Dith', 'Pipeline', 'ETime', 'Hart'))
                print('='*80)
                try:
                    window = ((self.b_data['iTime']
                               >= self.data['cTime'][i])
                              & (self.b_data['iTime']
                                 < self.data['cTime'][i+1])
                              )
                
                except IndexError:
                    window = ((self.b_data['iTime']
                               >= self.data['cTime'][i])
                              & (self.b_data['iTime'] < Time.now()))
                for (mjd, iso, exp_id, exp_type, dith,
                     detectors, etime, hart) in zip(
                    self.b_data['iTime'][window].mjd,
                    self.b_data['iTime'][window].iso,
                    self.b_data['iID'][window],
                    self.b_data['iEType'][window],
                    self.b_data['iDither'][window],
                    self.b_data['iDetector'][window],
                    self.b_data['iExdt'][window],
                    self.b_data['iHart'][window],
                ):
                    print('{:<5.0f} {:0>8} {:<8.0f} {:<7} {:<4} {:<11}'
                           ' {:<5.0f} {:<5}'
                           ''.format(mjd, iso[12:19], exp_id,
                                     exp_type.strip(),
                                     dith.strip(), detectors, etime,
                                     hart))
                try:
                    window = ((self.b_data['hTime']
                               >= self.data['cTime'][i])
                              & (self.b_data['hTime']
                                 < self.data['cTime'][i+1])
                              )
                
                except IndexError:
                    window = ((self.b_data['hTime']
                               >= self.data['cTime'][i])
                              & (self.b_data['hTime'] < Time.now()))
                for t, hart in zip(self.b_data['hTime'][window],
                                   self.b_data['hHart'][window]):
                    print(t)
                    print(self.hartmann_parse(hart))
                


    def pboss(self):
        print('='*80)
        print('{:^80}'.format('BOSS Data Summary'))
        print('='*80)
        print('{:<5} {:<8} {:<8} {:<8} {:<7} {:<4} {:<11} {:<5} {:<5}'
              ''.format('MJD', 'UTC', 'Cart', 'Exposure', 'Type', 'Dith',
                        'Pipeline', 'ETime', 'Hart'))
        print('='*80)
        for (mjd, iso, cart, plate, exp_id, exp_type, dith, detectors, etime,
             hart) in zip(
            self.b_data['iTime'].mjd,
            self.b_data['iTime'].iso,
            self.b_data['iCart'],
            self.b_data['iPlate'],
            self.b_data['iID'],
            self.b_data['iEType'],
            self.b_data['iDither'],
            self.b_data['iDetector'],
            self.b_data['iExdt'],
            self.b_data['iHart']):
            print('{:<5.0f} {:<8} {:0>2.0f}-{:<5.0f} {:<8.0f} {:<7} {:<4}'
                  ' {:<11}'
                  ' {:<5.0f} {:<5}'
               ''.format(mjd, iso[12:19], cart, plate, exp_id, exp_type.strip(),
                         dith.strip(), detectors, etime, hart))

    def papogee(self):
        print('='*80)
        print('{:^80}'.format('APOGEE Data Summary'))
        print('='*80)
        print('{:<5} {:<8} {:<8} {:<8} {:<12} {:<4} {:<6} {:<9}'
              ' {:<4}'.format('MJD', 'UTC', 'Cart', 'Exposure', 'Type',
                              'Dith', 'nReads', 'Pipeline',
                              'Seeing'))
        print('='*80)
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
            print('{:<5.0f} {:<8} {:0>2.0f}-{:<5.0f} {:<8.0f} {:<12} {:<4}'
                  ' {:<6}'
                  ' {:<9}'
                  ' {:<4.1f}'.format(mjd, iso[12:19], cart, plate, exp_id,
                                     exp_type,
                                     dith, nread, detectors, see))


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
    parser.add_argument('-b', '--boss', action='store_true',
            help='Print MaANGA Summary')
    parser.add_argument('-a', '--apogee', action='store_true',
            help='Print APOGEE Summary')
    parser.add_argument('--noprogress', action='store_true',
            help='Show no progress in processing images. WARNING: Might be'
            ' slower, but it could go either way.')
    args = parser.parse_args()
    if args.today:
        now = Time.now()
        mjd = int(now.mjd + 3/24)
    elif args.mjd:
        mjd = args.mjd
    else:
        raise s.GatlinError('Must provide -t or -m in arguments')
   
    if args.summary:
        args.boss = True
        args.apogee = True
    ap_data_dir = '/data/apogee/archive/{}/'.format(mjd)
    b_data_dir = '/data/spectro/{}/'.format(mjd)
    ap_images = Path(ap_data_dir).glob('apR-a*.apz')
    b_images = Path(b_data_dir).glob('sdR-r1*fit.gz')

    if not args.noprogress:
        ap_images = list(ap_images)
        b_images = list(b_images)

    schedule = Schedule(ap_images, b_images, mjd, args)
    schedule.parse_images()
    schedule.sort()
    schedule.count_dithers()

    if args.print:
        args.summary = True
        args.data = True
        args.boss = True
        args.apogee = True

    if args.summary:
        args.boss = True
        args.apogee = True
        schedule.psummary()
        print('\n')

    if args.data:
        args.boss = True
        args.apogee = True
        schedule.pdata()
        print('\n')

    if args.boss:
        schedule.pboss()
        print('\n')

    if args.apogee:
        schedule.papogee()
        print('\n')

    # if args.log_support:
        # schdule.log_support()


if __name__ == '__main__':
    main()

