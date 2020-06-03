#!/usr/bin/env python

# bernie Tue. 26 June '18
# playing around

from channelarchiver import Archiver, codes, utils
ss='http://sdss-telemetry.apo.nmsu.edu/telemetry/cgi/ArchiveDataServer.cgi'
#ss='http://localhost:5080/telemetry/cgi/ArchiveDataServer.cgi'

archiver = Archiver(ss)
archiver.scan_archives()

start='2018-06-25 10:00:00' 
end='2018-06-26 11:00:00'

archiver.scan_archives()
data1= archiver.get('25m:boss:SP1B2LN2TempRead', start, end, interpolation='raw',scan_archives=False)
data2= archiver.get('25m:boss:SP1R0LN2TempRead', start, end, interpolation='raw',scan_archives=False)
data3= archiver.get('25m:boss:SP2B2LN2TempRead', start, end, interpolation='raw',scan_archives=False)
data4= archiver.get('25m:boss:SP2R0LN2TempRead', start, end, interpolation='raw',scan_archives=False)


n=len(data1.values)
for i in range(n):
    t=data1.times[i]
    print("%s\t%5.2f\t%5.2f\t%5.2f\t%5.2f" % (t.strftime('%Y-%m-%d %H:%M:%S.%f'), data1.values[i],  data2.values[i], data3.values[i],  data4.values[i]))
