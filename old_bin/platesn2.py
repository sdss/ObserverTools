#!/usr/bin/env python

"""
Automatic observation report
"""

import sys
import os

import psycopg2 as db

#- Global DB connection objects
dbx = db.connect(database='apo_platedb', host='sdss-db-p.apo.nmsu.edu', user='postgres') 
cx = dbx.cursor()

def get_plug_exps(plate):
    """return summary dictionary of observations of plate prior to mjd"""
    global cx

    query = """
    select exposure_no, exposure_time, start_time, camera.label, sn2, fscan_mjd, fscan_id, exposure_status.label
    from exposure, exposure_status, camera_frame, camera, observation, plugging, plate
    where camera_frame.exposure_pk = exposure.pk
    and camera_frame.camera_pk = camera.pk
    and exposure.exposure_status_pk = exposure_status.pk
    and exposure.observation_pk = observation.pk
    and observation.plugging_pk = plugging.pk
    and plugging.plate_pk = plate.pk
    and plate_id = %d
    """ % (plate, )
    cx.execute(query)

    pluggings = dict()

    for expid, texp, tstart, camera, sn2, fscan_mjd, fscan_id, status in cx.fetchall():
        plugid = '%04d-%05d-%02d' % (plate, fscan_mjd, fscan_id)
        obs_mjd = int( tstart/(24*3600) )
        if plugid not in pluggings:
            pluggings[plugid] = dict()

        if expid not in pluggings[plugid]:
            pluggings[plugid][expid] = dict(mjd=obs_mjd, texp=float(texp), status=status, sn2=dict())

        pluggings[plugid][expid]['sn2'][camera] = float(sn2)
        
    return pluggings

def get_sn2_thresholds():
    global cx

    #- Get limits, ordered by version; assuming latest is current
    query = """
    select camera.label, sn2_threshold
    from boss_sn2_threshold, camera
    where boss_sn2_threshold.camera_pk = camera.pk
    order by boss_sn2_threshold.version
    """
    cx.execute(query)

    sn2_thresholds = dict()
    for camera, threshold in cx.fetchall():
        sn2_thresholds[camera] = float(threshold)

    return sn2_thresholds

#----

plate = int(sys.argv[1])

pluggings = get_plug_exps(plate)

for plugid, exps in sorted(pluggings.items()):
    print('--- Plugging %s ---' % plugid)
    print("MJD    ExpID   texp    b1    b2    r1    r2   Status")

    sn2sum = dict(b1=0.0, b2=0.0, r1=0.0, r2=0.0)
    for expid, expinfo in sorted(exps.items()):
        print('%5d  %6d  %5.1f' % (expinfo['mjd'], expid, expinfo['texp']), end=' ')
        for camera in ('b1', 'b2', 'r1', 'r2'):
            if camera in expinfo['sn2']:
                print('%5.2f' % (expinfo['sn2'][camera], ), end=' ')
                sn2sum[camera] += expinfo['sn2'][camera]
            else:
                print(' ---', end=' ') 
        print(' '+expinfo['status'])

    sn2_thresholds = get_sn2_thresholds()
    done = True
    for camera in ('b1', 'b2', 'r1', 'r2'):
        if sn2sum[camera] < sn2_thresholds[camera]:
            done = False

    print("Totals:             ", end=' ')
    for camera in ('b1', 'b2', 'r1', 'r2'):
        print('%5.2f' % (sn2sum[camera], ), end=' ')

    if done:
        print(" Done")
    else:
        print(" Incomplete")
        print("Remaining:          ", end=' ')
        for camera in ('b1', 'b2', 'r1', 'r2'):
            dsn2 = sn2_thresholds[camera] - sn2sum[camera]
            if dsn2 > 0:
                print('%5.2f' % (dsn2, ), end=' ')
            else:
                print('  ok ', end=' ') 
        print() 






