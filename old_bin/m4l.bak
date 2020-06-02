#!/bin/env python

"""m4l, m4l.py -  Get the mirror numbers"""

from telnetlib import Telnet
from traceback import format_exc

def mirrors () :
	'''Get the mirror numbers'''
	HOST = 'sdss4-host2.apo.nmsu.edu'
	PORT = 2001

#	Open the network connection
	try :
		tn = Telnet (HOST, PORT)
	except :
		print 'Telnet connection to %s:%d failed: %s' % (HOST, PORT, format_exc())
		return -1

#	Read the data

	try:
		tn.write ('\n')
	except :
		print 'Telnet write to %s:%d failed: %s' % (HOST, PORT, format_exc())
		return -1

	try:
		reply = tn.read_all ()
	except :
		print 'Telnet read from %s:%d failed: %s' % (HOST, PORT, format_exc())
		return -1

	tn.close()

	return reply

if __name__ == '__main__' :
	print mirrors()
