#!/usr/bin/env python

"""
time track for october from Dan for testing:
./timetrack.py -b -m1 58393 -m2 58423

eBOSS Completed 31 out of a total 35 eBOSS plates
166 total science exposures (900s each)

Completed: 10763, 11324, 7766, 11278, 7744, 7748, 8733, 8746, 8748, 10902,
 11316, 10901, 11317, 7747, 11289, 11046, 11081, 7759, 11288, 8750, 11080,
 11086, 10904, 11315, 7758, 11285, 7750, 8752, 11318, 7769, 11284

Observed but not completed during October 2018: 11102, 11069, 11321, 11281
-----------------
Scan Include all eboss  schience exposures then exclude some of them:
if  (flavor !="science"):  continue
if  (PLATETYP=="APOGEE-2&MaNGA") :  continue
if  (EXPTIME < 850) : continue
----------------



"""

import glob
import re
import grepfitsLib
import configparser

from sdss.internal.database.connections.APODatabaseAdminLocalConnection import \
    db
import sdss.internal.database.apo.platedb.ModelClasses as platedb

# create a config parser object
config = configparser.RawConfigParser()
config.read('config.cfg')
pref = config.get('path_prefix', 'pref')


def getFiles(mask):
    files = glob.glob(mask)
    return sorted(files)


def getBoss(mjd1, mjd2, verbose):
    path_red = "/data/spectro/"
    red = "sdR-b1-*.fit.gz"
    reg = "\d{8}"  # sdR-b1-00270127.fit.gz
    plates = {}

    for mjd in range(mjd1, mjd2 + 1):
        path = "%s%s%s/%s" % (pref, path_red, mjd, red)
        files = getFiles(path)
        if verbose:
            print("      -------", mjd, "---------")  # "nFiles=", len(files)
            # print "mjd   expNum   flavor   ct  plate  exp   dith Plate_type
            # Lead"
        nexp = 0;
        for i, f in enumerate(files):
            ind = re.search(reg, f)
            expNum = f[ind.start():ind.end()]

            fl = grepfitsLib.grepfitsPro(
                ['', 'FLAVOR,PLATETYP,CARTID,PLATEID,EXPTIME,MGDPOS,SRVYMODE',
                 f])
            flavor = fl[1][1].strip()
            PLATETYP = fl[1][2].strip()  # plateType
            CARTID = fl[1][3]
            PLATEID = fl[1][4]
            plate = int(PLATEID)
            EXPTIME = float(fl[1][5])
            MGDPOS = fl[1][6].strip()  # dither ?
            SRVYMODE = fl[1][7].strip()  # lead survey ?

            # filter out:  not science exp; short exp; apogee-manga plate
            if flavor != "science":
                continue
            if PLATETYP == "APOGEE-2&MaNGA":
                continue
            if EXPTIME < 850:
                continue

            if verbose and nexp == 0:
                print(
                    "mjd   expNum   flavor   ct  plate  exp   dith Plate_type"
                    "  Lead")
            if verbose:
                print("%5s %8s %-7s  %2s  %5s  %5.1f  %2s  %-10s  %-s " %
                      (mjd, expNum, flavor, CARTID, PLATEID, EXPTIME, MGDPOS,
                       PLATETYP, SRVYMODE))

            nexp = nexp + 1
            if plate in plates:
                # plates[plate]=plates[plate]+1
                plates[plate][0] = plates[plate][0] + 1
                plates[plate][3] = plates[plate][3] + MGDPOS
            else:
                # plates[plate]=1
                plates[plate] = [1, CARTID, SRVYMODE, MGDPOS]

    return plates


def boss_str(plates, mjd1, mjd2, verbose):
    print("")
    print("**** eBOSS summary ****")

    session = db.Session()

    print("   ")
    print("ct   Plate  Nexp   Status       MJD ")

    nCompleted = 0
    nIncompl = 0
    nExp = 0
    platesCompl = []
    platesIncompl = []

    for plate in sorted(plates.keys()):
        nExp = nExp + plates[plate][0]
        plateObj = session.query(platedb.Plate).filter(
            platedb.Plate.plate_id == plate).one()
        mjdCompleted = None
        donness = plateObj.calculatedCompletionStatus()
        mjd = 0
        if donness == "Complete":
            for pl in plateObj.pluggings:
                for exp in pl.scienceExposures():
                    if exp.sjd() > mjd:
                        mjd = exp.sjd()
            mjdCompleted = mjd
            if mjdCompleted > mjd2:
                mjdCompleted = None
                donness = "-Incompl"
        else:
            donness = "-Incompl"

        if donness == "Complete":
            nCompleted = nCompleted + 1
            platesCompl.append(plate)
        else:
            nIncompl = nIncompl + 1
            platesIncompl.append(plate)

        print("%2s   %5s   %2d    %-10s  %5s   %-5s " %
              (plates[plate][1], plate, plates[plate][0], donness, mjdCompleted,
               plates[plate][3]))

    print("")
    print("eBOSS: completed %s plates among %s observed." % (
        nCompleted, len(plates)))
    print("   - %s science exposures (900 sec each)" % nExp)
    print("")
    print("List of observed eBOSS plates:")
    print(sorted(plates.keys()))

    print("")
    print("Completed %s plates:" % nCompleted)
    print(platesCompl)
    print("")
    print("Observed but not completed %s plates:" % nIncompl)
    print(platesIncompl)

    return None


def eboss(mjd1, mjd2, verbose):
    print("------------------------------------------------------------------")
    print("eBoss plates searching: %s -- %s,  wait ..  " % (mjd1, mjd2))
    print("------------------------------------------------------------------")
    plates = getBoss(mjd1, mjd2, verbose)
    if plates is None:
        print("  ...  did not find anything ")
    else:
        boss_str(plates, mjd1, mjd2, verbose)
    return None
