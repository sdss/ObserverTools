#!/usr/bin/env python3

"""A logging tool that is meant to perform the function of LogSupport scripts in
STUI, but by bypassing STUI and directly accessing telemetry

TODO: Thread these queries
"""
import argparse
import multiprocessing

import numpy as np

from astropy.time import Time
from pathlib import Path

from bin import influx_fetch, sjd

__version__ = '3.3.0'


def get_boss_callbacks(tstart, tend, call_dict):
    out = []
    boss_exp_path = Path(__file__).parent.parent / \
        "flux/science_exposures.flux"
    with boss_exp_path.open('r') as fil:
        tables = influx_fetch.query(fil.read(), tstart, tend)
    for table in tables:
        for row in table.records:
            out.append(row.get_time())

    call_dict["boss_calls"] = out


def get_apogee_callbacks(tstart, tend, call_dict):
    out = []
    apog_exp_path = Path(__file__).parent.parent / "flux/apogee_science.flux"
    with apog_exp_path.open('r') as fil:
        tables = influx_fetch.query(fil.read(), tstart, tend)
    for table in tables:
        for row in table.records:
            out.append(row.get_time())
    call_dict["apogee_calls"] = out


def get_enclosure_history(tstart, tend, call_dict):
    out_times = []
    out_states = []
    flx_path = Path(__file__).parent.parent / "flux/enclosure.flux"
    with flx_path.open('r') as fil:
        tables = influx_fetch.query(fil.read(), tstart, tend)
    for table in tables:
        for row in table.records:
            if row.get_value():
                out_times.append(row.get_time())
                out_states.append(row.get_value())
    call_dict["enclosure_times"] = out_times
    call_dict["enclosure_states"] = out_states


