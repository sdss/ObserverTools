#!/usr/bin/env python

# usage: 
# fwhmSweep.py 56530 7 14
# fwhmSweep.py <mjd> <file number first> <file nimber last>


import glob
import pyfits
import sys, os
import numpy as np
from scipy import ndimage  
from pylab import *
import scipy

directory="/data/ecam/%s/" % (sys.argv[1])

# if directory exist? 
if  os.path.exists(directory)  != True:	
    sys.exit("Error: no directory  %s  " % (directory))
print(directory)

f1=int(sys.argv[2])
f2=int(sys.argv[3])

fwhmArr=[]
fwhmPix=[]
focArr=[]

for i in range(f1,f2):
     ff='gimg-%04d' % (i)
     fname='%s%s.fits' % (directory,ff)
     if os.path.exists(fname):
        hdulist=pyfits.open(fname,'readonly')
        hdr = hdulist[0].header
        imType=hdr['IMAGETYP']
        if imType.strip() == 'object':
             dat = np.array(hdulist[0].data)
             datMax=dat.max() ;  
             datMin=dat.min(); 
             datHm=datMin+(datMax-datMin)/2.0
             cx,cy=ndimage.measurements.center_of_mass(dat>datHm)
             ll=np.where(dat > datHm); 
             nsq=len (ll[0])
             fw=2.0*np.sqrt(nsq/3.14); fwhmPix.append(fw)
             fw1=fw*0.428;   fwhmArr.append(fw1)
             if 'FOCUS' in hdr:
                 foc=hdr['FOCUS']
             else: foc=None
             focArr.append(foc)
             print("%s,  centerX=%4i,  centerY=%4i, fwhm = %4.2f pix, fwhm = %4.2f arcsec,  foc=%s" % (ff,  cy, cx,  fw, fw1, foc))
        else:
            print("%s -- %s " % (ff,imType))    
        hdulist.close()
     else:
        print("%s -- no file" % (ff)) 

#plot(focArr, fwhmArr, 'ro')
#xlabel('Focus')
#ylabel('fwhm, arcsec')
#show()

arrayPix = scipy.array(fwhmPix)
minPix=arrayPix.min()-(arrayPix.max()-arrayPix.min())*0.1
maxPix=arrayPix.max()+(arrayPix.max()-arrayPix.min())*0.1

arrayFoc = scipy.array(focArr)
polycoeffs = scipy.polyfit(arrayFoc, arrayPix, 2)
yfit = scipy.polyval(polycoeffs, arrayFoc)
foc=-polycoeffs[1]/(2.0*polycoeffs[0])
print("Focus = ",foc)

from scipy.interpolate import interp1d
xnew = np.linspace(arrayFoc.min(),arrayFoc.max(), 20)
yfitNew = scipy.polyval(polycoeffs, xnew)
f2 =interp1d(xnew, yfitNew, kind='cubic')

ax1 = subplot(111)
title("ecam focus sweep")
ylim([minPix,maxPix])
xlabel('Focus')
ylabel('FWHM, pixels')
ax1.grid(True, color="blue")
plot(xnew, f2(xnew), '--')
plot(focArr, fwhmPix, 'r.', markersize=10)
#ax1.annotate('local min = %s' % foc,xy=(foc, arrayPix.max()), xytext=(foc, 5),)

ax2 = twinx()
plot(focArr, fwhmArr, 'r.')
ylabel('FWHM, arcsec')
ax2.yaxis.tick_right()
ylim([minPix*0.428,maxPix*0.428])
#ax2.grid(True, color="red")

show()
