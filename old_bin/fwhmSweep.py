#!/usr/bin/env python

# usage: 
# fwhmSweep.py <mjd> <file number first> <file nimber last>
# python fwhmSweep.py 58652 100 150

import glob
import pyfits
import sys, os
import numpy as np
from scipy import ndimage  
from pylab import *

if len(sys.argv) < 4:
    print("Example:  python fwhmSweep.py 58652 100 150")
    sys.exit("fwhmSweep.py <mjd> <file1> <file2>")

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
indArr=[]

for i in range(f1,f2+1):
     ff='gimg-%04d' % (i)
     indArr.append(i)
     fname='%s%s.fits' % (directory,ff)
     if os.path.exists(fname):
        hdulist=pyfits.open(fname,'readonly')
        hdr = hdulist[0].header
        imType=hdr['IMAGETYP']
        if imType.strip() == 'object':
        #if True:
             dat = np.array(hdulist[0].data)
             datMax=dat.max() ;  
             datMin=dat.min(); 
             datHm=datMin+(datMax-datMin)/2.0
             cx,cy=ndimage.measurements.center_of_mass(dat>datHm)
             ll=np.where(dat > datHm); 
             nsq=len (ll[0])
             fw=2.0*np.sqrt(nsq/3.14); fwhmPix.append(fw)
             koeff=0 
             if hdr['BINX']==1 and hdr['BINY']==1:
                  koeff=0.428/2.
             elif hdr['BINX']==2 and hdr['BINY']==2:
                  koeff=0.428
             else: 
                  koeff=0 
                  print("unknown binning")

             fw1=fw*koeff;   
    #         fwhmArr.append(fw)
             fwhmArr.append(fw1)
             if 'FOCUS' in hdr:
                 foc=hdr['FOCUS']
             else: foc=None
             focArr.append(foc)
             print("%s,  centerX=%4i,  centerY=%4i, fwhm=%5.2f pix, fwhm = %4.2f arcsec,  foc=%s" % (ff,  cy, cx,  fw, fw1, foc))
        else:
            print("%s -- %s " % (ff,imType))    
        hdulist.close()
     else:
        print("%s -- no file" % (ff)) 

#to_plot=False
#if to_plot:
  #  plot(focArr, fwhmArr, 'ro')
#    plot(indArr, fwhmArr, 'ro-')
  #  xlabel('focus')
  #  plot(indArr, focArr, 'bo-')
  #  ll=len(indArr)
 #   axis([,,0, 5]); 
 #   grid(True)
  
    
 #   ylabel('fwhm, pix')
 #   show()

#array = scipy.array(focArr)
#dd=array.max()
#print dd

#ax1 = subplot(111)
#t = arange(0.01, 10.0, 0.01)
#s1 = exp(t)
#plot(t, s1, 'b-')
#pylab.ylim([0,1000])

#plot(focArr, fwhmPix, 'b-')
#xlabel('Focus')
#ylabel('FWHM, pixels')

#ax2 = twinx()
#s2 = sin(2*pi*t)
#plot(t,  fwhmArr, 'r.')
#plot(focArr, fwhmArr, 'r.')
#ylabel('FWHM, arcsec')
#ax2.yaxis.tick_right()

#show()
