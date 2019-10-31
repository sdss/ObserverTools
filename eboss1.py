#!/usr/bin/env python

import glob
import re
import grepfitsLib
import ConfigParser

from sdss.internal.database.connections.APODatabaseAdminLocalConnection import db
import sdss.internal.database.apo.platedb.ModelClasses as platedb

# create a config parser object
config = ConfigParser.RawConfigParser()
config.read('config.cfg')
pref = config.get('path_prefix', 'pref')

def getFiles(mask):
    files = glob.glob(mask)
    return sorted(files)

def getBoss(mjd1, mjd2, verbose):
    path_red="/data/spectro/"
    red="sdR-b1-*.fit.gz"
    reg="\d{8}" #  sdR-b1-00270127.fit.gz
    plates={}
    
    for mjd in range (mjd1, mjd2+1):
        path="%s%s%s/%s"  % (pref, path_red, mjd, red)
        files=getFiles(path)
        if verbose: 
            print  "      -------", mjd, "---------"  # "nFiles=", len(files)
            #print "mjd   expNum   flavor   ct  plate  exp   dith Plate_type  Lead"
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
            SRVYMODE=fl[1][7].strip()  # lead survey ? 
            
            # filter out:  not science exp; short exp; apogee-manga plate
            if  (flavor !="science"):  continue
            if  (PLATETYP=="APOGEE-2&MaNGA") :  continue
            if  (EXPTIME < 850) : continue

            if verbose and nexp==0:    
                print "mjd   expNum   flavor   ct  plate  exp   dith Plate_type  Lead"           
            if verbose:    
                print "%5s %8s %-7s  %2s  %5s  %5.1f  %2s  %-10s  %-s " % \
                 (mjd,expNum,flavor, CARTID,PLATEID,EXPTIME,MGDPOS,PLATETYP, SRVYMODE)
                
            nexp=nexp+1
            if plate in plates:
                #plates[plate]=plates[plate]+1
                plates[plate][0]=plates[plate][0]+1
                plates[plate][3]=plates[plate][3]+MGDPOS
            else: 
                #plates[plate]=1
                plates[plate]=[1,CARTID, SRVYMODE, MGDPOS]

    return plates

def boss_str(plates, verbose):
    print ""
    print "**** eBOSS summary ****"    
    #print plates
    session = db.Session()
    nExp=0;   nCompleted=0
    for plate in sorted(plates.keys()):
        nExp=nExp+plates[plate][0]
        plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one()
        mjdCompleted=None 
        donness=plateObj.calculatedCompletionStatus()  
        if donness == "Complete":
            nCompleted=nCompleted+1


    print "eBOSS: completed %s plates among %s observed." % (nCompleted, len(plates))
    print "   - %s science exposures (900 sec each)"  % (nExp)
    print ""
    print "List of observed eBOSS plates:"
    print sorted(plates.keys())
    
    #print "Npl=%s, Nexp=%s"  % (len(plates), nExp)
    #print "Plates: ", sorted(plates.keys())
    print "   "
    print  "ct   Plate     Nexp "
    
    for plate in sorted(plates.keys()):
        plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one()
        mjdCompleted=None 
        mjd=0
        donness=plateObj.calculatedCompletionStatus()
        if donness == "Complete": 
            for  pl in plate.pluggings:
                for exp in pl.scienceExposures():
                    if exp.mjd() > mjd:
                        mjd=exp.mjd()
            mjdCompleted=mjd  
            #pluggings =session.query(platedb.Plugging).join(platedb.Plate).filter(platedb.Plate.plate_id==plate).all()
            #npl=len(pluggings)
            #if npl==1:
            #    plugging=pluggings[0]
            #    exposures=plugging.scienceExposures()
            #    for exposure in exposures:
            #        if exposure.mjd() > mjdCompl: mjdCompl=exposure.mjd()
            #if npl>1:
            #    for i in range(npl):
            #        print pluggings[i].plplugmapm      
            #        plugging=pluggings[i]
            #        exposures=plugging.scienceExposures()
            #        mjdCompl=None 
            #        for exposure in exposures:
            #            if exposure.mjd() > mjdCompl: mjdCompl=exposure.mjd()            

            #plugging=pluggings[0]
            #exposures=plugging.scienceExposures()
            #for exposure in exposures:
            #    if exposure.mjd() > mjdCompl: mjdCompl=exposure.mjd()
        if donness == "Incomplete":
            donness="Incompl"
        print "%2s   %5s   %2dx900    %-10s   %5s   %1s  %-5s " % \
               (plates[plate][1], plate, plates[plate][0], donness, mjdCompleted, npl, plates[plate][3])  
  
    return None

def eboss(mjd1, mjd2, verbose):
    print "------------------------------------------------------------------" 
    print "eBoss plates searching: %s -- %s,  wait ..  " % (mjd1, mjd2)
    print "------------------------------------------------------------------" 
    plates=None 
    plates=getBoss(mjd1, mjd2, verbose) 
    if plates == None:
        print  "  ...  did not find anything "     
    else:
        boss_str(plates,verbose)
    return None
