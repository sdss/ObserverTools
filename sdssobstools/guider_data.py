#!/usr/bin/env python
"""A script to parse guider images and grab essential variables from it.
While the rest of this repository is focused on logging, this is mostly
piggybacking off of previous work in order to collect guider data to
identify anomolous lurches in guiding, first identified around 2019-10-30.

2019-10-31:     dgatlin     Init
2019-11-11:     dgatlin     Moved outputs to a separate folder by mjd, made
                                table to help find lurch events.
"""
import numpy as np
import argparse
import glob
import os
import stat

try:
    from bin import sjd
except ImportError as e:
    try:
        import sjd
    except ImportError as e:
        raise ImportError(f"Please add ObserverTools/bin to your PYTHONPATH:\n"
                          f"    {e}")

from astropy.io import fits
from astropy.time import Time
# from pathlib import Path

__version__ = '3.0.1'


class GuiderRaw:
    """A class to parse raw data from APOGEE. The purpose of collecting this
    raw data is to future-proof things that need these ouptuts in case
    things like autoschedulers change, which many libraries depend on. This
    will hopefully help SDSS-V logging"""
    def __init__(self, fits_file, ext):
        fil = fits.open(fits_file)
        # layer = self.image[layer_ind]
        header = fil[ext].header
        # An A dither is DITHPIX=12.994, a B dither is DITHPIX=13.499
        self.hdu = fil[ext]
        self.exp_time = header['EXPTIME']
        self.datetimet = Time(header['DATE-OBS'])  # Local
        self.exp_id = int(str(fits_file).split('-')[-1].split('.')[0])
        # self.seeing = header['SEEING'] # Inconsistent
        self.img_type = header['IMAGETYP']
        self.n_read = len(fil)-1
        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true')
    parser.add_argument('-m', '--mjd',
                        help='If not today (-t), the mjd to search')
    parser.add_argument('-l', '--lurches', nargs='+', default=[],
                        help='The exposure ids of known lurches')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Whether or not you want to print a table')

    args = parser.parse_args()
    if args.today:
        mjd_today = sjd.curSjd()
        data_dir = '/data/gcam/{}/'.format(mjd_today)
        mjd_target = mjd_today
    elif args.mjd:
        data_dir = '/data/gcam/{}/'.format(args.mjd)
        mjd_target = args.mjd
    else:
        raise Exception('Must provide -t or -m in arguments')
    print(data_dir)
    if args.lurches:
        print('Looking for lurches at {}'.format(', '.join(args.lurches)))

    eids = []
    ts = []
    rot = []
    ra = []
    dec = []
    seeing = []
    scale = []
    lurches = []
    files = glob.glob(data_dir + 'proc-gimg*.fits.gz')
    for i, fil in enumerate(files):
        try:
            img = GuiderRaw(fil, 0)
            rot.append(img.hdu.header['DROT'])  # Must be the first one in
            # case there is no DROT, so that it fails before appending
            ra.append(img.hdu.header['DRA'])
            dec.append(img.hdu.header['DDEC'])
            ts.append(Time(img.hdu.header['DATE-OBS']))
            seeing.append(img.hdu.header['SEEING'])
            scale.append(img.hdu.header['SCALE'])
            eids.append(str(int(fil.split('-')[-1].split('.')[0])))
            lurches.append(eids[-1] in args.lurches)
            if i % 100 == 0:
                print('{}/{}'.format(i, len(files)))
        except KeyError:
            pass

    for i, lu in enumerate(lurches):  # in order to display well in the tab
        if lu:
            lurches[i] = 'Y'
        else:
            lurches[i] = ' '
    # There are ridiculous errors on slews (-gazillion), so I need to filter
    # those out. Also, glob.glob is infamously unsorted, so I need to sort
    # what's left. I also need to filter eids before I sort them or I will
    # have index errors
    eids = np.array(eids).astype(int)
    rot = np.array(rot) * 3600
    filt = rot > -1e6
    sorter = eids[filt].argsort()
    eids = eids[filt][sorter]
    ts = np.array(ts)[filt][sorter]
    rot = rot[filt][sorter]
    lurches = np.array(lurches)[filt][sorter]
    ra = np.array(ra)[filt][sorter] * 3600
    dec = np.array(dec)[filt][sorter] * 3600
    seeing = np.array(seeing)[filt][sorter]
    scale = (np.array(scale)[filt][sorter] - 1) * 1e5
    # print(ts.shape, rot.shape, ra.shape, dec.shape)
    
    save_dir = os.path.dirname(os.path.realpath(
        __file__)) + '/guider_issues/{}'.format(mjd_target)
    # print(save_dir)
    t_out = [t.in_time for t in ts]
    os.system('rm -r {}'.format(save_dir))
    os.system('mkdir {}'.format(save_dir))
    np.save(save_dir + '/times.npy', t_out)
    np.save(save_dir + '/rotator.npy', rot)
    np.save(save_dir + '/ra.npy', ra)
    np.save(save_dir + '/dec.npy', dec)
    np.save(save_dir + '/lurches.npy', np.array(args.lurches).astype(int))
    np.save(save_dir + '/ids.npy', eids)
    
    tab = open(save_dir + '/guiding_table.txt', 'w')
    
    tab.write('# {:<6}  {:<8}  {:<8}  {:<7}  {:<7}  {:<7}  {:<7}'
              '  {:<6}\n'.format('Time', 'Exp ID', "Rot ('')", "RA ('')",
                                 "Dec ('')", "See ('')", 'Scale-1 (e5)',
                                 'Lurch?'))
    if args.verbose:
        print('# {:<6}  {:<8}  {:<8}  {:<8}  {:<7}  {:<7}  {:<7}'
              '  {:<6}'.format('Time', 'Exp ID', "Rot ('')", "RA ('')",
                               "Dec ('')", "See ('')", 'Scale-1 (e5)',
                               'Lurch?'))

    tab.write('#' + '-' * 79 + '\n')
    if args.verbose:
        print('#' + '-' * 79)
    for t, i, r, a, d, s, sc, lu in zip(
            ts, eids, rot, ra, dec, seeing, scale, lurches):
        tab.write('{}  {:<8.0f}  {:<+8.2f}  {:<+8.2f}  {:<+8.2f}  {:<+8.1f}'
                  '  {:<+8.1f} {:<6}\n'.format(t.time, i, r, a, d, s, sc, lu))
        if args.verbose:
            print('{}  {:<8.0f}  {:<+8.2f}  {:<+8.2f}  {:<+8.2f}  {:<+8.1f}'
                  '  {:<+8.1f} {:<6}'.format(t.time, i, r, a, d, s, sc, lu))
    
    os.chmod(save_dir, stat.S_IRWXO)  # If someone else runs this, I need to
    # still have access or I can't use git on the repo. This makes sure I
    # maintain access to every file
    os.chmod(save_dir, 0o777)
    for fil in glob.glob(save_dir + '/*'):
        os.chmod(fil, 0o777)


if __name__ == '__main__':
    main()
