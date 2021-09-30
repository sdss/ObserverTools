#!/usr/bin/env python3

import gzip
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
from astropy.time import Time
from astropy.table import Table
from argparse import ArgumentParser

from sdssobstools import sdss_paths


sns.set(style='darkgrid')

__version__ = '3.1.0'


class TPMSJD:
    def __init__(self, sjd:int, channels:iter, verbose=False):
        self.sjd = sjd
        self.channels = channels
        self.verbose = verbose
        print('Searching through {}'.format(sjd))
        uncompressed = sdss_paths.mcp_logs / f"tpm-archive-{sjd}.dat"
        if uncompressed.exists():
            if verbose:
                print('    Reading uncompressed data')
            useful_lines = []
            with uncompressed.open('r') as f:
                for line in f:
                    for channel in self.channels:
                        if channel in line:
                            useful_lines.append(line.split())
            useful_lines = np.array(useful_lines)
            self.data = Table(useful_lines, names=('Time', 'Key', 'Value'),
                    dtype=(float, str, float))
            # self.data = ascii.read(uncompressed,
            #                        names=('Time', 'Key', 'Value'))
        else:
            compressed = uncompressed.parent / (uncompressed.name + '.gz')
            if compressed.exists():
                if verbose:
                    print('    Reading compressed data')
                useful_lines = []
                with gzip.open(compressed, 'rb') as f:
                    for line in f:
                        line = line.decode('utf-8')
                        for channel in self.channels:
                            if channel in line:
                                useful_lines.append(line.split())
                    useful_lines = np.array(useful_lines)
                    self.data = Table(useful_lines,
                                      names=('Time', 'Key', 'Value'))
            else:
                print('    No data found for {}'.format(sjd))
                self.data = None
                return
        self.data['Time'] = Time(self.data['Time'], format='unix')


def parse_args():
    parser = ArgumentParser(description='A tool to query the TPM data archives')
    parser.add_argument('--t1', nargs=1,
                        help='The start time of the query')
    parser.add_argument('--t2', nargs=1,
                        help='The start time of the query')
    parser.add_argument('-m', '--mjd', type=int,
                        help='The mjd to search, can be used as an alternative'
                             ' to --t1 and --t2')
    parser.add_argument('-c', '--channels', nargs='+',
                        help='Channel names to query. For an exhaustive list,'
                             ' run `tpm_feed.py --list-channels`')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Prints help text')
    args = parser.parse_args()
    return args


def main(args=None):
    if args is None:
        args = parse_args()
    if args.mjd:
        args.t1 = '{}'.format(Time(args.mjd, format='mjd').isot)
        args.t2 = '{}'.format(Time(args.mjd + 1, format='mjd').isot)
    if args.channels:
        for channel in args.channels:
            if args.verbose:
                print(channel)
            if not args.t1:
                print('No time window given, check -h for info, exiting')
                return
            arg_times = Time([args.t1, args.t2])
            tpmsets = []
            for sjd in range(int(arg_times.mjd[0]),
                             int(arg_times.mjd[1]) + 1):
                tpm = TPMSJD(sjd, args.channels, verbose=args.verbose)
                if tpm.data is None:
                    continue
                window = ((tpm.data['Time'] >= (arg_times[0]))
                          & (tpm.data['Time'] <= (arg_times[1])))
                if args.verbose:
                    print('    {} times for day {} are within the window, out'
                          ' of {} times.'.format(np.sum(window), sjd,
                                                 len(tpm.data)))
                tpm.data = tpm.data[window]
                tpmsets.append(tpm)

            times = []
            values = []
            for tpm in tpmsets:
                filt = tpm.data['Key'] == channel
                times = np.append(times, tpm.data['Time'][filt])
                values = np.append(values, tpm.data['Value'][filt])
            if len(times) == 0:
                print('    No times found')
                continue
            times = Time(times)
            values = np.array(values).astype(float)
            fig = plt.figure(figsize=(6, 4), dpi=100)
            ax = fig.gca()
            ax.plot_date(times.plot_date, values, '-', drawstyle='steps-post')
            ax.set_title(channel)
            ax.set_xlabel('{} to {}'.format(times[0].iso[:16],
                                            times[-1].iso[:16]))
            ax.set_xlim(*(arg_times).plot_date)
            ax.set_xticklabels(ax.get_xticks(), rotation=35)
            ax.xaxis.set_major_formatter(DateFormatter('%RZ'))
            plt.show()
    else:
        print('No channel specified, nothing to do')


if __name__ == '__main__':
    main()
