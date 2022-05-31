#!/usr/bin/env python3
import pytest
import signal
from pathlib import Path
from bin import tpm_feed


class DummyArgs(object):
    pass


args = DummyArgs()
args.channels = ['dewar_sp1_lb']
args.plot = True
args.verbose = True
args.version = False
args.dt = 5
args.list_channels = False


class TestTPMFeed():
    @staticmethod
    def handler(signum, frame):
        print('Exiting call')
        raise TimeoutError('The function reached timeout without other errors')

    def test_print(self):
        signal.signal(signal.SIGALRM, self.handler)
        signal.alarm(10)
        args.version = True
        try:
            pass
            # TODO These tests fail if tpmdata.packet(1, 1) cannot close. This
            # function cannot be caught with a signal timeout, another method
            # is needed
            # tpm_feed.main(args=self.args)
        except TimeoutError as t:
            print(t)

    def test_list_channels(self):
        args.plot = False
        args.list_channels = True
        signal.signal(signal.SIGALRM, self.handler)
        signal.alarm(10)
        try:
            pass
            # tpm_feed.main(args=self.args)
        except TimeoutError as t:
            print(t)


if __name__ == '__main__':
    pytest.main()
