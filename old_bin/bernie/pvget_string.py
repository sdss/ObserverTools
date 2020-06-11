#!/usr/bin/env python3

# bernie Tue. 26 June '18
# just playing around:  a script to retrieve arbitrarily defined intervals of APO process variables

import datetime
from channelarchiver import Archiver, codes, utils
ss='http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'

archiver = Archiver(ss)
archiver.scan_archives()

# DEFAULT INTERVAL IS PAST 24 HOURS BUT WE SHOULD BE ABLE TO OVERRIDE ON THE COMMAND-LINE:
start = str(datetime.datetime.utcnow() - datetime.timedelta(days=1))	# 1 day before current moment
end = str(datetime.datetime.utcnow())			# current moment
archiver.scan_archives()

# NEED TO TAKE THIS FROM THE COMMAND LINE
pvs_to_retrieve=[ '25m:guider:survey:surveyMode' ]

for pv in pvs_to_retrieve:
	print("# " + pv)
	print("# DIAGNOSTIC: start:  " + start)
	print("# DIAGNOSTIC: end:    " + end)
	retrieved_pv = archiver.get(pv, start, end, interpolation='raw',scan_archives=False)
	for i in range(len(retrieved_pv.values)):
		print("%s\t%s" % (retrieved_pv.times[i].strftime('%Y-%m-%d %H:%M:%S.%f'), retrieved_pv.values[i]))
