#!/usr/bin/env python


#
import apogee, eboss, manga, mjd
import warnings
warnings.filterwarnings('ignore')
import argparse

from sdss.internal.database.connections.APODatabaseAdminLocalConnection import db
import sdss.internal.database.apo.platedb.ModelClasses as platedb

session = db.Session()

def prn_report(mjd1, plates,mangaPlates):
     print "mjd=", mjd1
     print  "Cart-Plate    Name           Apogee        Manga        Lead        Done?  "
     print "-"*80
     #for plate in sorted(plates.keys()):
     for plate in plates.keys():
          plateObj=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate).one() 
          if plate in mangaPlates:
               mm=" %2d*%3d sec" % (mangaPlates[plate][0],mangaPlates[plate][1])
               #print "manga:", plate, mangaPlates[plate][0],  mangaPlates[plate][1], mangaPlates[plate][3]
          else:
              mm=" -----     "
#          print "%2s-%5s   %-13s   %s*AB*%s   %s     %-7s " % \
#               (plates[plate][5], plate, plateObj.name, plates[plate][0]/2, plates[plate][1], mm,  plates[plate][2] ) 
          ss="%2s-%5s" % (plates[plate][5], plate)   # cart:plate
          ss="%s     %-13s" % (ss,  plateObj.name)   # name
          ss="%s   %s*AB*%s rd" % (ss,  plates[plate][0]/2, plates[plate][1])   # apogee   4*AB*47
          ss="%s   %s " % (ss, mm)  #  mm - manga observations
          lead=plates[plate][2];    lead=lead.strip();  ss="%s   %s"  % (ss, lead) # lead
          print ss
 






if __name__ == "__main__":
    #print "Current mjd=", mjd.curSjd()
    desc = 'list of files for time tracking report '
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m1', '--mjd1', help='start mjd, default current mjd', default=mjd.curSjd(), type=int)
    #parser.add_argument('-m2', '--mjd2', help='end mjd, default current mjd', default=mjd.curSjd(), type=int)           
    #parser.add_argument('-a', '--apogee',  help='get apogee report',  action="store_true") 
    #parser.add_argument('-b', '--boss',  help='get boss report',  action="store_true") 
    #parser.add_argument('-m', '--manga',  help='get manga report',  action="store_true") 
    parser.add_argument('-v', '--verbose',  help='verbose data',  action="store_true") 
    args = parser.parse_args()   
       
     
    mjd1=args.mjd1;  
   
    ebossPlates=eboss.getBoss(mjd1, mjd1, args.verbose)
    apogeePlates=apogee.getApogee(mjd1, mjd1, args.verbose)
    mangaPlates=manga.getManga(mjd1, mjd1, args.verbose)

    prn_report(mjd1, apogeePlates,mangaPlates)
    print ""