#!/usr/bin/env python

import argparse
import time
import datetime
from channelarchiver import Archiver, codes, utils
ss='http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'
#ss='http://localhost:5080/telemetry/cgi/ArchiveDataServer.cgi'
archiver = Archiver(ss)

#TAI_UTC =34;
TAI_UTC =0;  aSjd=40587.3;   bSjd=86400.0

def curSjd():
# current mjd
  sjd=(time.time()+TAI_UTC)/bSjd + aSjd
  return int(sjd)

def sjd_to_time(sjd):
   sjd1=sjd
   tm=(sjd1-aSjd)*bSjd-TAI_UTC
   return tm  # time in seconds time.time()

def getTimeStamps(sjd):
    startStamp=sjd_to_time(int(sjd+0.3))
    endStamp=sjd_to_time(int(sjd+1+0.3))
    start=datetime.datetime.fromtimestamp(startStamp)
    end=datetime.datetime.fromtimestamp(endStamp)
    return start, end
    
if __name__ == "__main__":
    sjd=curSjd()
    print("sjd=",sjd)
    desc = 'integral dust calculation for one mjd'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument( '-m', '--mjd',  help='enter mjd, default is current mjd',    
        default=curSjd(), type=int)  
    parser.add_argument('-v', '--verbose', action="store_true", help='print incremental dust data' )   
    args = parser.parse_args() 
    mjd=args.mjd
    vBool=args.verbose
    
    start,end=getTimeStamps(mjd)
    print("MJD start/end times")
    print(start)
    print(end)
    
    archiver.scan_archives()
    data1= archiver.get('25m:apo:dustb', start, end, interpolation='raw',scan_archives=False)
    data2= archiver.get('25m:apo:encl25m', start, end, interpolation='raw',scan_archives=False)

    print("         Enlosure open/close times")
    print(data2)
    print("") 
    sum=0
    nn=len(data1.values)
    print("date   time    dust    encl    sum")
    for i in range(nn):
        tm=data1.times[i]
        encl= archiver.get('25m:apo:encl25m', tm, tm, interpolation='raw',scan_archives=False)
        if encl.values[0] > 0:
            sum=sum+ data1.values[i]*5/60.0
        if vBool:
        	print(data1.times[i], " %7.0f    %2i    %10.0f"%(data1.values[i], encl.values[0], sum))
    print("sum=%6.2f"%(sum))
    
    
    
