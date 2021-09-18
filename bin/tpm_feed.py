#!/usr/bin/env python3
import tpmdata
import pprint
import numpy as np
import matplotlib as mpl
mpl.use("GTK3Agg")
import matplotlib.pyplot as plt
from matplotlib import dates
from astropy.time import Time
from argparse import ArgumentParser
from matplotlib import animation
import astropy.units as u


__version__ = '3.0.1'

tpmdata.tinit()


class StripChart:
    def __init__(self, key, fig, ax):
        self.key = key
        # self.fig = plt.figure(figsize=(6, 4))
        # self.ax = self.fig.gca()
        self.fig = fig
        self.ax = ax
        self.formatter = dates.DateFormatter('%H:%M')
        data = tpmdata.packet(1, 1)

        self.t0 = Time.now()
        self.times = Time([data['ctime']], format='unix')
        self.values = np.array([data[self.key]])

        self.line = plt.plot(self.times.plot_date, self.values)
        self.ax.xaxis.set_major_formatter(self.formatter)
        # self.fig.canvas.show()
        # plt.draw()

    def update(self, i):

        data = tpmdata.packet(1, 1)
        self.times = Time(np.append(self.times, Time(data['ctime'],
                                                     format='unix')))

        self.values = np.append(self.values, data[self.key])
        sorter = np.argsort(self.times)
        self.times = self.times[sorter]
        self.values = self.values[sorter]
        cutoff = self.times >= self.t0
        self.times = self.times[cutoff]
        self.values = self.values[cutoff]
        if self.times.shape == (0,):
            print('No times to plot')
            return
        self.ax.clear()
        # print(self.times.to_datetime(), self.values)
        self.ax.plot(self.times.to_datetime(), self.values, linewidth=3,
                     label=self.key)
        self.ax.xaxis.set_major_formatter(self.formatter)
        self.ax.axhline(self.values[0], c='r', linewidth=1,
                        label=f'Initial Value {self.key}')
        self.ax.legend()


def parseargs():
    parser = ArgumentParser(description='A tool to create strip charts using'
                                        ' the TPM')
    parser.add_argument('-c', '--channels', nargs='+', default=['dewar_sp1_lb'],
                        help='Channel(s) to query and print')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='Channel(s) to plot')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--dt', nargs=1, type=float, default=5,
                        help='Time interval between prints (used with'
                             ' --channels)')
    parser.add_argument('--list-channels', dest='list_channels',
                        action='store_true',
                        help='Prints a list of all queriable channels')

    args = parser.parse_args()

    return args


def main(args=None):
    if args is None:
            args = parseargs()

    if args.list_channels:
        args.channels = []

    if args.version:
        print(__version__)

    if args.list_channels:
        data = tpmdata.packet(1, 1)
        pprint.pprint(data.keys())

    if args.plot:
        charts = []
        anis = []
        for channel in args.channels:
            fig = plt.figure(figsize=(6, 4))
            ax = fig.add_subplot(1, 1, 1)
            chart = StripChart(channel, fig, ax)
            anis.append(animation.FuncAnimation(fig, chart.update,
                                                interval=args.dt * 1000))
            charts.append(chart)
        print('Close the plots to get a table feed')
        plt.show()

    if args.channels:
        print()
        print(f"{'Time':10}" + ''.join([' {:<12}'.format(channel)
                                        for channel in args.channels]))
        while True:
            data = tpmdata.packet(1, 1)
            old_t = Time(data['ctime'], format='unix')
            new_t = old_t
            loop_cond = True
            while loop_cond:
                data = tpmdata.packet(1, 1)
                new_t = Time(data['ctime'], format='unix')
                # print((new_t - old_t).to(u.s))
                loop_cond = (new_t - old_t) < (args.dt * u.s)
            print(f'{new_t.isot[11:19]:<10}' + ''.join([' {:12}'.format(
                data[channel]) for channel in args.channels]))


if __name__ == '__main__':
    main()
