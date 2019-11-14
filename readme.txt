Package for preparation of time tracking report. 
-------------
[observer@sdss4-hub time_tracking]$ ./timetrack.py -h
Current mjd= 58766
usage: timetrack.py [-h] [-m1 MJD1] [-m2 MJD2] [-a] [-b] [-m] [-v]

list of files for time tracking report

optional arguments:
  -h, --help            show this help message and exit
  -m1 MJD1, --mjd1 MJD1
                        start mjd, default current mjd
  -m2 MJD2, --mjd2 MJD2
                        end mjd, default current mjd
  -a, --apogee          get apogee report
  -b, --boss            get boss report
  -m, --manga           get manga report
  -v, --verbose         verbose data
--------------------

apogee.py program uses autoschedule, setup: 
module use /home/sdss4/products/Linux64/moduleFiles
module load autoscheduler  

example for apogee:
./timetrack.py -a -m1 58760 -m2 58766

-------------------
programs to use: 

timetrack.py
end_of_night.py
mjd.py
---------------
Other libraries:

lessfits.sh
grepfits.py
------------

config.cfg
to set path, it will be different when run on other computer with mounted hib 

---------------
Limitation: 
1)  I do not separate exposure durations for plates. I have 
consider exposure time (nreads) the same for each exposures for this plate
and equal the first considered exposure
2) I did not separate different pluggings
3) I read data from reduction directory, so, if not reduction, I might skip original data. 

sum by plugging and exposure duration ( to separate  twi observations 
of apogee  on manga plate isApogee vs co-observing apogee on manga plate. 
(exp time different, 42 reads vs 47 reads, need to separate this 
filter aborted data as different exp time vs time of observations - abort
filter not object and sciense

By Elena Malanushenko
2018-2019
elenam@apo.nmsu.edu