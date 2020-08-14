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

