#!/usr/bin/env python3

"""A logging tool that is meant to perform the function of LogSupport scripts in
STUI, but by bypassing STUI and directly accessing telemetry

2020-01-28  dgatlin     Init, after just learning about telemetry queries
2020-06-20  dgatlin     Changed some times around, it's very easy to mix up mjd
    and mjd in channelarchiver
"""
import argparse

import numpy as np

from astropy.time import Time
from pathlib import Path

from bin import influx_fetch, sjd

__version__ = '3.3.0'

class LogSupport:
    def __init__(self, tstart, tend, args):
        self.tstart = Time(tstart)
        self.tend = Time(tend)
        self.args = args

        self.call_times = []
        self.offsets = ""
        self.focus = ""
        self.weather = ""
        self.hartmann = ""

    def set_callbacks(self):
        self.call_times = Time(np.arange((self.tstart + 0.3).mjd, self.tend.mjd,
                15 * 60 / 86400), format="mjd")

    def get_offsets(self):
        self.offsets = f"{'Time':<8} {'Az':<6} {'Alt':<4} {'Rot':<6}\n"
        self.offsets += '=' * 80 + '\n'
        offsets_tab = {}
        offsets_tab_path = Path(__file__).parent.parent / "flux/offsets.flux"
        off_tables = influx_fetch.query(offsets_tab_path.open('r').read(),
            self.tstart, self.tend)
        for table in off_tables:
            for row in table.records:
                field = row.get_field()
                if field in offsets_tab.keys():
                    offsets_tab[f"t{field}"].append(row.get_time())
                    offsets_tab[field].append(row.get_value())
                else:
                    offsets_tab[f"t{field}"] = [row.get_time()]
                    offsets_tab[field] = [row.get_value()]
        for key in offsets_tab.keys():
            if key[0] == 't':
                offsets_tab[key] = Time(offsets_tab[key])
            else:
                offsets_tab[key] = np.array(offsets_tab[key])
        for t in self.call_times:
            line = [t.isot[11:19]] 
            skip_line = False
            for key in ["az", "alt", "rot"]:
                before = offsets_tab['t' + key] < t
                if before.sum() == 0:
                    continue
                line.append(offsets_tab[key][before][-1])
            self.offsets += "{:<8} {:>6.1f} {:>4.1f} {:>6.1f}\n".format(*line)
                
            
        # offsets_tab_keys = ['25m:guider:cartridgeLoaded:cartridgeID',
        #                 '25m:guider:cartridgeLoaded:plateID',
        #                 '25m:guider:survey:plateType',
        #                 '25m:tcc:axePos:az', '25m:tcc:axePos:alt',
        #                 '25m:tcc:axePos:rot', '25m:tcc:objArcOff:az',
        #                 '25m:tcc:objArcOff:alt', '25m:tcc:guideOff:rot',
        #                 '25m:tcc:calibOff:az', '25m:tcc:calibOff:alt',
        #                 '25m:tcc:calibOff:rot', '25m:guider:guideRMS:RMSerror']
        # # self.offsets_tab += '=' * 80 + '\n'
        # self.offsets_tab += '{:^80}\n'.format(
        #     'Telescope Offsets and Scale (arcsec)')
        # self.offsets_tab += '=' * 80 + '\n\n'
        # self.offsets_tab += ('{:<5} {:<9} {:<6} {:<4} {:<6} {:<13} {:<8} {:<10}'
        #                  ' {:<8}\n'.format('Time', 'Cart', 'Az', 'Alt', 'Rot',
        #                                    '(\u03B4RA, \u03B4Dec)', 'guideRot',
        #                                    'calibOff', 'guideRMS'))
        # self.offsets_tab += '-' * 80 + '\n'
        # for i, time in enumerate(self.call_times):
        #     if off_data[offsets_tab_keys[2]][i] == '':
        #         continue
        #     self.offsets_tab += ('{:>5} {:>2}-{:0>5} {:>1} {:>6.1f} {:>4.1f}'
        #                      ' {:>6.1f} ({:>5.1f},{:>5.1f}) {:>8.1f}'
        #                      ' ({:2.0f},{:2.0f},{:2.0f}) {:>8.3f}'
        #                      '\n'.format(time.isot[11:16],
        #                                  off_data[offsets_tab_keys[0]][i],
        #                                  off_data[offsets_tab_keys[1]][i],
        #                                  off_data[offsets_tab_keys[2]][i][0],
        #                                  off_data[offsets_tab_keys[3]][i],
        #                                  off_data[offsets_tab_keys[4]][i],
        #                                  off_data[offsets_tab_keys[5]][i],
        #                                  off_data[offsets_tab_keys[6]][i][0] * 3600,
        #                                  off_data[offsets_tab_keys[7]][i][0] * 3600,
        #                                  off_data[offsets_tab_keys[8]][i][0] * 3600,
        #                                  off_data[offsets_tab_keys[9]][i][0] * 3600,
        #                                  off_data[offsets_tab_keys[10]][
        #                                      i][0] * 3600,
        #                                  off_data[offsets_tab_keys[11]][
        #                                      i][0] * 3600,
        #                                  off_data[offsets_keys[12]][i])
        #                      )

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
        self.hartmann = f"{'Time':8} {'TSP1':<6} {'R off':<6} {'B off':<6}"
        self.hartmann += f" {'Move':<6} {'Resid':<6}\n"
        self.hartmann += '=' * 80 + '\n'
        harts = {}
        boss_temps = []
        boss_times = []
        hartmanns_path = Path(__file__).parent.parent / "flux/hartmanns.flux"
        boss_temps_path = Path(__file__).parent.parent / "flux/boss_temps.flux"
        hart_tables = influx_fetch.query(hartmanns_path.open('r').read(),
            self.tstart, self.tend)
        boss_tables = influx_fetch.query(boss_temps_path.open('r').read(),
            self.tstart, self.tend)
        for table in boss_tables:
            for row in table.records:
                boss_times.append(row.get_time()) 
                boss_temps.append(row.get_value())
        for table in hart_tables:
            for row in table.records:
                if row.get_measurement() in harts.keys():
                    harts[f"t{row.get_measurement()}"].append(row.get_time())
                    harts[row.get_measurement()].append(row.get_value())
                else:
                    harts[f"t{row.get_measurement()}"] = [row.get_time()]
                    harts[row.get_measurement()] = [row.get_value()]
        for key in harts.keys():
            if key[0] == 't':
                harts[key] = Time(harts[key])
            else:
                harts[key] = np.array(harts[key])
        boss_times = Time(boss_times)
        boss_temps = np.array(boss_temps)
        for t in harts["tsp1Residuals"]:
            line = [t.isot[11:19]]
            last_temp_filt = boss_times < t
            line.append(boss_temps[last_temp_filt][-1])
            for key in ["r1PistonMove", "b1RingMove",
                        "sp1AverageMove", "sp1Residuals"]:
                in_window = np.abs(harts['t' + key] - t) < 10 / 86400
                line.append(harts[key][in_window][0])
            self.hartmann += ("{:8} {:>6.1f} {:>6.0f} {:>6.1f} {:>6.0f}"
                              " {:>6.1f}\n".format(*line))

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
        now = Time.now()
        start = Time(sjd.sjd(), format='mjd') - 0.3
        end = now
    elif args.mjd:
        mjd = args.mjd
        start = Time(mjd, format='mjd') - 0.3
        end = Time(int(mjd) + 1, format='mjd') - 0.3
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
