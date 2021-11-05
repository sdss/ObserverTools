#!/usr/bin/env python3
"""A tool to convert from the FSC coordinates of r, theta to standard RA, Dec
 for tcc
"""
import numpy as np
from argparse import ArgumentParser, ArgumentError

__author__ = "Dylan Gatlin"
__version__ = "3.0.0"


def converter(r, theta):
    return r * np.sin(np.deg2rad(theta)), r * np.cos(np.deg2rad(theta))


def arg_parse():
    parser = ArgumentParser(description="A tool for converting coordinates to"
            " from FSC's r, theta to RA and Dec offsets for tcc. If given with"
            " arguments, give them in pairs of space-separated r and thetas."
            " You can put multiple, as long as they're in order. If no pairs"
            " are given, then a default value will be filled which will cover"
            " the entire focal plane and is what we have done in the past.")
    parser.add_argument("rthetapairs",
            help="r and theta, separated by spaces, as many times as you like."
                 " in sky degrees (1.5deg = 333.3mm)", nargs='*', type=float)
    parser.add_argument("--tcc-offset", action="store_true", help="Print tcc"
            " offset commands instead of a table")
    return parser.parse_args()


def main(args=None):
    if args is None:
        args = arg_parse()
    if len(args.rthetapairs) % 2 != 0:
        raise ArgumentError("rthetapairs must be an even number of args!")
    if len(args.rthetapairs) == 0:
        for r in np.array([1.5, 1.125, 0.75, 0.375]):
            for th in np.arange(180, -180, -60):
                args.rthetapairs.append(r)
                args.rthetapairs.append(th)
    if not args.tcc_offset:
        print(f"{'R':10} {'Theta':10} {'RA':10} {'Dec':10}")
    for i in range(len(args.rthetapairs) // 2):
        r = args.rthetapairs[i * 2]
        theta = args.rthetapairs[i * 2 + 1]
        ra, dec = converter(r, theta)
        if not args.tcc_offset:
            print(f"{r:9.5f}\N{DEGREE SIGN} {theta:9.1f}\N{DEGREE SIGN}"
            f"{ra:9.5f}\N{DEGREE SIGN} {dec:9.5f}\N{DEGREE SIGN}")
        else:
            print(f"tcc offset arc/pabs /computed {ra:.5f}, {dec:.5f}")
    return 0


if __name__ == "__main__":
    main()

