#!/usr/bin/env python

import time

TAI_UTC =0;  #TAI_UTC =34; 
TAI_UTC =0;  aSjd=40587.3;   bSjd=86400.0


def curSjd():
# current mjd
    d= time.gmtime();  tt=time.mktime(d)
    sjd=(tt+TAI_UTC)/bSjd + aSjd
    return int(sjd)
    
    
if __name__ == "__main__":
    print curSjd()