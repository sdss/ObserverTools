#!/usr/bin/env python 

"""spVersion - get versions of idlmapper and idlspec2d for night log"""

import os

if __name__ == "__main__":
    cmd = ('setup idlspec2d;  path=!path+":/home/observer/"; .compile'
           ' /home/observer/list_ap.pro; .compile headfits,fxposit,mrd_hread,'
           'fxpar,gettok,valid_num; list_ap,56344| idl2 > /dev/null &')
    mapVer = os.popen(cmd).read()
