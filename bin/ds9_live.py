#!/usr/bin/env python3
"""
Description:	Opens and continuously updates ds9 with the latest file. Run
ds9_live.py -h for details.

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
import hashlib
import pyds9
import time

default_dir = Path('/data/apogee/utr_cdr/')
boss_cams = ['r1', 'r2', 'b1', 'b2']

__version__ = 3.0


class DS9Window:
    """Displays the last image in a given directory in ds9
    inputs:
    name: The name of the window, it will add the fits dir and a hash onto this
        in the actual window
    fits_dir: a directory of dated folders where images are stored
    regex: The formatting of the fits images we want to display
    scale: The image scale
    zoom: The image zoom
    verbose: A debugging tool
    """

    def __init__(self, name, fits_dir, regex, scale, zoom, verbose):

        # Constants and variables

        self.last_file = ''

        # Arguments
        self.name = name
        self.fits_dir = Path(fits_dir)
        self.regex = regex
        self.scale = scale
        self.zoom = zoom
        self.verbose = verbose

        hsh = hashlib.sha1(''.join(self.name + str(self.fits_dir) + self.regex
                                   + self.scale).encode())
        self.ds9_target = '{}: {}: {}'.format(self.name, self.fits_dir,
                                              hsh.hexdigest()[:10])

        if self.verbose:
            print('dir = {}\nName = {}\nscale = {}\nzoom = {}'.format(
                self.fits_dir, self.name, self.scale,
                self.zoom))

        # Initialize

        self.ds9 = pyds9.DS9(self.name)

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

        for file in Path(self.fits_dir).glob('*'):
            file = file.absolute()

            if file.is_dir():

                # Store the name and mtime of only the latest FITS file, reads
                # through every file, checks its mtime, and keeps the most
                # recent for the return

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

            if self.zoom:
                self.ds9.set('zoom to {}'.format(self.zoom))

            if self.scale:
                self.ds9.set('scale {}'.format(self.scale))

    def update(self):
        """Update the display"""

        file = self.latest_fits_file(self.regex)
        if self.verbose:
            print('latest fits file = {}, last fits file = {}'
                  ''.format(file, self.last_file))

        if file != self.last_file:
            if self.verbose:
                print('displaying {}'.format(file))
            # Because BOSS has 4 cameras, it must loop 4 times
            if self.name == 'BOSS':
                for i, cam in enumerate(boss_cams):
                    self.display(file.replace('r1', cam), i)
            else:
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
    parser.add_argument('-a', '--apogee', action='store_true',
                        help='If included, will display APOGEE images.'
                             ' Overrides most arguments')
    parser.add_argument('-b', '--boss', action='store_true',
                        help='If included, will display BOSS images.'
                             ' Overrides most arguments')
    parser.add_argument('-d', '--directory', dest='fits_dir',
                        default=default_dir, type=str,
                        help='Set FITS data directory. It needs to be a'
                             'directory of dated folders, where the newest'
                             'folder has the newest data.'
                             ' Default is {}'.format(default_dir))

    parser.add_argument('-e', '--ecam', action='store_true',
                        help='If included, will display engineering camera'
                             'images. Overrides most arguments.')
    parser.add_argument('-g', '--guider', action='store_true',
                        help='If included, will display guider images.'
                             ' Overrides most arguments.')
    parser.add_argument('-i', '--interval', dest='interval', default=60,
                        type=int, help='Set the refresh rate.	Default is 5'
                                       'seconds. Refreshes will be this '
                                       'number  of seconds apart.')
    parser.add_argument('-n', '--name', dest='name', default='Scanner',
                        type=str,
                        help='Set ds9 Window name. Default is autogenerated.')
    parser.add_argument('-r', '--regex', default='apRaw*',
                        help='A regex to match the fits files, default is'
                             ' {}'.format('apRaw*'))
    parser.add_argument('-s', '--scale', dest='scale', default='histequ',
                        type=str, help='Set scaling. Default is "histequ"')

    parser.add_argument('--version', action='store_true', help='Version info')

    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        default=False,
                        help='Be verbose. Default is to be quiet.')
    parser.add_argument('-z', '--zoom', dest='zoom', default='1.0',
                        type=str, help='Set zoom factor. Default is 1.0')

    args = parser.parse_args()

    if args.verbose:
        print('interval = {}'.format(args.interval))
        print('scale = {}'.format(args.scale))
        print('zoom = {}'.format(args.zoom))

    if args.version:
        print(__version__)

    if args.apogee and args.boss:
        raise Exception('Cannot do both boss and apogee')

    if args.apogee:
        if Path('/summary-ics/').exists():
            args.fits_dir = Path('/summary-ics')
        else:
            args.fits_dir = Path('/data/apogee/utr_cdr/')
        args.name = 'APOGEE'
        # TODO set these to better values
        args.scale = args.scale
        args.zoom = args.zoom

    elif args.boss:
        args.fits_dir = Path('/data/spectro/')
        args.name = 'BOSS'
        args.scale = args.scale
        args.zoom = args.zoom
        args.regex = 'sdR-r1*'

    elif args.guider:
        args.fits_dir = Path('/data/gcam/')
        args.name = 'Guider Camera'
        args.scale = args.scale
        args.zoom = args.zoom
        args.regex = 'gimg-*'

    elif args.ecam:
        args.fits_dir = Path('/data/gcam/')
        args.name = 'Engineering Camera'
        args.scale = args.scale
        args.zoom = args.zoom
        args.regex = 'proc-gimg-*'

    return args


def main():
    args = parseargs()
    # Start the display
    window = DS9Window(args.name, args.fits_dir, args.regex, args.scale,
                       args.zoom, args.verbose)
    while True:
        window.update()

        time.sleep(args.interval)


if __name__ == '__main__':
    main()
