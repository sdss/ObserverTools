#!/usr/bin/env python3

"""A logging tool that is meant to perform the function of LogSupport scripts in
STUI, but by bypassing STUI and directly accessing telemetry

2020-01-28  dgatlin     Init, after just learning about telemetry queries
2020-06-20  dgatlin     Changed some times around, it's very easy to mix up sjd
    and mjd in channelarchiver
"""
from astropy.time import Time
import argparse

try:
    from bin import epics_fetch
except ImportError as e:
    raise ImportError('Please add ObserverTools/bin to your PYTHONPATH:\n'
                      '    {}'.format(e))

__version__ = '3.2.0'


class LogSupport:
    def __init__(self, tstart, tend, args):
        self.tstart = Time(tstart)
        self.tend = Time(tend)
        self.args = args
        self.telemetry = epics_fetch.telemetry

        self.call_times = []
        self.offsets = ''
        self.focus = ''
        self.weather = ''
        self.hartmann = ''

    def query(self, key, tstart, tend, tel_dict):
        data = self.telemetry.get(key, tstart, tend,
                                  interpolation='raw', scan_archives=False)
        if isinstance(key, list):
            for k, d in zip(key, data):
                tel_dict[k].append(d.values[0])
        else:
            value = data.values[0]
            tel_dict[key].append(value)
        return data

    def set_callbacks(self):
        data = self.telemetry.get([
            # '25m:sop:doApogeeBossScience_nDither'
            # ':nDitherDone',
            # '25m:sop:doBossScience_nExp'
            # ':nExpDone',
            # '25m:sop:doMangaSequence_ditherSeq:index',
            # '25m:sop:doApogeeMangaSequence_ditherSeq:'
            # 'index',
            # '25m:sop:doApogeeScience_index:index'],
            '25m:apogee:exposureWroteSummary'],
            (self.tstart - 0.3).datetime,
            (self.tend - 0.3).datetime,
            interpolation='raw',
            scan_archives=False)
        self.call_times = []
        for dat in data:
            self.call_times += dat.times
        self.call_times = Time(self.call_times)
        callback_sorter = self.call_times.argsort()
        self.call_times = self.call_times[callback_sorter]

        if self.args.verbose:
            print('Callback start: {}'.format(self.tstart.isot))
            print('Callback end: {}'.format(self.tend.isot))
            print(self.call_times)

        filt = self.tstart - 0.3 < self.call_times
        self.call_times = self.call_times[filt]

    def get_offsets(self):
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
            self.query(offsets_keys, time.datetime, time.datetime,
                       off_data)

        self.offsets += '=' * 80 + '\n'
        self.offsets += '{:^80}\n'.format(
            'Telescope Offsets and Scale (arcsec)')
        self.offsets += '=' * 80 + '\n\n'
        self.offsets += ('{:<5} {:<9} {:<6} {:<4} {:<6} {:<13} {:<8} {:<10}'
                         ' {:<8}\n'.format('Time', 'Cart', 'Az', 'Alt', 'Rot',
                                           '(\u03B4RA, \u03B4Dec)', 'guideRot',
                                           'calibOff', 'guideRMS'))
        self.offsets += '-' * 80 + '\n'
        for i, time in enumerate(self.call_times):
            if off_data[offsets_keys[2]][i] == '':
                continue
            self.offsets += ('{:>5} {:>2}-{:0>5} {:>1} {:>6.1f} {:>4.1f}'
                             ' {:>6.1f} ({:>5.1f},{:>5.1f}) {:>8.1f}'
                             ' ({:2.0f},{:2.0f},{:2.0f}) {:>8.3f}'
                             '\n'.format(time.isot[11:16],
                                         off_data[offsets_keys[0]][i],
                                         off_data[offsets_keys[1]][i],
                                         off_data[offsets_keys[2]][i][0],
                                         off_data[offsets_keys[3]][i],
                                         off_data[offsets_keys[4]][i],
                                         off_data[offsets_keys[5]][i],
                                         off_data[offsets_keys[6]][i][0] * 3600,
                                         off_data[offsets_keys[7]][i][0] * 3600,
                                         off_data[offsets_keys[8]][i][0] * 3600,
                                         off_data[offsets_keys[9]][i][0] * 3600,
                                         off_data[offsets_keys[10]][
                                             i][0] * 3600,
                                         off_data[offsets_keys[11]][
                                             i][0] * 3600,
                                         off_data[offsets_keys[12]][i])
                             )

    def get_focus(self):
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
            self.query(focus_keys, time.datetime, time.datetime,
                       foc_data)

        self.focus += '=' * 80 + '\n'
        self.focus += '{:^80}\n'.format('Telescope Focus')
        self.focus += '=' * 80 + '\n\n'
        self.focus += ('{:<5} {:<9} {:<6} {:<5} {:<5} {:<5} {:<6} {:<5}'
                       ' {:<5} {:<4} {:<3}'
                       ' {:<4}\n'.format('Time', 'Cart', 'Scale', 'M1', 'M2',
                                         'Focus', 'Az', 'Alt', 'Temp',
                                         'Wind', 'Dir', 'FWHM'))
        self.focus += '-' * 80 + '\n'
        for i, time in enumerate(self.call_times):
            if foc_data[focus_keys[2]][i] == '':
                continue
            self.focus += ('{:>5} {:>2}-{:0>5}{:>1} {:>6.1f} {:>5.0f}'
                           ' {:>5.0f}'
                           ' {:>5.0f} {:>6.1f} {:>5.1f} {:>5.1f} {:>4.0f}'
                           ' {:>3.0f}'
                           ' {:>4.1f}\n'.format(time.isot[11:16],
                                                foc_data[focus_keys[0]][i],
                                                foc_data[focus_keys[1]][i],
                                                foc_data[focus_keys[2]][i][0],
                                                (foc_data[focus_keys[3]][i]
                                                 - 1) * 1e6,
                                                foc_data[focus_keys[4]][i],
                                                foc_data[focus_keys[5]][i],
                                                foc_data[focus_keys[6]][i],
                                                foc_data[focus_keys[7]][i],
                                                foc_data[focus_keys[8]][i],
                                                foc_data[focus_keys[9]][i],
                                                foc_data[focus_keys[10]][i],
                                                foc_data[focus_keys[11]][i],
                                                foc_data[focus_keys[12]][i]))

    def get_weather(self):
        weather_keys = ['25m:guider:cartridgeLoaded:cartridgeID',
                        '25m:guider:cartridgeLoaded:plateID',
                        '25m:guider:survey:plateType',
                        '25m:apo:airTempPT', '25m:apo:dpTempPT',
                        '25m:apo:humidPT', '25m:apo:winds',
                        '25m:apo:windd', '25m:apo:dustb',
                        '25m:apo:irscsd', '25m:apo:irscmean']
        weather_data = {}
        for key in weather_keys:
            weather_data[key] = []
        for time in self.call_times:
            self.query(weather_keys, time.datetime, time.datetime,
                       weather_data)

        self.weather = '=' * 80 + '\n'
        self.weather += '{:^80}\n'.format('Weather Log')
        self.weather += '=' * 80 + '\n\n'
        self.weather += ('{:<5} {:<9} {:<5} {:<5} {:<4} {:<5} {:<4} {:<3}'
                         ' {:<6} {:<7} {:<5}'
                         '\n'.format('Time', 'Cart', 'Temp', 'DP', 'Diff',
                                     'Humid', 'Wind', 'Dir', '1\u03BCmDst',
                                     'IRSC\u03C3', 'IRSC\u03BC'))
        self.weather += '-' * 80 + '\n'
        for i, time in enumerate(self.call_times):
            if weather_data[weather_keys[2]][i] == '':
                continue
            self.weather += ('{:>5} {:>2}-{:0>5}{:>1} {:>5.1f} {:>5.1f}'
                             ' {:>4.1f} {:>5}'
                             ' {:>4.0f} {:>3.0f} {:>6.0f} {:>7.1f} {:>5.1f}'
                             '\n'.format(time.isot[11:16],
                                         weather_data[weather_keys[0]][i],
                                         weather_data[weather_keys[1]][i],
                                         weather_data[weather_keys[2]][i][0],
                                         weather_data[weather_keys[3]][i],
                                         weather_data[weather_keys[4]][i],
                                         weather_data[weather_keys[3]][i]
                                         - weather_data[weather_keys[4]][i],
                                         '{:>.0f}%'.format(
                                             weather_data[weather_keys[5]][i]),
                                         weather_data[weather_keys[6]][i],
                                         weather_data[weather_keys[7]][i],
                                         weather_data[weather_keys[8]][i],
                                         weather_data[weather_keys[9]][i],
                                         weather_data[weather_keys[10]][i]))

    def get_hartmann(self):
        data = self.telemetry.get('25m:hartmann:sp1Residuals:deg',
                                  (self.tstart - 0.3).datetime,
                                  (self.tend - 0.3).datetime,
                                  interpolation='raw',
                                  scan_archives=False)
        hart_times = data.times
        hart_times = Time(hart_times)
        hart_sorter = hart_times.argsort()
        hart_times = hart_times[hart_sorter]
        filt = self.tstart - 0.3 < hart_times
        hart_times = hart_times[filt]

        if self.args.verbose:
            print('hart_times: ', hart_times)
        hartmann_keys = ['25m:guider:cartridgeLoaded:cartridgeID',
                         '25m:guider:cartridgeLoaded:plateID',
                         '25m:guider:survey:plateType',
                         '25m:hartmann:r1PistonMove', '25m:hartmann:b1RingMove',
                         '25m:hartmann:sp1AverageMove',
                         '25m:hartmann:sp1Residuals:deg',
                         '25m:boss:sp1Temp:median']
        # '25m:hartmann:r2PistonMove', '25m:hartmann:b2RingMove
        # '25m:hartmann:sp2AverageMove',
        # '25m:hartmann:sp2Residuals:deg',
        # '25m:boss:sp2Temp:median']
        hart_data = {}
        for key in hartmann_keys:
            hart_data[key] = []
        for time in hart_times:
            self.query(hartmann_keys, time.datetime,
                       time.datetime,
                       hart_data)

        self.hartmann += '=' * 80 + '\n'
        self.hartmann += '{:^80}\n'.format('Hartmann Log')
        self.hartmann += '=' * 80 + '\n\n'
        self.hartmann += ('{:<5} {:<9} {:<5} {:<5} {:<5} {:<7} {:<4}'
                          '\n'.format('Time', 'Cart', 'R1', 'B1', 'Move1',
                                      'B1Resid', 'TSP1'))
        self.hartmann += '-' * 80 + '\n'
        for i, time in enumerate(hart_times):
            if hart_data[hartmann_keys[2]][i] == '':
                continue
            self.hartmann += ('{:>5} {:>2}-{:0>5}{:<1} {:>5.0f} {:>5.1f}'
                              ' {:>5.0f} {:>7.1f} {:>4.1f}'
                              '\n'.format(time.isot[11:16],
                                          hart_data[hartmann_keys[0]][i],
                                          hart_data[hartmann_keys[1]][i],
                                          hart_data[hartmann_keys[2]][i][0],
                                          hart_data[hartmann_keys[3]][i],
                                          hart_data[hartmann_keys[4]][i],
                                          hart_data[hartmann_keys[5]][i],
                                          hart_data[hartmann_keys[6]][i],
                                          hart_data[hartmann_keys[7]][i], ))
            # hart_data[hartmann_keys[8]][i],
            # hart_data[hartmann_keys[9]][i],
            # hart_data[hartmann_keys[10]][i],
            # hart_data[hartmann_keys[11]][i],
            # hart_data[hartmann_keys[12]][i]))


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
    parser.add_argument('-k', '--key',  # nargs=1,
                        help='The key to be queries, space separated.'
                             '\nEx: 25m:apogee:ditherPosition:pixels')
    parser.add_argument('-o', '--offsets', action='store_true',
                        help='Whether or not to print the offsets log')
    parser.add_argument('-f', '--focus', action='store_true',
                        help='Whether or not to print the focus log')
    parser.add_argument('-w', '--weather', action='store_true',
                        help='Whether or not to print the weather log')
    parser.add_argument('--hartmann', action='store_true',
                        help='Whether or not to print the hartmann log')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose outputs for debugging')
    args = parser.parse_args()

    if args.today:
        now = Time.now() + 0.3
        sjd = int(now.mjd)
        start = Time(sjd, format='mjd')
        end = now
    elif args.mjd:
        sjd = args.mjd
        start = Time(sjd, format='mjd')
        end = Time(int(sjd) + 1, format='mjd')
    else:
        raise argparse.ArgumentError(args.mjd,
                                     'Must provide -t or -m in arguments')

    if args.print:
        args.offsets = True
        args.focus = True
        args.weather = True
        args.hartmann = True

    if args.verbose:
        print('Start: {}'.format(start))
        print('End: {}'.format(end))

    if args.key:
        tel = LogSupport(start, end, args)
        tel.set_callbacks()
        dummy_dic = {args.key: []}
        data = []
        print('Key: {}'.format(args.key))
        print('Time: Value')
        for time in tel.call_times:
            data = tel.query(args.key, time.datetime, time.datetime, dummy_dic)
            print('{}: {}'.format(data.times[0], data.values[0]))

        print('Units: {}'.format(data.units))

    tel = LogSupport(start, end, args)
    tel.set_callbacks()

    if args.offsets:
        tel.get_offsets()
        print(tel.offsets)

    if args.focus:
        tel.get_focus()
        print(tel.focus)

    if args.weather:
        tel.get_weather()
        print(tel.weather)

    if args.hartmann:
        tel.get_hartmann()
        print(tel.hartmann)


if __name__ == '__main__':
    main()
