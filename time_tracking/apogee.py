#!/usr/bin/env python
    
'''
Author Elena Malanushenko
Program to make summary of Apogee observations 
for time tracking report. 

Use '/data/apogee/quickred/<mjd>' directry to scan files. 
Read header  and filter out data if EXPTYPE !="OBJECT"
Run this main program for test. 

This program uses autoschedule, need to set up
module use /home/sdss4/products/Linux64/moduleFiles
module load autoscheduler  

Updates:
2019-05-31 DO added lines 105 and 106 in order for the new dither positions to reflect 'A' and 'B' correctly.
2019-10-09 EM  Added the completeness of apogee plates using authoschedule. Consuted with John Donnor.
'''

import glob
import re
import grepfitsLib
import configparser

from sdss.internal.database.connections.APODatabaseAdminLocalConnection import db
import sdss.internal.database.apo.platedb.ModelClasses as platedb

config =configparser.RawConfigParser()
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
            print("      -------", mjd, "nFiles=", len(files))
            print("mjd   expNum    imtype  ct plate  Nrd   Dith  Plate_type      Lead")

        nexp=0; 
        for i,f in enumerate(files):
            #print i, f
            ind=re.search(regex, f); expNum=f[ind.start():ind.end()]
            fl=grepfitsLib.grepfitsPro(['',\
               'EXPTYPE,CARTID,PLATEID,NFRAMES,DITHPIX,PLATETYP,SRVYMODE',f])
            EXPTYPE=fl[1][1].strip();   
            exptype=EXPTYPE[:6]  # imtype

            # filter out if  not science exp
            if  (EXPTYPE !="OBJECT"):  continue

            CARTID=fl[1][2].strip()
            PLATEID=fl[1][3].strip(); 
            #print EXPTYPE, CARTID, PLATEID

            plate=int(PLATEID)
            NFRAMES=fl[1][4].strip(); nframes=int(NFRAMES)
            DITHPIX=fl[1][5].strip(); dithpix=float(DITHPIX)
            PLATETYP=fl[1][6].strip()
            SRVYMODE=fl[1][7].strip();  lead=SRVYMODE #[:6]
 
            if dithpix == 12.994:  dith="A"
            elif  dithpix == 13.499:  dith="B"
            elif  dithpix == 10.495:  dith="A"
            elif  dithpix == 11.0:  dith="B"
            else: "?"
  
            if verbose:
                print("%5s %8s  %-7s %2s %5s   %2d   %1s     %-14s  %s" % \
                   (mjd,  expNum, exptype, CARTID, plate, nframes, dith, PLATETYP, lead))

            nexp=nexp+1
            if plate in plates:
                plates[plate][0]=plates[plate][0]+1
                plates[plate][3]=plates[plate][3]+dith
            else: 
                plates[plate]=[1,nframes, lead, dith, PLATETYP,CARTID]
    return plates
     
   
