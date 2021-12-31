#!/usr/bin/env python3
"""
This is a prototype script that can't really be tested until we have an
InfluxDB key, but it's a work in progress.
Author: Dylan Gatlin
"""
import platform    # For getting the operating system name
import getpass
import argparse
import subprocess as sub

from pathlib import Path
from influxdb_client import InfluxDBClient
from astropy.time import Time

from bin import sjd


__version__ = "3.0.0"

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
     Remember that a host may not respond to a ping (ICMP) request even if the
     host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', "-i", "0.5", host]
    x = sub.run(command, stdout=sub.PIPE)
    return x.returncode == 0

def get_key():
    """Finds a file called .influx.key that has 3 lines, a user id, an org id,
    and a token, each on its own line. The file can be in the current directory
    or the home directory
    TODO: Put an influx.key somewhere that all observers can use it.
    """
    key_path = Path.home() / ".influx.key"
    if not key_path.exists():
        key_path = Path(".") / ".influx.key"
    with key_path.open('r') as fil:
        user_id = fil.readline().rstrip('\n')
        org_id = fil.readline().rstrip('\n')
        token = fil.readline().rstrip('\n')
    return user_id, org_id, token


def get_client(org_id, token):
    client = InfluxDBClient(url="http://10.25.1.221:8086", token=token,
                            org=org_id)
    
    if not client.ready():
        print("Did not reach 10.25.1.221")
        client = InfluxDBClient(host="localhost", port=8086, username=None,
                                password=None, headers={"Authorization": token})
    return client



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mjd", type=float, help="SJD of observations")
    parser.add_argument("--t1", "--start-time", dest="start_time", help="Start"
        " time for astropy.time to parse, preferable isot")
    parser.add_argument("--t2", "--end-time", dest="end_time", help="Start time"
        " for astropy.time to parse, preferable isot")
    parser.add_argument("-f", "--file", nargs='+', help="A file path of a .flux"
        " influxdb query file")
    parser.add_argument("-i", "--interval", default="1m", help="Time interval")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="Verbose debugging")

    args = parser.parse_args()

    if (not args.mjd ) and (not args.start_time and not args.end_time):
        args.start_time = Time(sjd.sjd(), format="mjd")
        args.end_time = Time.now()
    elif args.mjd:
        args.start_time = Time(args.mjd - 1, format="mjd")
        args.end_time = Time(args.mjd, format="mjd")
    return args


def main(args=None):
    if args is None:
        args = parse_args()
    user_id, org_id, token = get_key()
    client = get_client(org_id, token)
    query_api = client.query_api()
    if args.verbose:
        print(f"Querying from {args.start_time.isot} to {args.end_time.isot}")
    if args.file:
        for f_path in args.file:
            f_path = Path(f_path)
            if f_path.exists():
                query = f_path.open('r').read()
        query_api = client.query_api()
        query = query.replace("v.timeRangeStart", f"{args.start_time.isot}Z")
        query = query.replace("v.timeRangeStop", f"{args.end_time.isot}Z")
        query = query.replace("v.windowPeriod", args.interval)
        if args.verbose:
            print(query)
        query_result = query_api.query(org=org_id, query=query)[0]
        print(query_result.records[-1]["_value"])
        
    return 0


if __name__ == "__main__":
    main()
