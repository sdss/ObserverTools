# ObserverTools

### Dylan Gatlin

This is a home for Python 3 tools which came from the sdss-hub:~/bin directory.
 It is designed primarily for SDSS-V usage. This README should be updated to
 include any new scripts intended for users in normal observing.
 
## sloan-log.py

This tool is designed to be able to populate the majority of the night log by
 pulling all necessary info from the files produced that night. It uses
 log_apogee.py, log_boss.py, log_support.py, and mjd.py, and will print a
 variety of logging outputs. Run `./sloan-log.py -h` for usage documentation.
 
## TimeTracking

Originally under sdss-hub:~/bin/time_tracking, it contains scripts designed for
 time tracking.
 
## Design Goals

All scripts designed for users should follow PEP-8, include a main function,
 and use argparse if arguments are needed. All scripts should avoid any GUIs
 as they will likely be run on terminals without any GUI functionality.