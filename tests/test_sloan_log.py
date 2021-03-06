#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import sloan_log


class TestSloanLog(unittest.TestCase):

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        ap_data_dir = sloan_log.ap_dir
        b_data_dir = sloan_log.b_dir
        self.assertTrue(Path(ap_data_dir).exists())
        self.assertTrue(Path(b_data_dir).exists())

    def test_known_data(self):
        """Runs on an old dataset that I know used to run successfully"""

        class Dummy(object):
            pass

        args = Dummy()
        args.mjd = 59011
        args.print = True
        args.summary = True
        args.data = True
        args.boss = True
        args.apogee = True
        args.p_boss = True
        args.p_apogee = True
        args.log_support = True
        args.morning = False
        args.verbose = True
        args.noprogress = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(args.mjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(args.mjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.p_summary()
        log.p_data()
        log.p_boss()
        log.p_apogee()
        log.log_support()

    def test_known_data_boss(self):
        """Runs on an old dataset that I know used to run successfully, this one
        only runs BOSS data summary
        """

        class Dummy(object):
            pass

        args = Dummy()
        args.mjd = 59011
        args.print = False
        args.summary = False
        args.data = False
        args.boss = True
        args.apogee = False
        args.p_boss = True
        args.p_apogee = False
        args.log_support = False
        args.morning = False
        args.verbose = True

        ap_data_dir = sloan_log.ap_dir / '{}'.format(args.mjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(args.mjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.p_boss()

    def test_known_data_apogee(self):
        """Runs on an old dataset that I know used to run successfully, this one
        only checks APOGEE and prints its summary
        """

        class Dummy(object):
            pass

        args = Dummy()
        args.mjd = 59011
        args.print = False
        args.summary = False
        args.data = False
        args.boss = False
        args.apogee = True
        args.p_boss = False
        args.p_apogee = True
        args.log_support = False
        args.morning = False
        args.verbose = True

        ap_data_dir = sloan_log.ap_dir / '{}'.format(args.mjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(args.mjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.p_apogee()

    def test_known_data_log_support(self):
        """Runs on an old dataset that I know used to run successfully"""

        class Dummy(object):
            pass

        args = Dummy()
        args.mjd = 59011
        args.print = False
        args.summary = False
        args.data = False
        args.boss = False
        args.apogee = False
        args.p_boss = False
        args.p_apogee = False
        args.log_support = True
        args.morning = False
        args.verbose = True

        ap_data_dir = sloan_log.ap_dir / '{}'.format(args.mjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(args.mjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.log_support()


if __name__ == '__main__':
    unittest.main()
