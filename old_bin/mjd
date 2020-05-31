#!/usr/bin/env python
# Description:
#	Calculates the SDSS Julian Date, which is the MJD + 0.3 days
#	See http://maia.usno.navy.mil/
#
# History:
#	Jon Brinkmann, Apache Point Observatory, 9 Jan 1999
#		Created file

from time import time

def sjd () :
	''' Calculates the SDSS Julian Date, which is the MJD + 0.3 days
		See http://maia.usno.navy.mil/
	'''

#	NOTE: The next line must be changed everytime TAI-UTC changes
#		unless the host computer is already on TAI

#	TAI_UTC = 34	# TAI-UTC = 34 seconds as of 1/1/09
	TAI_UTC = 0	# hub25m is on TAI, so no conversion is necessary

	return int ((time() + TAI_UTC) / 86400.0 + 40587.3)

if __name__ == '__main__' :
	print sjd()
