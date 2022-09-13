#!/usr/bin/env python3
"""This is a tool used to compile a night log time tracking summary, which
is usually kind of a pain.
"""
import sys
import click

import numpy as np
import multiprocessing as mp

from astropy.time import Time, TimeDelta
from pathlib import Path

from bin import sjd, influx_fetch
from sdssobstools import sdss_paths


def get_from_influx(name: str, query_name: str, influx_times,
                    out_dict: dict = {},
                    verbose=0):
    q_path = Path(sdss_paths.__file__).parent.parent / "flux" / query_name
    if not q_path.exists():
        raise FileNotFoundError(
            f"Couldn't find Flux query {q_path.absolute()}")
    with q_path.open('r') as fil:
        q_query = fil.read()

    results = influx_fetch.query(q_query, influx_times.min(),
                                 influx_times.max(), verbose=verbose - 1)
    influx_times = []
    values = []
    if len(results) != 0:
        for row in results[0].records:
            v = row.get_value()
            # if len(values) >= 1:
                # if v == values[-1]:
                    # continue
            values.append(row.get_value())
            influx_times.append(row.get_time())
        influx_times = Time(influx_times)
        values = np.array(values)
        sorter = influx_times.argsort()
        influx_times = influx_times[sorter]
        values = values[sorter]
    else:
        influx_times = Time([], format="isot")
        values = np.array([])

    out_dict['t' + name] = influx_times
    out_dict[name] = values


