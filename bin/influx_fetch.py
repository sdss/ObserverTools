#!/usr/bin/env python3
"""
This is a prototype script that can't really be tested until we have an
InfluxDB key, but it's a work in progress.
Author: Dylan Gatlin
"""
import platform    # For getting the operating system name
import getpass
import subprocess as sub

from influxdb_client import InfluxDBClient


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
     Remember that a host may not respond to a ping (ICMP) request even if the
     host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return sub.run(command, stdout=sub.PIPE) == 0


pwrd = getpass.getpass("Please enter InfluxDB Password: ")
if ping("10.25.1.221"):
    client = InfluxDBClient(host="10.25.1.221", port=8086,
                            username="influx_user", password=pwrd)

else:
    client = InfluxDBClient(host="localhost", port=8086, username="influx_user",
                            password=pwrd)
    print(client.ping())
    if client.ping() != "pong":
        raise ConnectionError("Unable to reach Influx")

print(client.ping())  # It shouldn't actually return "pong", it should return
# the version of InfluxDB used
