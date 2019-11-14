#!/usr/bin/env python
    
'''
(SJD 58240) - (SJD 58270)

path for remote 
used ExpanDrive and work on my computer
ls /Volumes/observer@sdss4-hub/data/apogee/utr_cdr

read raw data from utr_cdr:
read 'IMAGETYP' only (no plate and dither here)
ff='/Volumes/observer@sdss4-hub/data/apogee/utr_cdr/58268/apRaw-27060018.fits'
hdr = pyfits.getheader(ff) >> print hdr  
print hdr.get('IMAGETYP') >> Object
hdr.get('IMAGETYP')=='Object'  >> True

ff='/Volumes/observer@sdss4-hub/data/apogee/utr_cdr/58268/apRaw-27060049.fits'
regex="apRaw-\d{8}.fits"
m = re.search(regex, ff)
print ff[m.start():m.end()]  >  apRaw-27060049.fits
regex="\d{8}";  
m = re.search(regex, ff)
print ff[m.start():m.end()]  >  27060049

import pyfits
f='/Volumes/observer@sdss4-hub/data/apogee/quickred/58268/ap2D-a-27060049.fits.fz'
hdr = pyfits.getheader(f)
print hdr
print hdr.get('DITHPIX') >> 13.499
print hdr.get('EXPTYPE') >> OBJECT
    exp=27060003
print hdr.get('EXPTYPE')  >> QUARTZFLAT    

can simplify algprithm if use just quick reduction and do not use raw files 
at all, all information there. 

plates={}  
plate=900; nreads=94
plates[plate]=[1, nreads]
plates[plate][0]=plates[plate][0]+1
plates[plate]= [2, 94]

May 31, 2019 -- DO added lines 105 and 106 in order for the new dither positions to reflect 'A' and 'B' correctly.
'''

import glob
import re
import pyfits
import grepfitsLib
import ConfigParser

from sdss.internal.database.connections.APODatabaseAdminLocalConnection import db
import sdss.internal.database.apo.platedb.ModelClasses as platedb


config =ConfigParser.RawConfigParser()
config.read('config.cfg')
pref = config.get('path_prefix', 'pref')

def getFiles(mask):
    files = glob.glob(mask)
    return sorted(files)


def getApogee(mjd1, mjd2, verbose):
    path_red='/data/apogee/quickred/'
    red='ap2D-a-*.fits.fz'
    regex="\d{8}"; 
    plates={}
    
    for mjd in range (mjd1, mjd2+1):
        path="%s%s%s/%s"  % (pref, path_red, mjd, red)
        files=getFiles(path)
        if verbose:
            print  "      -------", mjd, "nFiles=", len(files)
            print "mjd   expNum    imtype  ct plate  Nrd   Dith  Plate_type      Lead"

        nexp=0; 
        for i,f in enumerate(files):
            #print i, f
            ind=re.search(regex, f); expNum=f[ind.start():ind.end()]
            fl=grepfitsLib.grepfitsPro(['',\
               'EXPTYPE,CARTID,PLATEID,NFRAMES,DITHPIX,PLATETYP,SRVYMODE',f])
            EXPTYPE=fl[1][1].strip();   
            exptype=EXPTYPE[:6]  # imtype

            # filter out:  not science exp; short exp; apogee-manga plate
            if  (EXPTYPE !="OBJECT"):  continue

            CARTID=fl[1][2].strip()
            PLATEID=fl[1][3].strip(); 
            #print EXPTYPE, CARTID, PLATEID

            plate=int(PLATEID)
            NFRAMES=fl[1][4].strip(); nframes=int(NFRAMES)
            DITHPIX=fl[1][5].strip(); dithpix=float(DITHPIX)
            PLATETYP=fl[1][6].strip()
            SRVYMODE=fl[1][7].strip();  lead=SRVYMODE #[:6]

            # filter out:  not science exp; short exp; apogee-manga plate
            
            if dithpix == 12.994:  dith="A"
            elif  dithpix == 13.499:  dith="B"
            elif  dithpix == 10.495:  dith="A"
            elif  dithpix == 11.0:  dith="B"
            else: "?"
  
            if verbose:
                print "%5s %8s  %-7s %2s %5s   %2d   %1s     %-14s  %s" % \
                   (mjd,  expNum, exptype, CARTID, plate, nframes, dith, PLATETYP, lead)

            nexp=nexp+1
            if plate in plates:
                plates[plate][0]=plates[plate][0]+1
                plates[plate][3]=plates[plate][3]+dith
            else: 
                plates[plate]=[1,nframes, lead, dith, PLATETYP,CARTID]
    return plates
     
   
def ap_str(plates, mjd1, mjd2):
    print ""
    print "**** Apogee summary ****"    
    #print plates
    #nExp=0
    #for plate in sorted(plates.keys()):
    #    nExp=nExp+plates[plate][0]
    #print "Npl=%s, Nexp=%s, Npairs =%s"  % (len(plates), nExp, nExp/2.0)
    #print "Plates: ", sorted(plates.keys())
    #print  sorted(plates.keys())
    
