#!/usr/bin/env python

# EM 
#  program to check if guider shutter works properly with flats
#  1) calculate mean and std in dark area not affected by bad shutter  
#  as nx=100;  mean=int(npData[:,0:nx].mean())
#  2) calculate indexes of pixels more then 2500 (belong to fibers) and 
#   re-set them to mean value               
#  3) set threshhold level 20% above mean, get number of pixels above that 
#  level. If more then 10000, consider this image as potensially 
#  illuminated with not proper closed shutter.                  

#  gShutterCheck.py 56378 56379
#--------------------------------------------------
#   i   mjd  dir  files flats  bad    % 
#--------------------------------------------------
#   0  56378  1  1097    24     3
#       /data/gcam/56378/gimg-0266.fits
#       /data/gcam/56378/gimg-0269.fits
#       /data/gcam/56378/gimg-0518.fits
#   1  56379  0     0     0     0
#--------------------------------------------------
#Summary for guider flats  MJDs  56378 -- 56379: 
#    total flats=24 
#    bad flats=3 
#    percent = 12% 
#--------------------------------------------------

# history 
# 2013/05/21 EM:  added argparse input


import sys, os
import glob, pyfits, numpy
import argparse

desc = "program to check if guider shutter closes properly (using flats) "
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("mjd1", help="start mjd", type=int)
parser.add_argument("mjd2", help="end mjd ", type=int)
parser.add_argument('-l', '--list', help='print bad file names', dest="list", action='store_true')
args = parser.parse_args()   

mjd1=args.mjd1
mjd2=args.mjd2
mjdsList=sorted([mjd1, mjd2])
mjds=range(mjdsList[0], mjdsList[1]+1)

def prnLine(j, mjd, nfiles=0,  nflats=0,  nbad=0, pers='n/a'):
       ss="%4i  %5i  %4i  %4i  %4i    %5.1f"  % (j, mjd, nfiles, nflats, nbad, pers)
       print ss

header="   i   mjd   files  flats   bad    % "   
width = 50
print "Checking guider flats for MJDs  %s - %s" % (mjdsList[0], mjdsList[1])
print "-"*width
print header
print "-"*width

nflatsTot=0
nbadTot=0
for j, m in enumerate(mjds): 
    mdir="/data/gcam/%s/" % (m)
    if  os.path.exists(mdir)  != True:
        # prnLine(j, m,)
         print "%4i  %5i - no directory"  % (j, m,)
         continue
    ndirs=1
    files = glob.glob(mdir+'/gimg-*.fits.gz')
    nfiles= len(files)
    if  nfiles  == 0:
      #  prnLine(j, m, ndirs) 
         print "%4i  %5i - no files in this directory"  % (j, m,)
         continue
         
    nflats=0
    nbad=0
    nbadList=[]
    nbadLev=[]
    for f  in sorted(files) :
         hdulist=pyfits.open(f,'readonly')
         hdr = hdulist[0].header
         imType=hdr['IMAGETYP']
         if imType.strip() == 'flat':
              nflats=nflats+1
              data=hdulist[0].data
              npData=numpy.array(data)
#  calculate mean and std in dark area not affected by bad shutter  
              nx=100
              mean=int(npData[:,0:nx].mean())
              std=int(npData[:,0:nx].std())
              
#  calculate indexes of pixels more then 2500 (belong to fibers) and 
#  re-set them to mean value               
              ll=numpy.where(npData > 2500)
              npData[ll]=mean
#  set level of threshhold level 20% above mean, 
#  if number of pixels above level more then 10000, 
# consider this image as bad, affected with not closed shutter.                  
              level=mean*0.2
              ll=numpy.where(npData > mean+level)
              if len(ll[0]) > 10000:  
                    nbad= nbad+1
                    nbadList.append(f)
                    nbadLev.append(len(ll[0]))
         else:
              pass
         hdulist.close()
    if nflats==0:  proc=0.0
    else:  proc=nbad*100.0/nflats     
    prnLine(j, m,  nfiles, nflats, nbad, proc) 
    if args.list: 
         for fbad, lev in zip(nbadList,nbadLev):
              print  "        %s %7i " % (fbad, lev)
    nflatsTot=nflatsTot+nflats 
    nbadTot=nbadTot+nbad

print "-"*width
#print "Summary for guider flats  MJDs  %s - %s:"   % (mjdsList[0], mjdsList[1])
s1="Total flats = %s"  % nflatsTot
s2="Bad flats = %s"  %   nbadTot
if nflatsTot !=0:  pers=nbadTot*100/nflatsTot
else:  pers=0
s3="Percent = %5.1f" % ( pers) + '%'
print " %s, %s, %s" % (s1,s2,s3)
# print "-"*width


