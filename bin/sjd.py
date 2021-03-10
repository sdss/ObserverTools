#!/usr/bin/env python3
"""
sjd.py
Written by Elena Malanushenko, moved to ObserverTools by Dylan Gatlin

If run as a script, it prints the Sloan Julian Date, which is mjd + 0.3.
 This tool is often imported in other
 Python functions. This is probably the most used script in this library, so
 stability is critical.

Changelog:

2020-07-02  DG  Renamed sjd inside sjd function to current_sjd
"""
import time

__version__ = '3.2.1'

TAI_UTC = 0  # TAI_UTC =34;
aSjd = 40587.25
bSjd = 86400.0


def sjd():
    # current mjd
    d = time.gmtime()
    tt = time.mktime(d)
    current_sjd = (tt + TAI_UTC) / bSjd + aSjd
    return int(current_sjd)


def sjd_to_time(sjd_float):
    sjd1 = sjd_float
    tm = (sjd1 - aSjd) * bSjd - TAI_UTC
    return tm  # time in seconds time.time()


def main():
    print(sjd())


if __name__ == "__main__":
    main()
