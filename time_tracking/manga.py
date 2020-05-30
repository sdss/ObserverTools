#!/usr/bin/env python

'''
Manga good example
timetrack.py -m  -m1 58243 -m2 58244 -v

timetrack.py -m  -m1 58625 -m2 58625 -v  #  Manga, Mastar, Apogee

'''

import glob
import re
import grepfitsLib
import configparser

from sdss.internal.database.connections.APODatabaseAdminLocalConnection import db
import sdss.internal.database.apo.platedb.ModelClasses as platedb


# create a config parser object
config = configparser.RawConfigParser()
config.read('config.cfg')
pref = config.get('path_prefix', 'pref')

def getFiles(mask):
    files = glob.glob(mask)
    return sorted(files)

def getManga(mjd1, mjd2, verbose):
    path_red="/data/spectro/"
    red="sdR-b1-*.fit.gz"
    reg="\d{8}" #  sdR-b1-00270127.fit.gz
    plates={}
    
    for mjd in range (mjd1, mjd2+1):
        path="%s%s%s/%s"  % (pref, path_red, mjd, red)
        files=getFiles(path)
        if verbose: 
            print("      -------", mjd, "nFiles=", len(files))
            print("mjd   expNum   flavor   ct  plate  exp   dith Plate_type      Lead")
        nexp=0;  
        for i,f in enumerate(files):
            ind=re.search(reg, f); expNum=f[ind.start():ind.end()]
            
            fl=grepfitsLib.grepfitsPro(['','FLAVOR,PLATETYP,CARTID,PLATEID,EXPTIME,MGDPOS,SRVYMODE',f]);  
            flavor=fl[1][1].strip()
            PLATETYP=fl[1][2].strip()  # plateType
            CARTID=fl[1][3]
            PLATEID=fl[1][4]; plate=int(PLATEID)
            EXPTIME=float(fl[1][5]);
            MGDPOS=fl[1][6].strip()   #  dither ? 
            SRVYMODE=fl[1][7].strip();  lead=SRVYMODE  # [:6]  # lead survey ? 
            
            # filter: apogee-manga plate only;  science exp; 
            if  (PLATETYP != "APOGEE-2&MaNGA") :  continue
            if  (flavor !="science"):  continue
            #if  (EXPTIME < 25) : continue
                                 
            if verbose:    
                print("%5s %8s %-7s  %2s  %5s  %5.1f  %2s  %-14s  %-15s " % \
                 (mjd,expNum,flavor, CARTID,PLATEID,EXPTIME,MGDPOS,PLATETYP, lead))
            
            nexp=nexp+1
            if plate in plates:
                plates[plate][0]=plates[plate][0]+1
                plates[plate][3]=plates[plate][3]+MGDPOS
            else: 
                plates[plate]=[1,EXPTIME,lead, MGDPOS,CARTID,PLATETYP]
                
    return plates


def manga_str(plates, verbose):
    print("")
    print("**** MANGA summary ****")    

    session = db.Session()
    nExp=0;   nCompleted=0
    for plate in sorted(plates.keys()):
        nExp=nExp+plates[plate][0]
        plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one()
        mjdCompleted=None 
        donness=plateObj.calculatedCompletionStatus()  
        if donness == "Complete":
            nCompleted=nCompleted+1
    print(nExp, nCompleted)

    #nExp=0
    #for plate in sorted(plates.keys()):
    #    nExp=nExp+plates[plate][0]
    #print "Npl=%s, Nexp=%s"  % (len(plates), nExp)
    #print "Plates: ", sorted(plates.keys())
    
    mPlates=[];  apExp=0;  mExp=0
    tripl=0; orphan=0;  nd=0; sd=0; ed=0;
    other_lead=0;  other_exposures=0; other_plates=[]
    for plate in sorted(plates.keys()):
        if ("MaNGA dither" in plates[plate][2]):  # manga lead
             mPlates.append(plate)         # list of plates
             mExp1=plates[plate][0]
             nd1=plates[plate][3].count("N")
             sd1=plates[plate][3].count("S")
             ed1=plates[plate][3].count("E")
             tripl1=min(nd1,sd1,ed1)
             orphan1=mExp1-3*tripl1

             mExp=mExp+mExp1
             nd=nd+nd1; sd=sd+sd1;  ed=ed+ed1
             tripl=tripl+tripl1
             orphan=orphan+orphan1 

        elif ("APOGEE lead" in plates[plate][2]):
             apExp=apExp+plates[plate][0]
        #elif ("None" in plates[plate][2]):
		#     apExp=apExp+plates[plate][0]
        else: 
            other_lead=other_lead+1
            other_exposures=plates[plate][0]
            other_plates.append(plate)
		    
    a=0
    print("")
    print("MaNGA: completed %s plates", "among %s observed." % (len(mPlates)))
    print("  - %3s manga-dither exposures  (%d x'N', %d x'S', %s x'E') " % (mExp, nd,sd, ed))
    print("          %3s 'NSE' triplets  and %s  orphan exposures" % (tripl, orphan))
    print("  - %3s manga 'C' exposures obtained on APOGEE-led co-obs plates" % (apExp))
    print("  - addition %s exposures on %s other lead plates:" % (other_exposures, other_lead))
    print("")
    
    print("List of observed MaNGA_dither plates:")
    print(mPlates)  
    print("List of observed other MaNGA plates:")
    print(other_plates)
    

    print("")    
    print("  -MaNGA dither-")
    print("Ct   Plate  Nexp Texp  Plate_Name   Plate_Type      Lead            Observations")
    for plate in sorted(plates.keys()):
        if "MaNGA dither"  in plates[plate][2]: 
            print("%2s   %5s   %2d   %3d               %s  %-14s  %s  " % \
                (plates[plate][4], plate, plates[plate][0],plates[plate][1],plates[plate][5] ,plates[plate][2],plates[plate][3], ))   
    print("")
    print("   -Other lead-") 
    print("Ct   Plate  Nexp Texp  Plate_Name   Plate_Type      Lead            Observations")
    for plate in sorted(plates.keys()):
        if ("MaNGA dither" not in plates[plate][2]) and "APOGEE lead" not in plates[plate][2]: 
            print("%2s   %5s   %2d   %3d               %s  %-14s  %s  " % \
                (plates[plate][4], plate, plates[plate][0],plates[plate][1],plates[plate][5] ,plates[plate][2],plates[plate][3], ))   

    print("")
    print("  -APOGEE lead-")
    print("Ct   Plate  Nexp Texp  Plate_Name   Plate_Type      Lead            Observations")
    for plate in sorted(plates.keys()):
        if "APOGEE lead" in plates[plate][2]: 
            print("%2s   %5s   %2d   %3d               %s  %-14s  %s  " % \
                (plates[plate][4], plate, plates[plate][0],plates[plate][1],plates[plate][5] ,plates[plate][2],plates[plate][3], ))   


    return None


def manga(mjd1, mjd2, verbose):
    print("------------------------------------------------------------------") 
    print("MANGA plates searching: %s -- %s,  wait ..  " % (mjd1, mjd2))
    print("------------------------------------------------------------------") 
    plates=None 
    plates=getManga(mjd1, mjd2, verbose) 
    if plates == None:
        print("  ...  did not find anything ")     
    else:
        manga_str(plates,verbose)
    return None
