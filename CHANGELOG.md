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


## [3.5.1] - 2020-11-5

- Removed pyfits from requirements.txt. The newest verion of pyfits breaks on
 the Macs
 
## [3.5.2] - 2020-11-5

- Removed fitsio version from requirements.txt The newest version of fitsio
 breaks on the Macs
 
## [3.5.3] - 2020-11-5

- With more Mac issues, I removed any fits package requirements and numpy's
 version
 
## [3.5.4] - 2020-11-5

- Screw it, removed all versions from requirements.txt because of this new pip
 change
 
## [3.5.5] - 2020-11-5

- By installing packages one by one, it looks like pytest-astropy uses psutil
 which is not python-3-only pip ready. Removing from requirements.txt
 
## [3.5.5] - 2020-11-5

- In sloan_log.py, it would break without tpmdgram via telescope_status.py,
 fixed 
 
## [3.5.6] - 2020-11-5

- Minor fix pushes

## [3.5.7] - 2020-11-5

- Fixed a case where has_tpm might not exist

## [3.5.8] - 2020-11-6

- Implemented the dt argument in tpm_fetch

- Undid all those software version changes I made because the bug was actually
 in the sdss-obs2 PYTHONPATH

- Started sossy.py, a tool to find SOS total signal to noise

- m4l.py can now save nominals with the write argument

- soss.py can handle plates with no signal

## [3.5.9] - 2020-11-25

- Changed tpm_fetch to tpm_feed, added tpm_fetch, that queries past data

- Changed main for tpm_fetch and tpm_feed so that main can be run in tests

- Added a master flat, taken from the previous nights of data since the MTP
 cleaning, only including upgraded carts

- Added tests for tpm_fetch.py

- telescope_status.py now more closely matches other tpmdgram-based scripts

- Added new scripts to help.py

- sloan_log.py now reports average fiber throughput percentage.

## [3.5.10] - 2020-11-30

- Added dat and tests to packages in an attempt to get them included in the dist
 which is more important now that we have a new master flat.
 
- Converted pathlib.Path to str in sloan_log.py

- Added dat folder contents to setup.py as package_data, works on my machine,
 ready for testing at hub
 
## [3.5.11] - 2020-11-30

- hub installs a script differently than I do locally, so the previous method
 didn't work. pkg_resources also didn't work, so I settled on using a path
 relative to apogee_data, which installs in a location more similar to the
 master flat than scripts like sloan_log.py
 
## [3.5.12] - 2020-12-05

- Made some changes to tpm_fetch.py to have some features Dan0 included in a
 similar script.
 
- Added an mjd window test for test_tpm_fetch.py

## [3.6.0] - 2021-01-20

- Replaced tpmdgram with tpmdata, runs while tpm is open!

- Working on changes in time tracking to work in SDSS-V

- Working draft of time_track.py added to bin

- sloan_log.py shows 1 or 2 or x for APOGEE quickred

- sloan_log.py shows the dithers for all APOGEE images even if no dither occured

- log_support uses apogee:exposureWroteSummary for callbacks

- log_support checks to see if the mission is defined in each callback 
  (not during cals)

- Fixed a bug with sossy on plates with only 1 table row

- Some changes to ds9_live.py to handle name conflicts

- Changed a variety of tests to support Macs that can't make /data and must
  instead use ~/data
 
## [3.6.1] - 2021-03-09

- Fixed a bug in time_track.py where images taken with NoBOSS bypass would
  replace the lead survey from BHM to MWM.
  
- Added support for the legacy aptest in sloan_log.py

## [3.6.2] - 2021-04-11

- Added test suite for legacy aptest

- Changed the apogee data print to a max min and average instead of a long list

## [3.6.3] - 2021-04-11

- Fixed a printing bug in sloan_log.py

## [3.6.4] - 2021-04-11

- Fixed the object dither to be in the right units

## [3.6.5] - 2021-05-11

- Fixed a bug in object offsets in sloan_log.py

- Added legacy aptest support to ap_test.py

- Refactored python/* to python/sdssobstools/*

## [3.6.6] - 2021-05-11

- Trying a different method of setuptools that might be better, 3.6.5 doesn't
 work once installed
  
## [3.6.7] - 2021-05-11

- Same as 3.6.6...again

## [3.6.8] - 2021-05-12

- A method more like what it used to be, without calling the package python to
 prevent mixups
  
## [3.6.9] - 2021-05-12

- Caught some relative file path mixups that needed to be returned to what they
 were
  
## [3.6.10] - 2021-05-12

- Updated dependencies

## [3.6.11] - 2021-06-09

- Finally figured out how to get setuptools to handle a python library correctly

## [3.6.12] - 2021-08-20

- Added initial influx support

- Modified time_track.py to support ap2D images.

## [3.6.13] - 2021-08-22

- Fixed a bug in sloan_log.py where images with plate_id==0 didn't display
