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
