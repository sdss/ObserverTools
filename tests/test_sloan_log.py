#!/usr/bin/env python3
import unittest
from pathlib import Path
import sloan_log, sjd


class TestSloanLog(unittest.TestCase):

    def test_directory(self):
        """Checks to see if the directory for new data is available to this
        computer"""
        ap_data_dir = sloan_log.ap_dir
        b_data_dir = sloan_log.b_dir
        print(ap_data_dir, b_data_dir)
        self.assertTrue(Path(ap_data_dir).exists())
        self.assertTrue(Path(b_data_dir).exists())

    def setUp(self) -> None:

        class Dummy(object):
            pass

        self.args = Dummy()

    def test_known_data(self):
        """Runs on an old dataset that I know used to run successfully"""

        self.args.sjd = 59011
        self.args.print = True
        self.args.summary = True
        self.args.data = True
        self.args.boss = True
        self.args.apogee = True
        self.args.p_boss = True
        self.args.p_apogee = True
        self.args.log_support = True
        self.args.morning = False
        self.args.verbose = True
        self.args.noprogress = False
        self.args.mirrors = True
        self.args.telstatus = True
        self.args.legacy_aptest = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, self.args)
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

        self.args.sjd = 59011
        self.args.print = False
        self.args.summary = False
        self.args.data = False
        self.args.boss = True
        self.args.apogee = False
        self.args.p_boss = True
        self.args.p_apogee = False
        self.args.log_support = False
        self.args.morning = False
        self.args.verbose = True
        self.args.mirrors = False
        self.args.telstatus = False
        self.args.legacy_aptest = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, self.args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.p_boss()

    def test_known_data_apogee(self):
        """Runs on an old dataset that I know used to run successfully, this one
        only checks APOGEE and prints its summary
        """

        self.args.sjd = 59011
        self.args.print = False
        self.args.summary = False
        self.args.data = False
        self.args.boss = False
        self.args.apogee = True
        self.args.p_boss = False
        self.args.p_apogee = True
        self.args.log_support = False
        self.args.morning = False
        self.args.verbose = True
        self.args.morrors = False
        self.args.telstatus = False
        self.args.legacy_aptest = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, self.args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.p_apogee()

    def test_log_support(self):
        """Runs on an old dataset that I know used to run successfully"""

        self.args.sjd = 59011
        self.args.print = False
        self.args.summary = False
        self.args.data = False
        self.args.boss = False
        self.args.apogee = False
        self.args.p_boss = False
        self.args.p_apogee = False
        self.args.log_support = True
        self.args.morning = False
        self.args.verbose = True
        self.args.mirrors = False
        self.args.telstatus = False
        self.args.legacy_aptest = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, self.args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.log_support()

    def test_log_support_today(self):
        """Runs on an old dataset that I know used to run successfully"""

        self.args.sjd = sjd.sjd()
        self.args.print = False
        self.args.summary = False
        self.args.data = False
        self.args.boss = False
        self.args.apogee = False
        self.args.p_boss = False
        self.args.p_apogee = False
        self.args.log_support = True
        self.args.morning = False
        self.args.verbose = True
        self.args.mirrors = False
        self.args.telstatus = False
        self.args.legacy_aptest = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, self.args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.log_support()

    def test_mirror_numbers(self):
        """Runs on an old dataset that I know used to run successfully"""

        self.args.sjd = sjd.sjd()
        self.args.print = False
        self.args.summary = False
        self.args.data = False
        self.args.boss = False
        self.args.apogee = False
        self.args.p_boss = False
        self.args.p_apogee = False
        self.args.log_support = False
        self.args.morning = False
        self.args.verbose = True
        self.args.mirrors = True
        self.args.telstatus = False
        self.args.legacy_aptest = False

        ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
        b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
        ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
        b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
        log = sloan_log.Logging(ap_images, b_images, self.args)
        log.parse_images()
        log.sort()
        log.count_dithers()
        log.log_support()
        log.mirror_numbers()


def test_tel_status(self):
    """Test telstatus integration"""

    self.args.sjd = sjd.sjd()
    self.args.print = False
    self.args.summary = False
    self.args.data = False
    self.args.boss = False
    self.args.apogee = False
    self.args.p_boss = False
    self.args.p_apogee = False
    self.args.log_support = False
    self.args.morning = False
    self.args.verbose = True
    self.args.mirrors = False
    self.args.telstatus = True
    self.args.legacy_aptest = False

    ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
    b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
    ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
    b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
    log = sloan_log.Logging(ap_images, b_images, self.args)
    log.parse_images()
    log.sort()
    log.count_dithers()
    log.log_support()


def test_legacy_aptest(self):
    """Test utr_cdr-based aptest that matches the old aptest script"""

    class Dummy(object):
        pass

    args = Dummy()
    self.args.sjd = sjd.sjd()
    self.args.print = False
    self.args.summary = False
    self.args.data = True
    self.args.boss = False
    self.args.apogee = False
    self.args.p_boss = False
    self.args.p_apogee = False
    self.args.log_support = False
    self.args.morning = False
    self.args.verbose = True
    self.args.mirrors = False
    self.args.telstatus = False
    self.args.legacy_aptest = True

    ap_data_dir = sloan_log.ap_dir / '{}'.format(self.args.sjd)
    b_data_dir = sloan_log.b_dir / '{}'.format(self.args.sjd)
    ap_images = list(Path(ap_data_dir).glob('apR-a*.apz'))
    b_images = list(Path(b_data_dir).glob('sdR-r1*fit.gz'))
    log = sloan_log.Logging(ap_images, b_images, self.args)
    log.parse_images()
    log.sort()
    log.count_dithers()
    log.p_data()


if __name__ == '__main__':
    unittest.main()
