#!/usr/bin/env python3
import unittest
from pathlib import Path
from astropy.time import Time
from bin import sloan_log


class TestSloanLog(unittest.TestCase):
    def test_no_args(self):
        class dummy(object):
            pass
        args = dummy()
        args.today = True
        args.mjd = int(Time.now().mjd + 0.3)
        # args.print = 
        # args.summary = True
        # args.data = True
        args.boss = False
        args.apogee = False
        # args.p_boss = True
        # args.p_apogee = True
        # args.log_support = True
        ap_data_dir = sloan_log.ap_dir / '{}'.format(args.mjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(args.mjd)
        ap_images = Path(ap_data_dir).glob('apR-a*.apz')
        b_images = Path(b_data_dir).glob('sdR-r1*fit.gz')
        log = sloan_log.Logging(ap_images, b_images, args)
        log.parse_images()
        log.sort()
        log.count_dithers()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        ap_data_dir = sloan_log.ap_dir
        b_data_dir = sloan_log.b_dir
        self.assertTrue(Path(ap_data_dir).exists())
        self.assertTrue(Path(b_data_dir).exists())

    def test_old_known_data(self):
        """Runs on an old dataset that I know used to run successfully"""
        class dummy(object):
            pass
        args = dummy()
        args.mjd = 58900
        args.print = True
        args.summary = True
        args.data = True
        args.boss = True
        args.apogee = True
        args.p_boss = True
        args.p_apogee = True
        args.log_support = True
        args.morning = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(args.mjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(args.mjd)
        ap_images = Path(ap_data_dir).glob('apR-a*.apz')
        b_images = Path(b_data_dir).glob('sdR-r1*fit.gz')
        log = sloan_log.Logging(ap_images, b_images, args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.p_summary()
        log.p_data()
        log.p_boss()
        log.p_apogee()
        log.log_support()


if __name__ == '__main__':
    unittest.main()

