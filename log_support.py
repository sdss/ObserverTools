"""A logging tool that is meant to perform the function of LogSupport scripts in
STUI, but by bypassing STUI and directly accessing telemetry

2020-01-28  dgatlin     Init, after just learning about telemetry queries
"""
import numpy as np
try:
    import starcoder42 as s
except ImportError:
    sys.path.append('/Users/dylangatlin/python/')
    sys.path.append('/home/gatlin/python/')
    import starcoder42 as s
try:
    from astropy.time import Time
except ImportError:
    raise s.GatlinError('Astropy not found for interpreter\n'
                        '{}'.format(sys.executable))
from channelarchiver import Archiver, codes, utils
import argparse


class Telemetry:
    def __init__(self, tstart, tend):
        self.tstart = tstart
        self.tend = tend
        self.telemetry = Archiver('http://sdss-telemetry.apo.nmsu.edu/'
                                  'telemetry/cgi/ArchiveDataServer.cgi')
        self.telemetry.scan_archives()
        self.data = {}
        self.call_times = []

    def query(self, key):
        if key in self.data.keys():
            return
        data = self.telemetry.get(key, self.tstart, self.tend,
                                  interpolation='raw', scan_archives=False)
        data.times = Time(data.times)
        data.values = np.array(data.values)
        self.data[key] = data

    def set_callbacks(self):
        for key in ['25m:sop:doMangaSequence_ditherSeq:index',
                    '25m:sop:doApogeeMangaSequence_ditherSeq:index']:
            self.query(key)
            self.call_times.extend(self.data[key].times)
        self.call_times = Time(self.call_times)
        callback_sorter = self.call_times.argsort()
        self.call_times = self.call_times[callback_sorter]
        print(self.call_times)

    def tel_offsets(self):
        offsets_keys = ['25m:guider:cartridgeLoaded:cartridgeID',
                        '25m:guider:cartridgeLoaded:plateID',
                        '25m:guider:survey:plateType',
                        '25m:tcc:axePos:az', '25m:tcc:axePos:alt',
                        '25m:tcc:axePos:rot', '25m:tcc:objArcOff:az',
                        '25m:tcc:objArcOff:alt', '25m:tcc:guideOff:rot',
                        '25m:tcc:calibOff:az', '25m:tcc:calibOff:alt',
                        '25m:tcc:calibOff:rot', '25m:guider:guideRMS:RMSerror']
        # , '25m:tcc:guideOff:az','25m:tcc:objArcOff:alt'
        for key in offsets_keys:
            self.query(key)
        offset_data = [self.call_times]
        for key in offsets_keys:
            item = []
            for time in self.call_times:
                t_cutoff = time > self.data[key].times
                item.append(self.data[key].values[t_cutoff][-1])
            offset_data.append(item)
        print(self.data['25m:tcc:axePos:az'].times)
        self.offsets = ''
        self.offsets += '--- Telescope Offsets and Scale (arcsec)---\n'
        self.offsets += ('{:<5} {:<9} {:<6} {:<4} {:<6} {:<13} {:<8} {:<10}'
                         ' {:<8}\n'.format('Time', 'Cart', 'Az', 'Alt', 'Rot',
                                           'objOff', 'guideRot', 'calibOff',
                                           'guideRMS'))
        self.offsets += '=' * 80 +'\n'
        for (t, c, p, s, az, alt, rot, obj_az, obj_alt, guide_rot, calib_az,
                calib_alt, calib_rot, rms) in zip(*offset_data):
            self.offsets += ('{:<5} {:>2}-{:0>5}{:<1} {:<+6.1f} {:<4.1f}'
                             ' {:<+6.1f}'
                             ' ({:<5.1f},{:<5.1f}) {:<+8.1f} ({:2.0f},'
                             '{:2.0f},{:2.0f}) {:<8.3f}'
                             '\n'.format(t.iso[11:16], c, p, s[0], az, alt, rot,
                                 obj_az[0]*3600, obj_alt[0]*3600,
                                 guide_rot[0]*3600, calib_az[0]*3600,
                                 calib_alt[0]*3600, calib_rot[0]*3600,
                                 rms))




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true',
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 00:00Z")
    parser.add_argument('-m', '--mjd',
                       help='If not today (-t), the mjd to search')
    parser.add_argument('-s', '--summary', help='Print the data summary',
            action='store_true')
    parser.add_argument('-d', '--data', action='store_true',
            help='Print the data log')
    parser.add_argument('-p', '--print', action='store_true',
            help='Print all possible outputs')
    parser.add_argument('-k', '--keys', nargs='+',
            help='The keys to be queries, space separated.'
                 '\nEx: 25m:apogee:ditherPosition:pixels')
    parser.add_argument('-o', '--offsets', action='store_true',
            help='Whether or not to print the offsets log')
    args = parser.parse_args()
    if args.print:
        args.data = True
        args.summary = True
    if args.today:
        now = Time.now()
        mjd = int(now.mjd)
        start = Time(mjd, format='mjd').iso.split('.')[0]
        end = now.iso.split('.')[0]
    elif args.mjd:
        mjd = args.mjd
        start = Time(mjd, format='mjd').iso.split('.')[0]
        end = Time(int(mjd) + 1, format='mjd').iso.split('.')[0]
    else:
        raise s.GatlinError('Must provide -t or -m in arguments')
    print(start, end)
    if args.keys:
        tel = Telemetry(start, end)
        for k in args.keys:
            tel.query(k)
        for k, dat in tel.data.items():
            print('{:30} {:10}'.format('Key', 'Units'))
            print('{} {}'.format(k, dat.units))
            print('    {:23} {}'.format('Time', 'Value'))
            for t, v in zip(Time(dat.times), dat.values):
                print('    {} {}'.format(t.iso[:23], v))

    if args.offsets:
        tel = Telemetry(start, end)
        tel.set_callbacks()
        tel.tel_offsets()
        print(tel.offsets)


if __name__ == '__main__':
    main()