def ap_str(plates, mjd1, mjd2):
    print("")
    
    session = db.Session()

    # plates[plate][4]   Plate_type
    # plates[plate][2]  Plate_lead
    apPlates=[] # list of apogee lead plates 
    apExp=0;  # total number of exposures
    ad=0;  bd=0;  pairs=0; orphan=0; #  number of A, B, pairs and orphan 
    dblPairs=0; dblOrp=0  #  pairs and orphan  for DBA
    mPlates=[];   # list of other lead plates
    mExp=0;       #  total number of exposures for other plates
    dblExp=0     # do not use for now, reserved for DBA for other lead observations

    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if (tp=="APOGEE-2&MaNGA" and ld=="APOGEE lead") or (tp=="APOGEE-2" and ld=="None"):
        #if ("APOGEE" in plates[plate][2]) or ("None" in plates[plate][2]):  
            apPlates.append(plate) 
            
            # numbers for this plate
            apExp1=plates[plate][0]  # total number of exposures , A  or B
            ad1=plates[plate][3].count("A")   # number "A"
            bd1=plates[plate][3].count("B")   # number "B"
            pairs1=min(ad1,bd1)      # number of pairs
            orphan1=apExp1-pairs1*2   # number of orphans 

            # add plate numbers to total numbers  
            apExp=apExp+apExp1
            ad=ad+ad1; bd=bd+bd1; 
            pairs=pairs+pairs1
            orphan=orphan+orphan1 
            
            # select double exposures
            if plates[plate][1]==94:
                dblPairs=dblPairs+pairs1  # pairs for DBA
                dblOrp=dblOrp+orphan1   # orphans for DBA
        else:        
            mPlates.append(plate)   # list of other plates
            mExp=mExp+plates[plate][0]   #  total number of exposures for other plates
    
    from autoscheduler.plateDBtools.apogee import get_apogee_plates
    
    apDone=[];   apNotDone=[] 
    print("Autosheduler query:") 
    platesD = get_apogee_plates.get_plates(plateList=apPlates)
    for p in platesD:
        if p.pct() >= 1.0:
            hist=p.hist.split(",");   lastMjd=int(hist[-2])-2400000;   
            # print p.plateid,  "    history=", p.hist, "  last=", lastMjd, "end =", mjd2
            if lastMjd <=mjd2:
                apDone.append(p.plateid)
            else:
                apNotDone.append(p.plateid)
        else:
            apNotDone.append(p.plateid)
    
    bold='\033[01m' ;  reset='\033[0m'
    print("")
    print(bold, "**** Apogee summary ****", reset)    
    print("")
    
    red='\033[31m'
    black='\033[30m'
    print(red, "APOGEE-2: completed %s plates among %s observed." % (len(apDone), len(apPlates)))
    print("  - %3d apogee-led exposures  (%d x'A', %d x'B')" % (apExp, ad,bd))
    print("  - %3d AB-exposure pairs obtained on APOGEE-led plates + %s single A or B"  % \
        (pairs, orphan))
    print("         including %s x double DAB-exposure pairs and %s unpaired"  % \
        (dblPairs, dblOrp))
    print("  - %3s short SAB-exposures  pairs obtained on MaNGA-led co-obs plates" % (mExp/2), black)
    
    print("")
    print("Observed APOGEE-lead plates: %s " % (len(apPlates)))
    print("   ", apPlates)
    
    print("Completed  APOGEE-lead plates:  %s" % (len(apDone)))
    print("   ", apDone)

    print("Not completed APOGEE-lead plates:  %s" % (len(apNotDone)))
    print("   ", apNotDone)

    print("Observed Non-APOGEE plates:  %s " % (len(mPlates)))
    print("   ", mPlates)


    # plates[plate][4]   Plate_type
    # plates[plate][2]  Plate_lead
    # APOGEE-2&MaNGA    APOGEE lead 
    # APOGEE-2          None - use any ld    
    # APOGEE-2&MaNGA    MaNGA dither
    # APOGEE-2&MaNGA    MaNGA Globular
    # APOGEE-2&MaNGA    MaStar
    
    print("")
    print(bold,"APOGEE-2&MaNGA  and APOGEE lead", reset)  
    print("Plate   Nexp Nread Plate_name           Plate_type        Lead          Done? Observations ")
    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if tp=="APOGEE-2&MaNGA" and ld=="APOGEE lead":
            plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one() 
            # donness=plateObj.calculatedCompletionStatus() - not valid for apogee
            if plate in apDone:
                 dd="Done"
            else:
                 dd="No  " 
            print("%5s   %2d    %2d   %-18s   %-15s   %-10s   %s  %s" % \
                (plate, plates[plate][0], plates[plate][1],  plateObj.name,  plates[plate][4], plates[plate][2],dd, plates[plate][3] ))  

    print("") 
    print(bold,"APOGEE-2", reset)  
    print("Plate   Nexp Nread Plate_name           Plate_type        Lead          Done?  Observations ")
    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if tp=="APOGEE-2":
            plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one() 
            # donness=plateObj.calculatedCompletionStatus() - not valid for apogee
            if plate in apDone:
                 dd="Done"
            else:
                 dd="No  " 
            print("%5s   %2d    %2d   %-18s   %-15s   %-12s  %s   %s" % \
                (plate, plates[plate][0], plates[plate][1],  plateObj.name,  plates[plate][4], plates[plate][2],dd, plates[plate][3] ))  

    print("")
    print(bold,"APOGEE-2&MaNGA but not APOGEE lead", reset)  
    print("Plate   Nexp Nread Plate_name           Plate_type        Lead          Done?  Observations ")
    for plate in sorted(plates.keys()):
        tp=plates[plate][4]; ld=plates[plate][2]
        if tp=="APOGEE-2&MaNGA" and ld !="APOGEE lead":
            plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one() 
            # donness=plateObj.calculatedCompletionStatus() - not valid for apogee
            print("%5s   %2d    %2d   %-19s  %-15s   %-12s  -      %s" % \
                (plate, plates[plate][0], plates[plate][1],  plateObj.name.strip(),  plates[plate][4], plates[plate][2],plates[plate][3] ))  

    print('')
    return None
    
    
def apogee (mjd1, mjd2, verbose):
    print("-------------------------------------------------------------") 
    print("Apogee plates searching: %s -- %s,  wait ..  " % (mjd1, mjd2))
    print("-------------------------------------------------------------") 

    #plates=None 
    plates=getApogee(mjd1, mjd2, verbose)
    if None in plates:
        print("  ...  did not find anything ")     
    else:
        ap_str(plates, mjd1, mjd2)

if __name__ == "__main__":
    mjd1=58760;  mjd2=58766
    apogee(mjd1,mjd2,'')
