Files: 
timetrack.py
end_of_night.py
mjd.py

lessfits.sh
grepfits.py

config.cfg

timeTrackLib.py
timeTrackTest.py
---------------

-s:  spectro (boss, manga, maStar and so on)
-a:  apogee 
-v:  list of files for verification 

API for libs: 
getFiles
getHeaders
getHeadersSpectro
getHeadersApogee
sum by plugging and exposure duration ( to separate  twi observations 
of apogee  on manga plate isApogee vs co-observing apogee on manga plate. 
(exp time different, 42 reads vs 47 reads, need to separate this 
filter aborted data as different exp time vs time of observations - abort
filter not object and sciencse

API for timetracking: 
import getHeadersSpectro
import getHeadersApogee
options -a and -s - to print summary, options m1-m2 mjd range
create summary output

API for endOfNight: 
import getHeadersSpectro
import getHeadersApogee
options - mjd (one date)
get  both -s and -a  header




