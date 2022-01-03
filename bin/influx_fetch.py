#!/usr/bin/env python3
"""
This is a prototype script that can't really be tested until we have an
InfluxDB key, but it's a work in progress.
Author: Dylan Gatlin
"""
import os
import argparse

from pathlib import Path
from influxdb_client import InfluxDBClient
from astropy.time import Time

from bin import sjd


__version__ = "3.0.0"


def get_key():
    """Finds a file called .influx.key that has 3 lines, a user id, an org id,
    and a token, each on its own line. The file can be in the current directory
    or the home directory
    TODO: Put an influx.key somewhere that all observers can use it.
    """
    if os.environ["INFLUXDB_V2_TOKEN"]:
        user_id = os.environ["INFLUXDB_V2_USER"]
        org_id = os.environ["INFLUXDB_V2_ORG"]
        token = os.environ["INFLUXDB_V2_TOKEN"]
        return user_id, org_id, token
        
    key_path = Path.home() / ".influx.key"
    if not key_path.exists():
        key_path = Path(".") / ".influx.key"
    elif not key_path.exists():
        raise KeyError("Influx Key not found, cannot send a query without one")
    with key_path.open('r') as fil:
        user_id = fil.readline().rstrip('\n')
        org_id = fil.readline().rstrip('\n')
        token = fil.readline().rstrip('\n')
    return user_id, org_id, token


def get_client(org_id=None, token=None):
    if (org_id is None) or (token is None):
        user_id, org_id, token = get_key()
    client = InfluxDBClient(url="http://10.25.1.221:8086", token=token,
                            org=org_id)
    
    if not client.ready():
        print("Did not reach 10.25.1.221")
        client = InfluxDBClient(host="localhost", port=8086, username=None,
                                password=None, headers={"Authorization": token})
    return client.query_api()


def query(flux_script, start, end, interval="1s"):
    user, org, token = get_key()
    client = get_client(org_id=org, token=token)
    query = flux_script
    query = query.replace("v.timeRangeStart", f"{start.isot}Z")
    query = query.replace("v.timeRangeStop", f"{end.isot}Z")
    query = query.replace("v.windowPeriod", interval)
    result = client.query(query=query, org=org)
    return result
    

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
    if args.verbose:
        print(f"Querying from {args.start_time.isot} to {args.end_time.isot}")
    if args.file:
        for f_path in args.file:
            f_path = Path(f_path)
            if f_path.exists():
                query = f_path.open('r').read()
        query = query.replace("v.timeRangeStart", f"{args.start_time.isot}Z")
        query = query.replace("v.timeRangeStop", f"{args.end_time.isot}Z")
        query = query.replace("v.windowPeriod", args.interval)
        if args.verbose:
            print(query)
        query_result = client.query(org=org_id, query=query)
        print(query_result)
        print(f"{'Time':23} {'Measurement':15} {'Field':15} {'Value':}")
        print("=" * 80)
        for res in query_result:
            for val in res:
                print(f"{Time(val.get_time()).isot:23} {val.get_measurement():15} {val.get_field():15} {val.get_value()}")
    return 0


if __name__ == "__main__":
    main()
