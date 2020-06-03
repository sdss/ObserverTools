#!/usr/bin/env python

# bernie Tue. 27 Nov. '18
# batch script dividing up into months, because longer periods can cause trouble

import datetime
from channelarchiver import Archiver, codes, utils
ss='http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'

archiver = Archiver(ss)
archiver.scan_archives()

# only INTEGERS in this script:
pvs_to_retrieve=['25m:guider:cartridgeLoaded:plateID', '25m:guider:guideState' ]

for year in (2017, 2018):
	if (year % 4):
		monthdays=(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
	else:
		monthdays=(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
	for month in range(12):
		start=str("%d-%02d-%02d 00:00:00.0" % (year, month+1, 1))
		end=str("%d-%02d-%02d 00:00:00.0" % (year, month+1, monthdays[month]))
		for pv in pvs_to_retrieve:
		    	print("# " + pv)
		    	print(("## interval: %s to %s" % (start, end)))
		    	retrieved_pv = archiver.get(pv, start, end, interpolation='raw',scan_archives=False)
		    	for i in range(len(retrieved_pv.values)):
					print("%s\t%s" % (retrieved_pv.times[i].strftime('%Y-%m-%d %H:%M:%S.%f'), retrieved_pv.values[i]))
