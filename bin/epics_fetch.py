#!/usr/bin/env python3

"""
A terminal tool to access the SDSS EPICS server using channeltelemetry

See this CA library  https://github.com/RobbieClarken/channeltelemetry

Based off of cafetch.py, written by Elena, with a few features removed to limit
 dependencies.

Changelog:
2020-06-08  DG  Ported to Python 3 and ObserverTools, takes a series of keys or
 just one.

"""

from re import A
import numpy as np
from channelarchiver import Archiver
from argparse import ArgumentParser
from astropy.time import Time
import socket

try:
    telemetry = Archiver('http://sdss-telemetry.apo.nmsu.edu/'
                         'telemetry/cgi/ArchiveDataServer.cgi')
    telemetry.scan_archives()
except (socket.gaierror, ConnectionRefusedError):
    try:
        telemetry = Archiver('http://localhost:5080/'
                             'telemetry/cgi/ArchiveDataServer.cgi')
        telemetry.scan_archives()
    except (socket.gaierror, ConnectionRefusedError) as e:
        raise Exception('Cannot access EPICS Server, aborting, you should try\n'
                        'ssh -L 5080:sdss4-telemetry.apo.nmsu.edu:80 observer@'
                        'sdss-gateway.apo.nmsu.edu')

__version__ = '3.1.1'


def get_data(channel, start_time, end_time):
    """ Grabs the channel data. If a list is passed to channel, it will return
    a list of datasets"""
    telemetry.scan_archives()
    data = telemetry.get(channel, start_time, end_time, interpolation='raw')
    if isinstance(data, list):
        for i, dat in enumerate(data):
            data[i].times = Time([t.isoformat(sep=" ")[:19]
                                  for t in dat.times], precision=0)
            data[i].values = np.array(dat.values)

    else:  # Non-list inputs aren't supposed internally, they're only for use
        # in other programs like sloan_log.py
        try:
            data.times = Time(data.times)
            data.values = np.array(data.values)
        except ValueError:
            data.times = Time(data.times, format='iso')
    return data


def _print_data(datasets: list, channel_names: list, verbose=False):
    times = datasets[0].times
    modified_times = False
    if len(datasets) > 1:
        for dataset in datasets[1:]:
            for t in dataset.times:
                if t not in times:
                    modified_times = True
                    times = np.append(times, t)
        if modified_times:
            if verbose:
                print("Unique times sets were merged")
            times = Time(times)
            times = times[np.argsort(times)]
    fmt_stem = "# {:20}" + "{:15}" * len(datasets)
    print(fmt_stem.format(
        "Time", *[channel.split(":")[-1] for channel in channel_names]))
    print("=" * 80)
    fmt_stem = "{:22}"
    for dataset in datasets:
        if dataset.values.ndim > 1:  # An array of output (like coutnerweights)
            fmt_stem += "{}"
        elif dataset.values.dtype == int:
            fmt_stem += "{:15.0f}"
        elif dataset.values.dtype == float:
            fmt_stem += "{:15.3f}"
        else:
            fmt_stem += "{:15}"
    for i, time in enumerate(times):
        values = []
        for dataset in datasets:
            v = dataset.values[dataset.times == time]
            if v.size > 0:
                values.append(v[0])
            else:
                values.append(np.nan)
        print(fmt_stem.format(time.iso[:19], *values))

    # print('    Channel:'.format(datasets.channel))
    # print('    Units: {}'.format(datasets.units))
    # print('    {:<30}| {:<30}'.format('Time', 'Value'))
    # print('    ' + ('=' * 76))
    # for t, v, in zip(datasets.times, datasets.values):
    # print('    {:<30}| {}'.format(t.isot, v))


def parse_args():
    now = Time.now() + 0.3
    parser = ArgumentParser(description='A command line interface for the SDSS'
                            ' EPICS Server. Prints a simple table'
                            ' of data. If no time window is'
                                        ' specified, it will print the most'
                                        ' recent value only.')

    parser.add_argument('-c', '--channels', nargs='+',
                        default=["25m:mcp:cwPositions"],
                        help='A list of channel names, default is'
                             ' 25m:mcp:cwPositions')
    parser.add_argument('--t1', '--startTime', dest='startTime',
                        default=now.isot,
                        help='start time of query, default is 5 min ago, format'
                             ' "2015-06-23 22:10"')
    parser.add_argument('--t2', '--endTime', dest='endTime', default=now.isot,
                        help='end time of query, default is current time now,'
                             ' format "2015-06-23 22:15"')
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose debugging")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    datasets = get_data(args.channels, args.startTime, args.endTime)
    _print_data(datasets, args.channels, args.verbose)
    print(f"Ended at {Time.now()}")


if __name__ == '__main__':
    main()
