# Change Log

## [3.1.0] - 2020-07-01

### Changed

- Added changelog and changed version numbers to 3-part strings in compliance
 with SDSS coding standards
 
## [3.2.0] - 2020-07-02

### Changed

- Added help.py and test_help.py

## [3.2.1] - 2020-07-05

### Changed

- Improved authorship credit in bin, included authors from old_bin into README

## [3.2.2] - 2020-07-09

### Changed

- ds9_live.py now reads the previous image if it's APOGEE and not on the APOGEE
 virtual machine. This eliminates all known crashes.

- Added several symlinks to scripts to preserve old naming support, this won't
 work for all scripts though
 
- Added BSD 3 Clause License

## [3.2.3] - 2020-07-29

### Changed

- sloan_log.py now returns a clear warning when you try to get morning cals that
 don't exist yet

- If the APOGEE dither position is not A or B, it still formats well in the
 list_ap table

- Added some PyCharm files and fits files to gitignore properly

## [3.3.0] - 2020-08-12

### Changed

- sloan_log.py uses the ap_test in apogee_data instead of ap_test. It will be
 more like the actual APOGEE reduction since it uses the quickred files.
 
- Removed several TODOs related to ap_test, now passes unittests

- Changed the apogee quickred flat file to one of the oldest available at APO,
 this is not a permanent solution, the original file's quickred version should
 be used once found.
 
## [3.3.1] - 2020-08-17

### Changed

- help.py now includes WAVEMID and XMID

- Tests for XMID and WAVEMID now in tests

- WAVEMID and XMID are now symlinked to x_mid.py and wave_mid.py for import
 (this usually won't work, but it gives some flexibility)
 
- ds9_live.py should support 2-camera modes and should only open 2 ds9 tiles

- help text has been updated in several argparses

## [3.4.0] - 2020-10-10

### Changed

- Added setup.py, requirements, and a modulefile, both of which could be used to
 setup an environment, although if you need to setup an Anaconda environment,
 modules cannot do that, but an Anaconda environment can set up sdss-obstools
 via setuptools

- Replaced conda_env.yml with the minimum requirements

- Replaced all import _____ from the project to from ___ import _____ which is
 better for setuptools

- Commented out pyds9's test module because it takes forever.

- For all channelarchiver input times, .isot was replaced with .datetime because
 their string parsing algorithm has an internal bug that can be bypassed when
 .datetime is given as input.

- Installable via PyPI via `pip install sdss-obstools==3.4.0

## [3.4.1] - 2020-10-11

### Changed

- Removed `python=3.7.8` from requirements.txt because that breaks the pip
 install

## [3.4.2] - 2020-10-11

### Changed

- Added MANIFEST.in to include CHNAGELOG and LICENSE for installation

## [3.4.3] - 2020-10-11

### Changed

- Added requirements.txt to MANIFEST.in

## [3.4.4] - 2020-10-12

### Changed

- Offset outputs now print using textwrap more efficiently

- Changed requirements.txt from >= to ~=

- Added a pypi long_description

- Fixed sjd from 0.25 to 0.3

- Added authors, author email, and license to setup.py

## [3.4.5] - 2020-10-17

### Changed

- log_support has a new keyword based on the changes made to actorkeys today
 (note: the new keyword will not work until there has been a sequence using that
 keyword.)

- Changed a raise Warning in apogee_data.py to a print so it doesn't cause
 the program to exit, encountered in img 35780004
 
## [3.4.6] - 2020-10-18

- ds9_live.py has args.info incorporated throughout (also in the tests)

- sloan_log.py now looks for sos directory when BHM is lead.

## [3.4.7] - 2020-10-18

- Internally, most programs use sjd instead of mjd

- sloan_log.py and log_support.py now only consider sp1 for hartmanns

- A printing bug in sloan_log.py where the times would be cut off is fixed

## [3.4.8] - 2020-10-18

- Removed a .swp file that breaks the install

## [3.4.9] - 2020-10-18

- Added m4l->m4l.py

- Added sdss-obstools to the outputs of sp_version.py

- Fixed wave_mid.py and x_mid.py in the help tools

- XMID and WAVEMID now support single-camera modes with tests

- Added test for m4l.py

## [3.4.10] - 2020-10-18

- Fixed a bug in m4l.py where it expected byte types in Python 3

- Added mirror numbers to sloan_log.py

- Removed the xx-xx for SP2 in sloan_log.py if they're not found

## [3.4.11] - 2020-10-22

- Modified m4l to run from home via a localhost forward

- Fixed some sloan_log.py tests to include mirror numbers

- Fixed sloan_log.py to include a section name for Mirror numbers

- Gave m4l.py __version__

## [3.4.12] - 2020-10-24

- Increased the mirror number timeout to 2s

- Removed ./sdss-obstools because it was meant for modules which we will not use

- Swapped '--mirrors' and '--mirror' in sloan_log's argparse section so that
 mirrors is the actual argument name

## [3.4.13] - 2020-10-24

- Removed SP2 from sloan_log.py hartmann outputs

- Updated sloan_log.py summary to more accurately fit SDSS-V

## [3.5.0] - 2020-11-1

- ds9_live.py now has a vertical layout option

- New file: tpm_fetch.py, that plots a tpm variable or prints it

- Tests for tpm_fetch.py

- New file: telescope_status.py, with symlink telStatus

- telescope_status.py tests

- epics_fetch.py now handles list inputs directly

- Added vertical layout option to ds9_live tests  

- Integrated telescope_status into sloan_log
