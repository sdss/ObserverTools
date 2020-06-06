#!/usr/bin/env python
""" test run of DOS from manga from sdss-hub
[manga@sdss4-manga ~]$ mangadrp_version
trunk 8043
"""

import subprocess
import sys

HOST = "manga@sdss-manga"
Command = "mangadrp_version"

ssh = subprocess.Popen(["ssh", "%s" % HOST, Command],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
result = ssh.stdout.readlines()
if not result:
    error = ssh.stderr.readlines()
    print("ERROR, %s" % error, file=sys.stderr)
else:
    print(result)
