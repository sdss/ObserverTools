#!/usr/bin/env python3

"""
Creates an file with a list of sha1 hashes in the same directory as the raw data
under /data/spectro. This script run like

boss_sha1sum.py MJD [MJD2] [MJD3]...



Created by Stephen Bailey (LBNL) Fall 2011
2020-06-01      dgatlin     Completely rewrote it for Python 3 and modern
    libraries. It now includes tests and runs more flexibly.
"""

import hashlib
from argparse import ArgumentParser
from pathlib import Path
from bin import sjd

__version__ = '3.0.0'


def create_hash_line(file):
    file = Path(file)
    hsh = hashlib.sha1(file.read_bytes())
    out = '{}  {}\n'.format(hsh.hexdigest(), file.name)
    return out


def write_hashes(path, output_file):
    path = Path(path)
    out = output_file.open('w')
    for fits in path.glob('*.fit.gz'):
        out.write(create_hash_line(fits))


def parseargs():
    parser = ArgumentParser(description='Creates a file with a list of sha1'
                                        ' hashes in the same directory as the'
                                        ' data, which is stored at the provided'
                                        ' mjd. If no mjd is provided, then it'
                                        ' is run for today.')
    parser.add_argument('mjds', nargs='?', default=[sjd.sjd()],
                        help='The mjd (or mjds) which you want to create a sum'
                             ' for')
    parser.add_argument('-f', '--file', 
                        help='The location of the sha1sum file for output,'
                             ' default is /data/spectro/<mjd>/<mjd>.sha1sum.'
                             ' Only works if one or fewer mjds is provided.')

    args = parser.parse_args()
    return args


def main():
    args = parseargs()
    for mj in args.mjds:
        data_dir = Path('/data/spectro/{}'.format(mj))
        if args.file:
            output_file = Path(args.file)
        else:
            output_file = data_dir / '{}.sha1sum'.format(mj)
        print(args.file)
        write_hashes(data_dir, output_file)


if __name__ == '__main__':
    main()
