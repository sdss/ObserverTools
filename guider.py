import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import argparse
import glob
from astropy.io import fits
from astropy.time import Time
# from pathlib import Path
mpl.use('Agg')

class GuiderRaw:
    '''A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like autoschedulers change, which many libraries depend on. This
    will hopefully help SDSS-V logging'''
    def __init__(self, file, ext):
        fil = fits.open(file)
        # layer = self.image[layer_ind]
        header = fil[ext].header
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        self.hdu = fil[ext]
        self.exp_time = header['EXPTIME']
        self.datetimet = Time(header['DATE-OBS']) # Local
        self.exp_id = int(str(file).split('-')[-1].split('.')[0])
        # self.seeing = header['SEEING'] # Inconsistent
        self.img_type = header['IMAGETYP']
        self.n_read = len(fil)-1
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true')
    args = parser.parse_args()
    if args.today:
        now = datetime.datetime.now()
        mjd_today = int(Time(now).mjd)
        data_dir = '/data/gcam/{}/'.format(mjd_today)
        ts = []
        rot = []
        ra = []
        dec = []
        for fil in glob.glob(data_dir + 'proc-gimg*.fits.gz'):
            try:
                print(fil)
                img = GuiderRaw(fil, 0)
                rot.append(img.hdu.header['DROT'])
                ra.append(img.hdu.header['DRA'])
                dec.append(img.hdu.header['DDEC'])
                ts.append(img.hdu.header['DATE-OBS'])

            except KeyError:
                pass
        ts = np.array(ts)
        rot = np.array(rot)
        ra = np.array(ra)
        dec = np.array(dec)
        print(ts.shape, rot.shape, ra.shape, dec.shape)
        np.save('times.npy', ts)
        np.save('rotator.npy', rot)
        np.save('ra.npy', ra)
        np.save('dec.npy', dec)
        # Hub matplotlib sucks, export instead
        # plt.plot([0,0,0,], [1,1,1])
        # fig, axs = plt.subplots(3, 1, sharex=True, figsize=(6,4))
        # rotax, decax, raax = axs
        # rotax.plot(ts, rot)
        # rotax.set_title('Rotator Axis Error')
        # decax.plot(ts, dec)
        # decax.set_title('Declination Axis Error')
        # raax.plot(ts, dec)
        # raax.set_title('Right Ascension Axis Error')
        # fig.savefig('~/dgatlin/plots/guider_errors.png')
        


if __name__ == '__main__':
    main()
