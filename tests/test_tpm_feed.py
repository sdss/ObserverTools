#!/usr/bin/env python3
import unittest
import signal
from pathlib import Path
import tpm_feed


class TestTPMFeed(unittest.TestCase):
    def setUp(self):
        self.file = Path(__file__).absolute().parent.parent / 'bin/tpm_feed.py'

        class DummyArgs(object):
            pass

        self.args = DummyArgs()
        self.args.channels = ['dewar_sp1_lb']
        self.args.plot = True
        self.args.verbose = True
        self.args.version = False
        self.args.dt = 5
        self.args.list_channels = False

    @staticmethod
    def handler(signum, frame):
        print('Exiting call')
        raise TimeoutError('The function reached timeout without other errors')

    def test_print(self):
        signal.signal(signal.SIGALRM, self.handler)
        signal.alarm(10)
        self.args.version = True
        try:
            pass
            tpm_feed.main(args=self.args)
        except TimeoutError as t:
            print(t)

    def test_list_channels(self):
        self.args.plot = False
        self.args.list_channels = True
        signal.signal(signal.SIGALRM, self.handler)
        signal.alarm(10)
        tpm_feed.main(args=self.args)


if __name__ == '__main__':
    unittest.main()
