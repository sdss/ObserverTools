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

        self.call_times = []
    
    def query(self, key, tstart, tend, tel_dict):
        data = self.telemetry.get(key, tstart, tend,
                                  interpolation='raw', scan_archives=False)
        time = Time(data.times[0])
        value = data.values[0]
        tel_dict[key].append(value)
        return data

    def set_callbacks(self):
        for key in ['25m:sop:doMangaSequence_ditherSeq:index',
                    '25m:sop:doApogeeMangaSequence_ditherSeq:index']:
            data = self.telemetry.get(key, self.tstart, self.tend,
                                  interpolation='raw', scan_archives=False)
            self.call_times.extend(data.times)
        self.call_times = Time(self.call_times)
        callback_sorter = self.call_times.argsort()
        self.call_times = self.call_times[callback_sorter]
        filt = self.tstart < self.call_times
        self.call_times = self.call_times[filt]

    def tel_offsets(self):
        offsets_keys = ['25m:guider:cartridgeLoaded:cartridgeID',
                        '25m:guider:cartridgeLoaded:plateID',
                        '25m:guider:survey:plateType',
                        '25m:tcc:axePos:az', '25m:tcc:axePos:alt',
                        '25m:tcc:axePos:rot', '25m:tcc:objArcOff:az',
                        '25m:tcc:objArcOff:alt', '25m:tcc:guideOff:rot',
                        '25m:tcc:calibOff:az', '25m:tcc:calibOff:alt',
                        '25m:tcc:calibOff:rot', '25m:guider:guideRMS:RMSerror']
        off_data = {}
        for key in offsets_keys:
            off_data[key] = []
        for time in self.call_times:
            for key in offsets_keys:
                self.query(key, time.isot, time.isot, off_data)

        self.offsets = '=' * 80 + '\n'
        self.offsets += '{:^80}\n'.format(
                'Telescope Offsets and Scale (arcsec)')
        self.offsets += '=' * 80 +'\n'
        self.offsets += ('{:<5} {:<9} {:<6} {:<4} {:<6} {:<13} {:<8} {:<10}'
                         ' {:<8}\n'.format('Time', 'Cart', 'Az', 'Alt', 'Rot',
                                           'objOff', 'guideRot', 'calibOff',
                                           'guideRMS'))
        self.offsets += '=' * 80 +'\n'
        for i, time in enumerate(self.call_times):
            self.offsets += ('{:<5} {:>2}-{:0>5}{:<1} {:<+6.1f} {:<4.1f}'
                              ' {:<+6.1f} ({:<5.1f},{:<5.1f}) {:<+8.1f}'
                              ' ({:2.0f},{:2.0f},{:2.0f})'
                              ' {:<8.3f}\n'.format(
                                 time.isot[11:16],
                                 off_data[offsets_keys[0]][i],
                                 off_data[offsets_keys[1]][i],
                                 off_data[offsets_keys[2]][i][0],
                                 off_data[offsets_keys[3]][i],
                                 off_data[offsets_keys[4]][i],
                                 off_data[offsets_keys[5]][i],
                                 off_data[offsets_keys[6]][i][0]*3600,
                                 off_data[offsets_keys[7]][i][0]*3600,
                                 off_data[offsets_keys[8]][i][0]*3600,
                                 off_data[offsets_keys[9]][i][0]*3600,
                                 off_data[offsets_keys[10]][i][0]*3600,
                                 off_data[offsets_keys[11]][i][0]*3600,
                                 off_data[offsets_keys[12]][i]))

    def tel_focus(self):
        focus_keys = ['25m:guider:cartridgeLoaded:cartridgeID',
                      '25m:guider:cartridgeLoaded:plateID',
                      '25m:guider:survey:plateType',
                      '25m:tcc:scaleFac', '25m:tcc:primOrient:pos',
                      '25m:tcc:secOrient:piston', '25m:tcc:secFocus',
                      '25m:tcc:axePos:az', '25m:tcc:axePos:alt',
                      '25m:apo:airTempPT', '25m:apo:winds',
                      '25m:apo:windd', '25m:guider:seeing']
        foc_data = {}
        for key in focus_keys:
            foc_data[key] = []
        for time in self.call_times:
            for key in focus_keys:
                self.query(key, time.isot, time.isot, foc_data)

        self.focus = '=' * 80 + '\n'
        self.focus += '{:^80}\n'.format('Telescope Focus')
        self.focus += '=' * 80 +'\n'
        self.focus += ('{:<5} {:<9} {:<6} {:<5} {:<5} {:<5} {:<6} {:<5}'
                       ' {:<5} {:<4} {:<3}'
                       ' {:<4}\n'.format('Time', 'Cart', 'Scale', 'M1', 'M2',
                                       'Focus', 'Az', 'Alt', 'Temp',
                                       'Wind', 'Dir', 'FWHM'))
        self.focus += '=' * 80 +'\n'
        for i, time in enumerate(self.call_times):
            self.focus += ('{:<5} {:>2}-{:0>5}{:<1} {:<+6.1f} {:<+5.0f}'
                            ' {:<+5.0f}'
                            ' {:<+5.0f} {:<+6.1f} {:<5.1f} {:<+5.1f} {:<4.0f}'
                            ' {:<3.0f}'
                            ' {:<4.1f}\n'.format(
                                 time.isot[11:16],
                                 foc_data[focus_keys[0]][i],
                                 foc_data[focus_keys[1]][i],
                                 foc_data[focus_keys[2]][i][0],
                                 (foc_data[focus_keys[3]][i]-1)*1e6,
                                 foc_data[focus_keys[4]][i],
                                 foc_data[focus_keys[5]][i],
                                 foc_data[focus_keys[6]][i],
                                 foc_data[focus_keys[7]][i],
                                 foc_data[focus_keys[8]][i],
                                 foc_data[focus_keys[9]][i],
                                 foc_data[focus_keys[10]][i],
                                 foc_data[focus_keys[11]][i],
                                 foc_data[focus_keys[12]][i]))



        

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--today', action='store_true',
                        help="Whether or not you want to search for today's"
                             " data, whether or not the night is complete."
                             " Note: must be run after 00:00Z")
    parser.add_argument('-m', '--mjd',
                       help='If not today (-t), the mjd to search')
    parser.add_argument('-p', '--print', action='store_true',
            help='Print all possible outputs')
    parser.add_argument('-k', '--key',#  nargs=1,
            help='The key to be queries, space separated.'
                 '\nEx: 25m:apogee:ditherPosition:pixels')
    parser.add_argument('-o', '--offsets', action='store_true',
            help='Whether or not to print the offsets log')
    parser.add_argument('-f', '--focus', action='store_true',
            help='Whether or not to print the focus log')
    args = parser.parse_args()
    
    if args.today:
        now = Time.now()
        mjd = int(now.mjd)
        start = Time(mjd, format='mjd').iso.split('.')[0]
        end = (now).iso.split('.')[0]
    elif args.mjd:
        mjd = args.mjd
        start = Time(mjd, format='mjd').iso.split('.')[0]
        end = Time(int(mjd) + 1, format='mjd').iso.split('.')[0]
    else:
        raise s.GatlinError('Must provide -t or -m in arguments')

    print('Start: {}'.format(start))
    print('End: {}'.format(end))

    if args.key:
        tel = Telemetry(start, end)
        tel.set_callbacks()
        dummy_dic = {args.key: []}
        data = []
        print('Key: {}'.format(args.key))
        print('Time: Value')
        for time in tel.call_times:
            data = tel.query(args.key, time.isot, time.isot, dummy_dic)
            print('{}: {}'.format(data.times[0], data.values[0]))
            
        print('Units: {}'.format(data.units))

    if args.offsets:
        tel = Telemetry(start, end)
        tel.set_callbacks()
        tel.tel_offsets()
        print(tel.offsets)
    
    if args.focus:
        tel = Telemetry(start, end)
        tel.set_callbacks()
        tel.tel_focus()
        print(tel.focus)


if __name__ == '__main__':
    main()

