# Change Log

## [3.1.0] - 2020-07-01

- Added changelog and changed version numbers to 3-part strings in compliance
 with SDSS coding standards

## [3.2.0] - 2020-07-02

- Added help.py and test_help.py

## [3.2.1] - 2020-07-05

- Improved authorship credit in bin, included authors from old_bin into README

## [3.2.2] - 2020-07-09

- ds9_live.py now reads the previous image if it's APOGEE and not on the APOGEE
 virtual machine. This eliminates all known crashes.

- Added several symlinks to scripts to preserve old naming support, this won't
 work for all scripts though

- Added BSD 3 Clause License

## [3.2.3] - 2020-07-29

- sloan_log.py now returns a clear warning when you try to get morning cals that
 don't exist yet

- If the APOGEE dither position is not A or B, it still formats well in the
 list_ap table

- Added some PyCharm files and fits files to gitignore properly

## [3.3.0] - 2020-08-12

- sloan_log.py uses the ap_test in apogee_data instead of ap_test. It will be
 more like the actual APOGEE reduction since it uses the quickred files.

- Removed several TODOs related to ap_test, now passes unittests

- Changed the apogee quickred flat file to one of the oldest available at APO,
 this is not a permanent solution, the original file's quickred version should
 be used once found.

## [3.3.1] - 2020-08-17

- help.py now includes WAVEMID and XMID

- Tests for XMID and WAVEMID now in tests

