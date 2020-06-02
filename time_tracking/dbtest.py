#!/usr/bin/env python


from sdss.internal.database.connections.APODatabaseAdminLocalConnection import \
    db
import sdss.internal.database.apo.platedb.ModelClasses as platedb

# mjd=58391
# plate1= 10724  # done
# plate2=7756 # not done

# session = db.Session()
# plate=session.query(platedb.Plate).filter(platedb.Plate.plate_id==plate1).one()

# print plate
# print plate.__dict__

# print "plate.comment=", plate.comment
# print "plate.completionStatusHistory=", plate.completionStatusHistory
# print "plate.completionStatus =", plate.completionStatus

session = db.Session()


def getPlateInfo(plateID):
    plate = session.query(platedb.Plate).filter(
        platedb.Plate.plate_id == plateID).one()
    pluggings = session.query(platedb.Plugging).join(platedb.Plate).filter(
        platedb.Plate.plate_id == plateID).all()
    for i, plugging in enumerate(pluggings):
        print(i, plugging.fscan_mjd, plateID, plugging.percentDone(), plugging)
        print("    ", plugging.plplugmapm)

        exposures = plugging.scienceExposures()
        if len(exposures) > 0:
            mjd = 0
            for exposure in exposures:
                print(exposure.exposure_no, exposure.mjd(),
                      exposure.flavor.label,
                      exposure.survey.label)
                if exposure.mjd() > mjd: mjd = exposure.mjd()
            if "Complete" == plate.calculatedCompletionStatus():
                print("Complete on ", mjd)
        else:
            print("     no_exposures")


def test1(plate_id):  # Brian
    # get a plate 7917
    plate = session.query(platedb.Plate).filter(
        platedb.Plate.plate_id == plate_id).one()
    print("----")
    print("plate_ID=", plate.plate_id)
    print("plate.name=", plate.name)
    print("plate.completionStatus.label=",
          plate.completionStatus.label)  # Automatic ?
    print("plate.calculatedCompletionStatus()=",
          plate.calculatedCompletionStatus())
    print(plate.surveys)

    print("    pluggings:")
    mjd = 0
    for pl in plate.pluggings:
        nexp = len(pl.scienceExposures())
        print("   ", "Nexp=", nexp, ",   pl.status.label=", pl.status.label,
              ",   fscan=", pl.fscan_mjd, ",  percentDone=", pl.percentDone())
        # if any of it Good or
        for exp in pl.scienceExposures():
            print("        ", exp.exposure_no, exp.mjd())
            if exp.mjd() > mjd:
                mjd = exp.mjd()

    print("plate=", plate.plate_id, "status=",
          plate.calculatedCompletionStatus(), "mjd_of_last_exposure=", mjd)

    # print "---dir(plate)"
    # print dir(plate)
    # print "---plate.__dict__"
    # print plate.__dict__
    # print "---"


if __name__ == "__main__":
    # test1(11375)  # not done   Automatic
    # test1(11054)  # done
    # test1(7917)  # apogee
    # test1(8754)

    test1(11229)  # apogee new

    # print "------"
    # plateID= 10724; getPlateInfo(plateID)
    # print "------"
    # plateID= 7756; getPlateInfo(plateID)
    # print "------"
    # plateID= 11081; getPlateInfo(plateID)
    # print "------"
'''

 >>> dir(plug1)
['__class__', '__delattr__', '__dict__', '__doc__', '__format__', '__getattribute__', 
'__hash__', '__init__', '__mapper__', '__module__', '__new__', '__reduce__', 
'__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 
'__table__', '__table_args__', '__tablename__', '__weakref__', '_decl_class_registry',
 '_sa_class_manager', '_sa_instance_state', 'activePlugging', 'bossPluggingInfo', 
 'cartridge', u'cartridge_pk', 'fscan_datetime', u'fscan_id', u'fscan_mjd', 'getSumSn2', 
 'instruments', 'mangaUpdateStatus', 'metadata', u'name', 'observations', 'percentDone', 
 u'pk', 'plate', u'plate_pk', 'plplugmapm', u'plugging_status_pk', 'profilometries', 
 'scienceExposures', 'status', 'updateStatus']
 
 >>> plug1.cartridge_pk
2183
>>> plug1.plate_pk
13802
>>> plug1.observations
[<Observation: mjd = 58419 (pk=22015)>]
>>> plug0.plplugmapm
[<PlPlugMapM file: plPlugMapM-11318-58403-01.par (id=72059)>]

>>> plug1.fscan_mjd
58403
>>> plug1.percentDone()
100.0
>>> plug0.percentDone()
0

 e=plug1.observations[0].exposures
 for e1 in e:
...     print e1.flavor.label
... 
Science
Science
Science
Science



 '''
