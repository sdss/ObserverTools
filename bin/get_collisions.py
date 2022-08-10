#!/usr/bin/env python3

import re
import gzip
import click

from astropy.time import Time
from sdssobstools import sdss_paths


@click.command()
@click.option("-1", "--t1", "time_1", default=Time.now() - 20,
              help="The start time, preferably in isot or SJD format."
              " By default, it's 20 days ago.")
@click.option("-2", "--t2", "time_2", default=Time.now(),
              help="The end time, preferably in isot or SJD format. By default,"
              " it is today")
@click.option("-c", "--collisions", is_flag=True, default=True,
              help="If used, will report fiber collision detections")
@click.option("-o", "--outofrange", is_flag=True,
              help="If used, will report VALUE_OUT_OF_RANGE errors")
@click.option("-v", "--verbose", count=True, help="Verbose debugging")
def main(time_1, time_2, collisions, outofrange, verbose: int):
    run_collisions = collisions
    run_outofrange = outofrange
    try:
        time_1 = Time(time_1)
    except ValueError:
        time_1 = Time(time_1, format="mjd")
    try:
        time_2 = Time(time_2)
    except ValueError:
        time_2 = Time(time_2, format="mjd")

    re_iso = re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    targets = []
    collisions = {"Name": "Collisions",
                  "Fibers": [],
                  "Times": [],
                  "RETime": re_iso,
                  "REEvent": "[\d-]+ [\d:,]+ - ERROR - A collision was"
                             " detected in positioner \d+",
                  "REFiber": re.compile("(?<=positioner )\d+")}
    oor_errors = {"Name": "Out of Range",
                  "Fibers": [],
                  "Times": [],
                  "RETime": re_iso,
                  "REEvent": "[\d-]+ [\d:,]+ - WARNING - JaegerUserWarning -"
                             " Positioner \d+ replied to SEND_TRAJECTORY_DATA"
                             " UID=\d+ with 'VALUE_OUT_OF_RANGE'.",
                  "REFiber": re.compile("(?<=Positioner )\d+")}
    if run_collisions:
        targets.append(collisions)
    if run_outofrange:
        targets.append(oor_errors)
    for sjd in range(int(time_1.mjd), int(time_2.mjd) + 1):
        sjd = Time(sjd, format="mjd")
        log_path = (sdss_paths.logs
                    / f"jaeger/jaeger.log.{sjd.isot.replace('T', '_')[:19]}")
        if not log_path.exists():
            log_path = log_path.with_suffix(".gz")
        if verbose >= 1:
            print(log_path)
        if log_path.suffix == ".gz":
            with gzip.open(log_path, "rb") as fil:
                text = fil.read().decode('utf-8')
        else:
            with log_path.open('r') as fil:
                text = fil.read()
        for d in targets:
            for match in re.findall(d["REEvent"], text):
                time = Time(d["RETime"].search(match).group(0), format="iso")
                if time in d["Times"]:
                    continue
                d["Times"].append(time)
                d["Fibers"].append(int(d["REFiber"].search(match).group(0)))

    for d in targets:
        print(f"{d['Name']} Events")
        print(f"{'Time':<20} {'SJD':>6} {'Fiber':>5}")
        print('=' * 80)
        for t, c in zip(Time(d['Times']), d['Fibers']):
            print(f"{t.iso[:19]:<20} {t.mjd:>6.0f} {c:>5.0f}")

        print(f"\n{'Fiber':>5} {'Count':>10}")
        print('=' * 80)
        for fiber in set(d["Fibers"]):
            print(f"{fiber:>5.0f} {d['Fibers'].count(fiber):>10.0f}")
        print()

    return 0


if __name__ == "__main__":
    main()
