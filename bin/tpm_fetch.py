#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from astropy.time import Time
from astropy.io import ascii
from argparse import ArgumentParser
from pathlib import Path


sns.set(style='darkgrid')

__version__ = '3.0.0'


class TPMSJD:
    def __init__(self, sjd, verbose=False):
        print('Searching through {}'.format(sjd))
        uncompressed = Path('/Users/dylan/data/logs/mcp/tpm-archive-{}.dat'
                            ''.format(sjd))
        if uncompressed.exists():
            if verbose:
                print('    Reading uncompressed data')
            self.data = ascii.read(uncompressed,
                                   names=('Time', 'Key', 'Value'))
        else:
            if verbose:
                print('    Reading compressed data')
            compressed = uncompressed.parent / (uncompressed.name + '.gz')
            if compressed.exists():
                self.data = ascii.read(compressed,
                                       names=('Time', 'Key', 'Value'))
            else:
                print('No data found for {}'.format(sjd))
        self.data['Time'] = Time(self.data['Time'], format='unix')


def parse_args():
    parser = ArgumentParser(description='A tool to query the TPM data archives')
    parser.add_argument('--t1', nargs=1,
                        help='The start time of the query')
    parser.add_argument('--t2', nargs=1,
                        help='The start time of the query')
    parser.add_argument('-c', '--channels', nargs='+',
                        help='Channel names to query. For an exhaustive list,'
                             ' run `tpm_feed.py --list-channels`')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Prints help text')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    arg_times = Time([args.t1, args.t2])
    tpmsets = []
    for sjd in range(int(arg_times.mjd[0] + 0.3),
                     int(arg_times.mjd[1] + 0.3)+1):
        tpm = TPMSJD(sjd, verbose=args.verbose)
        window = ((tpm.data['Time'] >= arg_times[0])
                  & (tpm.data['Time'] <= arg_times[1]))
        if args.verbose:

            print('{} times for day {} are within the window, out of'
                  ' {} times.'.format(np.sum(window), sjd, len(tpm.data)))
        tpm.data = tpm.data[window]
        tpmsets.append(tpm)

    for channel in args.channels:
        if args.verbose:
            print(channel)
        times = []
        values = []
        for tpm in tpmsets:
            filt = tpm.data['Key'] == channel
            times = np.append(times, tpm.data['Time'][filt])
            values = np.append(values, tpm.data['Value'][filt])
        if len(times) == 0:
            print(' No times found')
            continue
        times = Time(times)
        values = np.array(values).astype(float)
        fig = plt.figure(figsize=(6, 4), dpi=100)
        ax = fig.gca()
        ax.plot_date(times.plot_date, values, '-', drawstyle='steps-post')
        ax.set_title(channel)
        ax.set_xlabel('{} to {}'.format(*times.iso))
        ax.set_xlim(*arg_times.plot_date)
        plt.show()


if __name__ == '__main__':
    main()