#    MaNGA: completed %s plates among 5 observed.
#  -  42 manga-led exposures  (14 x'N', 14 x'S', 14 x'E') 
#           14 'NSE' triplets  and -24  orphan exposures
#  -  26 manga 'C' exposures obtained on APOGEE-led co-obs plates

    session = db.Session()


    # plates[plate][4]   Plate_type
    # plates[plate][2]  Plate_lead
    apPlates=[];  mPlates=[];  apExp=0; mExp=0; dblExp=0
    ad=0;  bd=0; pairs=0; orphan=0; dblPairs=0; dblOrp=0
    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if (tp=="APOGEE-2&MaNGA" and ld=="APOGEE lead") or (tp=="APOGEE-2" and ld=="None"):
        #if ("APOGEE" in plates[plate][2]) or ("None" in plates[plate][2]):  
            apPlates.append(plate)
            
            apExp1=plates[plate][0]
            ad1=plates[plate][3].count("A")
            bd1=plates[plate][3].count("B")
            pairs1=min(ad1,bd1)
            orphan1=apExp1-pairs1*2

            apExp=apExp+apExp1
            ad=ad+ad1; bd=bd+bd1; 
            pairs=pairs+pairs1
            orphan=orphan+orphan1 
            
            if plates[plate][1]==94:
                dblPairs=dblPairs+pairs1
                dblOrp=dblOrp+orphan1
        else:        
            mPlates.append(plate)
            mExp=mExp+plates[plate][0]
    
    
    print "APOGEE-2: completed %s plates", "among %s observed." % (len(apPlates))
    print "  - %3d apogee-led exposures  (%d x'A', %d x'B')" % (apExp, ad,bd)
    print "  - %3d AB-exposure pairs obtained on APOGEE-led plates + %s single A or B"  % \
        (pairs, orphan)
    print "         including %s x double DAB-exposure pairs and %s unpaired"  % \
        (dblPairs, dblOrp)
    print "  - %3s short SAB-exposures  pairs obtained on MaNGA-led co-obs plates" % (mExp/2)
    print ""
    print "List of observed APOGEE-2 plates:"
    print apPlates
    
    print ""      

    # plates[plate][4]   Plate_type
    # plates[plate][2]  Plate_lead
    # APOGEE-2&MaNGA    APOGEE lead 
    # APOGEE-2          None - use any ld    
    # APOGEE-2&MaNGA    MaNGA dither
    # APOGEE-2&MaNGA    MaNGA Globular
    # APOGEE-2&MaNGA    MaStar
    
    print ""
    print "APOGEE-2&MaNGA  and APOGEE lead"
    print  "Ct   Plate   Nexp Nread Plate_name             Plate_type        Lead             Observations "
    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if tp=="APOGEE-2&MaNGA" and ld=="APOGEE lead":
            plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one() 
            # donness=plateObj.calculatedCompletionStatus() - not valid for apogee
            print "%2s   %5s   %2d    %2d   %-20s   %-15s   %-14s   %s" % \
                (plates[plate][5], plate, plates[plate][0], plates[plate][1],  plateObj.name,  plates[plate][4], plates[plate][2],plates[plate][3] )  

    print "" 
    print "APOGEE-2"
    print  "Ct   Plate   Nexp Nread Plate_name             Plate_type        Lead             Observations "
    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if tp=="APOGEE-2":
            plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one() 
            # donness=plateObj.calculatedCompletionStatus() - not valid for apogee
            print "%2s   %5s   %2d    %2d   %-20s   %-15s   %-14s   %s" % \
                (plates[plate][5], plate, plates[plate][0], plates[plate][1],  plateObj.name,  plates[plate][4], plates[plate][2],plates[plate][3] )  

    print ""
    print "APOGEE-2&MaNGA but not APOGEE lead"
    print  "Ct   Plate   Nexp Nread Plate_name             Plate_type        Lead             Observations "
    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if tp=="APOGEE-2&MaNGA" and ld !="APOGEE lead":
            plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one() 
            # donness=plateObj.calculatedCompletionStatus() - not valid for apogee
            print "%2s   %5s   %2d    %2d   %-20s   %-15s   %-14s   %s" % \
                (plates[plate][5], plate, plates[plate][0], plates[plate][1],  plateObj.name,  plates[plate][4], plates[plate][2],plates[plate][3] )  

    return None
    
    
def apogee (mjd1, mjd2, verbose):
    print "-------------------------------------------------------------" 
    print "Apogee plates searching: %s -- %s,  wait ..  " % (mjd1, mjd2)
    print "-------------------------------------------------------------" 

    #plates=None 
    plates=getApogee(mjd1, mjd2, verbose)
    if None in plates:
        print  "  ...  did not find anything "     
    else:
        ap_str(plates, mjd1, mjd2)
