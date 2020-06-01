#!/usr/bin/env python3

"""
boss_sha1sum.py [MJD]

- cd to BOSS raw data directory for MJD (default is today)
- run sha1sum for all raw data in that directory

Created by Stephen Bailey (LBNL) Fall 2011
"""

import sys
import os

if len(sys.argv) > 1:
    sjd = int(sys.argv[1])
else:
    from sjd import sjd   #- In /home/observer/bin/
    sjd = sjd()

os.chdir('/data/spectro/%d/' % sjd)
cmd = "sha1sum sdR-*.fit.gz > %d.sha1sum" % sjd
os.system(cmd)
