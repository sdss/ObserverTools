#!/usr/bin/env python3
import unittest
from pathlib import Path
from bin import sloan_log


class TestSloanLog(unittest.TestCase):
    def test_no_args(self):
        sloan_log.main()

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        log = sloan_log.main()
        self.assertTrue(Path(log.ap_images).exists())
        self.assertTrue(Path(log.b_images).exists())

    def test_old_known_data(self):
        """Runs on an old dataset that I know used to run successfully"""
        args = sloan_log.parseargs()
        args.mjd = 58900
        args.print = True
        args.summary = True
        args.data = True
        args.boss = True
        args.apogee = True
        args.p_boss = True
        args.p_apogee = True
        args.log_support = True

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
