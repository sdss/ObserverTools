#!/usr/bin/env python3

import re
import gzip
import click

from astropy.time import Time
from sdssobstools import sdss_paths

@click.command()
@click.option("-1", "--t1", "time_1", default=Time.now() - 20)
@click.option("-2", "--t2", "time_2", default=Time.now())
@click.option("-v", "--verbose", count=True)
def main(time_1, time_2, verbose: int):
    try:
        time_1 = Time(time_1)
    except ValueError:
        time_1 = Time(time_1, format="mjd")
    try:    
        time_2 = Time(time_2)
    except ValueError:
        time_2 = Time(time_2, format="mjd")
        
    collisions = []
    collision_times = []
    re_fiber = re.compile("(?<=positioner )\d+")
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
                text= fil.read()
        for match in re.findall("[\d-]+ [\d:,]+ - ERROR - A collision was"
                                " detected in positioner \d+", text):
            collision_times.append(Time(match.split(',')[0]))
            collisions.append(int(re_fiber.search(match).group(0)))
    
    print(f"{'Time':<20} {'Fiber':>5}")
    print('=' * 80)
    for t, c in zip(Time(collision_times), collisions):
        print(f"{t.iso[:19]:<20} {c:>5.0f}")
    
    print(f"\n{'Fiber':>5} {'Collisions':>10}")
    print('=' * 80)
    for fiber in set(collisions):
        print(f"{fiber:>5.0f} {collisions.count(fiber):>10.0f}")

        
    return 0

if __name__ == "__main__":
    main()