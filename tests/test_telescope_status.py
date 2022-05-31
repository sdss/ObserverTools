#!/usr/bin/env python3
import pytest
from pathlib import Path
from bin import telescope_status
import signal


class TestTelStatus():

    @staticmethod
    def handler(signum, frame):
        print('Exiting call')
        raise TimeoutError('The function reached timeout without other errors')

    # This is problematic, it needs to be switched to a multiprocessing style
    # def test_print(self):
    #     signal.signal(signal.SIGALRM, self.handler)
    #     signal.alarm(10)
    #     telescope_status.main()


if __name__ == '__main__':
    pytest.main()
