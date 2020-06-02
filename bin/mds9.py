#!/usr/bin/env python3
"""
Description:	Opens and continuously updates ds9 with the latest raw APOGEE file

History:
Jun 21, 2011	Jon Brinkmann	Apache Point Observatory Created file from
    spds9.py
2020-05-31      Dylan Gatlin    Replaced almost every library for a python 3
    upgrade. ds9 -> pyds9, os.path -> pathlib, optionparse -> argparse. Updated
    syntax to Python 3 and greatly improved PEP-8 compliance. Changed source
    of apogee data to work on any system

"""
from pathlib import Path
from argparse import ArgumentParser
import os
import pyds9
import time

verbose = False
default_dir = '/data/apogee/utr_cdr/'  # This works on any system, not just
# apogee

__version__ = 3.0


class ADS9:
    """Displays the last image from the guider camera in ds9"""

    def __init__(self, args):

        # Constants and variables

        self.last_file = ''

        # Arguments
        self.args = args
        if not self.args.fits_dir:
            self.args.fits_dir = default_dir

        if not self.args.target:
            self.args.target = 'ads9.{}'.format(os.getpid())

        if self.args.verbose:
            print('dir = {}\ntarget = {}\nscale = {}\nzoom = {}'.format(
                self.args.fits_dir, self.args.target, self.args.scale,
                self.args.zoom))

        # Initialize

        self.ds9 = pyds9.DS9(self.args.target)

    @staticmethod  # This means it doesn't take self as an argument
    def is_fits(filename):
        """Returns whether a file is a FITS file based on its extension"""
        if not isinstance(filename, Path):
            filename = Path(filename)

        if 'fit' in filename.name:
            return True
        else:
            return False

    def latest_fits_dir(self):
        """Returns the latest sub-directory"""

        max_time = -1
        dirname = ''

        # Obtain the files in the directory and add the full path to them

        for file in Path(self.args.fits_dir).glob('*'):
            file = file.absolute()

            if file.is_dir():

                # Store the name and mtime of only the latest FITS file

                mtime = file.stat().st_mtime
                # print max_time, file, mtime
                if max_time < mtime:
                    dirname = file
                    max_time = mtime

        return dirname

    def latest_fits_file(self, pattern):
        """Returns the latest FITS file matching <pattern>"""

        max_time = -1
        fits_filename = ''

        # Obtain the files in the directory and add the full path to them

        fits_dir = self.latest_fits_dir()

        # print 'dir = ', dir

        for file in Path(fits_dir).glob(pattern):
            file = file.absolute()

            # See if the file name matches the pattern and the file is a FITS
            # file

            if self.is_fits(file):

                # Store the name and mtime of only the latest FITS file

                mtime = Path(file).stat().st_mtime
                # print max_time, file, mtime
                if max_time < mtime:
                    fits_filename = file
                    max_time = mtime

        return fits_filename

    # return sorted (fits_files.items(), key=lambda (k,v): (v,k),
    # reverse=True)[0][0]

    def display(self, file, frame):
        """Display <file> in <frame> with optional scaling and zoom"""

        if frame >= 0 and file != '':
            self.ds9.set('frame {}'.format(frame))
            self.ds9.set('file {}'.format(file))

            if self.args.zoom:
                self.ds9.set('zoom to {}'.format(self.args.zoom))

            if self.args.scale:
                self.ds9.set('scale {}'.format(self.args.scale))

    def update(self):
        """Update the display"""

        file = self.latest_fits_file('apRaw*')
        if self.args.verbose:
            print('latest fits file = {}, last fits file = {}'
                  ''.format(file, self.last_file))

        if file != self.last_file:
            if verbose:
                print('displaying {}'.format(file))
            self.display(file, 0)
            self.last_file = file

    def close(self):
        self.ds9.set('exit')


# If run as a program, start here

def parseargs():
    # Define command line options

    parser = ArgumentParser(description='A tool to leave running continuously'
                                        'that will display the most current'
                                        'apogee exposure. By default, it will'
                                        'run every 60 seconds.')
    parser.add_argument('-d', '--directory', dest='fits_dir',
                        default=default_dir, type=str,
                        help='Set FITS data directory. It needs to be a'
                             'directory of dated folders, where the newest'
                             'folder has the newest data.'
                             ' Default is {}'.format(
                            default_dir))
    parser.add_argument('-V', '--version', action='store_true', help='Version'
                                                                     'info')
    parser.add_argument('-t', '--target', dest='target', default=None,
                        type=str,
                        help='Set ds9 target. Default is autogenerated.')
    parser.add_argument('-i', '--interval', dest='interval', default=60,
                        type=int, help='Set the refresh rate.	Default is 5'
                                       'seconds. Refreshes will be this '
                                       'number '
                                       ' of seconds apart.')
    parser.add_argument('-s', '--scale', dest='scale', default='histequ',
                        type=str, help='Set scaling. Default is "histequ"')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        default=False,
                        help='Be verbose. Default is to be quiet.')
    parser.add_argument('-z', '--zoom', dest='zoom', default='1.0',
                        type=str, help='Set zoom factor. Default is 1.0')

    # Get command line arguments

    args = parser.parse_args()

    if args.verbose:
        print('interval = {}'.format(args.interval))
        print('scale = {}'.format(args.scale))
        print('zoom = {}'.format(args.zoom))

    if args.version:
        print(__version__)

    return args


def main():
    args = parseargs()
    # Start the display
    a = ADS9(args)

    while True:
        a.update()

        time.sleep(args.interval)


if __name__ == '__main__':
    main()
