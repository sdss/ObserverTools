#!/usr/bin/env python 

# python fwhm.py <mjd> <fileNumber>
# python fwhm.py 55799 0021
# ff=/data/ecam/55799/gimg-0021.fits

import sys, os
import pyfits as pf
import numpy as np
from scipy import ndimage    

ff="/data/ecam/%s/gimg-%04d.fits" % (sys.argv[1], int(sys.argv[2]))
#ff="/data/ecam/55799/gimg-0012.fits"
#ff="gimg-0021.fits"
#ff="test.fits"

tt=os.path.exists(ff)
if tt != True:	
    sys.exit("Error: file does not exist:  ff= %s  " % (ff))

hdulist = pf.open(ff) # open a FITS file
hdr = hdulist[0].header
dat= np.array(hdulist[0].data)
hdulist.close()

datMax=dat.max() ;  
datMin=dat.min(); 
datHm=datMin+(datMax-datMin)/2.0

cx,cy=ndimage.measurements.center_of_mass(dat>datHm)

ll=np.where(dat > datHm); 
nsq=len (ll[0])

koeff=0 
if hdr['BINX']==1 and hdr['BINY']==1:
    koeff=0.428/2.
elif hdr['BINX']==2 and hdr['BINY']==2:
    koeff=0.428
else: 
    koeff=0 
    print "unknown binning"

foc=hdr['FOCUS']
fw=2.0*np.sqrt(nsq/3.14)

#print "%s,  CenterX=%4i,  CenterY=%4i,  fwhm=%4.2f" % (ff,  cy, cx,  fw*0.428)
ss="%s,  Xcen=%4i, Ycen=%4i, fwhm=%5.2f, fwhm=%5.2f(arcsec), foc=%s" % (ff,  cy, cx,  fw, fw*koeff, foc )
print ss


#idx =np.where(dat == datMax)
#print idx
