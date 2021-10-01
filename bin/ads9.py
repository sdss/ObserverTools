#!/usr/bin/env python3

import time
from bin import ds9_live
from sdssobstools import sdss_paths


window = ds9_live.DS9Window("APOGEE{:.10}".format(str(hash("APOGEE"))),
                            sdss_paths.ap_utr, "apRaw*", "histequ",
                            "1.0", False, False, False)
while True:
    window.update()
    time.sleep(60)