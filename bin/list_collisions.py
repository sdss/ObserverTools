#!/usr/bin/env python3

import re
import gzip
import time
import click
import tqdm

import multiprocessing as mp
import numpy as np

from astropy.time import Time
from pathlib import Path

from sdssobstools import sdss_paths
from bin import influx_fetch


def get_designs(time_1, time_2, out_dict: dict={}):
    out_dict["Success"] = False
    q_path = Path(influx_fetch.__file__
                  ).parent.parent / "flux/jaeger_designs.flux"
    if not q_path.exists():
        raise FileNotFoundError(
            f"Could not file Flux query at {q_path.absolute()}")
    with q_path.open('r') as fil:
        query = fil.read()
        
    results = influx_fetch.query(query, time_1 - 1, time_2)
    if len(results) == 0:
        return
    
    times = []
    designs = []
    for result in results:
        for row in result.records:
            times.append(row.get_time())
            designs.append(row.get_value())
    
    out_dict["Times"] = Time(times, format="datetime")
    out_dict["Designs"] = np.array(designs)
    sorter = out_dict["Times"].argsort()
    out_dict["Times"] = out_dict["Times"][sorter]
    out_dict["Designs"] = out_dict["Designs"][sorter]
    out_dict["Success"] = True


@click.command()
@click.option("-1", "--t1", "time_1", default=Time.now() - 20,
              help="The start time, preferably in isot or SJD format."
              " By default, it's 20 days ago.")
@click.option("-2", "--t2", "time_2", default=Time.now(),
              help="The end time, preferably in isot or SJD format. By default,"
              " it is today")
@click.option("-c", "--collisions", is_flag=True, default=True,
              help="If used, will report robot collision detections")
@click.option("-d", "--designs", "do_designs", is_flag=True,
              help="Will query Influx to pair collisions with designs")
@click.option("-o", "--outofrange", is_flag=True,
              help="If used, will report VALUE_OUT_OF_RANGE errors")
@click.option("-i", "--individuals", is_flag=True,
              help="Prints individual collision events")
@click.option("-v", "--verbose", count=True, help="Verbose debugging")
def main(time_1, time_2, collisions, do_designs, outofrange, individuals,
         verbose: int):
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
    
    tstart = Time.now()
    if do_designs:
        designs_dict = mp.Manager().dict()
        design_p = mp.Process(target=get_designs,
                              args=(time_1, time_2, designs_dict))
        design_p.start()

    re_iso = re.compile("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    targets = []
    collisions = {"Name": "Collisions",
                  "Robots": [],
                  "Times": [],
                  "Designs": [],
                  "RETime": re_iso,
                  "REEvent": "[\d-]+ [\d:,]+ - ERROR - A collision was"
                             " detected in positioner \d+",
                  "RERobot": re.compile("(?<=positioner )\d+")}
    oor_errors = {"Name": "Out of Range",
                  "Robots": [],
                  "Times": [],
                  "Designs": [],
                  "RETime": re_iso,
                  "REEvent": "[\d-]+ [\d:,]+ - WARNING - JaegerUserWarning -"
                             " Positioner \d+ replied to SEND_TRAJECTORY_DATA"
                             " UID=\d+ with 'VALUE_OUT_OF_RANGE'.",
                  "RERobot": re.compile("(?<=Positioner )\d+")}
    if run_collisions:
        targets.append(collisions)
    if run_outofrange:
        targets.append(oor_errors)
    paths = []
    for sjd in range(int(time_1.mjd), int(time_2.mjd) + 1):
        sjd = Time(sjd, format="mjd")
        log_path = (sdss_paths.logs
                    / f"jaeger/jaeger.log.{sjd.isot.replace('T', '_')[:19]}")
        if not log_path.exists():
            log_path = log_path.with_suffix(log_path.suffix + ".gz")
        if verbose >= 1:
            print(log_path)
        if log_path.exists():
            paths.append(log_path)
    if (sdss_paths.logs / "jaeger/jaeger.log").exists():
        paths.append(sdss_paths.logs / "jaeger/jaeger.log")
    for log_path in tqdm.tqdm(paths):
        if log_path.suffix == ".gz":
            with gzip.open(log_path, "rb") as fil:
                text = fil.read().decode('utf-8')
        else:
            with log_path.open('r') as fil:
                text = fil.read()
        for d in targets:
            for match in re.findall(d["REEvent"], text):
                time_str = d["RETime"].search(match).group(0)
                if time_str in d["Times"]:
                    continue
                d["Times"].append(time_str)
                d["Robots"].append(int(d["RERobot"].search(match).group(0)))
    if do_designs:
        tend = Time.now()
        dt = (tstart - tend).sec
        while design_p.is_alive() and dt < 6:
            tend = Time.now()
            dt = (tstart - tend).sec
            time.sleep(1)
        design_p.join(6)
        dt = (tend - tstart).sec
        if verbose:
            print(f"Influx query took {dt}s")
 
        if not designs_dict["Success"]:
            raise TimeoutError("Couldn't complete InfluxDB query")
    
    for d in targets:
        d["Times"] = Time(d["Times"], format="iso")
        d["Robots"] = np.array(d["Robots"])
        if do_designs:
            for t, robot in zip(d["Times"], d["Robots"]):
                before_filt = designs_dict["Times"] < t
                d["Designs"].append(designs_dict["Designs"][before_filt][-1])
            d["Designs"] = np.array(d["Designs"])

    for d in targets:
        if individuals:
            print(f"{d['Name']} Events")
            if do_designs:
                print(f"{'Time':<20} {'SJD':>6} {'Robot':>5} {'Design':>6}")
            else:
                print(f"{'Time':<20} {'SJD':>6} {'Robot':>5}")
            print('=' * 80)
            if do_designs:
                for t, c, de in zip(d['Times'], d['Robots'], d["Designs"]):
                    print(f"{t.iso[:19]:<20} {t.mjd:>6.0f} {c:>5.0f},"
                          f" {de:>6.0f}")
            else:
                for t, c in zip(d['Times'], d['Robots']):
                    print(f"{t.iso[:19]:<20} {t.mjd:>6.0f} {c:>5.0f}")
            print()

        print(f"{d['Name']} Summary")
        if do_designs:
            print(f"{'Robot':>5}  {'Count':>10}  {'Unique-design Count':>19}")
        else:
            print(f"{'Robot':>5}  {'Count':>10}")
        print('=' * 80)
        for robot in sorted(set(d["Robots"])):
            this_robot = d["Robots"] == robot
            if do_designs:
                design_events = d["Designs"][this_robot]
                designs = set(design_events)
                print(f"{robot:>5.0f}  {np.sum(d['Robots']== robot):>10.0f}"
                      f"  {len(designs):>19.0f}")
            else:
                print(f"{robot:>5.0f}  {np.sum(d['Robots']== robot):>10.0f}")
        print()

    return 0


if __name__ == "__main__":
    main()
