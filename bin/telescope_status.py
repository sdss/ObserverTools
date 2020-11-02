#!/usr/bin/env python
import socket
import struct
from astropy.time import Time
import sys

try:
    import epics_fetch
except ImportError as e:
    try:
        from bin import epics_fetch
    except ImportError:
        raise ImportError(f'epics_fetch.py not in PYTHONPATH:\n {sys.path}')


import tpmdgram

__version__ = '3.0.0'


def query(sock, sz):
    data, addr = sock.recvfrom(sz)
    data = tpmdgram.data2dict(data)

    t = Time(data['ctime'], format='unix')
    output = f'Status at:  {t.isot[12:19]}Z\n'
    output += (f"Telescope stowed at:  "
               f"{data['az_actual_pos']*data['az_spt']/3600:>5.1f},"
               f" {data['alt_actual_pos']*data['alt_spt']/3600:>5.1f},"
               f" {data['rot_actual_pos']*data['rot_spt']/3600:>5.1f} mount\n")
    epics_data = epics_fetch.get_data(['25m:mcp:instrumentNum'],
                                      start_time=Time.now().to_datetime(),
                                      end_time=Time.now().to_datetime())
    output += f"Instrument mounted:  {epics_data[0].values[-1]}\n"
    output += (f"Counterweights at:  {data['plc_cw_0']:.1f},"
               f" {data['plc_cw_1']:.1f},"
               f" {data['plc_cw_2']:.1f},"
               f" {data['plc_cw_3']:.1f}\n")
    # TODO Check if this is supposed to do something
    output += f"LN2 autofill systems:  Connected and turned on\n"
    output += (f"180L LN2 dewar scale:  SP1 {data['dewar_sp1_lb']:6.1f} lbs,"
               f" {data['dewar_sp1_psi']:6.1f} psi")
    return output


def main():
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
    print(query(sock, sz))


if __name__ == '__main__':
    main()