class LogSupport:
    def __init__(self, tstart, tend, args):
        self.tstart = Time(tstart)
        self.tend = Time(tend)
        self.args = args
        if args.verbose:
            print(f"Log Support Window: {self.tstart.iso}-{self.tend.iso}")

        self.call_times = []
        self.offsets = ""
        self.focus = ""
        self.weather = ""
        self.hartmann = ""

    def set_callbacks(self):
        callback_dict = multiprocessing.Manager().dict()
        boss = multiprocessing.Process(target=get_boss_callbacks,
                                       args=(self.tstart, self.tend,
                                             callback_dict,))
        apogee = multiprocessing.Process(target=get_apogee_callbacks,
                                         args=(self.tstart, self.tend,
                                               callback_dict,))
        enclosure = multiprocessing.Process(target=get_enclosure_history,
                                            args=(self.tstart, self.tend,
                                                  callback_dict,))
        boss.start()
        apogee.start()
        enclosure.start()
        boss.join(5)
        apogee.join(5)
        enclosure.join(5)
        if self.args.verbose:
            print(f"BOSS Calls: {len(callback_dict['boss_calls'])}, "
                  f"APOGEE Calls: {len(callback_dict['apogee_calls'])}, "
                  f"Enclosure calls: {len(callback_dict['enclosure_times'])}")
        try:
            all_times = Time(callback_dict["boss_calls"]
                             + callback_dict["apogee_calls"])
        except ValueError as e:
            print("ValueError setting call times:", e)
            self.call_times = Time([self.tstart, self.tend])
            return
        all_times = all_times[all_times.argsort()]
        if len(callback_dict["enclosure_times"]) == 0:
            encl_times = Time([self.tstart, self.tend])
            encl_vals = np.array([1, 0])
        else:
            encl_times = Time(callback_dict["enclosure_times"])
            encl_vals = np.array(callback_dict["enclosure_states"])
            encl_vals = encl_vals[encl_times.argsort()]
            encl_times = encl_times[encl_times.argsort()]
        new_times = []
        for time in all_times:
            before = encl_times < time
            if before.sum() == 0:
                continue
            if encl_vals[before][-1] != 1:
                continue
            if np.all([time - (15 / 24 / 60) > t for t in new_times]):
                new_times.append(time)
        if len(new_times) < 2:
            new_times.append(self.tend)
        try:
            self.call_times = Time(new_times)
        except ValueError:
            self.call_times = Time(new_times, format="mjd")
        # self.tstart = self.call_times[0]  # This messes with hartmanns
        # self.tend = self.call_times[-1]
        if self.args.verbose:
            print("Call times: ", self.call_times)
        # self.call_times = Time(np.arange((self.tstart + 0.3).mjd, self.tend.mjd,
            # 15 * 60 / 86400), format="mjd")

    def get_offsets(self, out_dict={}):
        start = Time.now()
        self.offsets = (f"{'Time':<8} {'Field':>6}-{'Design':<6} {'Az':>6}"
                        f" {'Alt':>4} {'Rot':>6} {'RA Off':>6} {'Dec Off':>7}"
                        f" {'Rot Off':>7} {'Guide RMS (um)':>14}\n")
        self.offsets += '=' * 80 + '\n'
        offsets_tab = {}
        offsets_tab_path = Path(__file__).parent.parent / "flux/offsets.flux"
        with offsets_tab_path.open('r') as fil:
            pre_query = Time.now()
            off_tables = influx_fetch.query(fil.read(),
                                            self.call_times[0], self.call_times[-1], interval="1m",
                                            verbose=self.args.verbose)
            post_query = Time.now()
        for table in off_tables:
            for row in table.records:
                field = row.get_field().lower()
                if field in offsets_tab.keys():
                    offsets_tab[f"t{field}"].append(row.get_time())
                    offsets_tab[field].append(row.get_value())
                else:
                    offsets_tab[f"t{field}"] = [row.get_time()]
                    offsets_tab[field] = [row.get_value()]
        post_parse = Time.now()
        for key in offsets_tab.keys():
            if key[0] == 't':
                offsets_tab[key] = Time(offsets_tab[key])
            else:
                offsets_tab[key] = np.array(offsets_tab[key])
        if len(offsets_tab) == 0:
            return
        post_sort = Time.now()
        for t in self.call_times:
            line = [t.isot[11:19]]
            for key in ["configuration_loaded_2", "configuration_loaded_1",
                        "axepos_az", "axepos_alt", "axepos_rot",
                        "objarcoff_0_p", "objarcoff_1_p", "guideoff_2_p",
                        "guide_rms_3"]:
                if 't' + key in offsets_tab.keys():
                    before = offsets_tab['t' + key] < t
                    if before.sum() == 0:
                        line.append(np.nan)
                    else:
                        line.append(offsets_tab[key][before][-1])
                else:
                    line.append(np.nan)
            if np.all(np.isnan(np.array(line[1:]))):
                continue
            self.offsets += ("{:<8} {:>6.0f}-{:<6.0f} {:>6.1f} {:>4.1f}"
                             " {:>6.1f} {:>6.3f} {:>7.3f} {:>7.3f} {:>14.3f}"
                             "\n".format(*line))
        post_print = Time.now()
        out_dict["offsets"] = self.offsets
        if self.args.verbose:
            times = Time([start, pre_query, post_query, post_parse, post_sort,
                          post_print]) - start
            print(f"Offsets overheads: {np.diff(times.sec)}")

    def get_focus(self, out_dict={}):
        self.focus = (f"{'Time':<8} {'Field':>6}-{'Design':<6} {'M1':>7}"
                      f" {'M2':>7} {'Focus':>5}"
                      f" {'Az':>6} {'Alt':>5} {'Temp':>5} {'Wind':>4}"
                      f" {'Dir':>3}\n")
        self.focus += '=' * 80 + '\n'
        focus_tab = {}
        focus_tab_path = Path(__file__).parent.parent / "flux/focus.flux"
        with focus_tab_path.open('r') as fil:
            off_tables = influx_fetch.query(fil.read(),
                                            self.call_times[0], self.call_times[-1], interval="1m",
                                            verbose=self.args.verbose)
        for table in off_tables:
            for row in table.records:
                field = row.get_field().lower()
                if field in focus_tab.keys():
                    focus_tab[f"t{field}"].append(row.get_time())
                    focus_tab[field].append(row.get_value())
                else:
                    focus_tab[f"t{field}"] = [row.get_time()]
                    focus_tab[field] = [row.get_value()]
        for key in focus_tab.keys():
            if key[0] == 't':
                focus_tab[key] = Time(focus_tab[key])
            else:
                focus_tab[key] = np.array(focus_tab[key])
        for t in self.call_times:
            line = [t.isot[11:19]]
            for key in ["configuration_loaded_2", "configuration_loaded_1",
                        "primorient_pos", "secorient_piston", "secfocus",
                        "axepos_az",
                        "axepos_alt", "airtemppt", "winds", "windd"]:
                if 't' + key in focus_tab.keys():
                    before = focus_tab['t' + key] < t
                    if before.sum() == 0:
                        line.append(np.nan)
                    else:
                        line.append(focus_tab[key][before][-1])
                else:
                    line.append(np.nan)
            if np.all(np.isnan(np.array(line[1:]))):
                continue
            self.focus += ("{:<8} {:>6.0f}-{:<6.0f} {:>7.2f} {:>7.2f} {:>5.0f}"
                           " {:>6.1f} {:>5.1f}"
                           " {:>5.1f} {:>4.0f} {:>3.0f}\n".format(
                               *line))
        out_dict["focus"] = self.focus

    def get_weather(self, out_dict={}):
        dust = "1\u03BCm Dust"
        irscs = "IRSC \u03C3"
        irscm = "IRSC \u03BC"
        self.weather = (f"{'Time':<8} {'Field':>6}-{'Design':<6} {'Temp':>5}"
                        f" {'DP':>5} {'Diff':>5}"
                        f" {'Humid':>5} {'Wind':>5} {'Dir':>3} {dust:>8}"
                        f" {irscs:>6} {irscm:>6}\n")
        self.weather += '=' * 80 + '\n'
        weather_tab = {}
        weather_tab_path = Path(__file__).parent.parent / "flux/weather.flux"
        with weather_tab_path.open('r') as fil:
            weather_tables = influx_fetch.query(fil.read(),
                                                self.call_times[0], self.call_times[-1], interval="1m",
                                                verbose=self.args.verbose)

        for table in weather_tables:
            for row in table.records:
                field = row.get_field().lower()
                if field in weather_tab.keys():
                    weather_tab[f"t{field}"].append(row.get_time())
                    weather_tab[field].append(row.get_value())
                else:
                    weather_tab[f"t{field}"] = [row.get_time()]
                    weather_tab[field] = [row.get_value()]

        # Filter out dpDep values by adding a fake value every time the humidity
        # is above 90
        for i, h in enumerate(weather_tab["humidpt"]):
            if h > 90:
                weather_tab["dustb"].append(np.nan)
                weather_tab["tdustb"].append(weather_tab["thumidpt"][i])
        for key in weather_tab.keys():
            if key[0] == 't':
                weather_tab[key] = Time(weather_tab[key])
            else:
                weather_tab[key] = np.array(weather_tab[key])
        # Most data is assumed to be sorted, but because of the dewpoint filter
        # for dust, we need to resort it to put the added values in their
        # proper places
        weather_tab["dustb"] = weather_tab["dustb"][
            weather_tab["tdustb"].argsort()]
        weather_tab["tdustb"] = weather_tab["tdustb"][
            weather_tab["tdustb"].argsort()]
        for t in self.call_times:
            line = [t.isot[11:19]]
            for key in ["configuration_loaded_2", "configuration_loaded_1",
                        "airtemppt", "airtemppt", "dptemppt", "humidpt",
                        "winds", "windd", "dustb", "irscsd", "irscmean"]:
                if 't' + key in weather_tab.keys():
                    before = weather_tab['t' + key] < t
                    if before.sum() == 0:
                        line.append(np.nan)
                    filtered = weather_tab[key][before]
                    if len(filtered) > 0:
                        line.append(filtered[-1])
                    else:
                        line.append(np.nan)
                else:
                    line.append(np.nan)

            if np.all(np.isnan(np.array(line[1:]))):
                continue
            self.weather += ("{:<8} {:>6.0f}-{:<6.0f} {:>5.1f} {:>5.1f}"
                             " {:>5.1f} {:>5.1f} {:>5.1f}"
                             " {:>3.0f} {:>8.0f} {:>6.1f} {:>6.0f}\n".format(
                                 *line))
        out_dict["weather"] = self.weather

    def get_hartmann(self, out_dict={}):
        self.hartmann = (f"{'Time':8} {'Field':>6}-{'Design':<6} {'Temp':>6}"
                         f" {'R off':>6} {'B off':>6} {'Move':>6} {'Resid':>6}"
                         " \n")
        self.hartmann += '=' * 80 + '\n'
        self.harts = {}
        boss_temps = []
        boss_times = []
        hartmanns_path = Path(__file__).parent.parent / "flux/hartmanns.flux"
        # boss_temps_path = Path(__file__).parent.parent / "flux/boss_temps.flux"
        with hartmanns_path.open('r') as fil:
            hart_tables = influx_fetch.query(fil.read(),
                                             self.tstart, self.tend,
                                             verbose=self.args.verbose)
        # with boss_temps_path.open('r') as fil:
            # boss_tables = influx_fetch.query(fil.read(),
            # self.tstart, self.tend)
        if len(hart_tables) == 0:
            return
        # for table in boss_tables:
            # for row in table.records:
            # boss_times.append(row.get_time())
            # boss_temps.append(row.get_value())
        for table in hart_tables:
            for row in table.records:
                if row.get_field() in self.harts.keys():
                    self.harts[f"t{row.get_field()}"].append(row.get_time())
                    self.harts[row.get_field()].append(row.get_value())
                else:
                    self.harts[f"t{row.get_field()}"] = [row.get_time()]
                    self.harts[row.get_field()] = [row.get_value()]
        for key in self.harts.keys():
            if key[0] == 't':
                self.harts[key] = Time(self.harts[key])
            else:
                self.harts[key] = np.array(self.harts[key])
        # boss_times = Time(boss_times)
        # boss_temps = np.array(boss_temps)
        for t in self.harts["tsp1Residuals_deg"]:
            line = [t.isot[11:19]]
            # last_temp_filt = boss_times < t
            # line.append(boss_temps[last_temp_filt][-1])
            for key in ["configuration_loaded_2", "configuration_loaded_1",
                        "sp1Temp_median",
                        "r1PistonMove_steps", "b1RingMove",
                        "sp1AverageMove_steps", "sp1Residuals_deg"]:
                if 't' + key in self.harts.keys():
                    if ("configuration_loaded" in key) or ("sp1Temp" in key):
                        before = self.harts['t' + key] < t
                        if before.sum() == 0:
                            line.append(np.nan)
                        else:
                            line.append(self.harts[key][before][-1])
                    else:
                        in_window = np.abs(
                            self.harts['t' + key] - t) < 10 / 86400
                        line.append(self.harts[key][in_window][0])
                else:
                    line.append(np.nan)
            self.hartmann += ("{:8} {:>6.0f}-{:<6.0f} {:>6.1f} {:>6.0f}"
                              " {:>6.1f} {:>6.0f}"
                              " {:>6.1f}\n".format(*line))
        out_dict["hartmann"] = self.hartmann
        out_dict["harts"] = self.harts


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
        raise NotImplementedError(
            "This feature stopped working when EPICS died")

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
