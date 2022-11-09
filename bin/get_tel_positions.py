#!/usr/bin/env python3

import click
import numpy as np
import matplotlib.pyplot as plt
from collections.abc import Iterable
from astropy.time import Time
from pathlib import Path
from bin import influx_fetch, sjd
from sdssobstools import sdss_paths


@click.command()
@click.option("-m", "--mjd", type=int, default=sjd.sjd())
@click.option("-p", "--plot", is_flag=True)
def main(mjd: int, plot):
    tstart = Time(mjd, format="mjd")
    tend = Time(mjd + 0.5, format="mjd")
    tend = Time.now() if Time.now() < tend else tend
    flux_dir = Path(sdss_paths.__file__).absolute().parent.parent / "flux"
    fields_fil = flux_dir / "jaeger_fields.flux"

    field_times = []
    fields = []
    fields_qry = influx_fetch.query(fields_fil.open('r').read(), tstart, tend)
    for table in fields_qry:
        for row in table.records:
            field_times.append(row.get_time())
            fields.append(row.get_value())
    field_times = Time(field_times, format='datetime')
    fields = np.array(fields)
    fields = fields[field_times.argsort()]
    field_times = field_times[field_times.argsort()]

    scis_fil = flux_dir / "science_exposures.flux"
    sci_times = []
    scis_qry = influx_fetch.query(scis_fil.open('r').read(), tstart, tend)
    for table in scis_qry:
        for row in table.records:
            sci_times.append(row.get_time())
    sci_times = Time(sci_times, format='datetime')
    sci_times = sci_times[sci_times.argsort()]

    target_times = []
    target_fields = []
    for t in sci_times[1::4]:
        field = fields[field_times < t][-1]
        if field not in target_fields:
            target_times.append(t)
            target_fields.append(field)

    offsets_fil = flux_dir / "offsets.flux"
    offs_query = influx_fetch.query(
        offsets_fil.open('r').read(), tstart, tend, "1s", timeout=60000)

    offs = {}

    for table in offs_query:
        for row in table.records:
            if row.get_field() in offs.keys():
                offs[row.get_field()].append(row.get_value())
                offs['t' + row.get_field()].append(row.get_time())
            else:
                offs[row.get_field()] = [row.get_value()]
                offs['t' + row.get_field()] = [row.get_time()]
    for key in offs.keys():
        if key[0] == 't':
            offs[key] = Time(offs[key], format='datetime')
        else:
            offs[key] = np.array(offs[key])

    tcc_fil = flux_dir / "tcc_positions.flux"

    tcc_qry = influx_fetch.query(
        tcc_fil.open('r').read(), tstart, tend, "1s"
    )
    for table in tcc_qry:
        for row in table.records:
            if row.get_field() in offs.keys():
                offs[row.get_field()].append(row.get_value())
                offs['t' + row.get_field()].append(row.get_time())
            else:
                offs[row.get_field()] = [row.get_value()]
                offs['t' + row.get_field()] = [row.get_time()]
    for key in offs.keys():
        if key[0] == 't':
            offs[key] = Time(offs[key], format='datetime')
        else:
            offs[key] = np.array(offs[key])
    if plot:
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        # ax.plot_date(offs['tobjArcOff_0_P'].plot_date, offs['objArcOff_0_P'],
        #  'k-',
        #  drawstyle="steps-post")
        ax.plot_date(offs["taxePos_alt"].plot_date,
                     offs["axePos_alt"],
                     "k-",
                     drawstyle="steps-post")
        for time in target_times:
            ax.axvline(time.plot_date, linewidth=0.5, c='r')
        # for time in field_times:
        # ax.axvline(time.plot_date, linewidth=0.5, c='b')

        plt.show()

    print(f"{'Time':<8} {'MJD':>6} {'Az':>9} {'Alt':>8} {'Rot':>9} {'RA':>9} {'Dec':>9}"
          f" {'dRA':>9} {'dDec':>9} {'Spider':>9} {'Max Time Error':>9}")
    print('=' * 80)
    for time in target_times:
        line = []
        time = offs["tobjArcOff_0_P"][offs["tobjArcOff_0_P"] < time][-1]
        errors = []
        for k in ("axePos_az", "axePos_alt", "axePos_rot", "objNetPos_0_P",
                  "objNetPos_1_P", "objArcOff_0_P", "objArcOff_1_P",
                  "spiderInstAng_P"):
            dts = np.abs((offs['t' + k] - time).sec)
            lhs = offs[k][dts.min() == dts]
            lhs = offs[k][offs['t' + k] <= time][-1]
            err = (offs['t' + k][dts.min() == dts] - time).sec
            if isinstance(err, Iterable):
                errors.append(err[0])
            else:
                errors.append(err)

            # rhs = offs[k][offs['t' + k] >= time][0]
            # line.append(np.mean((lhs, rhs)))
            line.append(lhs)
        print(f"{time.isot[11:19]:<8} {mjd:>6.0f} {line[0]:>9.4f} {line[1]:>8.4f}"
              f" {line[2]:>9.4f} {line[3]:>9.4f} {line[4]:>9.4f}"
              f" {line[5]:>9.4f} {line[6]:>9.4f} {line[7]:>9.4f}"
              f" {np.min(errors) if errors else np.nan:>9.1f}")


if __name__ == "__main__":
    main()
