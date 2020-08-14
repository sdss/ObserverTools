#!/usr/bin/env python3
"""
help.py

This is a file to pull the help for all programs in bin. Each script must be
 added individually, some scripts use argparse, so -h is called, others do not,
 and so their __doc__ is printed. Based on spHelp written by Elena.

2020-06-08  DG  Init, based on spHelp
"""
import subprocess as sub
from pathlib import Path
import sjd
import sp_version
# import wave_mid
# import x_mid

argparsed = ['ap_test.py', 'boss_sha1sum.py', 'ds9_live.py', 'epics_fetch.py',
             'get_dust.py', 'sloan_log.py']
non_argparsed = ['sjd.py', 'sp_version.py', 'wave_mid.py', 'x_mid.py']
bin_dir = Path(__file__).parent

for arg in argparsed:
    print('{:=^80}'.format(arg))
    sub.call([bin_dir / arg, '-h'])
    print()

print('{:=^80}'.format('sjd.py'))
print(sjd.__doc__)
print('{:=^80}'.format('sp_version.py'))
print(sp_version.__doc__)

# print(wave_mid.__doc__)
# print(x_mid.__doc__)
