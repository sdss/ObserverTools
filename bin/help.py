#!/usr/bin/env python3
"""
help.py

This is a file to pull the help for all programs in bin. Each script must be
 added individually, some scripts use argparse, so -h is called, others do not,
 and so their __doc__ is printed. Based on spHelp written by Elena.

2020-06-08  DG  Init, based on spHelp
2020-08-17  DG  Added XMID and WAVEMID
2020-10-18  DG  Added m4l
2022-01-09  DG Simplified the whole thing to text
"""

__version__ = '3.2.0'


doc="""
ObserverTools

Most of these tools have their own --help explanations that are more verbose

Scripts:
ads9.py: Shortcut for ds9_live.py -a
ap_test.py: Tests apogee dome flats (in progress)
aptest: Alias for ap_test.py
az_fiducial_error.sh: Checks mcp logs for fiducial crossings
boss_shap1sum.py: Hashes boss directories
ds9_live.py: Runs a ds9 window for any standard image directory
eval_pointint.py: Analyzes ecam pointing datasets
fsc_coord_conver.py: Converts tables of fsc coordinates to sky offsets
get_dust.py: Gets today's dust counts
getDust.py: Alias for get_dust.py
help.py: This script
influx_fetch.py: Queries InfluxDB, requires an influxdb key
list_ap: Prints apogee images, I recommend sloan_log.py -a instead
m4l: Alias for m4l.py
m4l.py: Gets Mirror numbers
mjd: Alias for sjd.py
plot_mcp_fiducials.py: Plots mcp fiducial crossings
sjd.py: Gets current sjd
sloan_log.py: A large and flexible logging tool including apogee, boss,
 log support, and much more.
sossy.py: Parse SOS outputs
spds9.py: Shortcut for ds9_live.py -b
spHelp: Alias for help.py
spVersion: Alias for versions.py
telescope_status.py: Creates telescope status section for night log
telStatus: Alias for telescope_status.py
time_track.py: A time tracking tool to anlayze monthly time usage
tpm_feed.py: Creates a feed/plot of TPM output
tpm_fetch.py: Queries TPM archive files without InfluxDB
versions.py: Prints various software versions and disk usage
wave_mid.py: Computes WAVEMID offsets
WAVEMID: Alias for wave_mid.py
x_mid.py: Computes XMID offsets
XMID: Alias for x_mid.py
"""
print(doc)
