#!/usr/bin/env python
import tpmdgram
import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates
from astropy.time import Time
from argparse import ArgumentParser
from matplotlib import animation
import astropy.units as u


__version__ = '3.0.1'


sz = tpmdgram.tinit()

multicast_group = '224.1.1.1'
server_address = ('', 2007)

# Init socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind to the server address
sock.bind(server_address)

# Tell the OS to add the socket to the multicast group on all interfaces
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


class StripChart:
    def __init__(self, key, fig, ax):
        self.key = key
        # self.fig = plt.figure(figsize=(6, 4))
        # self.ax = self.fig.gca()
        self.fig = fig
        self.ax = ax
        self.formatter = dates.DateFormatter('%H:%M')

        data, addr = sock.recvfrom(sz)
        data = tpmdgram.data2dict(data)

        self.t0 = Time.now()
        self.times = Time([data['ctime']], format='unix')
        self.values = np.array([data[self.key]])

        self.line = plt.plot(self.times.plot_date, self.values)
        self.ax.xaxis.set_major_formatter(self.formatter)
        # self.fig.canvas.show()
        # plt.draw()

    def update(self, i):

        data, addr, = sock.recvfrom(sz)
        data = tpmdgram.data2dict(data)
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
    parser.add_argument('--dt', nargs=1,
                        help='Time interval between prints (used with'
                             ' --channels)')

    args = parser.parse_args()

    if args.version:
        print(__version__)

    return args


def main():
    args = parseargs()

    if args.plot:
        charts = []
        anis = []
        for channel in args.channels:
            fig = plt.figure(figsize=(6, 4))
            ax = fig.add_subplot(1, 1, 1)
            chart = StripChart(channel, fig, ax)
            anis.append(animation.FuncAnimation(fig, chart.update,
                                                interval=1000))
            charts.append(chart)
        plt.show()

    if args.channels:
        print()
        print(f"{'Time':10}" + ''.join([' {:<12}'.format(channel)
                                        for channel in args.channels]))
        while True:
            data, addr, = sock.recvfrom(sz)
            data = tpmdgram.data2dict(data)
            old_t = Time(data['ctime'], format='unix')
            new_t = old_t
            loop_cond = True
            while loop_cond:
                data, addr, = sock.recvfrom(sz)
                data = tpmdgram.data2dict(data)
                new_t = Time(data['ctime'], format='unix')
                # print((new_t - old_t).to(u.s))
                loop_cond = (new_t - old_t) < (5 * u.s)
            print(f'{new_t.isot[11:19]:<10}' + ''.join([' {:12}'.format(
                data[channel]) for channel in args.channels]))


if __name__ == '__main__':
    main()
