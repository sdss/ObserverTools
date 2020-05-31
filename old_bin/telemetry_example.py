#!/usr/bin/env python


from channelarchiver import Archiver, codes, utils
ss='http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'
#ss='http://localhost:5080/telemetry/cgi/ArchiveDataServer.cgi'

archiver = Archiver(ss)
archiver.scan_archives()

start='2018-03-31 07:00:00' 
end='2018-03-31 07:10:00'

archiver.scan_archives()
data1= archiver.get('25m:guider:axisError:RA', start, end, interpolation='raw',scan_archives=False)
data2= archiver.get('25m:guider:axisError:DEC', start, end, interpolation='raw',scan_archives=False)

print "Example of telemetry data query"
print "N   startTime axisError:RA axisError:DEC"

n=len(data1.values)
for i in range(n):
    t=data1.times[i]
    print "%3i   %s     %5.2f      %5.2f" % ( i, t.strftime('%H:%M:%SZ'), data1.values[i],  data2.values[i])

