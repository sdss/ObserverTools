#!/bin/bash
#
# get plate list data for current JJD for LUI
#
# history:
# 09-24-2014 EM changed list_boss - to list;  list_ap1 to list_ap

export HOME=/home/observer
#-export HOME=/home/observer/bin
export SHELL=/bin/bash

BIN_DIR=$HOME/bin

if [ -f /home/sdss4/products/eups/bin/setups.sh ]; then
	source /home/sdss4/products/eups/bin/setups.sh
	setup idlspec2d
	SJD=`$BIN_DIR/sjd.py`
else
	exit
fi

# Get instrument

read -t 5 INSTRUMENT
INSTRUMENT=`echo $INSTRUMENT | tr -d '\r'`
[ $INSTRUMENT ] || INSTRUMENT=boss

# Create list

case $INSTRUMENT in
	'ap' | 'apogee' )
		/home/observer/bin/list_ap
	;;
	'boss' | 'eboss')
		idl 2> /dev/null <<EOF_BOSS
;-!path=!path+':/home/observer/'
!path=!path+':/home/observer/bin/'
;;#  -- print, !path
;;.compile /home/observer/list.pro
.compile /home/observer/bin/list.pro
.compile headfits,fxposit,mrd_hread,fxpar,gettok,valid_num
list,$SJD
EOF_BOSS
	;;
	'manga')
		idl 2> /dev/null <<EOF_MANGA
;-!path=!path+':/home/observer/'
!path=!path+':/home/observer/bin/'
;;#  -- print, !path
;;.compile /home/observer/list_manga.pro
.compile /home/observer/bin/list_manga.pro
.compile headfits,fxposit,mrd_hread,fxpar,gettok,valid_num
list_manga,$SJD
EOF_MANGA
	;;
### Marvels is GONE!
#	'mar')
#		idl 2> /dev/null <<EOF_MAR
#!path=!path+':/home/observer/'
#.compile /home/observer/list_mar.pro
#.compile headfits,fxposit,mrd_hread,fxpar,gettok,valid_num
#list_mar,$SJD
#EOF_MAR
#	;;
esac
