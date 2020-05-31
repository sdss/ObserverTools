#!/usr/bin/env python

# bernie Tue. 26 June '18
# just playing around:  a script to retrieve arbitrarily defined intervals of APO process variables

from channelarchiver import Archiver, codes, utils
ss='http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'

archiver = Archiver(ss)
archiver.scan_archives()

# NEED TO TAKE THIS FROM THE COMMAND LINE, PERHAPS WITH A DEFAULT INTERVAL OF THe PAST 24 HOURS:
start='2018-06-25 10:00:00'
end='2018-06-26 11:00:00'

archiver.scan_archives()

# NEED TO TAKE THIS FROM THE COMMAND LINE
# pvs_to_retrieve=[ '25m:boss:SP1B2LN2TempRead', '25m:boss:SP1R0LN2TempRead', '25m:boss:SP2B2LN2TempRead', '25m:boss:SP2R0LN2TempRead' ]
pvs_to_retrieve=[ '25m:apo:humidity' ]

for pv in pvs_to_retrieve:
	print "# " + pv
	retrieved_pv = archiver.get(pv, start, end, interpolation='raw',scan_archives=False)
	for i in range(len(retrieved_pv.values)):
		print "%s\t%f" % (retrieved_pv.times[i].strftime('%Y-%m-%d %H:%M:%S.%f'), retrieved_pv.values[i])
