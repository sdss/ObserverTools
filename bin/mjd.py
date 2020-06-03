#!/usr/bin/env python3
"""
If run as a script, it prints the mjd, but this tool is often imported in other
 Python functions. This is probably the most used script in this library, so
 stability is critical. The outputs here do disagree slightly from
 astropy.time.Time.now().mjd, and this discrepancy should be investigated.
"""
import time

__version__ = 3.0

TAI_UTC = 0  # TAI_UTC =34;
aSjd = 40587.3
bSjd = 86400.0


def mjd():
    # current mjd
    d = time.gmtime()
    tt = time.mktime(d)
    sjd = (tt + TAI_UTC) / bSjd + aSjd
    return int(sjd)


def main():
    print(mjd())


if __name__ == "__main__":
    main()
