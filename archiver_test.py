from channelarchiver import Archiver
from astropy.time import Time
telemetry = Archiver('http://sdss-telemetry.apo.nmsu.edu/'
                                  'telemetry/cgi/ArchiveDataServer.cgi')
telemetry.scan_archives()
tstart = Time('2020-03-15T00:00.00').datetime
tend = Time('2020-03-15T02:50.00').datetime
print(telemetry.get('25m:tcc:axePos:az',
    start=tstart,
    end=tend,
    interpolation='raw', scan_archives=False))

