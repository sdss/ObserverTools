#!/bin/env python3

"""m4l -> m4l.py -  Get the mirror numbers from the TPM. Simply run the script
 using Python 3 with no arguments:

 m4l.py
 """

from telnetlib import Telnet
from traceback import format_exc
import socket

__version__ = '3.1.2'


def mirrors():
    """Get the mirror numbers"""
    HOST = '10.25.1.205'
    PORT = 2001

    # Open the network connection
    try:
        tn = Telnet(HOST, PORT, timeout=2)
    except (ConnectionRefusedError, socket.timeout):
        try:
            tn = Telnet('localhost', PORT, timeout=2)
        except (ConnectionRefusedError, socket.timeout) as e:
            raise ConnectionRefusedError('Unable to connect to {0}, perhaps'
                                         ' try\n ssh -L 2001:{0}:2001'
                                         ' observer@sdss-gateway.apo.nmsu.edu\n'
                                         '{1}'
                                         ''.format(HOST, e))

    # Read the data

    try:
        tn.write(b'\n')
    except (ConnectionRefusedError, socket.timeout):
        raise Exception('Telnet write to {}:{} failed: {}'.format
                        (HOST, PORT, format_exc()))

    try:
        reply = tn.read_all()
    except (ConnectionRefusedError, socket.timeout):
        raise Exception('Telnet read from {}:{} failed: {}'.format(
            HOST, PORT, format_exc()))

    tn.close()

    return reply.decode('utf-8')


if __name__ == '__main__':
    print(mirrors())
