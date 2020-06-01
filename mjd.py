#!/usr/bin/env python3

import time

TAI_UTC = 0  # TAI_UTC =34;
TAI_UTC = 0
aSjd = 40587.3
bSjd = 86400.0


def current_sjd():
    # current mjd
    d = time.gmtime();
    tt = time.mktime(d)
    sjd = (tt + TAI_UTC) / bSjd + aSjd
    return int(sjd)


def main():
    print(current_sjd())


if __name__ == "__main__":
    main()