# @click.command()
# @click.option("-e", "--no-enclosure", is_flag=True,
# @click.argument("times", nargs=4)
#               help="If used, will ignore the enclosure state")
# @click.option("-v", "--verbose", count=True,
#               help="Verbose debugging, can be used multiple times")
def gen_summary(times, bright_first, no_enclosure, verbose):
    times = list(times)
    if bright_first:
        k_times = times[2:] + times[0:2]
    else:
        k_times = times
    now = Time.now()
    k_times = list(k_times)
    for i, time in enumerate(k_times):
        if " " in time:
            continue
        elif int(time.split(':')[0]) < 17:
            k_times[i] = now.iso.split()[0] + " " + time
        else:
            k_times[i] = (now - 1).iso.split()[0] + " " + time
            
    k_times = Time(k_times, format="iso")
    if verbose >= 1:
        print(f"Start: {k_times.min().iso}, End: {k_times.max().iso}")

    influx_vals = mp.Manager().dict()
    tstart = Time.now()
    encl_p = mp.Process(target=get_from_influx,
                        args=("Enclosure", "enclosure.flux", k_times, influx_vals,
                              verbose - 1))
    sci_p = mp.Process(target=get_from_influx,
                       args=("Science", "science_exposures.flux", k_times,
                             influx_vals, verbose - 1))
    encl_p.start()
    sci_p.start()
    encl_p.join(5)
    sci_p.join(5)
    tend = Time.now()
    if verbose >= 1:
        print(f"Influx queries took {(tend - tstart).sec:.1f}s")
    if verbose >= 3:
        print("Enclosure and Science times:")
        print(influx_vals["tEnclosure"])
        print(influx_vals["tScience"])
    
    if len(influx_vals["tEnclosure"]) > 0:
        influx_vals["tEnclosure"] = influx_vals["tEnclosure"][:-1][
            np.diff(influx_vals["Enclosure"]) != 0]
        influx_vals["Enclosure"] = influx_vals["Enclosure"][:-1][
            np.diff(influx_vals["Enclosure"]) != 0]

    time_tracking = {}
    time_tracking["BrightTotal"] = k_times[3] - k_times[2]
    time_tracking["DarkTotal"] = k_times[1] - k_times[0]
    time_tracking["BrightLost"] = TimeDelta(0, format="sec")
    time_tracking["DarkLost"] = TimeDelta(0, format="sec")
    time_tracking["BrightObserved"] = TimeDelta(0, format="sec")
    time_tracking["DarkObserved"] = TimeDelta(0, format="sec")
    time_tracking["DarkTech"] = TimeDelta(0, format="sec")
    time_tracking["BrightTech"] = TimeDelta(0, format="sec")

    surveys = ("Dark", "Bright")
    for i in range(len(k_times)//2):
        total_time = TimeDelta(0, format="sec")
        low, high = k_times[i * 2: (i + 1) * 2]
        for j, encl in enumerate(influx_vals["Enclosure"]):
            if encl == -1:
                continue
            if not no_enclosure:
                start = influx_vals["tEnclosure"][j]
                sci_window = influx_vals["tScience"] > influx_vals["tEnclosure"][j]
            else:
                start = low
                sci_window = influx_vals["tScience"] > low
            if len(influx_vals["tEnclosure"]) > j + 1 and not no_enclosure:
                sci_window = sci_window & (influx_vals["tScience"]
                                           < influx_vals["tEnclosure"][j + 1])
            t_sci = influx_vals["tScience"][sci_window]

            start = max(low, start)
            if not np.any(np.abs((start - t_sci).sec / 60) < 16):
                # If a science exposure started within 15 minutes from
                # opening/twilight, start is still twilight or opening, else,
                # `start` is the start of science
                window = t_sci > start
                if np.any(window):
                    start = t_sci[t_sci > start][0]
                    print(f"{surveys[i]} started science late")
                else:
                    continue  # No science was taken after opening/twilight

            if len(t_sci) != 0:
                end = t_sci[-1] + 8 / 60 / 24  # Science ends 8 minutes
                # after last exposure started
            if not no_enclosure:
                if len(influx_vals["tEnclosure"]) > j + 1:
                    end = max(influx_vals["tEnclosure"][j + 1], end)
            if np.abs((high - end).sec / 60) > 15:
                print(f"{surveys[i]} ended 15m away from end of window")
                
            in_window = ((influx_vals["tScience"] > start) &
                         (influx_vals["tScience"] < end))
            dts_mins = np.diff(influx_vals["tScience"][in_window].mjd) * 24 * 60
            wasted_time = TimeDelta(np.sum((dts_mins[dts_mins > 23] - 16) * 60),
                                    format="sec")
            if verbose >= 2:
                print(f"Survey {surveys[i]} adding from {start.iso} - {end.iso}"
                      f" with {wasted_time.sec / 3600:.1f} wasted time"
                      )
            total_time += (end - start
                           - wasted_time
                           )
            time_tracking[surveys[i] + "Tech"] += wasted_time
        time_tracking[
            surveys[i] + "Observed"] = (time_tracking[surveys[i] + "Observed"]
                                    + total_time)
        time_tracking[
            surveys[i] + "Observed"] = max(time_tracking[surveys[i] + "Observed"], 0)
    time_tracking["BrightLost"] = (time_tracking["BrightTotal"]
                                   - time_tracking["BrightObserved"]
                                   - time_tracking["BrightTech"])
    time_tracking["DarkLost"] = (time_tracking["DarkTotal"]
                                   - time_tracking["DarkObserved"]
                                   - time_tracking["DarkTech"])

    summary = "*=*=*= Observatory: APO\n"
    summary += f"*=*=*= MJD: {k_times.min().mjd:.0f}\n"
    summary += "       Fill night time in Hours below\n"
    summary += f"*=*=*= Total bright time                     :"
    summary += f" {time_tracking['BrightTotal'].sec / 3600:.1f}\n"
    summary += f"*=*=*= Bright time, queued observations      :"
    summary += f" {time_tracking['BrightObserved'].sec / 3600:.1f}\n"
    summary += f"*=*=*= Bright time, commissioning/engineering: 0\n"
    summary += f"*=*=*= Bright time lost to weather           :"
    summary += f" {time_tracking['BrightLost'].sec / 3600:.1f}\n"
    summary += f"*=*=*= Bright time lost to technical issues  :"
    summary += f" {time_tracking['BrightTech'].sec / 3600:.1f}\n"
    summary += f"\n"
    summary += f"*=*=*= Total dark time                       :"
    summary += f" {time_tracking['DarkTotal'].sec / 3600:.1f}\n"
    summary += f"*=*=*= Dark time, queued observations        :"
    summary += f" {time_tracking['DarkObserved'].sec / 3600:.1f}\n"
    summary += f"*=*=*= Dark time, commissioning/engineering  : 0\n"
    summary += f"*=*=*= Dark time lost to weather             :"
    summary += f" {time_tracking['DarkLost'].sec / 3600:.1f}\n"
    summary += f"*=*=*= Dark time lost to technical issues    :"
    summary += f" {time_tracking['DarkTech'].sec / 3600:.1f}\n"

    return summary


@click.command()
@click.argument("times", nargs=4)
@click.option("-e", "--no-enclosure", is_flag=True,
              help="If used, will ignore the enclosure state")
@click.option("-b", "--bright-first", is_flag=True,
              help="Include if bright time is listed first")
@click.option("-v", "--verbose", count=True,
              help="Verbose debugging, can be used multiple times")
def print_summary(times, bright_first, no_enclosure, verbose):
    print(gen_summary(times, bright_first, no_enclosure, verbose))


if __name__ == "__main__":
    # click interprets -- as a separator between options and arguments.
    # Kronos will display a null time as --, which breaks the command-line
    # functionality of this script. In order to fix that, we need to change
    # the inputs to something more parsible before it's read by click.
    # I tried a constant date, but that means Influx queries a large time 
    # range, so using now seems to cover the bases.
    for i, arg in enumerate(sys.argv):
        if arg == "--":
            sys.argv[i] = (Time.now() + 0.2).iso
    print_summary()