- WAVEMID and XMID are now symlinked to x_mid.py and wave_mid.py for import
 (this usually won't work, but it gives some flexibility)

- ds9_live.py should support 2-camera modes and should only open 2 ds9 tiles

- help text has been updated in several argparses

## [3.4.0] - 2020-10-10

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

- Removed `python=3.7.8` from requirements.txt because that breaks the pip
 install

## [3.4.2] - 2020-10-11

- Added MANIFEST.in to include CHNAGELOG and LICENSE for installation

## [3.4.3] - 2020-10-11

- Added requirements.txt to MANIFEST.in

## [3.4.4] - 2020-10-12

- Offset outputs now print using textwrap more efficiently

- Changed requirements.txt from >= to ~=

- Added a pypi long_description

- Fixed sjd from 0.25 to 0.3

- Added authors, author email, and license to setup.py

## [3.4.5] - 2020-10-17

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

- Refactored python /*to python/sdssobstools/*

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

## [3.6.14] - 2021-08-27

- Major changes to epics_fetch.py to parse multiple keys into one table

## [3.6.15] - 2021-09-06

- Added eval_pointing.py to study ecam images with plots, tables, and more

- Added pydl to requirements

- Added FPI support to sloan_log.py

## [3.7.0] - 2021-09-28

- Added sdssobstools/sdss_paths to find /data on different machines

- Fixed ap_test to work like sloan_log's implimentation

- Added shortcut scripts called ads9.py and spds9.py

- Fixed argparse to work with main function by setting the default argument
 in main to None, important for unittests

- Changed many unittests to use new dates (SJD 59392)

## [3.7.3] - 2021-10-13

- With the (alleged) death of sdss-telemetry, epics_fetch now always fails, it
 has been resolved in all testable ways

- After discovering that symlinks don't install with setuptools, some
 mini-scripts have been added to bin with common aliases that point to the
 desired location

- Fixed several keywords like cart id and plateid in apogee_data, boss_data,
 and sloan_log.py

- Added /Volumes/data to the sdss_paths library

- Added bin/fsc_coord_convert.py to help track coordinates in the fsc.

## [3.7.4] - 2021-11-14

- Supppressed the output when pyds9 initializes a DS9 window

- Removed epics_fetch.py from telescope_status.py, log_support.py,
 apogee_data.py, get_dust.py

- Changed apogee dither checker lines

- Added sdss_paths support to list_ap

- Fixed a ds9_live bug with nfs file mounts that aren't always ready to be read

## [3.7.5] - 2021-11-15

- Fixed a bug where setuptools wouldn't include files that didn't end in py

## [3.7.6] - 2021-11-21

- Fixed list_ap for non-hub
- Fixed ds9_live.py to run on sdss5-display for multiple days
- ds9_live.py now displays the most recent apogee images
- Added FVC to ds9_live.py with -k

## [3.7.7a] - 2021-12-04

- Added gfa_fwhm.py that computes the fwhm of gfa exposures
- Added kronos and roboscheduler to versions.py
- Almost have a working version of influx_fetch.py

## [3.7.7b] - 2021-12-14

- Supports gfa_fwhm.py for gzipped images.

## [3.7.7c] - 2021-12-31

- Major changes to influx_fetch.py
- Various flux queries added under /flux
- get_dust.py now uses influx
- log_support.py now uses influx
- versions.py checks disk usage
- telescope_status.py checks enclosure history
- influx_fetch.py can read an environment variable or influx.key file
- help.py simplified a ton
- epics_fetch.py removed

## [3.7.7] - 2022-01-16

- tpm queries use multiprocess to handle failure
- test updates to keep up with influx changes
- Added new master dome flat using apq quickred files
- Removed old_bin, almost nothing there works anymore.

## [3.7.8a] - 2022-01-17

- README.md changes
- setup.py added missing stuff like flux folder and master flat

## [3.7.8b] - 2022-01-17

- Remapped paths to .flux files

## [3.7.8] - 2022-01-20

- Bump version for release

## [3.7.9] - 2022-01-28

- gfa_fwhm.py accounts for optimal focus offsets of added filters, actual values
  may need adjustment
- tpm_feed.py was causing a seg fault for plotting, the GtkAgg setting was
  removed to fix it
- aptest can now plot (previously, the plot would close instantly)
- Cleaned up some .open('r').read() methods
- Some test case updates, mostly moving to newer dates
- Some NFS error hanlding in sloan_log.py

## [3.7.10] - 2022-01-30

- gfa_fwhm.py gained a function get_img_path that finds the optimal gfa image,
  now used everywhere in gfa_fwhm.py
- gfa_fwhm.py offsets have been adjusted, based on several nights of data
- gfa_fwhm.py refines the quadratic fit with chi squared rejection
- Various scripts have better nfs error handling (although it's not perfect)
- sloan_log.py bundles -d sets based on design, not time
- APOGEE master flat updated after a bug was found in the apogee pipeline
- gfa_fwhm.py can now ignore images with -i

## [3.7.11] - 2022-03-04

- Some flux queries use the new actors bucket, log support is now fully
 populated
- sloan_log.py -d adds a hartmann section for each field
- dither centers adjusted in sloan_log.py
- sloan_log.py uses a field-based pairing for the data section instead of a
  desgin-based pairing
- telescope_status.py reports chiller values
- gfa_fwhm.py -c default number of exposures reduced to 15

## [3.7.12] - 2022-04-03

- gfa_fwhm.py flexibly handles ignoring cameras
- silly tkinter dependancy in previous version removed, just a typo
- sloan_log.py summary matches survey requested format
- get_dust.py runs at higher time resolution
- APOGEE fiber ID order flipped
- Log Support timeouts increased
- sossy.py support fot field-design

## [3.7.13] - 2022-04-19

- Addressed empty log support windows

## [3.7.14] - 2022-04-19

- Whoops

## [3.8.0] - 2022-05-31

- Switched to pytest
- Fixed to log support on problematic nights
- moved dust.flux to actors bucket

## [3.8.1] - 2022-05-31

- Finally caught a bug that was giving empty log support sections

## [3.8.2] - 2022-06-02

- Fixed an enclosure-closed bug in log_support.py

## [3.8.3] - 2022-07-22

- Changes gfa_fwhm.py offsets

## [3.9.0] - 2022-08-07

- Added get_collisions.py, a tool to identify robot collisions
- Changed gfa_fwhm.py offsets again a little bit
- Fixed a bug in sloan_log.py with a new apogeeql change affecting FIELDID

## [3.9.1] - 2022-08-26

- Added time_summary.py to generate a time loss summary
- Improved various influx-dependant scripts for performance
- Renamed get_collisions.py to list_collisions.py
- list_collisions.py uses Influx to get designs

## [3.9.2] - 2022-10-28

- Created a new file, get_tel_positions.py, that is helpful for pointing models,
  mostly by pulling variables from InfluxDB.
- Added timeout function to influx_fetch.py query
- Switched influxdb to the new server location
- Removed apo-medium-retention from all queries
- Updated ap_test date
- Updated log support to fix weird capitalization errors in tcc
