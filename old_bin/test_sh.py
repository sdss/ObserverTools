#!/usr/bin/env python
''' test run of DOS from manga from sdss-hub 
[manga@sdss4-manga ~]$ mangadrp_version
trunk 8043
'''

import subprocess
import sys

HOST="manga@sdss-manga"
Command="mangadrp_version"

ssh=subprocess.Popen(["ssh", "%s" % HOST, Command],
                     shell=False,
					 stdout=subprocess.PIPE,
					 stderr=subprocess.PIPE)
result=ssh.stdout.readlines()
if result == []:
	error = ssh.stderr.readlines()
	print >> sys.stderr, "ERROR, %s" % error
else:
    print result



