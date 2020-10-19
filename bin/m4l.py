#!/bin/env python3

"""m4l -> m4l.py -  Get the mirror numbers from the TPM. Simply run the script
 using Python 3 with no arguments:

 m4l.py
 """

from telnetlib import Telnet
from traceback import format_exc


def mirrors():
    """Get the mirror numbers"""
    HOST = '10.25.1.205'
    PORT = 2001

    # Open the network connection
    try:
        tn = Telnet(HOST, PORT)
    except Exception:
        raise Exception('Telnet connection to {}:{} failed: {}'.format(
                HOST, PORT, format_exc()))

    # Read the data

    try:
        tn.write('\n')
    except Exception:
        raise Exception('Telnet write to {}:{} failed: {}'.format
                        (HOST, PORT, format_exc()))

    try:
        reply = tn.read_all()
    except Exception:
        raise Exception('Telnet read from {}:{} failed: {}'.format(
            HOST, PORT, format_exc()))

    tn.close()

    return reply


if __name__ == '__main__':
    print(mirrors())
