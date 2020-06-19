#!/usr/bin/env python3 

"""mcptpm.py [-m mjd] - the list of mcptpm directory """

import sys
import argparse
from bin import sjd
import subprocess as sb


# ------

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    desc = 'mcptpm directory list '
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-m', '--mjd',
                        help='mjd, default is current mjd',
                        default=sjd.sjd(),
                        type=int)
    args = parser.parse_args()
    day = args.mjd

    host = "hub25m"
    print("/data/mcptpm/%s" % day)
    print("need pwd for observer@sdsshost2")
    COMMAND = "ls -la /data/mcptpm/%s" % day
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
