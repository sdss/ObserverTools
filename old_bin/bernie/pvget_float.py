#!/usr/bin/env python

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
print "# DIAGNOSTIC: start:  " + start
print "# DIAGNOSTIC: end:    " + end

archiver.scan_archives()

# NEED TO TAKE THIS FROM THE COMMAND LINE
pvs_to_retrieve=[ '25m:boss:SP1B2CCDTempRead', '25m:boss:SP1R0CCDTempRead', '25m:boss:SP2B2CCDTempRead', '25m:boss:SP2R0CCDTempRead' ]
# pvs_to_retrieve=[ '25m:boss:SP1B2LN2TempRead', '25m:boss:SP1R0LN2TempRead', '25m:boss:SP2B2LN2TempRead', '25m:boss:SP2R0LN2TempRead', '25m:boss:sp1camSecondaryDewarPress', '25m:boss:SP1SecondaryDewarPress', '25m:boss:sp2camSecondaryDewarPress', '25m:boss:SP2SecondaryDewarPress' ]
# pvs_to_retrieve=[ '25m:boss:sp1camSecondaryDewarPress', '25m:boss:SP1SecondaryDewarPress', '25m:boss:sp2camSecondaryDewarPress', '25m:boss:SP2SecondaryDewarPress' ]
# pvs_to_retrieve=[ '25m:boss:sp1camSecondaryDewarPress', '25m:boss:sp2camSecondaryDewarPress' ]
# pvs_to_retrieve=[ '25m:boss:SP1R0CCDTempRead', '25m:boss:SP1B2CCDTempRead', '25m:boss:SP2R0CCDTempRead', '25m:boss:SP2B2CCDTempRead' ]
# pvs_to_retrieve=[ '25m:boss:tpm_Ndewar_spectro', '25m:boss:tpm_Sdewar_spectro' ]
# pvs_to_retrieve=[ '25m:boss:SP1SecondaryDewarPress', '25m:boss:SP2SecondaryDewarPress' ]
# pvs_to_retrieve=[ '25m:guider:axisError:RA', '25m:guider:axisError:DEC']

for pv in pvs_to_retrieve:
	print "# " + pv
	retrieved_pv = archiver.get(pv, start, end, interpolation='raw',scan_archives=False)
	for i in range(len(retrieved_pv.values)):
		print "%s\t%f" % (retrieved_pv.times[i].strftime('%Y-%m-%d %H:%M:%S.%f'), retrieved_pv.values[i])
