# ObserverTools

### Dylan Gatlin
This is a home for Python 3 tools which came from the sdss-hub:~/bin directory.
 It is designed primarily for SDSS-V usage. This README should be updated to
 include any new scripts intended for users in normal observing.
 
## Structure
Files that were once under sdss-hub:~/bin are now under old_bin, and Python 3
 scripts are now under bin. Any non-user tools are stored under python. All
 user tools have tests.
 
## sloan-log.py
This tool is designed to be able to populate the majority of the night log by
 pulling all necessary info from the files produced that night. It uses
 log_apogee.py, log_boss.py, log_support.py, and mjd.py, and will print a
 variety of logging outputs. Run `./sloan-log.py -h` for usage documentation.
 
## ads9.py
This creates a ds9 window displaying the most recent APOGEE image. Run
 `./ads9.py -h` for usage documentation. Needs no arguments for proper
 usage.
 
## TimeTracking
Originally under sdss-hub:~/bin/time_tracking, it contains scripts designed for
 time tracking.

## Guidelines
All scripts designed for users should follow PEP-8, include a main function,
 and use argparse if arguments are needed. Prefer pathlib and fitsio. Scripts
 should try to be runnable on sdss-hub if possible. Anything in old_bin should
 be considered not ready and should be avoided during standard observations.
 
## Dependencies

### Ubuntu
```bash
sudo apt install libxt-dev libbz2-dev
```

### Python
```bash
pip install pyds9 fitsio astropy numpy pathlib tqdm channelarchiver scipy pyfits channelarchiver
```