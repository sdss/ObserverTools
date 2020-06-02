#!/usr/bin/env python

'''
mount disk to read data from sdss-hub

May (SJD 58240) - (SJD 58270)
April 58210 -- 58239
mjd 58271 - data with boss, apogee, manga

Examples:
timeTrack.py -a -m1 58268 -m2 58269 -v
timetrack.py -a -m1 58268 -m2 58269 
timetrack.py -a -m1 58240 -m2 58270 -v  
timetrack.py -b -v 
timetrack.py -b -m1 58240 -m2 58270 -v

timetrack.py -b -a -m  -m1 58271 -m2 58271

'''

import argparse
#import time
import eboss, log_manga
from bin import mjd
from python import apogee_data
import warnings
warnings.filterwarnings('ignore')

if __name__ == "__main__":
    print("Current mjd=", mjd.curSjd())
    desc = 'list of files for time tracking report '
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m1', '--mjd1', help='start mjd, default current mjd', default=mjd.curSjd(), type=int)
    parser.add_argument('-m2', '--mjd2', help='end mjd, default current mjd', default=mjd.curSjd(), type=int)           
    parser.add_argument('-a', '--apogee',  help='get apogee report',  action="store_true") 
    parser.add_argument('-b', '--boss',  help='get boss report',  action="store_true") 
    parser.add_argument('-m', '--manga',  help='get manga report',  action="store_true") 
    parser.add_argument('-v', '--verbose',  help='verbose data',  action="store_true") 
    args = parser.parse_args()   
    #if args.mjd2 == None: args.mjd2=args.mjd1+1

    if args.boss: 
        eboss.eboss(args.mjd1, args.mjd2, args.verbose)
       
    if args.apogee: 
        apogee_data.apogee (args.mjd1, args.mjd2, args.verbose)
        
    if args.manga: 
        log_manga.manga(args.mjd1, args.mjd2, args.verbose)
    
    print("-------------------------------------------------------------") 
    print("")