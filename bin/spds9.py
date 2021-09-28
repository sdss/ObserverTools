#!/usr/bin/env python3

import time
from bin import ds9_live
from sdssobstools import sdss_paths


window = ds9_live.DS9Window("BOSS{:.10}".format(str(hash("BOSS"))),
                            sdss_paths.boss, "sdR-r1*", "histequ",
                            0.5, False, False, False)
while True:
    window.update()
    time.sleep(60)