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
            try:
                data[i].times = Time(dat.times)
            except ValueError:
                data[i].times = Time(dat.times, format='iso')

    else:
        try:
            data.times = Time(data.times)
        except ValueError:
            data.times = Time(data.times, format='iso')

    return data


def print_data(data):
    print('    Channel:'.format(data.channel))
    print('    Units: {}'.format(data.units))
    print('    {:<30}| {:<30}'.format('Time', 'Value'))
    print('    ' + ('=' * 76))
    for t, v, in zip(data.times, data.values):
        print('    {:<30}| {}'.format(t.isot, v))


def print_datasets(datasets):
    if isinstance(datasets, list):
        for dataset in datasets:
            print_data(dataset)
    else:
        print_data(datasets)


def parse_args():
    now = Time.now() + 0.3
    parser = ArgumentParser(description='A command line interface for the SDSS'
                                        ' EPICS Server. Prints a simple table'
                                        ' of data. If no time window is'
                                        ' specified, it will print the most'
                                        ' recent value only.')

    parser.add_argument('-c', '--channels', nargs='?',
                        default="25m:mcp:cwPositions",
                        help='A list of channel names, default is'
                             ' 25m:mcp:cwPositions')
    parser.add_argument('--t1', '--startTime', dest='startTime',
                        default=now.isot,
                        help='start time of query, default is 5 min ago, format'
                             ' "2015-06-23 22:10"')
    parser.add_argument('--t2', '--endTime', dest='endTime', default=now.isot,
                        help='end time of query, default is current time now,'
                             ' format "2015-06-23 22:15"')

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    print(args.channels)
    datasets = get_data(args.channels, args.startTime, args.endTime)
    print_datasets(datasets)


if __name__ == '__main__':
    main()
