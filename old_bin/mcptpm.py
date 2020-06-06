#!/usr/bin/env python 

"""mcptpm.py [-m mjd] - the list of mcptpm directory """

import sys
import argparse
from . import mjd
import subprocess as sb


# ------

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    mjd = mjd.mjd()
    desc = 'mcptpm directory list '
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', '--mjd',
                        help='mjd, default is current mjd',
                        default=mjd,
                        type=int)
    args = parser.parse_args()
    mjd = args.mjd

    host = "hub25m"
    print("/data/mcptpm/%s" % mjd)
    print("need pwd for observer@sdsshost2")
    COMMAND = "ls -la /data/mcptpm/%s" % mjd
    ssh = sb.Popen(["ssh", "%s" % host, COMMAND], shell=False, stdout=sb.PIPE,
                   stderr=sb.PIPE)
    result = ssh.stdout.readlines()

    if result == []:
        error = ssh.stderr.readlines()
        print("ERROR: %s" % error, file=sys.stderr)
    else:
        for r in result:
            print(r.strip())


# ------

if __name__ == "__main__":
    sys.exit(main())
