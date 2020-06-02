#!/usr/bin/env python

from pickle import loads
from telnetlib import Telnet
from traceback import print_exc

HOST = 'plate-mapper3-p.apo.nmsu.edu'
PORT = 2001

def readMIG() :
	'''Reads the Mitutoyo profilometry gauges from HOST:PORT,
	returning the values as a list of strings.  Bad gauge(es) are
	indicated by the string "MIG Error" instead of a value.
	'''

#	Open the network connection
	try :
		tn = Telnet (HOST, PORT)

	except :
		print('Telnet connection to ' + HOST + ':' + PORT + ' failed')
		print_exc()
		return -1

#	Read the pickle

	try:
		reply = tn.read_all ()
	except :
		print('Connection to ' + HOST + ':' + PORT + ' prematurely closed\nReply: ' + reply)
		print_exc()
		return -1

#	Return the values

	tn.close()
	return loads (reply)

if __name__ == '__main__' :
	print(readMIG())
